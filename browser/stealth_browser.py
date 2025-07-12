"""
Stealth Browser - Primary implementation with full anti-detection features

This is the main browser implementation that provides comprehensive
anti-detection capabilities using Playwright with stealth modifications.
"""

import asyncio
import base64
import json
import logging
import random
import time
import weakref
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Union

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, ElementHandle
from playwright.async_api import Error as PlaywrightError, TimeoutError

from browser.base import BaseBrowser, BrowserError
from anti_detection.bypasses import get_bypass_scripts
from utils.browser_utils import get_random_user_agent, get_realistic_viewport

logger = logging.getLogger(__name__)

# Global variables to store browser instances
_browser_pool = {}
_browser_contexts = weakref.WeakValueDictionary()

class StealthBrowser(BaseBrowser):
    """Manages a stealth browser session with anti-detection features"""
    
    def __init__(self, session_id: str = None, headless: bool = True, anti_detection: bool = True, proxy: str = None, **kwargs):
        """
        Initialize the browser controller
        
        Args:
            session_id: Optional unique ID for this browser session
            headless: Whether to run the browser in headless mode
            anti_detection: Enable anti-detection features
        """
        super().__init__(headless=headless)
        self.session_id = session_id or f"session_{int(time.time())}_{random.randint(1000, 9999)}"
        self.anti_detection = anti_detection
        self._is_shutting_down = False
        self.proxy = proxy
        
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
        self._active_pages: Set = weakref.WeakSet()
        self._cleanup_lock = asyncio.Lock()
        self._initialization_lock = asyncio.Lock()
        
        self.default_timeout = 60000  # 60 seconds
        self.default_navigation_timeout = 90000  # 90 seconds
        
        # Store the bypass scripts if anti-detection is enabled
        self.bypass_scripts = get_bypass_scripts() if anti_detection else []
    
    async def initialize(self) -> None:
        """Initialize the browser instance with stealth settings"""
        if self._is_shutting_down:
            raise BrowserError("Browser is shutting down")
            
        async with self._initialization_lock:
            if self._initialized:
                return
                
            try:
                self._playwright = await async_playwright().start()
                
                # Launch browser with common settings
                launch_args = [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--disable-breakpad',
                    '--disable-extensions',
                    '--ignore-certificate-errors',
                    '--no-default-browser-check',
                ]
                
                if self.anti_detection:
                    launch_args.extend([
                        '--disable-blink-features=AutomationControlled',
                    ])
                
                self._browser = await self._playwright.chromium.launch(
                    headless=self.headless,
                    args=launch_args
                )
                
                # Create a new browser context with realistic settings
                viewport = get_realistic_viewport() if self.anti_detection else {'width': 1920, 'height': 1080}
                user_agent = get_random_user_agent() if self.anti_detection else None
                
                context_options = {
                    'viewport': viewport,
                    'user_agent': user_agent,
                    'ignore_https_errors': True,
                    'locale': 'en-US',
                    'timezone_id': 'America/New_York'
                }
                
                if self.proxy:
                    context_options['proxy'] = {'server': self.proxy}
                
                self._context = await self._browser.new_context(**context_options)
                
                # Set default timeouts
                self._context.set_default_timeout(self.default_timeout)
                self._context.set_default_navigation_timeout(self.default_navigation_timeout)
                
                # Create the main page
                self._page = await self._context.new_page()
                self._active_pages.add(self._page)
                
                # Apply stealth scripts to avoid detection
                if self.anti_detection:
                    for script in self.bypass_scripts:
                        await self._page.add_init_script(script)
                
                # Register this browser in the global pool
                _browser_pool[self.session_id] = self
                _browser_contexts[self.session_id] = self._context
                
                self._initialized = True
                logger.info(f"Browser initialized with session ID: {self.session_id}")
                
            except Exception as e:
                await self.close()
                raise BrowserError(f"Failed to initialize browser: {str(e)}")
    
    @asynccontextmanager
    async def managed_page(self):
        """Create a new page in the current browser context"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
            
        page = None
        try:
            page = await self._context.new_page()
            page.set_default_timeout(self.default_timeout)
            page.set_default_navigation_timeout(self.default_navigation_timeout)
            
            # Apply stealth scripts
            if self.anti_detection:
                for script in self.bypass_scripts:
                    await page.add_init_script(script)
                    
            self._active_pages.add(page)
            yield page
        finally:
            if page and not page.is_closed():
                try:
                    await page.close()
                except Exception:
                    pass
                self._active_pages.discard(page)
    
    async def navigate(self, url: str, wait_until: str = 'domcontentloaded', max_retries: int = 3) -> Dict[str, Any]:
        """Navigate to a URL"""
        if not self._initialized:
            await self.initialize()
            
        for attempt in range(max_retries):
            try:
                # Add a small random delay to appear more human-like
                if self.anti_detection:
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                
                # Navigate to the URL
                response = await self._page.goto(
                    url,
                    wait_until=wait_until,
                    timeout=self.default_navigation_timeout
                )
                
                if not response:
                    raise BrowserError(f"No response from {url}")
                    
                if response.status >= 400:
                    raise BrowserError(f"HTTP {response.status} error")
                    
                # Wait a moment to let any dynamic content load
                if self.anti_detection:
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                
                return {
                    'url': self._page.url,
                    'status': response.status,
                    'success': True,
                    'title': await self._page.title()
                }
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Navigation failed after {max_retries} attempts: {str(e)}")
                    raise BrowserError(f"Navigation failed: {str(e)}")
                
                # Exponential backoff with jitter
                await asyncio.sleep(2 ** attempt + random.uniform(0.1, 1.0))
    
    async def get_content(self, selector: Optional[str] = None, timeout: Optional[int] = None) -> str:
        """Get page content, optionally from a specific element"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
            
        try:
            await self._page.wait_for_load_state(
                'domcontentloaded',
                timeout=timeout or self.default_timeout
            )
            
            if selector:
                element = await self._page.wait_for_selector(selector, timeout=timeout or self.default_timeout)
                if element:
                    return await element.inner_html()
                else:
                    return ""
            else:
                return await self._page.content()
        except Exception as e:
            raise BrowserError(f"Failed to get content: {str(e)}")
    
    async def execute_js(self, script: str, *args) -> Any:
        """Execute JavaScript in the browser"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
            
        try:
            return await self._page.evaluate(script, *args)
        except Exception as e:
            raise BrowserError(f"Failed to execute JavaScript: {str(e)}")
    
    async def take_screenshot(self, selector: Optional[str] = None, full_page: bool = False) -> bytes:
        """Take a screenshot of the current page or a specific element"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
            
        try:
            if selector:
                element = await self._page.wait_for_selector(selector)
                if element:
                    return await element.screenshot()
            else:
                return await self._page.screenshot(full_page=full_page)
        except Exception as e:
            raise BrowserError(f"Failed to take screenshot: {str(e)}")
    
    async def click(self, selector: str, delay: Optional[float] = None, force: bool = False) -> None:
        """Click on an element"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
            
        try:
            # Add a small random delay before clicking to appear more human-like
            if self.anti_detection:
                await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Click the element
            await self._page.click(
                selector,
                delay=delay or (random.uniform(50, 150) if self.anti_detection else 0),
                force=force
            )
            
            # Add a small random delay after clicking
            if self.anti_detection:
                await asyncio.sleep(random.uniform(0.2, 0.7))
        except Exception as e:
            raise BrowserError(f"Failed to click element: {str(e)}")
    
    async def type_text(self, selector: str, text: str, delay: Optional[float] = None) -> None:
        """Type text into an input element"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
            
        try:
            # Focus the element first
            await self._page.focus(selector)
            
            # Add a small random delay before typing
            if self.anti_detection:
                await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Type the text with randomized delays between characters
            await self._page.type(
                selector,
                text,
                delay=delay or (random.uniform(100, 200) if self.anti_detection else 0)
            )
            
            # Add a small random delay after typing
            if self.anti_detection:
                await asyncio.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            raise BrowserError(f"Failed to type text: {str(e)}")
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None, state: str = 'visible') -> bool:
        """Wait for an element to appear"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
            
        try:
            element = await self._page.wait_for_selector(
                selector,
                timeout=timeout or self.default_timeout,
                state=state
            )
            return element is not None
        except TimeoutError:
            return False
        except Exception as e:
            raise BrowserError(f"Failed to wait for selector: {str(e)}")
    
    async def login(self, url: str, username: str, password: str, 
                   username_selector: str, password_selector: str, 
                   submit_selector: str) -> bool:
        """Log in to a website"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # Navigate to the login page
            await self.navigate(url)
            
            # Wait for the username field to appear
            if not await self.wait_for_selector(username_selector):
                raise BrowserError(f"Username field not found: {username_selector}")
                
            # Fill in the username
            await self.type_text(username_selector, username)
            
            # Wait for the password field to appear
            if not await self.wait_for_selector(password_selector):
                raise BrowserError(f"Password field not found: {password_selector}")
                
            # Fill in the password
            await self.type_text(password_selector, password)
            
            # Wait for the submit button to appear
            if not await self.wait_for_selector(submit_selector):
                raise BrowserError(f"Submit button not found: {submit_selector}")
                
            # Click the submit button
            await self.click(submit_selector)
            
            # Wait a moment for the login to process
            await asyncio.sleep(random.uniform(2.0, 3.0))
            
            # Check if we're still on the login page
            current_url = self._page.url
            if url in current_url or "login" in current_url.lower() or "signin" in current_url.lower():
                # Check for error messages
                error_selectors = [
                    ".error", ".alert", ".notification", "[role='alert']", 
                    ".message--error", ".form-error", "#error-message"
                ]
                for error_selector in error_selectors:
                    if await self.wait_for_selector(error_selector, timeout=1000):
                        error_text = await self.extract_text(error_selector)
                        if error_text:
                            logger.warning(f"Login error detected: {error_text}")
                            return False
                
                logger.warning("Login might have failed - still on login page")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    async def fill_form(self, form_data: Dict[str, str], 
                       form_selector: Optional[str] = None, 
                       submit: bool = True,
                       submit_selector: Optional[str] = None) -> bool:
        """Fill out a form on the current page"""
        if not self._initialized:
            raise BrowserError("Browser not initialized")
            
        try:
            # If a form selector is provided, wait for it
            if form_selector:
                if not await self.wait_for_selector(form_selector):
                    raise BrowserError(f"Form not found: {form_selector}")
                    
            # Fill in each field
            for selector, value in form_data.items():
                # Wait for the field to appear
                if not await self.wait_for_selector(selector):
                    logger.warning(f"Form field not found: {selector}")
                    continue
                    
                # Get element type
                element_type = await self._page.evaluate(
                    f"""() => {{
                        const el = document.querySelector('{selector}');
                        return el ? el.type || el.tagName.toLowerCase() : null;
                    }}"""
                )
                
                if element_type:
                    # Handle different input types
                    if element_type in ['checkbox', 'radio']:
                        if value in [True, 'true', 'True', 1, '1']:
                            await self._page.check(selector)
                        else:
                            await self._page.uncheck(selector)
                    elif element_type == 'select':
                        await self._page.select_option(selector, value=value)
                    elif element_type == 'file':
                        await self._page.set_input_files(selector, value)
                    else:
                        # Clear the field first
                        await self._page.fill(selector, '')
                        # Type the text with a human-like delay
                        await self.type_text(selector, str(value))
                        
            # Submit the form if requested
            if submit:
                if submit_selector:
                    if not await self.wait_for_selector(submit_selector):
                        raise BrowserError(f"Submit button not found: {submit_selector}")
                    await self.click(submit_selector)
                elif form_selector:
                    # Submit the form using JavaScript
                    await self._page.evaluate(f"""() => {{
                        const form = document.querySelector('{form_selector}');
                        if (form) form.submit();
                    }}""")
                else:
                    # Try to find a submit button
                    for submit_sel in ['[type="submit"]', 'button[type="submit"]', 'input[type="submit"]']:
                        if await self.wait_for_selector(submit_sel, timeout=1000):
                            await self.click(submit_sel)
                            break
                            
            return True
        except Exception as e:
            logger.error(f"Form filling failed: {str(e)}")
            return False

    async def search(self, query: str, engine: str = "google") -> List[Dict[str, str]]:
        """Perform a search using a search engine and extract the results"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # Define search engine URLs and selectors
            engines = {
                "google": {
                    "url": f"https://www.google.com/search?q={query}",
                    "results_selector": ".g",
                    "title_selector": "h3",
                    "url_selector": "a",
                    "snippet_selector": ".VwiC3b"
                },
                "bing": {
                    "url": f"https://www.bing.com/search?q={query}",
                    "results_selector": ".b_algo",
                    "title_selector": "h2",
                    "url_selector": "a",
                    "snippet_selector": ".b_caption p"
                },
                "duckduckgo": {
                    "url": f"https://duckduckgo.com/?q={query}",
                    "results_selector": ".result",
                    "title_selector": ".result__title",
                    "url_selector": ".result__url",
                    "snippet_selector": ".result__snippet"
                }
            }
            
            engine = engine.lower()
            if engine not in engines:
                engine = "google"
                
            engine_config = engines[engine]
            
            # Navigate to the search engine
            await self.navigate(engine_config["url"])
            
            # Wait for results to load
            await self.wait_for_selector(engine_config["results_selector"])
            
            # Extract the search results
            results = []
            
            # Get all result elements
            result_elements = await self._page.query_selector_all(engine_config["results_selector"])
            
            for result in result_elements:
                try:
                    # Get title
                    title_element = await result.query_selector(engine_config["title_selector"])
                    title = await title_element.text_content() if title_element else ""
                    
                    # Get URL
                    url_element = await result.query_selector(engine_config["url_selector"])
                    url = await url_element.get_attribute("href") if url_element else ""
                    
                    # Get snippet
                    snippet_element = await result.query_selector(engine_config["snippet_selector"])
                    snippet = await snippet_element.text_content() if snippet_element else ""
                    
                    if title and url:
                        results.append({
                            "title": title.strip(),
                            "url": url,
                            "snippet": snippet.strip() if snippet else ""
                        })
                except Exception as e:
                    logger.warning(f"Error extracting search result: {str(e)}")
                    continue
                    
            return results
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    async def download(self, url: str, save_path: Optional[Path] = None) -> Optional[Path]:
        """Download a file from a URL"""
        if not self._initialized:
            await self.initialize()
            
        try:
            # Create a download directory if save_path is not provided
            if not save_path:
                download_dir = Path.cwd() / 'downloads'
                download_dir.mkdir(exist_ok=True, parents=True)
                filename = url.split('/')[-1].split('?')[0]  # Get filename from URL
                save_path = download_dir / filename
                
            # Set download behavior
            await self._context.route('**', lambda route: route.continue_())
            await self._page.set_content('<html><body></body></html>')
            
            download_path = save_path
            
            # Register download handler
            async with self._page.expect_download() as download_info:
                # Navigate to the URL
                await self._page.goto(url)
                
            # Wait for download to complete
            download = await download_info.value
            await download.save_as(download_path)
            
            return save_path
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return None
    
    async def close(self) -> None:
        """Clean up browser resources"""
        if self._is_shutting_down:
            return
            
        async with self._cleanup_lock:
            self._is_shutting_down = True
            self._initialized = False
            
            # Remove from global pool
            if self.session_id in _browser_pool:
                del _browser_pool[self.session_id]
            
            if self.session_id in _browser_contexts:
                del _browser_contexts[self.session_id]
            
            if self._page:
                try:
                    await self._page.close()
                except Exception:
                    pass
                self._page = None
            
            for page in list(self._active_pages):
                try:
                    if not page.is_closed():
                        await page.close()
                except Exception:
                    pass
            
            if self._context:
                try:
                    await self._context.close()
                except Exception:
                    pass
                self._context = None
            
            if self._browser:
                try:
                    await self._browser.close()
                except Exception:
                    pass
                self._browser = None
            
            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None
            
            logger.info(f"Browser with session ID {self.session_id} cleaned up")