#!/usr/bin/env python3
"""
Test 5: Verify WeakSet premature garbage collection of pages
Expected: Page objects get garbage collected while still in use
"""

import sys
import gc
import asyncio
import weakref
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_5_weakset.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_weakset_page_gc():
    """Test if pages in WeakSet get garbage collected prematurely"""
    from browser.stealth_browser import StealthBrowser
    
    try:
        # Create browser
        browser = StealthBrowser(headless=True)
        await browser.initialize()
        
        # Create a page using managed_page context
        page_ref = None
        page_was_collected = False
        
        # Use managed_page to create a page
        async with browser.managed_page() as page:
            # Create a weak reference to track if it gets GC'd
            def on_page_deleted(ref):
                nonlocal page_was_collected
                page_was_collected = True
                logger.warning("Page was garbage collected!")
            
            page_ref = weakref.ref(page, on_page_deleted)
            
            # Navigate somewhere
            await page.goto('https://example.com')
            logger.info("Page navigated successfully")
            
            # Force garbage collection while page should still be active
            logger.info("Forcing garbage collection...")
            gc.collect()
            
            # Check if page still exists
            if page_ref() is None:
                logger.error("✅ CRITICAL BUG CONFIRMED: Page was garbage collected while in use!")
                return True
            
            # Try to use the page
            try:
                title = await page.title()
                logger.info(f"Page still usable, title: {title}")
            except Exception as e:
                logger.error(f"Page no longer usable: {e}")
                return True
        
        # Page should be closed now
        await asyncio.sleep(0.5)
        gc.collect()
        
        if page_was_collected:
            logger.info("Page was collected after context exit (expected)")
        
        await browser.close()
        return False
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

async def test_multiple_pages_weakset():
    """Test multiple pages in WeakSet"""
    logger.info("\n=== Test 2: Multiple pages in WeakSet ===")
    
    try:
        from browser.stealth_browser import StealthBrowser
        
        browser = StealthBrowser(headless=True)
        await browser.initialize()
        
        # Check the _active_pages WeakSet
        logger.info(f"Initial active pages: {len(browser._active_pages)}")
        
        # Create multiple pages
        pages = []
        page_refs = []
        
        for i in range(3):
            page = await browser._context.new_page()
            pages.append(page)
            page_refs.append(weakref.ref(page))
            browser._active_pages.add(page)
            logger.info(f"Created page {i}, active pages: {len(browser._active_pages)}")
        
        # Force GC
        gc.collect()
        
        # Check how many pages are still tracked
        active_count = len(browser._active_pages)
        logger.info(f"After GC, active pages: {active_count}")
        
        # Check if any pages were collected
        collected = []
        for i, ref in enumerate(page_refs):
            if ref() is None:
                collected.append(i)
                logger.error(f"Page {i} was garbage collected!")
        
        if collected:
            logger.info(f"✅ CRITICAL BUG CONFIRMED: {len(collected)} pages were prematurely garbage collected")
            result = True
        else:
            logger.info("All pages remained in memory (good)")
            result = False
        
        # Cleanup
        for page in pages:
            if page and not page.is_closed():
                await page.close()
        
        await browser.close()
        return result
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

async def test_weakset_behavior():
    """Test basic WeakSet behavior to confirm the issue"""
    logger.info("\n=== Test 3: Basic WeakSet behavior ===")
    
    ws = weakref.WeakSet()
    
    class TestObject:
        def __init__(self, name):
            self.name = name
    
    # Create objects
    obj1 = TestObject("obj1")
    obj2 = TestObject("obj2")
    
    # Add to WeakSet
    ws.add(obj1)
    ws.add(obj2)
    
    logger.info(f"WeakSet size: {len(ws)}")
    
    # Delete strong reference to obj1
    del obj1
    gc.collect()
    
    logger.info(f"After deleting obj1 and GC, WeakSet size: {len(ws)}")
    
    if len(ws) == 1:
        logger.info("✅ WeakSet correctly removed garbage collected object")
        return True
    else:
        logger.info("WeakSet did not remove object (unexpected)")
        return False

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("TESTING: WeakSet premature garbage collection")
    logger.info("="*60)
    
    # Set timeout
    import signal
    def timeout_handler(signum, frame):
        logger.error("Test timed out after 30 seconds")
        sys.exit(1)
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        # Test 1: Page GC in context
        logger.info("\n=== Test 1: Page GC in managed context ===")
        result1 = asyncio.run(test_weakset_page_gc())
        
        # Test 2: Multiple pages
        result2 = asyncio.run(test_multiple_pages_weakset())
        
        # Test 3: Basic WeakSet behavior
        result3 = asyncio.run(test_weakset_behavior())
        
        # Write results
        if result1 or result2:
            logger.info("\n✅ CRITICAL BUG CONFIRMED: WeakSet causes premature page GC")
            with open('test_5_result.txt', 'w') as f:
                f.write("CONFIRMED: WeakSet premature GC is a critical bug\n")
        else:
            logger.info("\n❌ Bug not reproduced in tests")
            with open('test_5_result.txt', 'w') as f:
                f.write("NOT CONFIRMED: Unable to reproduce WeakSet GC issue\n")
                
    except Exception as e:
        logger.error(f"Test failed with exception: {type(e).__name__}: {str(e)}")
        with open('test_5_result.txt', 'w') as f:
            f.write(f"ERROR: Test failed - {str(e)}\n")
    finally:
        signal.alarm(0)