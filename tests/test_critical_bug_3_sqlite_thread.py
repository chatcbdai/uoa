#!/usr/bin/env python3
"""
Test 3: Verify SQLite thread safety violation
Expected: ProgrammingError when using connection across threads
"""

import sys
import os
import threading
import sqlite3
import logging
from pathlib import Path
from queue import Queue

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(thread)d - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_3_sqlite_thread.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_sqlite_thread_violation():
    """Test SQLite connections without check_same_thread=False"""
    from storage.sqlite import SQLiteStorage
    
    # Create storage instance
    storage = SQLiteStorage()
    errors_queue = Queue()
    success_queue = Queue()
    
    def worker_thread(thread_id):
        """Try to use storage from different thread"""
        try:
            logger.info(f"Thread {thread_id} starting")
            
            # Try to save content from this thread
            storage.save_content(
                url=f"http://test{thread_id}.com",
                content=f"Test content from thread {thread_id}",
                title=f"Test {thread_id}"
            )
            
            logger.info(f"Thread {thread_id} saved content successfully")
            success_queue.put(thread_id)
            
        except Exception as e:
            logger.error(f"Thread {thread_id} error: {type(e).__name__}: {str(e)}")
            errors_queue.put((thread_id, str(e)))
    
    # Start multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker_thread, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for threads
    for t in threads:
        t.join(timeout=5)
    
    # Check results
    errors = []
    while not errors_queue.empty():
        errors.append(errors_queue.get())
    
    successes = []
    while not success_queue.empty():
        successes.append(success_queue.get())
    
    logger.info(f"Errors: {len(errors)}, Successes: {len(successes)}")
    
    # Close storage
    storage.close()
    
    # Check if we got thread safety errors
    thread_errors = [e for e in errors if "thread" in e[1].lower()]
    
    if thread_errors:
        logger.info(f"✅ CRITICAL BUG CONFIRMED: SQLite thread safety violation detected")
        for thread_id, error in thread_errors:
            logger.info(f"  Thread {thread_id}: {error}")
        return True
    else:
        logger.info("❌ No thread safety violation detected")
        return False

def test_direct_sqlite_connection():
    """Test creating connections directly without check_same_thread"""
    logger.info("\n=== Test 2: Direct connection test ===")
    
    # Create a connection the same way the code does
    db_path = Path.cwd() / "storage" / "test_thread.db"
    db_path.parent.mkdir(exist_ok=True)
    
    try:
        # Create connection WITHOUT check_same_thread=False (like the bug)
        conn = sqlite3.connect(
            str(db_path),
            timeout=30.0,
            isolation_level=None
        )
        
        # Use it in main thread - should work
        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
        logger.info("Main thread: Connection works")
        
        # Try to use in another thread
        error_occurred = False
        
        def use_in_thread():
            nonlocal error_occurred
            try:
                conn.execute("INSERT INTO test VALUES (1)")
                logger.info("Other thread: Connection works (unexpected)")
            except Exception as e:
                logger.error(f"Other thread error: {type(e).__name__}: {str(e)}")
                error_occurred = True
        
        t = threading.Thread(target=use_in_thread)
        t.start()
        t.join()
        
        conn.close()
        os.unlink(db_path)
        
        if error_occurred:
            logger.info("✅ CRITICAL BUG CONFIRMED: SQLite objects can't be used across threads")
            return True
        else:
            logger.info("❌ SQLite allowed cross-thread usage (unexpected)")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("TESTING: SQLite thread safety violation")
    logger.info("="*60)
    
    # Set timeout
    import signal
    def timeout_handler(signum, frame):
        logger.error("Test timed out after 30 seconds")
        sys.exit(1)
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        # Test 1: Through SQLiteStorage
        logger.info("\n=== Test 1: SQLiteStorage thread safety ===")
        result1 = test_sqlite_thread_violation()
        
        # Test 2: Direct connection
        result2 = test_direct_sqlite_connection()
        
        # Write results
        if result1 or result2:
            logger.info("\n✅ CRITICAL BUG CONFIRMED: SQLite thread safety issue exists")
            with open('test_3_result.txt', 'w') as f:
                f.write("CONFIRMED: SQLite thread safety is a critical bug\n")
        else:
            logger.info("\n❌ Bug not reproduced in tests")
            with open('test_3_result.txt', 'w') as f:
                f.write("NOT CONFIRMED: Unable to reproduce SQLite thread issue\n")
                
    except Exception as e:
        logger.error(f"Test failed with exception: {type(e).__name__}: {str(e)}")
        with open('test_3_result.txt', 'w') as f:
            f.write(f"ERROR: Test failed - {str(e)}\n")
    finally:
        signal.alarm(0)