#!/usr/bin/env python3
"""
Investigation test for CLI event loop issue
Let's understand what's really happening
"""

import sys
import os
import asyncio
import subprocess
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_direct_cli_import():
    """Test if we can even import the CLI"""
    print("=== Test 1: Direct Import ===")
    try:
        from main import WebAssistantCLI
        print("✓ Successfully imported WebAssistantCLI")
        
        # Try to create instance
        cli = WebAssistantCLI()
        print("✓ Successfully created CLI instance")
        
        # Check what type of session it has
        print(f"Session type: {type(cli.session)}")
        print(f"Session methods: {[m for m in dir(cli.session) if not m.startswith('_')]}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_run_method():
    """Test the CLI run method structure"""
    print("\n=== Test 2: CLI Run Method ===")
    try:
        from main import WebAssistantCLI
        cli = WebAssistantCLI()
        
        # Check if run is async
        import inspect
        print(f"cli.run is coroutine: {inspect.iscoroutinefunction(cli.run)}")
        
        # Check prompt_async
        if hasattr(cli.session, 'prompt_async'):
            print(f"✓ session.prompt_async exists")
            print(f"prompt_async is coroutine: {inspect.iscoroutinefunction(cli.session.prompt_async)}")
        else:
            print("✗ session.prompt_async does not exist")
            
        return True
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        return False

def test_minimal_async_run():
    """Test minimal async execution"""
    print("\n=== Test 3: Minimal Async Run ===")
    try:
        from main import WebAssistantCLI
        
        async def minimal_test():
            cli = WebAssistantCLI()
            print("Created CLI in async context")
            
            # Try to mock a quick exit
            original_prompt = cli.session.prompt_async
            
            async def mock_prompt(*args, **kwargs):
                print("Mock prompt called")
                return "exit"
            
            cli.session.prompt_async = mock_prompt
            
            # Try to run briefly
            try:
                await cli.run()
                print("✓ CLI run completed")
            except Exception as e:
                print(f"Error in run: {e}")
                
        # Run the async test
        asyncio.run(minimal_test())
        return True
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_subprocess_behavior():
    """Test running main.py as subprocess to see actual behavior"""
    print("\n=== Test 4: Subprocess Behavior ===")
    
    # Create a simple input that should exit immediately
    test_input = "exit\n"
    
    try:
        # Run main.py with minimal interaction
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # Send exit command
        stdout, stderr = process.communicate(input=test_input, timeout=5)
        
        print(f"Return code: {process.returncode}")
        print(f"STDOUT preview: {stdout[:200] if stdout else 'None'}")
        print(f"STDERR preview: {stderr[:200] if stderr else 'None'}")
        
        # Check for specific errors
        if "no attribute 'coroutine'" in stderr:
            print("✗ Found 'no attribute coroutine' error")
            return False
        elif "no running event loop" in stderr:
            print("✗ Found 'no running event loop' error")
            return False
        else:
            print("✓ No critical errors found")
            return True
            
    except subprocess.TimeoutExpired:
        print("✗ Process timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        return False

def check_prompt_toolkit_version():
    """Check prompt_toolkit version and features"""
    print("\n=== Test 5: prompt_toolkit Version ===")
    try:
        import prompt_toolkit
        print(f"prompt_toolkit version: {prompt_toolkit.__version__}")
        
        # Check major version
        major_version = int(prompt_toolkit.__version__.split('.')[0])
        print(f"Major version: {major_version}")
        
        if major_version >= 3:
            print("✓ Using prompt_toolkit 3.x (async-native)")
        else:
            print("⚠ Using prompt_toolkit 2.x (may have different async behavior)")
            
        # Check for prompt_async availability
        from prompt_toolkit import PromptSession
        session = PromptSession()
        if hasattr(session, 'prompt_async'):
            print("✓ prompt_async method available")
        else:
            print("✗ prompt_async method NOT available")
            print(f"Available methods: {[m for m in dir(session) if 'prompt' in m]}")
            
        return True
    except ImportError:
        print("✗ prompt_toolkit not installed")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("CLI Event Loop Investigation")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(("Import Test", test_direct_cli_import()))
    results.append(("Run Method Test", test_cli_run_method()))
    results.append(("Minimal Async Test", test_minimal_async_run()))
    results.append(("Subprocess Test", test_subprocess_behavior()))
    results.append(("prompt_toolkit Version", check_prompt_toolkit_version()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    # Final verdict
    if all(r[1] for r in results):
        print("\n✓ No critical event loop issues found")
        print("The error in the original test was likely due to the test code itself")
    else:
        print("\n✗ Event loop issues detected - needs fixing")