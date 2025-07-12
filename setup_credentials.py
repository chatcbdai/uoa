#!/usr/bin/env python3
"""
Secure credential setup for social media automation

This script reads credentials from a template and securely stores them.
"""

import json
import sys
from pathlib import Path
from getpass import getpass
import logging

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from social_media.credential_manager import CredentialManager
from social_media.exceptions import CredentialError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_credentials(creds: dict) -> bool:
    """Validate credential format"""
    if not creds.get('username') or not creds.get('password'):
        return False
    if creds['username'].startswith('your_'):
        return False
    return True

def setup_from_file():
    """Setup credentials from filled template file"""
    template_path = Path("storage/social_media/credentials_filled.json")
    
    if not template_path.exists():
        print("❌ credentials_filled.json not found!")
        print("\nPlease:")
        print("1. Copy credentials_template.json to credentials_filled.json")
        print("2. Fill in your actual credentials")
        print("3. Run this script again")
        return False
    
    try:
        with open(template_path, 'r') as f:
            data = json.load(f)
        
        # Initialize credential manager
        storage_path = Path.cwd() / "storage" / "social_media"
        manager = CredentialManager(storage_path)
        
        platforms = data.get('platforms', {})
        saved_count = 0
        
        for platform, creds in platforms.items():
            # Skip metadata fields
            if platform.startswith('_'):
                continue
            
            # Clean credentials (remove _note fields)
            clean_creds = {
                'username': creds.get('username'),
                'password': creds.get('password')
            }
            
            if validate_credentials(clean_creds):
                try:
                    manager.save_credentials(platform, clean_creds)
                    print(f"✅ Saved credentials for {platform}")
                    saved_count += 1
                except Exception as e:
                    print(f"❌ Failed to save {platform}: {str(e)}")
            else:
                print(f"⚠️  Skipped {platform} - appears to be template values")
        
        if saved_count > 0:
            print(f"\n✅ Successfully saved credentials for {saved_count} platforms")
            print("\n⚠️  IMPORTANT: Delete credentials_filled.json now for security!")
            return True
        else:
            print("\n❌ No valid credentials were saved")
            return False
            
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials_filled.json")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def setup_interactive():
    """Interactive credential setup"""
    print("\n=== Interactive Credential Setup ===")
    
    storage_path = Path.cwd() / "storage" / "social_media"
    manager = CredentialManager(storage_path)
    
    platforms = ['instagram', 'twitter', 'facebook', 'linkedin']
    
    for platform in platforms:
        print(f"\n--- {platform.title()} ---")
        response = input(f"Set up {platform}? (y/n): ").lower()
        
        if response == 'y':
            username = input(f"{platform} username/email: ")
            password = getpass(f"{platform} password: ")
            
            if username and password:
                try:
                    manager.save_credentials(platform, {
                        'username': username,
                        'password': password
                    })
                    print(f"✅ Saved credentials for {platform}")
                except Exception as e:
                    print(f"❌ Failed to save: {str(e)}")

def main():
    """Main setup function"""
    print("Social Media Credential Setup")
    print("=" * 40)
    
    # Check if template exists
    template_path = Path("storage/social_media/credentials_template.json")
    if not template_path.exists():
        print("❌ Credential template not found!")
        print("Run the system once to create the template.")
        return
    
    print("\nSetup options:")
    print("1. From filled template file (recommended)")
    print("2. Interactive setup")
    
    choice = input("\nChoose option (1 or 2): ")
    
    if choice == '1':
        success = setup_from_file()
    elif choice == '2':
        setup_interactive()
        success = True
    else:
        print("Invalid choice")
        success = False
    
    if success:
        print("\n✅ Credential setup complete!")
        print("You can now use natural language commands like:")
        print('  - "post to instagram"')
        print('  - "publish on twitter"')
        print('  - "share on linkedin"')

if __name__ == "__main__":
    main()