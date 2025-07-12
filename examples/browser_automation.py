#!/usr/bin/env python3
"""
Browser automation examples using the Undetectable Toolkit
Demonstrates interactive browser control with anti-detection
"""

import asyncio
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from undetectable_toolkit.browser.factory import BrowserFactory
from undetectable_toolkit.browser.stealth_browser import StealthBrowser


async def example_basic_navigation():
    """Basic browser navigation example"""
    print("\n🌐 Basic Navigation Example")
    print("-" * 40)
    
    # Create a browser with anti-detection
    browser = StealthBrowser(
        session_id="demo_session",
        headless=False,  # Show browser window
        anti_detection=True
    )
    
    try:
        await browser.initialize()
        print("✅ Browser initialized with anti-detection")
        
        # Navigate to a website
        await browser.navigate("https://example.com")
        print("✅ Navigated to example.com")
        
        # Get page title
        title = await browser.execute_js("return document.title")
        print(f"📄 Page title: {title}")
        
        # Take a screenshot
        screenshot = await browser.screenshot()
        print(f"📸 Screenshot taken: {len(screenshot)} bytes")
        
        # Wait a bit to see the browser
        await asyncio.sleep(3)
        
    finally:
        await browser.close()
        print("✅ Browser closed")


async def example_form_interaction():
    """Interact with forms and buttons"""
    print("\n📝 Form Interaction Example")
    print("-" * 40)
    
    factory = BrowserFactory()
    browser = factory.create("playwright", headless=False)
    
    try:
        await browser.initialize()
        
        # Navigate to a search engine
        await browser.navigate("https://duckduckgo.com")
        print("✅ Navigated to DuckDuckGo")
        
        # Wait for search box
        await browser.wait_for_selector("#search_form_input_homepage")
        
        # Type in search box with human-like delays
        await browser.type_text(
            "#search_form_input_homepage",
            "undetectable web scraping python",
            delay=100  # milliseconds between keystrokes
        )
        print("✅ Typed search query")
        
        # Click search button
        await browser.click("#search_button_homepage")
        print("✅ Clicked search button")
        
        # Wait for results
        await browser.wait_for_selector(".results", timeout=5000)
        print("✅ Search results loaded")
        
        # Extract results
        results = await browser.execute_js("""
            return Array.from(document.querySelectorAll('.result__title')).map(el => ({
                title: el.textContent.trim(),
                link: el.querySelector('a')?.href
            })).slice(0, 5);
        """)
        
        print("\n🔍 Top 5 Search Results:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('title', 'No title')}")
        
    finally:
        await browser.close()


async def example_multi_engine_comparison():
    """Compare different browser engines"""
    print("\n🔧 Multi-Engine Comparison")
    print("-" * 40)
    
    factory = BrowserFactory()
    available = factory.get_available_browsers()
    
    print(f"Available engines: {', '.join(available)}")
    
    test_url = "https://httpbin.org/headers"
    
    for engine_type in available:
        print(f"\n🧪 Testing {engine_type} engine:")
        
        try:
            browser = factory.create(engine_type, headless=True)
            await browser.initialize()
            
            # Navigate and get headers
            await browser.navigate(test_url)
            content = await browser.get_content()
            
            # Check if user agent is visible
            if "User-Agent" in content:
                print(f"✅ {engine_type}: Successfully fetched headers")
            else:
                print(f"❌ {engine_type}: Headers not found")
            
            await browser.close()
            
        except Exception as e:
            print(f"❌ {engine_type}: Failed - {str(e)}")


async def example_javascript_heavy_site():
    """Handle JavaScript-heavy websites"""
    print("\n⚡ JavaScript-Heavy Site Example")
    print("-" * 40)
    
    browser = StealthBrowser(
        headless=True,
        anti_detection=True
    )
    
    try:
        await browser.initialize()
        
        # Navigate to a JS-heavy site
        await browser.navigate("https://react.dev/")
        print("✅ Navigated to React documentation")
        
        # Wait for React to load
        await browser.wait_for_selector(".css-1jqhuxz", timeout=10000)
        print("✅ React app loaded")
        
        # Execute complex JavaScript
        nav_items = await browser.execute_js("""
            // Get navigation items
            const items = document.querySelectorAll('nav a');
            return Array.from(items).map(item => ({
                text: item.textContent.trim(),
                href: item.href
            })).filter(item => item.text.length > 0).slice(0, 10);
        """)
        
        print("\n📋 Navigation Items:")
        for item in nav_items:
            print(f"  - {item['text']}")
        
        # Interact with the page
        await browser.execute_js("""
            // Scroll to documentation section
            const element = document.querySelector('h2');
            if (element) element.scrollIntoView({behavior: 'smooth'});
        """)
        print("\n✅ Scrolled to content section")
        
    finally:
        await browser.close()


async def example_session_management():
    """Manage multiple browser sessions"""
    print("\n🔐 Session Management Example")
    print("-" * 40)
    
    # Create multiple sessions for different tasks
    sessions = {
        "research": StealthBrowser(session_id="research_session"),
        "monitoring": StealthBrowser(session_id="monitoring_session"),
        "testing": StealthBrowser(session_id="testing_session")
    }
    
    try:
        # Initialize all sessions
        for name, browser in sessions.items():
            await browser.initialize()
            print(f"✅ Initialized {name} session")
        
        # Use different sessions for different sites
        await sessions["research"].navigate("https://scholar.google.com")
        await sessions["monitoring"].navigate("https://github.com")
        await sessions["testing"].navigate("https://example.com")
        
        print("\n📊 Session Status:")
        for name, browser in sessions.items():
            url = browser.get_current_url()
            print(f"  - {name}: {url if url else 'No URL'}")
        
    finally:
        # Clean up all sessions
        for name, browser in sessions.items():
            await browser.close()
            print(f"✅ Closed {name} session")


async def main():
    """Run all examples"""
    print("🚀 Browser Automation Examples")
    print("=" * 60)
    
    # Note: These examples require dependencies to be installed
    print("\n⚠️  Note: Make sure to run 'python install_toolkit.py' first!")
    print("\nUncomment the examples you want to run:")
    
    # await example_basic_navigation()
    # await example_form_interaction()
    # await example_multi_engine_comparison()
    # await example_javascript_heavy_site()
    # await example_session_management()


if __name__ == "__main__":
    asyncio.run(main())