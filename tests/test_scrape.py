#!/usr/bin/env python3
"""Direct test of scraping functionality"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import scrape_async

async def main():
    url = "https://docs.spaceandtime.io/docs/*"
    print(f"Testing scrape of: {url}")
    
    try:
        result = await scrape_async(url, mode="wildcard")
        print(f"Scraping completed successfully!")
        print(f"Files saved to: {result.get('output_dir', 'Unknown')}")
        print(f"Total pages scraped: {len(result.get('files', []))}")
    except Exception as e:
        print(f"Error during scraping: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())