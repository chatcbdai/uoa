#!/usr/bin/env python3
"""Debug scraping to see what links are found"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import browse_async

async def main():
    url = "https://docs.spaceandtime.io/docs"
    print(f"Checking links on: {url}")
    
    try:
        async with browse_async(headless=False) as browser:
            await browser.navigate(url)
            await asyncio.sleep(2)  # Wait for page to load
            
            # Get all links
            links = await browser.extract_links()
            
            print(f"\nFound {len(links)} total links")
            
            # Filter for docs links
            docs_links = [link for link in links if '/docs/' in link['href']]
            print(f"\nFound {len(docs_links)} docs links:")
            
            for link in docs_links[:20]:  # Show first 20
                print(f"  - {link['href']} ({link['text'][:50]}...)")
                
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())