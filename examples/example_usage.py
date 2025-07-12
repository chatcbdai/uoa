#!/usr/bin/env python3
"""
Example usage of the Undetectable Toolkit

This demonstrates how to use the unified API for web scraping and browsing.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from undetectable_toolkit import scrape, browse, search, screenshot, UndetectableConfig

def example_simple_scraping():
    """Example 1: Simple scraping"""
    print("\n=== Example 1: Simple Scraping ===")
    
    # Scrape a single URL
    result = scrape("https://example.com", anti_detection=True)
    print(f"Scraped: {result}")
    
    # Scrape with wildcards (documentation)
    # result = scrape("https://docs.python.org/3/*", output_format="markdown")
    # print(f"Scraped {result['pages_count']} pages")

def example_browser_automation():
    """Example 2: Browser automation"""
    print("\n=== Example 2: Browser Automation ===")
    
    # NOTE: This is a demonstration of the API
    # The actual browser implementation needs to be completed
    
    # Use browser context manager
    # with browse(headless=False) as browser:
    #     browser.visit("https://example.com")
    #     title = browser.execute_js("return document.title")
    #     print(f"Page title: {title}")
    #     
    #     # Fill out a form
    #     browser.fill_form({
    #         "#search": "python web scraping",
    #         "#submit": "click"
    #     })
    
    print("Browser automation example (implementation pending)")

def example_search():
    """Example 3: Web search with anti-detection"""
    print("\n=== Example 3: Web Search ===")
    
    # Search the web
    # results = search("undetectable web scraping", num_results=5)
    # for i, result in enumerate(results, 1):
    #     print(f"{i}. {result['title']}")
    #     print(f"   {result['url']}")
    
    print("Search example (implementation pending)")

def example_configuration():
    """Example 4: Global configuration"""
    print("\n=== Example 4: Configuration ===")
    
    # Create and apply global configuration
    config = UndetectableConfig(
        engine="stealth",
        anti_detection=True,
        headless=True,
        rate_limit=0.5,  # 2 requests per second
        concurrent_requests=5,
        proxy="http://proxy.example.com:8080"
    )
    
    print(f"Configuration created: {config.to_dict()}")
    
    # Apply configuration globally
    from undetectable_toolkit import set_config
    set_config(config)
    
    # Now all operations will use these settings
    # result = scrape("https://example.com")

def main():
    """Run all examples"""
    print("Undetectable Toolkit - Usage Examples")
    print("=" * 50)
    
    example_simple_scraping()
    example_browser_automation()
    example_search()
    example_configuration()
    
    print("\n" + "=" * 50)
    print("The toolkit provides a unified interface for:")
    print("- Web scraping (single URL, wildcards, full sites)")
    print("- Browser automation with anti-detection")
    print("- File downloads")
    print("- Web search")
    print("- Screenshots")
    print("\nAll with comprehensive anti-detection features!")

if __name__ == "__main__":
    main()