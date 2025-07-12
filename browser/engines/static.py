"""
Static engine adapter for the undetectable toolkit
Simple HTTP client without browser automation
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from contextlib import asynccontextmanager

from browser.base import BaseBrowser, BrowserError

# Import the original StaticEngine
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from engines.static import StaticEngine as OriginalStaticEngine
except ImportError:
    OriginalStaticEngine = None

# Fallback to basic implementation if original not available
try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)

class StaticBrowser(BaseBrowser):
    """
    Adapter for static HTTP requests without browser automation
    """
    
    def __init__(
        self,
        headless: bool = True,  # Ignored for static
        timeout: int = 30000,
        anti_detection: bool = True,
        proxy: Optional[str] = None,
        **kwargs
    ):
        super().__init__(headless=headless, timeout=timeout)
        
        self.proxy = proxy
        self.anti_detection = anti_detection
        self.extra_headers = kwargs.get('extra_headers', {})
        
        # Try to use original engine if available
        if OriginalStaticEngine:
            self.engine = OriginalStaticEngine(
                timeout=float(timeout) / 1000,  # Convert to seconds
                proxy=proxy,
                extra_headers=self.extra_headers,
                **kwargs
            )
            self.use_original = True
        else:
            self.engine = None
            self.use_original = False
            self.session = None
        
        self._current_url = None
        self._current_content = None
        self._current_status = None
    
    async def initialize(self) -> None:
        """Initialize the static engine"""
        if self._initialized:
            return
        
        if not self.use_original and aiohttp:
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout / 1000)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                **self.extra_headers
            }
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
        
        self._initialized = True
        logger.info("StaticEngine initialized")
    
    async def navigate(self, url: str, wait_until: str = 'domcontentloaded') -> Dict[str, Any]:
        """Navigate to a URL (simple HTTP GET)"""
        if not self._initialized:
            await self.initialize()
        
        try:
            if self.use_original:
                # Use original engine
                response = await self.engine.async_fetch(url)
                self._current_url = response.url
                self._current_content = response.text
                self._current_status = response.status
                
                return {
                    'url': response.url,
                    'status': response.status,
                    'success': response.status < 400,
                    'title': self._extract_title(response.text)
                }
            elif self.session:
                # Use aiohttp
                async with self.session.get(url) as response:
                    content = await response.text()
                    self._current_url = str(response.url)
                    self._current_content = content
                    self._current_status = response.status
                    
                    return {
                        'url': str(response.url),
                        'status': response.status,
                        'success': response.status < 400,
                        'title': self._extract_title(content)
                    }
            else:
                raise BrowserError("No HTTP client available")
                
        except Exception as e:
            raise BrowserError(f"Navigation failed: {str(e)}")
    
    def _extract_title(self, html: str) -> Optional[str]:
        """Extract title from HTML"""
        try:
            import re
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        except:
            pass
        return None
    
    async def get_content(self, selector: Optional[str] = None) -> str:
        """Get page content"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
        
        if not self._current_content:
            raise BrowserError("No content available - navigate to a page first")
        
        if selector:
            # Parse and extract selector
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(self._current_content, 'lxml')
                element = soup.select_one(selector)
                if element:
                    return str(element)
                return ""
            except Exception as e:
                logger.warning(f"Selector extraction not available: {str(e)}")
                return self._current_content
        else:
            return self._current_content
    
    async def execute_js(self, script: str, *args) -> Any:
        """Execute JavaScript - NOT SUPPORTED"""
        raise BrowserError("JavaScript execution not supported by StaticEngine")
    
    async def take_screenshot(self, selector: Optional[str] = None, full_page: bool = False) -> bytes:
        """Take a screenshot - NOT SUPPORTED"""
        raise BrowserError("Screenshots not supported by StaticEngine")
    
    async def click(self, selector: str, delay: Optional[float] = None) -> None:
        """Click an element - NOT SUPPORTED"""
        raise BrowserError("Click actions not supported by StaticEngine")
    
    async def type_text(self, selector: str, text: str, delay: Optional[float] = None) -> None:
        """Type text - NOT SUPPORTED"""
        raise BrowserError("Type actions not supported by StaticEngine")
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None, state: str = 'visible') -> bool:
        """Wait for selector - NOT SUPPORTED"""
        # Static engine gets content immediately
        return True if self._current_content else False
    
    async def close(self) -> None:
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
        
        self._initialized = False
        self._current_url = None
        self._current_content = None
        self._current_status = None
    
    @asynccontextmanager
    async def managed_page(self):
        """Create a managed page context"""
        if not self._initialized:
            await self.initialize()
        
        try:
            yield self
        finally:
            pass
    
    # Utility methods
    async def download(self, url: str, save_path: Optional[Path] = None) -> Optional[Path]:
        """Download a file"""
        if not self._initialized:
            await self.initialize()
        
        try:
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        if not save_path:
                            filename = url.split('/')[-1] or 'download'
                            save_path = Path.cwd() / filename
                        
                        save_path.write_bytes(content)
                        return save_path
            else:
                raise BrowserError("No HTTP client available")
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return None
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())