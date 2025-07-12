#!/usr/bin/env python3
"""
Test script for social media automation

This demonstrates how to use the social media posting feature.
"""

import sys
from pathlib import Path
# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import api as tk

def test_add_credentials():
    """Example of adding credentials (DO NOT commit real credentials!)"""
    print("=== Adding Credentials Example ===")
    print("In real usage, you would do:")
    print("""
    # Add Instagram credentials
    from social_media import SocialMediaOrchestrator
    
    storage_path = Path.cwd() / "storage" / "social_media"
    orchestrator = SocialMediaOrchestrator(storage_path, llm_client)
    
    # Add credentials
    orchestrator.add_credentials(
        platform='instagram',
        username='your_username',
        password='your_password'
    )
    """)

def test_direct_post():
    """Example of posting directly with content"""
    print("\n=== Direct Posting Example ===")
    print("""
    # Post to single platform
    result = tk.post_to_social(
        platforms='instagram',
        text="Hello from Undetectable Toolkit! 🚀",
        hashtags="#automation #python"
    )
    
    # Post to multiple platforms
    result = tk.post_to_social(
        platforms=['instagram', 'twitter'],
        text="Check out our awesome toolkit!",
        image_path="/path/to/image.jpg",
        hashtags="#tech #automation"
    )
    
    print(f"Success: {result['success']}")
    print(f"Platforms attempted: {result['platforms_attempted']}")
    print(f"Platforms succeeded: {result['platforms_succeeded']}")
    """)

def test_csv_posting():
    """Example of posting from CSV"""
    print("\n=== CSV Posting Example ===")
    print("""
    # Use the posts from scheduled_posts.csv
    result = tk.post_to_social(
        platforms=['instagram', 'twitter'],
        use_csv=True
    )
    
    # The system will:
    # 1. Read pending posts from scheduled_posts.csv
    # 2. Post to the specified platforms
    # 3. Mark posts as completed
    """)

def show_csv_format():
    """Show the CSV format"""
    print("\n=== CSV Format ===")
    csv_path = Path.cwd() / "storage" / "social_media" / "content" / "posts_template.csv"
    if csv_path.exists():
        with open(csv_path, 'r') as f:
            print(f.read())
    else:
        print("Template CSV not found. Run ContentManager to create it.")

def main():
    print("Social Media Automation Test Script")
    print("=" * 40)
    
    test_add_credentials()
    test_direct_post()
    test_csv_posting()
    show_csv_format()
    
    print("\n=== Important Notes ===")
    print("1. Add your credentials first using the credential manager")
    print("2. The browser will open in non-headless mode for social media")
    print("3. CSV posts in 'pending' status will be processed")
    print("4. Successfully posted items are marked as 'posted'")
    print("5. Media files should be placed in storage/social_media/media/")

if __name__ == "__main__":
    main()