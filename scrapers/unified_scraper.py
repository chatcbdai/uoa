"""
Unified scraper implementation with strategy pattern
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from urllib.parse import urlparse, urljoin, urldefrag
from datetime import datetime

from browser import BrowserFactory, BrowserError
from processors import ContentProcessor, ContentProcessorError
from storage import SQLiteStorage, StorageError
from utils.network import NetworkManager

logger = logging.getLogger(__name__)

class ScraperError(Exception):
    """Base exception for scraper errors"""
    pass

class UnifiedScraper:
    """
    Unified scraper that handles all scraping patterns.
    Uses strategy pattern to support different scraping modes.
    """
    
    def __init__(
        self,
        engine: str = "stealth",
        anti_detection: bool = True,
        headless: bool = True,
        rate_limit: float = 1.0,
        concurrent_requests: int = 3,
        output_format: str = "markdown",
        output_dir: Optional[Path] = None,
        storage_path: Optional[Path] = None,
        timeout: int = 30000,
        **kwargs
    ):
        """
        Initialize the unified scraper.
        
        Args:
            engine: Browser engine to use
            anti_detection: Enable anti-detection features
            headless: Run browser in headless mode
            rate_limit: Requests per second
            concurrent_requests: Number of concurrent requests
            output_format: Output format (markdown, json, html)
            output_dir: Directory to save scraped content
            storage_path: Path to SQLite database
            timeout: Request timeout in milliseconds
            **kwargs: Additional browser options
        """
        self.engine = engine
        self.anti_detection = anti_detection
        self.headless = headless
        self.rate_limit = rate_limit
        self.concurrent_requests = concurrent_requests
        self.output_format = output_format
        self.output_dir = output_dir or Path.cwd() / "storage" / "scraped_content"
        self.timeout = timeout
        self.browser_kwargs = kwargs
        
        # Initialize components
        self.browser = None
        self.content_processor = ContentProcessor()
        self.network_manager = NetworkManager()
        self.storage = SQLiteStorage(storage_path)
        
        # Scraping state
        self.scraped_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self._semaphore = asyncio.Semaphore(concurrent_requests)
        
        # Configure rate limiter
        self.network_manager.rate_limiter.rate_limit = rate_limit
    
    def get_file_extension(self):
        """Get the appropriate file extension for the output format"""
        extension_map = {
            "markdown": "md",
            "html": "html",
            "json": "json"
        }
        return extension_map.get(self.output_format, self.output_format)
    
    async def initialize(self):
        """Initialize the browser"""
        if not self.browser:
            self.browser = BrowserFactory.create(
                engine=self.engine,
                headless=self.headless,
                anti_detection=self.anti_detection,
                **self.browser_kwargs
            )
            await self.browser.initialize()
            logger.info(f"Initialized {self.engine} browser engine")
    
    async def cleanup(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.storage:
            self.storage.close()
        
        logger.info("Scraper cleanup completed")
    
    async def scrape(self, url: str, mode: str = "auto") -> Dict[str, Any]:
        """
        Main scraping method that handles all modes.
        
        Args:
            url: URL to scrape (can include wildcards)
            mode: Scraping mode (auto, single, wildcard, full_site, docs)
            
        Returns:
            Dictionary with scraping results
        """
        start_time = datetime.now()
        
        try:
            # Initialize browser if needed
            await self.initialize()
            
            # Auto-detect mode if needed
            if mode == "auto":
                mode = self.content_processor.detect_url_type(url)
                logger.info(f"Auto-detected mode: {mode}")
            
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Execute appropriate scraping strategy
            if mode == "single":
                result = await self._scrape_single_url(url)
            elif mode == "wildcard":
                result = await self._scrape_wildcard(url)
            elif mode == "full_site":
                result = await self._scrape_full_site(url)
            elif mode == "docs":
                result = await self._scrape_documentation(url)
            else:
                raise ScraperError(f"Unknown scraping mode: {mode}")
            
            # Calculate statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Get storage stats
            storage_stats = self.storage.get_stats()
            
            return {
                'success': True,
                'mode': mode,
                'url': url,
                'pages_scraped': len(self.scraped_urls),
                'pages_failed': len(self.failed_urls),
                'duration_seconds': duration,
                'output_dir': str(self.output_dir),
                'storage_stats': storage_stats,
                **result
            }
            
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'mode': mode,
                'url': url,
                'pages_scraped': len(self.scraped_urls),
                'pages_failed': len(self.failed_urls)
            }
    
    async def _scrape_single_url(self, url: str) -> Dict[str, Any]:
        """Scrape a single URL"""
        logger.info(f"Scraping single URL: {url}")
        
        content = await self._scrape_page(url)
        if content:
            # Save to file
            filename = self.content_processor.clean_filename(urlparse(url).path.split('/')[-1] or 'index')
            filepath = self.output_dir / f"{filename}.{self.get_file_extension()}"
            
            if self.output_format == "markdown":
                await self.content_processor.save_as_markdown(content['soup'], filepath)
            else:
                # Save as HTML or other format
                filepath.write_text(content['html'], encoding='utf-8')
            
            return {
                'files_created': [str(filepath)],
                'content_length': len(content['text'])
            }
        
        return {'files_created': [], 'content_length': 0}
    
    async def _scrape_wildcard(self, url_pattern: str) -> Dict[str, Any]:
        """Scrape URLs matching a wildcard pattern"""
        logger.info(f"Scraping wildcard pattern: {url_pattern}")
        
        # Extract base URL
        base_url = url_pattern.split('*')[0].rstrip('/')
        
        # Start with base URL
        urls_to_scrape = {base_url}
        files_created = []
        
        while urls_to_scrape:
            # Get next batch of URLs
            batch = set()
            for _ in range(min(self.concurrent_requests, len(urls_to_scrape))):
                if urls_to_scrape:
                    batch.add(urls_to_scrape.pop())
            
            # Scrape batch concurrently
            tasks = [self._scrape_page_with_links(url, url_pattern) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to scrape {url}: {result}")
                    self.failed_urls.add(url)
                    continue
                
                if result:
                    # Save content
                    filename = self.content_processor.clean_filename(urlparse(url).path.split('/')[-1] or 'index')
                    filepath = self.output_dir / f"{filename}.{self.get_file_extension()}"
                    
                    if self.output_format == "markdown":
                        await self.content_processor.save_as_markdown(result['soup'], filepath)
                    else:
                        filepath.write_text(result['html'], encoding='utf-8')
                    
                    files_created.append(str(filepath))
                    
                    # Add new URLs matching pattern
                    for link in result['links']:
                        if self._matches_pattern(link, url_pattern) and link not in self.scraped_urls:
                            urls_to_scrape.add(link)
        
        return {'files_created': files_created}
    
    async def _scrape_full_site(self, base_url: str) -> Dict[str, Any]:
        """Scrape an entire website"""
        logger.info(f"Scraping full site: {base_url}")
        
        # Parse domain
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Start with base URL
        urls_to_scrape = {base_url}
        files_created = []
        
        while urls_to_scrape and len(self.scraped_urls) < 1000:  # Limit to prevent infinite crawling
            # Get next batch
            batch = set()
            for _ in range(min(self.concurrent_requests, len(urls_to_scrape))):
                if urls_to_scrape:
                    batch.add(urls_to_scrape.pop())
            
            # Scrape batch
            tasks = [self._scrape_page_with_links(url, domain) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to scrape {url}: {result}")
                    self.failed_urls.add(url)
                    continue
                
                if result:
                    # Create folder structure based on URL path
                    url_path = urlparse(url).path.strip('/')
                    if url_path:
                        file_dir = self.output_dir / Path(url_path).parent
                        file_dir.mkdir(parents=True, exist_ok=True)
                        filename = Path(url_path).name or 'index'
                    else:
                        file_dir = self.output_dir
                        filename = 'index'
                    
                    filepath = file_dir / f"{self.content_processor.clean_filename(filename)}.{self.get_file_extension()}"
                    
                    if self.output_format == "markdown":
                        await self.content_processor.save_as_markdown(result['soup'], filepath)
                    else:
                        filepath.write_text(result['html'], encoding='utf-8')
                    
                    files_created.append(str(filepath))
                    
                    # Add new URLs from same domain
                    for link in result['links']:
                        if link.startswith(domain) and link not in self.scraped_urls:
                            urls_to_scrape.add(link)
        
        return {'files_created': files_created}
    
    async def _scrape_documentation(self, url: str) -> Dict[str, Any]:
        """Scrape documentation with special handling"""
        # For now, use wildcard scraping for docs
        if '*' not in url:
            url = url.rstrip('/') + '/*'
        
        return await self._scrape_wildcard(url)
    
    async def _scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single page and return content"""
        if url in self.scraped_urls:
            return None
        
        async with self._semaphore:
            try:
                # Rate limiting
                await self.network_manager.rate_limiter.acquire()
                
                # Navigate to URL
                logger.info(f"Navigating to: {url}")
                await self.browser.navigate(url)
                
                # Get page content
                html = await self.browser.get_content()
                
                # Extract content
                soup, html_element = self.content_processor.extract_content(html)
                text = soup.get_text(strip=True)
                
                # Save to storage
                title = await self.browser.execute_js("document.title")
                self.storage.save_content(
                    url=url,
                    content=text,
                    html=html,
                    title=title,
                    content_type="html",
                    metadata={'scraped_at': datetime.now().isoformat()}
                )
                
                self.scraped_urls.add(url)
                logger.info(f"Successfully scraped: {url}")
                
                return {
                    'url': url,
                    'html': html,
                    'text': text,
                    'soup': soup,
                    'title': title
                }
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
                self.failed_urls.add(url)
                return None
    
    async def _scrape_page_with_links(self, url: str, base_pattern: str) -> Optional[Dict[str, Any]]:
        """Scrape a page and extract links"""
        content = await self._scrape_page(url)
        
        if content:
            # Extract links from the original HTML, not the processed soup
            from bs4 import BeautifulSoup
            full_soup = BeautifulSoup(content['html'], 'lxml')
            links = self.content_processor.extract_links(full_soup, url)
            logger.info(f"Extracted {len(links)} total links from {url}")
            
            # Filter links based on pattern
            if '*' in base_pattern:
                # Wildcard pattern
                filtered_links = [
                    link for link in links
                    if self._matches_pattern(link, base_pattern)
                ]
            else:
                # Domain pattern
                filtered_links = [
                    link for link in links
                    if link.startswith(base_pattern)
                ]
            
            # Save links to storage
            self.storage.save_links(url, [{'url': link} for link in filtered_links])
            
            content['links'] = filtered_links
            
        return content
    
    def _matches_pattern(self, url: str, pattern: str) -> bool:
        """Check if URL matches wildcard pattern"""
        if '*' not in pattern:
            return url.startswith(pattern)
        
        # Simple wildcard matching
        base = pattern.split('*')[0]
        return url.startswith(base)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()