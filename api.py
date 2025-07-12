"""
Undetectable Toolkit - Main Public API

Simple, unified interface for web browsing and scraping with anti-detection.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from contextlib import asynccontextmanager, contextmanager
from urllib.parse import urlparse

from browser import BrowserFactory, UndetectableBrowser
from scrapers import UnifiedScraper
from utils import get_random_user_agent

# Configuration class
class UndetectableConfig:
    """Global configuration for the undetectable toolkit"""
    
    def __init__(
        self,
        engine: str = "stealth",
        anti_detection: bool = True,
        headless: bool = True,
        rate_limit: float = 1.0,
        concurrent_requests: int = 3,
        storage: str = "sqlite",
        storage_path: Optional[Path] = None,
        timeout: int = 30000,
        proxy: Optional[str] = None,
        log_level: str = "INFO",
        **kwargs
    ):
        self.engine = engine
        self.anti_detection = anti_detection
        self.headless = headless
        self.rate_limit = rate_limit
        self.concurrent_requests = concurrent_requests
        self.storage = storage
        self.storage_path = storage_path or Path.cwd() / "storage" / "scraping.db"
        self.timeout = timeout
        self.proxy = proxy
        self.log_level = log_level
        self.extra_options = kwargs
        
        # Apply logging configuration
        import logging
        logging.basicConfig(level=getattr(logging, log_level))
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'engine': self.engine,
            'anti_detection': self.anti_detection,
            'headless': self.headless,
            'rate_limit': self.rate_limit,
            'concurrent_requests': self.concurrent_requests,
            'storage': self.storage,
            'storage_path': str(self.storage_path),
            'timeout': self.timeout,
            'proxy': self.proxy,
            'log_level': self.log_level,
            **self.extra_options
        }

# Global configuration instance
_global_config = UndetectableConfig()

def set_config(config: UndetectableConfig):
    """Set global configuration"""
    global _global_config
    _global_config = config

# Main API functions

async def scrape_async(
    url: str,
    mode: str = "auto",
    output_format: str = "markdown",
    output_dir: Optional[Path] = None,
    anti_detection: Optional[bool] = None,
    engine: Optional[str] = None,
    headless: Optional[bool] = None,
    rate_limit: Optional[float] = None,
    concurrent: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Async version of scrape function.
    
    Args:
        url: URL to scrape (can include wildcards)
        mode: Scraping mode (auto, single, wildcard, full_site, docs)
        output_format: Output format (markdown, json, html)
        output_dir: Directory to save scraped content
        anti_detection: Enable anti-detection features
        engine: Browser engine to use
        headless: Run browser in headless mode
        rate_limit: Requests per second
        concurrent: Number of concurrent requests
        **kwargs: Additional options
        
    Returns:
        Dictionary with scraping results
    """
    # Use provided values or fall back to global config
    config = _global_config
    anti_detection = anti_detection if anti_detection is not None else config.anti_detection
    engine = engine or config.engine
    headless = headless if headless is not None else config.headless
    rate_limit = rate_limit or config.rate_limit
    concurrent = concurrent or config.concurrent_requests
    
    # Create scraper instance
    scraper = UnifiedScraper(
        engine=engine,
        anti_detection=anti_detection,
        headless=headless,
        rate_limit=rate_limit,
        concurrent_requests=concurrent,
        output_format=output_format,
        output_dir=output_dir,
        **kwargs
    )
    
    try:
        # Auto-detect mode if not specified
        if mode == "auto":
            if "*" in url:
                mode = "wildcard"
            elif url.endswith("/"):
                mode = "full_site"
            else:
                mode = "single"
        
        # Perform scraping
        result = await scraper.scrape(url, mode=mode)
        return result
    finally:
        await scraper.cleanup()

def scrape(
    url: str,
    mode: str = "auto",
    output_format: str = "markdown",
    output_dir: Optional[Path] = None,
    anti_detection: Optional[bool] = None,
    engine: Optional[str] = None,
    headless: Optional[bool] = None,
    rate_limit: Optional[float] = None,
    concurrent: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main scraping function that handles all scraping patterns.
    
    Args:
        url: URL to scrape (can include wildcards like https://example.com/docs/*)
        mode: Scraping mode - auto-detected if not specified
        output_format: Format for scraped content
        output_dir: Directory to save scraped content
        anti_detection: Enable anti-detection features
        engine: Browser engine to use
        headless: Run browser in headless mode
        rate_limit: Requests per second
        concurrent: Number of concurrent requests
        **kwargs: Additional engine-specific options
        
    Returns:
        Dictionary with scraping results and metadata
    """
    # Run async function in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            scrape_async(
                url, mode, output_format, output_dir,
                anti_detection, engine, headless,
                rate_limit, concurrent, **kwargs
            )
        )
    finally:
        loop.close()

@asynccontextmanager
async def browse_async(
    engine: Optional[str] = None,
    headless: Optional[bool] = None,
    anti_detection: Optional[bool] = None,
    proxy: Optional[str] = None,
    **kwargs
):
    """
    Async context manager for browser automation.
    
    Example:
        async with browse_async() as browser:
            await browser.navigate("https://example.com")
            content = await browser.get_content()
    """
    config = _global_config
    engine = engine or config.engine
    headless = headless if headless is not None else config.headless
    anti_detection = anti_detection if anti_detection is not None else config.anti_detection
    proxy = proxy or config.proxy
    
    browser = BrowserFactory.create(
        engine=engine,
        headless=headless,
        anti_detection=anti_detection,
        proxy=proxy,
        **kwargs
    )
    
    try:
        await browser.initialize()
        yield browser
    finally:
        await browser.close()

@contextmanager
def browse(
    engine: Optional[str] = None,
    headless: Optional[bool] = None,
    anti_detection: Optional[bool] = None,
    proxy: Optional[str] = None,
    **kwargs
):
    """
    Context manager for browser automation with anti-detection.
    
    Example:
        with browse(headless=False) as browser:
            browser.visit("https://example.com")
            browser.fill_form({"#username": "user", "#password": "pass"})
            browser.click("#submit")
            content = browser.get_content()
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        browser = None
        
        async def _create_browser():
            nonlocal browser
            async with browse_async(engine, headless, anti_detection, proxy, **kwargs) as b:
                browser = b
                # Keep the browser alive
                await asyncio.Event().wait()
        
        # Start browser in background
        task = loop.create_task(_create_browser())
        
        # Wait for browser to be ready
        while browser is None and not task.done():
            loop.run_until_complete(asyncio.sleep(0.1))
        
        if task.done() and browser is None:
            # Task completed without creating browser
            raise Exception("Failed to create browser")
        
        # Create synchronous wrapper
        from .browser.sync_wrapper import SyncBrowserWrapper
        sync_browser = SyncBrowserWrapper(browser, loop)
        
        yield sync_browser
        
    finally:
        # Cancel the browser task
        if 'task' in locals():
            task.cancel()
        loop.run_until_complete(asyncio.sleep(0.1))
        loop.close()

async def download_async(
    url: str,
    save_path: Optional[Path] = None,
    anti_detection: Optional[bool] = None,
    engine: Optional[str] = None,
    **kwargs
) -> Path:
    """Async version of download function"""
    async with browse_async(engine=engine, anti_detection=anti_detection, **kwargs) as browser:
        result = await browser.download(url, save_path)
        if result:
            return result
        raise Exception(f"Failed to download {url}")

def download(
    url: str,
    save_path: Optional[Path] = None,
    anti_detection: Optional[bool] = None,
    engine: Optional[str] = None,
    **kwargs
) -> Path:
    """Download a file with anti-detection"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            download_async(url, save_path, anti_detection, engine, **kwargs)
        )
    finally:
        loop.close()

async def search_async(
    query: str,
    search_engine: str = "google",
    num_results: int = 10,
    anti_detection: Optional[bool] = None,
    engine: Optional[str] = None,
    **kwargs
) -> List[Dict[str, str]]:
    """Async version of search function"""
    async with browse_async(engine=engine, anti_detection=anti_detection, **kwargs) as browser:
        results = await browser.search(query, search_engine)
        return results[:num_results]

def search(
    query: str,
    search_engine: str = "google",
    num_results: int = 10,
    anti_detection: Optional[bool] = None,
    engine: Optional[str] = None,
    **kwargs
) -> List[Dict[str, str]]:
    """Search the web with anti-detection"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            search_async(query, search_engine, num_results, anti_detection, engine, **kwargs)
        )
    finally:
        loop.close()

async def screenshot_async(
    url: str,
    save_path: Optional[Path] = None,
    full_page: bool = False,
    anti_detection: Optional[bool] = None,
    engine: Optional[str] = None,
    **kwargs
) -> Path:
    """Async version of screenshot function"""
    async with browse_async(engine=engine, anti_detection=anti_detection, **kwargs) as browser:
        await browser.navigate(url)
        screenshot_bytes = await browser.take_screenshot(full_page=full_page)
        
        if not save_path:
            save_path = Path.cwd() / f"screenshot_{urlparse(url).netloc}.png"
        
        save_path.write_bytes(screenshot_bytes)
        return save_path

def screenshot(
    url: str,
    save_path: Optional[Path] = None,
    full_page: bool = False,
    anti_detection: Optional[bool] = None,
    engine: Optional[str] = None,
    **kwargs
) -> Path:
    """Take a screenshot of a webpage"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            screenshot_async(url, save_path, full_page, anti_detection, engine, **kwargs)
        )
    finally:
        loop.close()

async def post_to_social_async(
    platforms: Union[str, List[str]],
    text: Optional[str] = None,
    image_path: Optional[str] = None,
    hashtags: Optional[str] = None,
    use_csv: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Post content to social media platforms.
    
    Args:
        platforms: Platform name(s) - 'instagram', 'twitter', 'facebook', 'linkedin'
        text: Post text content
        image_path: Path to image file
        hashtags: Hashtags to include
        use_csv: Read posts from CSV file instead
        **kwargs: Additional platform-specific options
        
    Returns:
        Dictionary with posting results for each platform
    """
    # Import here to avoid circular imports
    from social_media import SocialMediaOrchestrator
    
    # Ensure platforms is a list
    if isinstance(platforms, str):
        platforms = [platforms]
    
    # Get LLM client
    # Import the main config to get LLM settings
    from config import config as main_config
    if main_config.llm.default_provider == "openai":
        from llm.openai_client import OpenAIClient
        llm_client = OpenAIClient()
    else:
        from llm.anthropic_client import AnthropicClient
        llm_client = AnthropicClient()
    
    # Create orchestrator
    storage_path = Path.cwd() / "storage" / "social_media"
    orchestrator = SocialMediaOrchestrator(storage_path, llm_client)
    
    # Prepare content
    content = None
    if not use_csv:
        content = {
            'text': text,
            'image_path': image_path,
            'hashtags': hashtags,
            **kwargs
        }
    
    # Post to platforms
    results = await orchestrator.post_to_platforms(
        platforms=platforms,
        content=content,
        use_csv=use_csv
    )
    
    return {
        'success': all(r['success'] for r in results),
        'results': results,
        'platforms_attempted': len(platforms),
        'platforms_succeeded': sum(1 for r in results if r['success'])
    }

def post_to_social(
    platforms: Union[str, List[str]],
    text: Optional[str] = None,
    image_path: Optional[str] = None,
    hashtags: Optional[str] = None,
    use_csv: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """Synchronous version of post_to_social_async"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            post_to_social_async(
                platforms, text, image_path, hashtags, use_csv, **kwargs
            )
        )
    finally:
        loop.close()

__all__ = [
    'scrape', 'scrape_async',
    'browse', 'browse_async',
    'download', 'download_async',
    'search', 'search_async',
    'screenshot', 'screenshot_async',
    'post_to_social', 'post_to_social_async',
    'UndetectableConfig', 'set_config'
]