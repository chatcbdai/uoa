"""
Camoufox engine adapter for the undetectable toolkit
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from contextlib import asynccontextmanager

from browser.base import BaseBrowser, BrowserError

# Import the original CamoufoxEngine
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from engines.camo import CamoufoxEngine as OriginalCamoufoxEngine
except ImportError:
    OriginalCamoufoxEngine = None

logger = logging.getLogger(__name__)

class CamoufoxBrowser(BaseBrowser):
    """
    Adapter for the original CamoufoxEngine to work with our unified interface
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        anti_detection: bool = True,
        humanize: bool = True,
        block_images: bool = False,
        proxy: Optional[str] = None,
        **kwargs
    ):
        super().__init__(headless=headless, timeout=timeout)
        
        if not OriginalCamoufoxEngine:
            raise BrowserError("CamoufoxEngine not available - check engines/camo.py exists")
        
        # Map our parameters to original engine parameters
        self.engine_kwargs = {
            'headless': headless,
            'timeout': float(timeout),
            'humanize': humanize and anti_detection,
            'block_images': block_images,
            'proxy': proxy,
            'disable_resources': kwargs.get('disable_resources', False),
            'block_webrtc': kwargs.get('block_webrtc', False),
            'allow_webgl': kwargs.get('allow_webgl', True),
            'network_idle': kwargs.get('network_idle', False),
            'wait_selector': kwargs.get('wait_selector'),
            'wait_selector_state': kwargs.get('wait_selector_state', 'attached'),
            'google_search': kwargs.get('google_search', True),
            'extra_headers': kwargs.get('extra_headers', {}),
            'os_randomize': kwargs.get('os_randomize', None),
            'disable_ads': kwargs.get('disable_ads', False),
            'geoip': kwargs.get('geoip', False),
            'addons': kwargs.get('addons', []),
        }
        
        # Remove None values
        self.engine_kwargs = {k: v for k, v in self.engine_kwargs.items() if v is not None}
        
        self.engine = OriginalCamoufoxEngine(**self.engine_kwargs)
        self._current_url = None
        self._current_content = None
    
    async def initialize(self) -> None:
        """Initialize the Camoufox engine"""
        if self._initialized:
            return
        
        # Camoufox initializes on first use
        self._initialized = True
        logger.info("CamoufoxEngine ready")
    
    async def navigate(self, url: str, wait_until: str = 'domcontentloaded') -> Dict[str, Any]:
        """Navigate to a URL"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # CamoufoxEngine has both sync and async fetch
            if hasattr(self.engine, 'async_fetch'):
                response = await self.engine.async_fetch(url)
            else:
                # Run sync version in thread pool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self.engine.fetch, url)
            
            self._current_url = response.url
            self._current_content = response.text
            
            # Try to extract title from content
            title = None
            try:
                import re
                title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1)
            except:
                pass
            
            return {
                'url': response.url,
                'status': response.status,
                'success': response.status < 400,
                'title': title
            }
        except Exception as e:
            raise BrowserError(f"Navigation failed: {str(e)}")
    
    async def get_content(self, selector: Optional[str] = None) -> str:
        """Get page content"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
        
        if not self._current_content:
            raise BrowserError("No content available - navigate to a page first")
        
        if selector:
            # Parse content and extract selector
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(self._current_content, 'lxml')
                element = soup.select_one(selector)
                if element:
                    return str(element)
                return ""
            except Exception as e:
                raise BrowserError(f"Failed to extract content from selector: {str(e)}")
        else:
            return self._current_content
    
    async def execute_js(self, script: str, *args) -> Any:
        """Execute JavaScript - NOT SUPPORTED by Camoufox"""
        raise BrowserError("JavaScript execution not supported by CamoufoxEngine")
    
    async def take_screenshot(self, selector: Optional[str] = None, full_page: bool = False) -> bytes:
        """Take a screenshot - NOT SUPPORTED by Camoufox"""
        raise BrowserError("Screenshots not supported by CamoufoxEngine")
    
    async def click(self, selector: str, delay: Optional[float] = None) -> None:
        """Click an element - LIMITED SUPPORT"""
        raise BrowserError("Click actions have limited support in CamoufoxEngine - use page_action parameter instead")
    
    async def type_text(self, selector: str, text: str, delay: Optional[float] = None) -> None:
        """Type text - LIMITED SUPPORT"""
        raise BrowserError("Type actions have limited support in CamoufoxEngine - use page_action parameter instead")
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None, state: str = 'visible') -> bool:
        """Wait for selector - handled by engine configuration"""
        # This is configured via wait_selector in engine kwargs
        return True  # Assume it worked if we have content
    
    async def close(self) -> None:
        """Close the browser"""
        # Camoufox handles its own cleanup
        self._initialized = False
        self._current_url = None
        self._current_content = None
    
    @asynccontextmanager
    async def managed_page(self):
        """Create a managed page context"""
        if not self._initialized:
            await self.initialize()
        
        # Camoufox doesn't support multiple pages
        try:
            yield self
        finally:
            pass
    
    # Additional helper methods
    async def search(self, query: str, engine: str = "google") -> List[Dict[str, str]]:
        """Search not directly supported - navigate to search URL instead"""
        search_urls = {
            "google": f"https://www.google.com/search?q={query}",
            "bing": f"https://www.bing.com/search?q={query}",
            "duckduckgo": f"https://duckduckgo.com/?q={query}"
        }
        
        url = search_urls.get(engine.lower(), search_urls["google"])
        result = await self.navigate(url)
        
        # Would need to parse search results from content
        return []
    
    def __del__(self):
        """Cleanup on deletion"""
        pass  # Camoufox handles its own cleanup