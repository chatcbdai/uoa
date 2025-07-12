"""
Playwright engine adapter for the undetectable toolkit
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from contextlib import asynccontextmanager

from browser.base import BaseBrowser, BrowserError
from anti_detection.bypasses import get_bypass_scripts

# Import the original PlaywrightEngine
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from engines.pw import PlaywrightEngine as OriginalPlaywrightEngine
except ImportError:
    OriginalPlaywrightEngine = None

logger = logging.getLogger(__name__)

class PlaywrightBrowser(BaseBrowser):
    """
    Adapter for the original PlaywrightEngine to work with our unified interface
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        anti_detection: bool = True,
        stealth: bool = True,
        real_chrome: bool = False,
        proxy: Optional[str] = None,
        **kwargs
    ):
        super().__init__(headless=headless, timeout=timeout)
        
        if not OriginalPlaywrightEngine:
            raise BrowserError("PlaywrightEngine not available - check engines/pw.py exists")
        
        # Map our parameters to original engine parameters
        self.engine_kwargs = {
            'headless': headless,
            'timeout': timeout,
            'stealth': stealth and anti_detection,
            'real_chrome': real_chrome,
            'proxy': proxy,
            'disable_resources': kwargs.get('disable_resources', False),
            'useragent': kwargs.get('user_agent'),
            'network_idle': kwargs.get('network_idle', False),
            'wait_selector': kwargs.get('wait_selector'),
            'wait_selector_state': kwargs.get('wait_selector_state', 'attached'),
            'extra_headers': kwargs.get('extra_headers', {}),
            'cdp_url': kwargs.get('cdp_url'),
        }
        
        # Remove None values
        self.engine_kwargs = {k: v for k, v in self.engine_kwargs.items() if v is not None}
        
        self.engine = None
        self._current_url = None
    
    async def initialize(self) -> None:
        """Initialize the Playwright engine"""
        if self._initialized:
            return
        
        try:
            self.engine = OriginalPlaywrightEngine(**self.engine_kwargs)
            await self.engine.initialize()
            self._initialized = True
            logger.info("PlaywrightEngine initialized successfully")
        except Exception as e:
            raise BrowserError(f"Failed to initialize PlaywrightEngine: {str(e)}")
    
    async def navigate(self, url: str, wait_until: str = 'domcontentloaded') -> Dict[str, Any]:
        """Navigate to a URL"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # The original engine returns a Response object
            response = await self.engine.navigate(url)
            self._current_url = response.url
            
            return {
                'url': response.url,
                'status': response.status,
                'success': response.status < 400,
                'title': await self.engine._page.title() if hasattr(self.engine, '_page') else None
            }
        except Exception as e:
            raise BrowserError(f"Navigation failed: {str(e)}")
    
    async def get_content(self, selector: Optional[str] = None) -> str:
        """Get page content"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
        
        try:
            if selector:
                # Get content from specific selector
                element = await self.engine._page.wait_for_selector(selector, timeout=self.timeout)
                if element:
                    return await element.inner_html()
                return ""
            else:
                # Get full page content
                return await self.engine.get_content()
        except Exception as e:
            raise BrowserError(f"Failed to get content: {str(e)}")
    
    async def execute_js(self, script: str, *args) -> Any:
        """Execute JavaScript"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
        
        try:
            return await self.engine._page.evaluate(script, *args)
        except Exception as e:
            raise BrowserError(f"Failed to execute JavaScript: {str(e)}")
    
    async def take_screenshot(self, selector: Optional[str] = None, full_page: bool = False) -> bytes:
        """Take a screenshot"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
        
        try:
            if selector:
                element = await self.engine._page.wait_for_selector(selector)
                if element:
                    return await element.screenshot()
            else:
                return await self.engine._page.screenshot(full_page=full_page)
        except Exception as e:
            raise BrowserError(f"Failed to take screenshot: {str(e)}")
    
    async def click(self, selector: str, delay: Optional[float] = None) -> None:
        """Click an element"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
        
        try:
            await self.engine._page.click(selector, delay=delay)
        except Exception as e:
            raise BrowserError(f"Failed to click element: {str(e)}")
    
    async def type_text(self, selector: str, text: str, delay: Optional[float] = None) -> None:
        """Type text into an element"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
        
        try:
            await self.engine._page.type(selector, text, delay=delay)
        except Exception as e:
            raise BrowserError(f"Failed to type text: {str(e)}")
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None, state: str = 'visible') -> bool:
        """Wait for an element"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
        
        try:
            element = await self.engine._page.wait_for_selector(
                selector,
                timeout=timeout or self.timeout,
                state=state
            )
            return element is not None
        except:
            return False
    
    async def close(self) -> None:
        """Close the browser"""
        if self.engine:
            await self.engine.close()
        self._initialized = False
        self._current_url = None
    
    @asynccontextmanager
    async def managed_page(self):
        """Create a managed page context"""
        if not self._initialized:
            await self.initialize()
        
        # The original engine doesn't support multiple pages
        # So we'll just yield the main page functionality
        try:
            yield self
        finally:
            pass  # Page management handled by engine
    
    # Additional methods from original engine
    async def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch a URL (compatibility method)"""
        return await self.navigate(url)
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.engine and hasattr(self.engine, '__del__'):
            self.engine.__del__()