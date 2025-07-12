"""
Content processing module for HTML extraction and conversion
"""

import os
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Union, Tuple, Optional, List
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from lxml import html
import markdownify

logger = logging.getLogger(__name__)

# Try to import readability as a fallback
try:
    from readability import Document
    HAS_READABILITY = True
except ImportError:
    HAS_READABILITY = False

class ContentProcessorError(Exception):
    """Custom exception for content processing errors"""
    pass

class ContentProcessor:
    """Processes HTML content for extraction and conversion"""
    
    def __init__(self):
        self.unwanted_selectors = [
            'nav', 'header', 'footer', '.navigation', '.nav', '.menu', '.sidebar',
            '.filter', '.filters', '.tag-filter', '.social-share', '.related-posts',
            '.pagination', '.breadcrumb', '#navigation', '.navbar', '.search',
            'script', 'style', 'meta', 'link', 'iframe', 'noscript',
            '[role="navigation"]', '[role="complementary"]', '[role="banner"]',
            'form', '.form', '#searchform', '.search-form',
            '.comments', '#comments', '.comment-form',
            '.advertisement', '.ads', '.advert',
            '.product-recommendations', '.product-upsell',
            '.newsletter-signup', '.footer-signup'
        ]
        
        self.content_selectors = [
            '.shopify-section-article',
            '.article__content',
            '.rte',
            '[data-section-type="article"]',
            '.article__body',
            '.article-template__content',
            'article .post-content',
            'article .entry-content',
            'article .article-content',
            '.post-content',
            '.entry-content',
            '.article-content',
            'article',
            '.post',
            'div.article__content',
            'main article',
            '#main-content',
            '[role="main"]',
            '#primary',
            '.content-area',
            '.site-content',
            '.page-content'
        ]
        
        self._last_extracted_html = None

    def extract_content(self, html_content: str) -> Tuple[BeautifulSoup, html.HtmlElement]:
        """Extract meaningful content while removing unwanted navigation and UI elements."""
        if not html_content:
            raise ContentProcessorError("Empty HTML input")
            
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            logger.debug(f"Initial HTML length: {len(html_content)}")
            
            # Remove unwanted elements
            for selector in self.unwanted_selectors:
                removed = soup.select(selector)
                if removed:
                    logger.debug(f"Removed {len(removed)} elements matching '{selector}'")
                for element in removed:
                    element.decompose()
            
            main_content = None
            
            # Try each candidate selector in order
            for selector in self.content_selectors:
                element = soup.select_one(selector)
                if element:
                    text_content = element.get_text(strip=True)
                    logger.debug(f"Selector '{selector}' found content length: {len(text_content)}")
                    if len(text_content) > 100:
                        main_content = element
                        logger.info(f"Selected content using '{selector}' with length {len(text_content)}")
                        break
            
            # Fallback strategies
            if not main_content:
                logger.warning("No content found with primary selectors")
                
                if HAS_READABILITY:
                    logger.debug("Using readability fallback")
                    doc = Document(html_content)
                    summary_html = doc.summary(html_partial=True)
                    main_content = BeautifulSoup(summary_html, 'lxml')
                    logger.info("Content extracted using readability fallback")
                else:
                    # Find largest text block
                    text_blocks = []
                    for tag in soup.find_all(['div', 'section', 'main']):
                        if not tag.find_all(['nav', 'ul', 'menu']):
                            text = tag.get_text(strip=True)
                            if len(text) > 200:
                                text_blocks.append((len(text), tag))
                    
                    if text_blocks:
                        main_content = max(text_blocks, key=lambda x: x[0])[1]
                        logger.info(f"Content extracted using largest text block: {len(main_content.get_text(strip=True))} chars")
            
            if not main_content or len(main_content.get_text(strip=True)) == 0:
                logger.error("No meaningful content found in the HTML")
                raise ContentProcessorError("No meaningful content found")
            
            # Store the extracted HTML
            self._last_extracted_html = str(main_content)
            logger.info(f"Final extracted content length: {len(self._last_extracted_html)}")
            
            html_element = html.fromstring(self._last_extracted_html)
            return main_content, html_element
            
        except Exception as e:
            logger.error(f"Content extraction failed: {str(e)}", exc_info=True)
            raise ContentProcessorError(f"Content extraction failed: {str(e)}")

    def convert_to_markdown(self, content: Union[str, BeautifulSoup]) -> str:
        """Convert HTML content to Markdown format."""
        try:
            # Get HTML content
            if isinstance(content, BeautifulSoup):
                html_content = str(content)
            elif hasattr(self, '_last_extracted_html') and self._last_extracted_html:
                html_content = self._last_extracted_html
            else:
                html_content = str(content)
            
            logger.debug(f"Converting {len(html_content)} bytes of HTML to Markdown")
            
            if len(html_content.strip()) < 10:
                raise ContentProcessorError(f"Content too short: {len(html_content)} bytes")
            
            # Convert to markdown using markdownify
            markdown = markdownify.markdownify(
                html_content,
                heading_style="ATX",
                bullets="-",
                strip=['script', 'style'],
                strong_em_symbol="*"
            )
            
            if not markdown.strip():
                raise ContentProcessorError("Markdown conversion produced empty content")
            
            logger.debug(f"Markdown conversion successful, length: {len(markdown)}")
            return markdown.strip()
            
        except Exception as e:
            logger.error(f"Markdown conversion failed: {str(e)}")
            raise ContentProcessorError(f"Markdown conversion failed: {str(e)}")

    async def save_as_markdown(self, content: Union[str, BeautifulSoup], filepath: Union[str, Path]) -> None:
        """Save content as a Markdown file with metadata."""
        filepath = Path(filepath)
        
        try:
            # Convert to markdown
            markdown = self.convert_to_markdown(content)
            
            # Create markdown with metadata
            metadata = {
                'title': filepath.stem,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'path': str(filepath),
            }
            
            markdown_with_meta = "---\n"
            for key, value in metadata.items():
                markdown_with_meta += f"{key}: {value}\n"
            markdown_with_meta += "---\n\n"
            markdown_with_meta += markdown
            
            # Ensure output directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the file (using aiofiles if available, otherwise sync)
            try:
                import aiofiles
                async with aiofiles.open(filepath, mode='w', encoding='utf-8', errors='replace') as f:
                    await f.write(markdown_with_meta)
            except ImportError:
                # Fallback to synchronous write
                with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(markdown_with_meta)
            
            logger.info(f"Saved markdown file ({len(markdown_with_meta)} bytes) to: {filepath}")
            
        except ContentProcessorError:
            raise
        except Exception as e:
            logger.error(f"Failed to save markdown: {str(e)}")
            raise ContentProcessorError(f"Failed to save markdown: {str(e)}")

    def detect_url_type(self, url: str) -> str:
        """Detect URL type based on pattern and path structure."""
        if '*' in url:
            return 'wildcard'
            
        parsed = urlparse(url)
        path = parsed.path.rstrip('/')
        
        # Check for file extensions
        if any(path.endswith(ext) for ext in ('.html', '.htm', '.php', '.asp', '.aspx', '.jsp')):
            return 'single'
        
        # Check for blog/article patterns
        if re.search(r'/(blog|article|post|news|learn)/[\w-]+/?$', path):
            return 'single'
        
        # If has query parameters or deep path, likely single page
        if parsed.query or len(path.split('/')) > 3:
            return 'single'
        
        return 'full_site'

    def get_folder_name(self, url: str) -> str:
        """Extract a suitable folder name from a URL."""
        try:
            parsed = urlparse(url.replace('*', '').rstrip('/'))
            parts = [p for p in parsed.path.split('/') if p]
            
            if parts:
                folder_name = parts[-1]
            else:
                # Use domain name
                folder_name = parsed.netloc.replace('www.', '').split('.')[0]
            
            return self.clean_filename(folder_name)
        except Exception:
            return "scraped_content"

    def clean_filename(self, text: str) -> str:
        """Convert a string into a valid filename."""
        if not text:
            return 'index'
        
        # Remove invalid filename characters
        cleaned = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores
        cleaned = re.sub(r'[\s]+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        
        return cleaned.lower() or 'unnamed'

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from the content."""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convert relative URLs to absolute
            if not href.startswith(('http://', 'https://', '#', 'javascript:', 'mailto:')):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            
            # Only include HTTP(S) links
            if href.startswith(('http://', 'https://')):
                links.append(href)
        
        return list(set(links))  # Remove duplicates