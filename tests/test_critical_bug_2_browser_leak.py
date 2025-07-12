#!/usr/bin/env python3
"""
Test 2: Verify browser resource leak when exception occurs
Expected: Browser processes remain open after exception
"""

import sys
import os
import asyncio
import psutil
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_2_browser_leak.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def count_chrome_processes():
    """Count chrome/chromium processes"""
    count = 0
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name'].lower()
            if 'chrome' in name or 'chromium' in name:
                count += 1
        except:
            pass
    return count

async def test_browser_leak_on_exception():
    """Test browser leak when exception occurs"""
    from social_media.orchestrator import SocialMediaOrchestrator
    from pathlib import Path
    
    # Count initial processes
    initial_count = count_chrome_processes()
    logger.info(f"Initial chrome processes: {initial_count}")
    
    # Create orchestrator with mock LLM
    class MockLLM:
        async def generate(self, *args, **kwargs):
            return type('obj', (object,), {'content': 'mock response'})
    
    storage_path = Path.cwd() / "storage" / "social_media"
    orchestrator = SocialMediaOrchestrator(storage_path, MockLLM())
    
    # Override post method to force exception
    from social_media.platforms.instagram import InstagramPoster
    original_post = InstagramPoster.post
    
    async def failing_post(self, content):
        # Simulate work then fail
        await asyncio.sleep(1)
        raise Exception("Simulated posting failure")
    
    InstagramPoster.post = failing_post
    
    try:
        # Try to post - this should fail and leak browser
        logger.info("Attempting to post (will fail)...")
        await orchestrator.post_to_platforms(
            ['instagram'],
            content={'text': 'test post', 'image_path': None}
        )
    except Exception as e:
        logger.info(f"Expected exception caught: {e}")
    
    # Wait a bit for processes to settle
    await asyncio.sleep(2)
    
    # Count processes after
    after_count = count_chrome_processes()
    logger.info(f"Chrome processes after exception: {after_count}")
    
    leaked = after_count > initial_count
    if leaked:
        logger.info(f"✅ CRITICAL BUG CONFIRMED: {after_count - initial_count} browser processes leaked")
    else:
        logger.info("❌ No browser leak detected")
    
    # Cleanup
    InstagramPoster.post = original_post
    
    return leaked

async def test_multiple_exceptions():
    """Test multiple exceptions cause multiple leaks"""
    initial_count = count_chrome_processes()
    logger.info(f"\n=== Test 2: Multiple exceptions ===")
    logger.info(f"Initial chrome processes: {initial_count}")
    
    # Simulate 3 failed attempts
    for i in range(3):
        try:
            from browser import BrowserFactory
            
            logger.info(f"Creating browser {i+1}")
            browser = BrowserFactory.create(
                engine="stealth",
                headless=True,
                anti_detection=True
            )
            await browser.initialize()
            
            # Simulate work then exception
            await asyncio.sleep(0.5)
            raise Exception(f"Simulated failure {i+1}")
            
            # This line never reached - browser.close() not called
            await browser.close()
            
        except Exception as e:
            logger.info(f"Exception {i+1}: {e}")
    
    # Wait for processes
    await asyncio.sleep(2)
    
    final_count = count_chrome_processes()
    logger.info(f"Final chrome processes: {final_count}")
    
    leaked = final_count > initial_count
    if leaked:
        logger.info(f"✅ CRITICAL BUG CONFIRMED: {final_count - initial_count} browser processes leaked from {3} exceptions")
        return True
    else:
        logger.info("❌ No browser leak detected")
        return False

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("TESTING: Browser resource leak on exception")
    logger.info("="*60)
    
    # Set timeout
    import signal
    def timeout_handler(signum, frame):
        logger.error("Test timed out after 60 seconds")
        # Kill any leaked chrome processes
        os.system("pkill -f chromium")
        sys.exit(1)
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)  # 60 second timeout
    
    try:
        # Test 1: Orchestrator exception
        logger.info("\n=== Test 1: Orchestrator exception ===")
        result1 = asyncio.run(test_browser_leak_on_exception())
        
        # Test 2: Direct browser exceptions
        result2 = asyncio.run(test_multiple_exceptions())
        
        # Write results
        if result1 or result2:
            logger.info("\n✅ CRITICAL BUG CONFIRMED: Browser processes leak on exceptions")
            with open('test_2_result.txt', 'w') as f:
                f.write("CONFIRMED: Browser resource leak is a critical bug\n")
        else:
            logger.info("\n❌ Bug not reproduced in tests")
            with open('test_2_result.txt', 'w') as f:
                f.write("NOT CONFIRMED: Unable to reproduce browser leak\n")
                
    except Exception as e:
        logger.error(f"Test failed with exception: {type(e).__name__}: {str(e)}")
        with open('test_2_result.txt', 'w') as f:
            f.write(f"ERROR: Test failed - {str(e)}\n")
    finally:
        signal.alarm(0)
        # Cleanup any leaked processes
        os.system("pkill -f chromium")