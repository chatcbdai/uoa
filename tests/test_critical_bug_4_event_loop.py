#!/usr/bin/env python3
"""
Test 4: Verify event loop conflict between asyncio.run and prompt_toolkit
Expected: Nested event loop errors or conflicts
"""

import sys
import os
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
        logging.FileHandler('test_4_event_loop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_cli_event_loop():
    """Test running the CLI to check for event loop conflicts"""
    logger.info("Testing CLI event loop initialization")
    
    try:
        from main import WebAssistantCLI
        
        # Create CLI instance
        cli = WebAssistantCLI()
        
        # Check if asyncio.run will work
        logger.info("Attempting to run CLI with asyncio.run()")
        
        # Create a test that exits immediately
        async def test_run():
            # Override prompt to exit immediately
            cli.session.prompt_async = lambda _: asyncio.coroutine(lambda: 'exit')()
            await cli.run()
        
        # This should work if no conflict
        asyncio.run(test_run())
        
        logger.info("CLI ran without event loop conflict")
        return False
        
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            logger.info(f"✅ CRITICAL BUG CONFIRMED: Event loop conflict - {e}")
            return True
        else:
            logger.error(f"Different RuntimeError: {e}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        return False

def test_prompt_toolkit_conflict():
    """Test prompt_toolkit async handling conflict"""
    logger.info("\n=== Test 2: prompt_toolkit async conflict ===")
    
    try:
        import prompt_toolkit
        logger.info(f"prompt_toolkit version: {prompt_toolkit.__version__}")
        
        # Check if prompt_toolkit 3.0+ behavior
        from prompt_toolkit import PromptSession
        from prompt_toolkit.application import Application
        
        # Test if prompt_toolkit manages its own event loop
        async def test_prompt():
            session = PromptSession()
            # This should work in prompt_toolkit 3.0+
            result = await session.prompt_async('test> ')
            return result
        
        # Try to run in existing event loop
        async def test_nested():
            # Already in event loop
            try:
                # This might conflict
                result = await test_prompt()
                logger.info("No conflict with nested prompt_toolkit")
                return False
            except Exception as e:
                logger.error(f"Conflict detected: {e}")
                return True
        
        # Run test
        conflict = asyncio.run(test_nested())
        
        if conflict:
            logger.info("✅ CRITICAL BUG CONFIRMED: prompt_toolkit event loop conflict")
            return True
        else:
            logger.info("No prompt_toolkit conflict detected")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

def test_actual_cli_startup():
    """Test actual CLI startup behavior"""
    logger.info("\n=== Test 3: Actual CLI startup ===")
    
    import subprocess
    import time
    
    # Create a test input file
    with open('test_cli_input.txt', 'w') as f:
        f.write('help\nexit\n')
    
    try:
        # Run the CLI with test input
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdin=open('test_cli_input.txt'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for completion or timeout
        try:
            stdout, stderr = process.communicate(timeout=10)
            
            # Check for event loop errors
            if "cannot be called from a running event loop" in stderr:
                logger.info("✅ CRITICAL BUG CONFIRMED: Event loop error in CLI startup")
                logger.info(f"Error: {stderr}")
                return True
            elif "no running event loop" in stderr:
                logger.info("✅ CRITICAL BUG CONFIRMED: Event loop not running error")
                logger.info(f"Error: {stderr}")
                return True
            else:
                logger.info("CLI started without event loop errors")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error("CLI startup timed out")
            return False
            
    finally:
        if os.path.exists('test_cli_input.txt'):
            os.unlink('test_cli_input.txt')

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("TESTING: Event loop conflict in CLI")
    logger.info("="*60)
    
    # Set timeout
    import signal
    def timeout_handler(signum, frame):
        logger.error("Test timed out after 30 seconds")
        sys.exit(1)
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        # Test 1: Basic CLI event loop
        logger.info("\n=== Test 1: Basic CLI event loop ===")
        result1 = test_cli_event_loop()
        
        # Test 2: prompt_toolkit conflict
        result2 = test_prompt_toolkit_conflict()
        
        # Test 3: Actual CLI startup
        result3 = test_actual_cli_startup()
        
        # Write results
        if result1 or result2 or result3:
            logger.info("\n✅ CRITICAL BUG CONFIRMED: Event loop conflicts exist")
            with open('test_4_result.txt', 'w') as f:
                f.write("CONFIRMED: Event loop conflict is a critical bug\n")
        else:
            logger.info("\n❌ Bug not reproduced in tests")
            with open('test_4_result.txt', 'w') as f:
                f.write("NOT CONFIRMED: Unable to reproduce event loop conflict\n")
                
    except Exception as e:
        logger.error(f"Test failed with exception: {type(e).__name__}: {str(e)}")
        with open('test_4_result.txt', 'w') as f:
            f.write(f"ERROR: Test failed - {str(e)}\n")
    finally:
        signal.alarm(0)