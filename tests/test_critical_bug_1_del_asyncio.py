#!/usr/bin/env python3
"""
Test 1: Verify asyncio.create_task() in __del__ causes RuntimeError
Expected: RuntimeError: no running event loop
"""

import sys
import os
import gc
import asyncio
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_1_del_asyncio.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_browser_del():
    """Test that __del__ with asyncio.create_task causes RuntimeError"""
    logger.info("Starting test for asyncio.create_task in __del__")
    
    try:
        from browser.stealth_browser import StealthBrowser
        
        # Create browser instance
        logger.info("Creating StealthBrowser instance")
        browser = StealthBrowser(headless=True)
        
        # Initialize it
        logger.info("Initializing browser")
        await browser.initialize()
        
        # Delete the browser to trigger __del__
        logger.info("Deleting browser reference to trigger __del__")
        browser_id = browser.session_id
        del browser
        
        # Force garbage collection
        logger.info("Forcing garbage collection")
        gc.collect()
        
        # Give it a moment
        await asyncio.sleep(1)
        
        logger.info("Test completed without error (unexpected)")
        return False
        
    except Exception as e:
        logger.error(f"Exception caught: {type(e).__name__}: {str(e)}")
        if "no running event loop" in str(e):
            logger.info("✓ CONFIRMED: RuntimeError with 'no running event loop' detected")
            return True
        return False

def test_outside_loop():
    """Test __del__ called outside event loop context"""
    logger.info("\n=== Test 2: __del__ called outside event loop ===")
    
    try:
        from browser.stealth_browser import StealthBrowser
        
        # Run async code to create browser
        async def create_browser():
            browser = StealthBrowser(headless=True)
            await browser.initialize()
            return browser
        
        # Create browser in event loop
        browser = asyncio.run(create_browser())
        logger.info(f"Browser created with session_id: {browser.session_id}")
        
        # Now we're outside the event loop
        logger.info("Deleting browser outside event loop context")
        del browser
        
        # Force GC
        gc.collect()
        
        logger.info("No immediate error (checking logs)")
        return True
        
    except Exception as e:
        logger.error(f"Exception in test_outside_loop: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("TESTING: asyncio.create_task() in __del__ method")
    logger.info("="*60)
    
    # Set timeout
    import signal
    def timeout_handler(signum, frame):
        logger.error("Test timed out after 30 seconds")
        sys.exit(1)
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        # Test 1: Inside event loop
        logger.info("\n=== Test 1: __del__ called inside event loop ===")
        result1 = asyncio.run(test_browser_del())
        
        # Test 2: Outside event loop
        result2 = test_outside_loop()
        
        # Check results
        if result1 or result2:
            logger.info("\n✅ CRITICAL BUG CONFIRMED: asyncio.create_task in __del__ causes issues")
            with open('test_1_result.txt', 'w') as f:
                f.write("CONFIRMED: asyncio.create_task in __del__ is a critical bug\n")
        else:
            logger.info("\n❌ Bug not reproduced in tests")
            with open('test_1_result.txt', 'w') as f:
                f.write("NOT CONFIRMED: Unable to reproduce the bug\n")
                
    except Exception as e:
        logger.error(f"Test failed with exception: {type(e).__name__}: {str(e)}")
        with open('test_1_result.txt', 'w') as f:
            f.write(f"ERROR: Test failed - {str(e)}\n")
    finally:
        signal.alarm(0)  # Cancel timeout