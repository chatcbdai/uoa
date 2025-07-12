#!/usr/bin/env python3
"""Debug link extraction from ContentProcessor"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers import UnifiedScraper

async def main():
    url = "https://docs.spaceandtime.io/docs/*"
    print(f"Testing scrape of: {url}")
    
    try:
        async with UnifiedScraper(
            engine="stealth",
            headless=False,
            anti_detection=True
        ) as scraper:
            # Scrape the main page
            result = await scraper._scrape_page_with_links("https://docs.spaceandtime.io/docs", url)
            
            if result and 'links' in result:
                print(f"\nFound {len(result['links'])} links matching pattern {url}")
                
                # Show first 20 links
                for link in result['links'][:20]:
                    print(f"  - {link}")
            else:
                print("No result or no links found")
                
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())