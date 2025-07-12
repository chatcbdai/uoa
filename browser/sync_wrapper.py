"""
Synchronous wrapper for async browser operations
"""

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

class SyncBrowserWrapper:
    """Wraps an async browser to provide synchronous interface"""
    
    def __init__(self, async_browser, loop):
        self._browser = async_browser
        self._loop = loop
    
    def _run_async(self, coro):
        """Run an async coroutine in the event loop"""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()
    
    def visit(self, url: str, wait_until: str = 'domcontentloaded') -> Dict[str, Any]:
        """Navigate to a URL"""
        return self._run_async(self._browser.navigate(url, wait_until))
    
    def get_content(self, selector: Optional[str] = None) -> str:
        """Get page content"""
        return self._run_async(self._browser.get_content(selector))
    
    def execute_js(self, script: str, *args) -> Any:
        """Execute JavaScript"""
        return self._run_async(self._browser.execute_js(script, *args))
    
    def screenshot(self, selector: Optional[str] = None, full_page: bool = False) -> bytes:
        """Take a screenshot"""
        return self._run_async(self._browser.take_screenshot(selector, full_page))
    
    def click(self, selector: str, delay: Optional[float] = None) -> None:
        """Click an element"""
        return self._run_async(self._browser.click(selector, delay))
    
    def type_text(self, selector: str, text: str, delay: Optional[float] = None) -> None:
        """Type text into an element"""
        return self._run_async(self._browser.type_text(selector, text, delay))
    
    def fill_form(self, form_data: Dict[str, str], **kwargs) -> bool:
        """Fill out a form"""
        return self._run_async(self._browser.fill_form(form_data, **kwargs))
    
    def wait_for_selector(self, selector: str, timeout: Optional[int] = None, state: str = 'visible') -> bool:
        """Wait for an element"""
        return self._run_async(self._browser.wait_for_selector(selector, timeout, state))
    
    def scroll(self, selector: Optional[str] = None, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Scroll the page"""
        return self._run_async(self._browser.scroll(selector, x, y))
    
    def extract_text(self, selector: Optional[str] = None) -> str:
        """Extract text content"""
        return self._run_async(self._browser.extract_text(selector))
    
    def extract_links(self, selector: Optional[str] = None) -> List[Dict[str, str]]:
        """Extract links"""
        return self._run_async(self._browser.extract_links(selector))
    
    def login(self, url: str, username: str, password: str, **kwargs) -> bool:
        """Log in to a website"""
        return self._run_async(self._browser.login(url, username, password, **kwargs))
    
    def search(self, query: str, engine: str = "google") -> List[Dict[str, str]]:
        """Search the web"""
        return self._run_async(self._browser.search(query, engine))
    
    def download(self, url: str, save_path: Optional[Path] = None) -> Optional[Path]:
        """Download a file"""
        return self._run_async(self._browser.download(url, save_path))