"""
Browser factory for creating different browser engine instances
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from .base import BaseBrowser, BrowserError

class BrowserEngine(Enum):
    """Available browser engines"""
    STEALTH = "stealth"
    PLAYWRIGHT = "playwright"
    CAMOUFOX = "camoufox"
    STATIC = "static"

class BrowserFactory:
    """Factory class for creating browser instances"""
    
    _engines: Dict[BrowserEngine, type] = {}
    
    @classmethod
    def register_engine(cls, engine: BrowserEngine, browser_class: type):
        """Register a browser engine implementation"""
        if not issubclass(browser_class, BaseBrowser):
            raise TypeError(f"{browser_class} must inherit from BaseBrowser")
        cls._engines[engine] = browser_class
    
    @classmethod
    def create(
        cls,
        engine: str = "stealth",
        headless: bool = True,
        anti_detection: bool = True,
        **kwargs
    ) -> BaseBrowser:
        """
        Create a browser instance with the specified engine.
        
        Args:
            engine: Browser engine to use (stealth, playwright, camoufox, static)
            headless: Run browser in headless mode
            anti_detection: Enable anti-detection features
            **kwargs: Additional engine-specific arguments
            
        Returns:
            Browser instance
            
        Raises:
            BrowserError: If engine is not available
        """
        try:
            engine_enum = BrowserEngine(engine.lower())
        except ValueError:
            available = [e.value for e in BrowserEngine]
            raise BrowserError(
                f"Unknown engine '{engine}'. Available engines: {', '.join(available)}"
            )
        
        if engine_enum not in cls._engines:
            # Try to import the engine dynamically
            cls._try_import_engine(engine_enum)
        
        if engine_enum not in cls._engines:
            raise BrowserError(f"Engine '{engine}' is not available")
        
        browser_class = cls._engines[engine_enum]
        
        # Add anti_detection to kwargs if the browser supports it
        if anti_detection and hasattr(browser_class, '__init__'):
            import inspect
            sig = inspect.signature(browser_class.__init__)
            if 'anti_detection' in sig.parameters:
                kwargs['anti_detection'] = anti_detection
        
        return browser_class(headless=headless, **kwargs)
    
    @classmethod
    def _try_import_engine(cls, engine: BrowserEngine):
        """Try to import and register an engine dynamically"""
        try:
            if engine == BrowserEngine.STEALTH:
                from .stealth_browser import StealthBrowser
                cls.register_engine(BrowserEngine.STEALTH, StealthBrowser)
            elif engine == BrowserEngine.PLAYWRIGHT:
                from .engines.playwright import PlaywrightBrowser
                cls.register_engine(BrowserEngine.PLAYWRIGHT, PlaywrightBrowser)
            elif engine == BrowserEngine.CAMOUFOX:
                from .engines.camoufox import CamoufoxBrowser
                cls.register_engine(BrowserEngine.CAMOUFOX, CamoufoxBrowser)
            elif engine == BrowserEngine.STATIC:
                from .engines.static import StaticBrowser
                cls.register_engine(BrowserEngine.STATIC, StaticBrowser)
        except ImportError:
            pass  # Engine not available
    
    @classmethod
    def list_available_engines(cls) -> List[str]:
        """List all available browser engines"""
        # Try to import all engines
        for engine in BrowserEngine:
            cls._try_import_engine(engine)
        
        return [engine.value for engine in cls._engines.keys()]