#!/usr/bin/env python3
"""
Simple test for event loop issues
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test if we can even import and run the CLI
try:
    import asyncio
    from main import WebAssistantCLI
    
    cli = WebAssistantCLI()
    
    # This will show if there's an event loop issue
    print("Testing asyncio.run with CLI...")
    
    async def quick_test():
        print("Inside async function")
        return True
    
    result = asyncio.run(quick_test())
    print(f"Basic asyncio.run works: {result}")
    
    # Now test actual CLI
    print("\nNow testing actual CLI run...")
    # Don't actually run it, just check if it would work
    print("CLI instance created successfully")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()