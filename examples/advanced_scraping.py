#!/usr/bin/env python3
"""
Advanced scraping examples using the Undetectable Toolkit
Demonstrates various scraping strategies and configurations
"""

import asyncio
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from undetectable_toolkit import scrape, UndetectableConfig
from undetectable_toolkit.scrapers import UnifiedScraper
from undetectable_toolkit.storage import SQLiteStorage


async def example_wildcard_scraping():
    """Scrape multiple pages using wildcard patterns"""
    print("\n📚 Wildcard Scraping Example")
    print("-" * 40)
    
    # Scrape all Python tutorial pages
    config = UndetectableConfig(
        headless=True,
        anti_detection=True,
        rate_limit=1.0  # 1 request per second
    )
    
    result = await scrape(
        "https://docs.python.org/3/tutorial/*",
        mode="wildcard",
        config=config
    )
    
    print(f"✅ Scraped {result.get('pages_count', 0)} pages")
    print(f"📄 Total content: {result.get('total_size', 0)} bytes")
    
    # Access individual pages
    if 'pages' in result:
        for page in result['pages'][:3]:  # Show first 3
            print(f"  - {page['url']}: {page.get('title', 'No title')}")


async def example_full_site_scraping():
    """Scrape an entire website with depth control"""
    print("\n🌐 Full Site Scraping Example")
    print("-" * 40)
    
    scraper = UnifiedScraper(
        browser_type="static",  # Use static for speed
        max_depth=2,  # Limit crawl depth
        max_pages=10  # Limit total pages
    )
    
    try:
        result = await scraper.scrape(
            "https://example.com",
            mode="full_site"
        )
        
        print(f"✅ Site scraped successfully")
        print(f"📊 Statistics:")
        print(f"  - Pages scraped: {result.get('pages_count', 0)}")
        print(f"  - Total links found: {result.get('total_links', 0)}")
        print(f"  - Time taken: {result.get('duration', 0):.2f}s")
        
    finally:
        await scraper.close()


async def example_docs_scraping():
    """Scrape documentation sites with smart content extraction"""
    print("\n📖 Documentation Scraping Example")
    print("-" * 40)
    
    # Configure for documentation scraping
    config = UndetectableConfig(
        content_selectors=[
            "main",
            "article",
            ".documentation",
            "#content"
        ],
        remove_elements=["nav", "header", "footer", "aside"],
        output_format="markdown"
    )
    
    result = await scrape(
        "https://docs.python.org/3/library/asyncio.html",
        mode="docs",
        config=config
    )
    
    print(f"✅ Documentation scraped")
    print(f"📝 Markdown preview (first 500 chars):")
    print(result.get('markdown', '')[:500] + "...")


async def example_with_storage():
    """Scrape and store results in SQLite database"""
    print("\n💾 Scraping with Storage Example")
    print("-" * 40)
    
    # Initialize storage
    storage = SQLiteStorage(Path("./scraping_results.db"))
    
    # Create scraper with storage
    scraper = UnifiedScraper(
        browser_type="playwright",
        storage=storage
    )
    
    try:
        # Scrape multiple URLs
        urls = [
            "https://example.com",
            "https://example.org",
            "https://example.net"
        ]
        
        for url in urls:
            result = await scraper.scrape(url)
            print(f"✅ Scraped and stored: {url}")
        
        # Query stored results
        stats = storage.get_stats()
        print(f"\n📊 Storage Statistics:")
        print(f"  - Total documents: {stats['content_count']}")
        print(f"  - Database size: {stats['db_size_mb']:.2f} MB")
        
        # Search stored content
        search_results = storage.search("example")
        print(f"\n🔍 Search results for 'example': {len(search_results)} found")
        
    finally:
        await scraper.close()
        storage.close()


async def example_anti_detection_comparison():
    """Compare scraping with and without anti-detection"""
    print("\n🛡️ Anti-Detection Comparison")
    print("-" * 40)
    
    test_url = "https://bot.sannysoft.com/"  # Bot detection test site
    
    # Without anti-detection
    print("Testing WITHOUT anti-detection...")
    scraper1 = UnifiedScraper(
        browser_type="playwright",
        anti_detection=False
    )
    
    try:
        result1 = await scraper1.scrape(test_url)
        print("❌ Without anti-detection: May be detected as bot")
    finally:
        await scraper1.close()
    
    # With anti-detection
    print("\nTesting WITH anti-detection...")
    scraper2 = UnifiedScraper(
        browser_type="playwright",
        anti_detection=True,
        stealth=True
    )
    
    try:
        result2 = await scraper2.scrape(test_url)
        print("✅ With anti-detection: Should pass bot detection")
    finally:
        await scraper2.close()


async def main():
    """Run all examples"""
    print("🚀 Advanced Undetectable Toolkit Examples")
    print("=" * 60)
    
    # Note: Some examples may require dependencies to be installed
    try:
        # await example_wildcard_scraping()
        # await example_full_site_scraping()
        # await example_docs_scraping()
        # await example_with_storage()
        # await example_anti_detection_comparison()
        
        print("\n⚠️  Note: Examples are commented out until dependencies are installed")
        print("Run 'python install_toolkit.py' first to install all requirements")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure to install dependencies first!")


if __name__ == "__main__":
    asyncio.run(main())