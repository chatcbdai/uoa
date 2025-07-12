"""
Base browser interface for all browser implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
from contextlib import asynccontextmanager

class BaseBrowser(ABC):
    """Abstract base class for all browser implementations"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the browser instance"""
        pass
    
    @abstractmethod
    async def navigate(self, url: str, wait_until: str = 'domcontentloaded') -> Dict[str, Any]:
        """Navigate to a URL"""
        pass
    
    @abstractmethod
    async def get_content(self, selector: Optional[str] = None) -> str:
        """Get page content"""
        pass
    
    @abstractmethod
    async def execute_js(self, script: str, *args) -> Any:
        """Execute JavaScript"""
        pass
    
    @abstractmethod
    async def take_screenshot(self, selector: Optional[str] = None, full_page: bool = False) -> bytes:
        """Take a screenshot"""
        pass
    
    @abstractmethod
    async def click(self, selector: str, delay: Optional[float] = None) -> None:
        """Click an element"""
        pass
    
    @abstractmethod
    async def type_text(self, selector: str, text: str, delay: Optional[float] = None) -> None:
        """Type text into an element"""
        pass
    
    @abstractmethod
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None, state: str = 'visible') -> bool:
        """Wait for an element"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the browser"""
        pass
    
    @abstractmethod
    @asynccontextmanager
    async def managed_page(self):
        """Create a managed page context"""
        pass
    
    # Common methods that can be overridden
    async def scroll(self, selector: Optional[str] = None, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Scroll the page or element"""
        if selector:
            await self.execute_js(f"""
                document.querySelector('{selector}').scrollIntoView({{behavior: 'smooth'}});
            """)
        else:
            if x is not None and y is not None:
                await self.execute_js(f"window.scrollTo({x}, {y})")
            elif y is not None:
                await self.execute_js(f"window.scrollTo(0, {y})")
    
    async def extract_text(self, selector: Optional[str] = None) -> str:
        """Extract text content"""
        if selector:
            return await self.execute_js(f"""
                (() => {{
                    const el = document.querySelector('{selector}');
                    return el ? el.textContent : '';
                }})()
            """)
        else:
            return await self.execute_js("document.body.innerText")
    
    async def extract_links(self, selector: Optional[str] = None) -> List[Dict[str, str]]:
        """Extract links from the page"""
        if selector:
            script = f"""
                Array.from(document.querySelectorAll('{selector} a')).map(a => ({{
                    href: a.href,
                    text: a.textContent.trim()
                }}))
            """
        else:
            script = """
                Array.from(document.querySelectorAll('a')).map(a => ({
                    href: a.href,
                    text: a.textContent.trim()
                }))
            """
        return await self.execute_js(script)

class BrowserError(Exception):
    """Base exception for browser-related errors"""
    pass