# Complete Social Media Automation Implementation Plan

## Overview

This plan enables fully automated social media posting through natural language commands in the CLI. Users can simply type "post to instagram" and the system will automatically:
1. Find the next pending post from the CSV
2. Use stored credentials to login
3. Post the content
4. Mark as completed

## Architecture Decision: Single vs Multiple CSVs

**Decision: Use SINGLE CSV with platform column** (current implementation)

**Reasons:**
- Industry best practice in 2025 (confirmed by research)
- Centralized content management
- Easier bulk operations
- Supports content recycling
- Simpler for users to manage

## Complete Flow Diagram

```
User Input: "publish a post on instagram"
    ↓
CLI (main.py) → WebAssistant (assistant.py)
    ↓
Natural Language Processing
    ↓
Action Mapping: post_social(platform='instagram')
    ↓
TaskExecutor → SocialMediaOrchestrator
    ↓
1. Check credentials exist
2. Get next pending Instagram post from CSV
3. If no posts → return "No posts available"
4. If post found → proceed
    ↓
5. Create browser instance (anti-detection)
6. Login using stored credentials
7. Navigate and create post
8. Mark as completed in CSV
9. Return success message
```

## Files to Create

### 1. `/storage/social_media/credentials_template.json`
```json
{
  "_README": "IMPORTANT: Fill out this template and run setup_credentials.py to securely store your credentials",
  "_WARNING": "NEVER commit this file with real credentials to git!",
  "_INSTRUCTIONS": [
    "1. Copy this file to credentials_filled.json",
    "2. Fill in your actual usernames and passwords",
    "3. Run: python setup_credentials.py",
    "4. Delete credentials_filled.json after setup"
  ],
  
  "platforms": {
    "instagram": {
      "username": "your_instagram_username",
      "password": "your_instagram_password",
      "_note": "Use your Instagram username, not email"
    },
    "twitter": {
      "username": "your_twitter_username_or_email",
      "password": "your_twitter_password",
      "_note": "Can use username, email, or phone number"
    },
    "facebook": {
      "username": "your_facebook_email",
      "password": "your_facebook_password",
      "_note": "Usually your email address"
    },
    "linkedin": {
      "username": "your_linkedin_email",
      "password": "your_linkedin_password",
      "_note": "Use your LinkedIn email address"
    }
  }
}
```

### 2. `/setup_credentials.py`
```python
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
    if creds['username'] == 'your_' + creds.get('platform', '') + '_username':
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
        print("Creating credential template...")
        template_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create template
        # (template content here)
    
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
```

## Files to Update

### 1. Update `/main.py`
Add social media commands to help menu and word completer:

```python
# In __init__ method, update word completer:
self.session = PromptSession(
    history=FileHistory('.assistant_history'),
    completer=WordCompleter([
        'help', 'exit', 'search', 'scrape', 'screenshot',
        'navigate', 'extract', 'compare', 'monitor',
        'post', 'publish', 'share',  # Add these
        'instagram', 'twitter', 'facebook', 'linkedin',  # Add these
        'social', 'media'  # Add these
    ])
)

# In show_help method, add to commands list:
commands = [
    ("search", "Search the web for information"),
    ("scrape", "Extract content from websites"),
    ("screenshot", "Take screenshots of web pages"),
    ("navigate", "Go to a specific website"),
    ("extract", "Extract specific data from pages"),
    ("compare", "Compare information across sites"),
    ("monitor", "Monitor websites for changes"),
    ("post/publish", "Post to social media platforms"),  # Add this
    ("help", "Show this help message"),
    ("exit", "Exit the assistant")
]

# Add examples section after the table:
self.console.print("\n[bold]Social Media Examples:[/bold]")
self.console.print("  • post to instagram")
self.console.print("  • publish on twitter") 
self.console.print("  • share on facebook")
self.console.print("  • post on linkedin")
```

### 2. Update `/assistant.py`
Add social media action parsing in `_parse_action` method:

```python
def _parse_action(self, action_text: str) -> Dict[str, Any]:
    """Parse LLM action response (simplified)"""
    # In production, use structured output
    # This is a simplified parser
    action_text_lower = action_text.lower()
    
    # Add social media parsing BEFORE other actions
    if any(word in action_text_lower for word in ['post', 'publish', 'share']) and \
       any(platform in action_text_lower for platform in ['instagram', 'twitter', 'facebook', 'linkedin', 'social']):
        # Extract platform
        platform = None
        for p in ['instagram', 'twitter', 'facebook', 'linkedin']:
            if p in action_text_lower:
                platform = p
                break
        
        if not platform and 'social' in action_text_lower:
            # Default to all platforms if just "social media"
            platform = 'all'
        
        return {
            'action': 'post_social',
            'parameters': {
                'platforms': [platform] if platform != 'all' else ['instagram', 'twitter', 'facebook', 'linkedin'],
                'use_csv': True  # Always use CSV for natural language commands
            }
        }
    
    # Existing parsing logic...
    elif 'navigate(' in action_text:
        # ... rest of existing code
```

### 3. Update `/llm/prompts.py`
Update WEB_ACTION_MAPPING_PROMPT to include social media:

```python
WEB_ACTION_MAPPING_PROMPT = """Convert the following natural language instruction into a specific browser action.

Available actions:
- navigate(url): Go to a specific URL
- search(query, engine): Search using Google/Bing/DuckDuckGo
- click(selector): Click an element
- fill_form(fields): Fill out form fields
- screenshot(url, full_page): Take a screenshot
- scrape(url, mode): Extract content from a page
- extract_data(selectors): Extract specific data using CSS selectors
- post_social(platforms, use_csv): Post to social media platforms from CSV

Social media examples:
- "post to instagram" → post_social(platforms=['instagram'], use_csv=True)
- "publish on twitter" → post_social(platforms=['twitter'], use_csv=True)
- "share on all social media" → post_social(platforms=['instagram','twitter','facebook','linkedin'], use_csv=True)

Instruction: {instruction}

Return the appropriate action with parameters."""
```

### 4. Update `/social_media/orchestrator.py`
Fix the platform filtering issue:

```python
async def post_to_platforms(
    self,
    platforms: List[str],
    content: Optional[Dict[str, str]] = None,
    use_csv: bool = True
) -> List[Dict[str, Any]]:
    """Post to multiple platforms"""
    results = []
    
    # Get content from CSV if requested
    if use_csv and not content:
        all_posts = []
        # Get posts for each requested platform
        for platform in platforms:
            platform_posts = self.content_manager.get_pending_posts(platform=platform)
            if platform_posts:
                # Only take the first pending post for each platform
                all_posts.append(platform_posts[0])
        
        if not all_posts:
            # Return friendly message instead of raising error
            return [{
                'success': False,
                'platform': 'all',
                'error': 'No pending posts found in CSV',
                'message': 'No posts available. Please add posts to scheduled_posts.csv'
            }]
        
        posts = all_posts
    else:
        # Use provided content for all platforms
        posts = [{'platform': p, **content} for p in platforms]
    
    # Rest of the method remains the same...
```

### 5. Update `/api.py`
Add a helper function for credential setup:

```python
def setup_social_credentials(
    platform: str,
    username: str,
    password: str
) -> bool:
    """
    Set up credentials for a social media platform
    
    Args:
        platform: Platform name ('instagram', 'twitter', 'facebook', 'linkedin')
        username: Username or email for the platform
        password: Password for the platform
        
    Returns:
        bool: True if successful
    """
    from social_media import SocialMediaOrchestrator
    from config import config as main_config
    
    # Get LLM client
    if main_config.llm.default_provider == "openai":
        from llm.openai_client import OpenAIClient
        llm_client = OpenAIClient()
    else:
        from llm.anthropic_client import AnthropicClient
        llm_client = AnthropicClient()
    
    # Create orchestrator
    storage_path = Path.cwd() / "storage" / "social_media"
    orchestrator = SocialMediaOrchestrator(storage_path, llm_client)
    
    # Add credentials
    return orchestrator.add_credentials(platform, username, password)

# Add to __all__
__all__ = [
    'scrape', 'scrape_async',
    'browse', 'browse_async',
    'download', 'download_async',
    'search', 'search_async',
    'screenshot', 'screenshot_async',
    'post_to_social', 'post_to_social_async',
    'setup_social_credentials',  # Add this
    'UndetectableConfig', 'set_config'
]
```

### 6. Update `/__init__.py`
Export the new credential setup function:

```python
from .api import (
    scrape,
    browse,
    download,
    search,
    screenshot,
    post_to_social,
    setup_social_credentials,  # Add this
    UndetectableConfig
)

__all__ = [
    "scrape",
    "browse", 
    "download",
    "search",
    "screenshot",
    "post_to_social",
    "setup_social_credentials",  # Add this
    "UndetectableConfig",
    "UndetectableBrowser",
    "UnifiedScraper"
]
```

### 7. Create `/storage/social_media/content/scheduled_posts.csv`
Example content file for users:

```csv
platform,text,image_path,video_path,scheduled_time,hashtags,location,status
instagram,Good morning! Starting the day with positive vibes ☀️,sunrise.jpg,,2025-07-13 09:00:00,#morning #motivation #positivity,New York,pending
twitter,Just launched our new feature! Check it out 🚀,,,2025-07-13 10:00:00,#launch #newfeature #tech,,pending
facebook,Weekend adventures await! Where are you exploring today?,weekend.jpg,,2025-07-13 11:00:00,#weekend #adventure #explore,,pending
linkedin,Excited to share insights from our latest project...,,,2025-07-13 12:00:00,#projectmanagement #insights #business,,pending
instagram,Sunset views from the office 🌅,sunset.jpg,,2025-07-13 18:00:00,#sunset #office #views,San Francisco,pending
```

## Usage Instructions

### 1. Initial Setup (One Time)

```bash
# Step 1: Copy and fill the credential template
cp storage/social_media/credentials_template.json storage/social_media/credentials_filled.json
# Edit credentials_filled.json with your actual credentials

# Step 2: Run setup script
python setup_credentials.py
# Choose option 1 and follow prompts

# Step 3: Delete the filled template for security
rm storage/social_media/credentials_filled.json
```

### 2. Add Content to CSV

Edit `storage/social_media/content/scheduled_posts.csv`:
- Add rows with platform-specific content
- Set status to "pending" for new posts
- Add images to `storage/social_media/media/` folder if needed

### 3. Use Natural Language Commands

In the CLI:
```
> post to instagram
> publish on twitter
> share on facebook
> post on all social media
```

The system will:
1. Find the next pending post for that platform
2. Login automatically using stored credentials
3. Create the post
4. Mark as completed in CSV
5. Show success message

## Security Considerations

1. **Credential Storage**:
   - Encrypted with Fernet + keyring
   - Never stored in plain text
   - Git-ignored by default

2. **Template Safety**:
   - Template file has clear warnings
   - Setup script validates inputs
   - Prompts to delete filled template

3. **Logging Safety**:
   - Credentials never logged
   - Sanitized error messages
   - No sensitive data in outputs

## Error Handling

The system handles these scenarios gracefully:

1. **No Pending Posts**: Returns friendly message instead of error
2. **Missing Credentials**: Prompts to run setup_credentials.py
3. **Login Failure**: Retries with anti-detection measures
4. **Missing Media Files**: Skips media, posts text only
5. **Platform Errors**: Logs error, continues with other platforms

## Future Enhancements

1. **Scheduling**: Add time-based posting
2. **Analytics**: Track post performance
3. **Content Generation**: Use LLM to generate posts
4. **Multi-Account**: Support multiple accounts per platform
5. **Webhooks**: Integration with external systems

## Testing Checklist

- [ ] Credential template is clear and unambiguous
- [ ] Setup script works with file and interactive modes
- [ ] Natural language commands are recognized
- [ ] Posts are filtered by platform correctly
- [ ] CSV status updates work properly
- [ ] Error messages are user-friendly
- [ ] No credentials appear in logs
- [ ] Anti-detection browser works for all platforms

This implementation provides a complete, secure, and user-friendly social media automation system that responds to natural language commands.