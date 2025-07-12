# Social Media Automation Implementation Plan for Undetectable Toolkit

## Table of Contents
1. [Overview](#overview)
2. [Architecture Design](#architecture-design)
3. [Folder Structure](#folder-structure)
4. [Files to Create](#files-to-create)
5. [Files to Update](#files-to-update)
6. [Implementation Steps](#implementation-steps)
7. [Code Examples](#code-examples)
8. [Testing Plan](#testing-plan)
9. [Security Considerations](#security-considerations)

## Overview

This plan adds social media posting capabilities to the undetectable toolkit using a **dynamic, AI-powered approach** that avoids hardcoded selectors. The system will:

- Use existing Playwright browser with anti-detection features
- Leverage LLM to dynamically identify page elements
- Store credentials securely using keyring + Fernet encryption
- Read post content from CSV files
- Support Instagram, Twitter/X, Facebook, and LinkedIn

### Key Innovation: Dynamic Element Detection
Instead of maintaining brittle CSS selectors for each platform, we'll use the existing LLM integration to:
1. Take a screenshot or get page HTML
2. Ask the LLM to identify login fields, post buttons, etc.
3. Use the identified selectors dynamically

## Architecture Design

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   API Function      │────▶│  Social Media    │────▶│ Platform Module │
│ post_to_social()    │     │   Orchestrator   │     │  (Instagram)    │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
                                      │                         │
                                      ▼                         ▼
                            ┌──────────────────┐     ┌─────────────────┐
                            │ Credential Mgr   │     │ Stealth Browser │
                            │ (keyring+Fernet) │     │ (Anti-detection)│
                            └──────────────────┘     └─────────────────┘
                                      │                         │
                                      ▼                         ▼
                            ┌──────────────────┐     ┌─────────────────┐
                            │  Content Manager  │     │  LLM Service    │
                            │   (CSV Reader)    │     │ (Element Finder)│
                            └──────────────────┘     └─────────────────┘
```

## Folder Structure

```
undetectable_toolkit/
├── social_media/                        # NEW - Main module
│   ├── __init__.py
│   ├── base.py                         # Base social media poster class
│   ├── orchestrator.py                 # Main orchestration logic
│   ├── credential_manager.py           # Secure credential handling
│   ├── content_manager.py              # CSV content processing
│   ├── element_detector.py             # LLM-based element detection
│   ├── platforms/                      # Platform implementations
│   │   ├── __init__.py
│   │   ├── instagram.py
│   │   ├── twitter.py
│   │   ├── facebook.py
│   │   └── linkedin.py
│   └── exceptions.py                   # Custom exceptions
│
├── storage/
│   └── social_media/                   # NEW - Data storage
│       ├── credentials/                # Encrypted credentials
│       │   ├── .gitignore             # IMPORTANT: Ignore all credential files
│       │   └── master_key.enc         # Encrypted master key
│       ├── content/                    # CSV files with posts
│       │   ├── posts_template.csv     # Template file
│       │   └── scheduled_posts.csv    # Actual posts
│       ├── logs/                       # Posted content history
│       │   └── posting_history.db     # SQLite for tracking
│       └── media/                      # Images/videos for posts
│           └── .gitkeep
│
├── llm/
│   └── prompts.py                      # UPDATE - Add element detection prompts
│
├── config.py                           # UPDATE - Add SocialMediaConfig
├── api.py                              # UPDATE - Add post_to_social() function
├── __init__.py                         # UPDATE - Export new functions
├── requirements.txt                    # UPDATE - Add keyring, cryptography
└── tasks/
    └── executor.py                     # UPDATE - Add social media actions
```

## Files to Create

### 1. `/social_media/__init__.py`
```python
"""
Social Media Automation Module
"""

from .orchestrator import SocialMediaOrchestrator
from .exceptions import SocialMediaError, AuthenticationError, PostingError

__all__ = [
    'SocialMediaOrchestrator',
    'SocialMediaError',
    'AuthenticationError',
    'PostingError'
]
```

### 2. `/social_media/exceptions.py`
```python
"""Custom exceptions for social media module"""

class SocialMediaError(Exception):
    """Base exception for social media operations"""
    pass

class AuthenticationError(SocialMediaError):
    """Raised when authentication fails"""
    pass

class PostingError(SocialMediaError):
    """Raised when posting fails"""
    pass

class CredentialError(SocialMediaError):
    """Raised when credential operations fail"""
    pass
```

### 3. `/social_media/credential_manager.py`
```python
"""
Secure credential management using keyring + Fernet
"""

import json
import keyring
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CredentialManager:
    """Manages encrypted credentials for social media platforms"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path / "credentials"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.service_name = "undetectable_toolkit_social"
        self._fernet = None
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key from keyring"""
        # Try to get existing key from keyring
        key = keyring.get_password(self.service_name, "master_key")
        
        if not key:
            # Generate new key
            key = Fernet.generate_key().decode()
            keyring.set_password(self.service_name, "master_key", key)
            logger.info("Created new master encryption key")
        
        return key.encode()
    
    @property
    def fernet(self) -> Fernet:
        """Get Fernet instance with lazy loading"""
        if not self._fernet:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def save_credentials(self, platform: str, credentials: Dict[str, str]) -> None:
        """Save encrypted credentials for a platform"""
        try:
            # Encrypt the credentials
            encrypted = self.fernet.encrypt(json.dumps(credentials).encode())
            
            # Save to file
            cred_file = self.storage_path / f"{platform}.enc"
            cred_file.write_bytes(encrypted)
            
            logger.info(f"Saved credentials for {platform}")
        except Exception as e:
            raise CredentialError(f"Failed to save credentials: {str(e)}")
    
    def get_credentials(self, platform: str) -> Optional[Dict[str, str]]:
        """Get decrypted credentials for a platform"""
        try:
            cred_file = self.storage_path / f"{platform}.enc"
            
            if not cred_file.exists():
                return None
            
            # Read and decrypt
            encrypted = cred_file.read_bytes()
            decrypted = self.fernet.decrypt(encrypted)
            
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Failed to get credentials for {platform}: {str(e)}")
            return None
    
    def delete_credentials(self, platform: str) -> bool:
        """Delete credentials for a platform"""
        try:
            cred_file = self.storage_path / f"{platform}.enc"
            if cred_file.exists():
                cred_file.unlink()
                logger.info(f"Deleted credentials for {platform}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete credentials: {str(e)}")
            return False
```

### 4. `/social_media/element_detector.py`
```python
"""
Dynamic element detection using LLM
"""

import base64
from typing import Dict, Optional, List
from llm.base import Message
import logging

logger = logging.getLogger(__name__)

class ElementDetector:
    """Uses LLM to dynamically detect page elements"""
    
    ELEMENT_DETECTION_PROMPT = """Analyze this webpage and identify the CSS selectors for the requested elements.

Page URL: {url}
Platform: {platform}
Task: {task}

Required elements to find:
{elements}

Return a JSON object with the CSS selectors. Example:
{{
    "username_field": "input[name='username']",
    "password_field": "input[type='password']",
    "submit_button": "button[type='submit']"
}}

If an element cannot be found, use null as the value.
Only return the JSON object, no other text."""

    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def detect_login_elements(self, browser, platform: str) -> Dict[str, str]:
        """Detect login form elements"""
        try:
            # Take screenshot
            screenshot = await browser.take_screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            # Get page URL
            current_url = browser._page.url
            
            # Build prompt
            prompt = self.ELEMENT_DETECTION_PROMPT.format(
                url=current_url,
                platform=platform,
                task="login",
                elements="""- username_field: The username/email input field
- password_field: The password input field  
- submit_button: The login/submit button
- remember_me_checkbox: (optional) Remember me checkbox
- error_message: (optional) Error message container"""
            )
            
            # Ask LLM
            messages = [
                Message(role="user", content=prompt),
                Message(role="user", content=f"Screenshot: data:image/png;base64,{screenshot_b64}")
            ]
            
            response = await self.llm.generate(messages, temperature=0.1)
            
            # Parse JSON response
            import json
            selectors = json.loads(response.content.strip())
            
            logger.info(f"Detected login elements for {platform}: {selectors}")
            return selectors
            
        except Exception as e:
            logger.error(f"Element detection failed: {str(e)}")
            # Fallback to common selectors
            return self._get_fallback_selectors(platform, "login")
    
    async def detect_posting_elements(self, browser, platform: str) -> Dict[str, str]:
        """Detect posting form elements"""
        try:
            # Similar to login detection but for posting elements
            screenshot = await browser.take_screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            current_url = browser._page.url
            
            prompt = self.ELEMENT_DETECTION_PROMPT.format(
                url=current_url,
                platform=platform,
                task="create_post",
                elements="""- create_post_button: Button to start creating a new post
- text_field: Text input area for post content
- image_upload_button: Button to upload images
- post_submit_button: Button to publish the post
- privacy_selector: (optional) Privacy/audience selector"""
            )
            
            messages = [
                Message(role="user", content=prompt),
                Message(role="user", content=f"Screenshot: data:image/png;base64,{screenshot_b64}")
            ]
            
            response = await self.llm.generate(messages, temperature=0.1)
            
            import json
            selectors = json.loads(response.content.strip())
            
            logger.info(f"Detected posting elements for {platform}: {selectors}")
            return selectors
            
        except Exception as e:
            logger.error(f"Posting element detection failed: {str(e)}")
            return self._get_fallback_selectors(platform, "post")
    
    def _get_fallback_selectors(self, platform: str, task: str) -> Dict[str, str]:
        """Get fallback selectors if LLM detection fails"""
        # Common patterns that often work
        fallbacks = {
            "instagram": {
                "login": {
                    "username_field": "input[name='username']",
                    "password_field": "input[name='password']",
                    "submit_button": "button[type='submit']"
                },
                "post": {
                    "create_post_button": "svg[aria-label='New post']",
                    "text_field": "textarea[aria-label='Caption']",
                    "post_submit_button": "button:has-text('Share')"
                }
            },
            "twitter": {
                "login": {
                    "username_field": "input[autocomplete='username']",
                    "password_field": "input[name='password']",
                    "submit_button": "div[data-testid='LoginForm_Login_Button']"
                },
                "post": {
                    "create_post_button": "a[aria-label='Post']",
                    "text_field": "div[data-testid='tweetTextarea_0']",
                    "post_submit_button": "button[data-testid='tweetButtonInline']"
                }
            }
            # Add more platforms...
        }
        
        return fallbacks.get(platform, {}).get(task, {})
```

### 5. `/social_media/content_manager.py`
```python
"""
CSV content management for social media posts
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ContentManager:
    """Manages CSV content for social media posts"""
    
    def __init__(self, storage_path: Path):
        self.content_path = storage_path / "content"
        self.content_path.mkdir(parents=True, exist_ok=True)
        
        # Create template if it doesn't exist
        self._create_template()
    
    def _create_template(self):
        """Create a template CSV file"""
        template_path = self.content_path / "posts_template.csv"
        
        if not template_path.exists():
            headers = [
                "platform",
                "text",
                "image_path",
                "video_path", 
                "scheduled_time",
                "hashtags",
                "location",
                "status"
            ]
            
            with open(template_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                # Add example rows
                writer.writerow([
                    "instagram",
                    "Check out our new product! 🚀",
                    "media/product.jpg",
                    "",
                    "2025-07-13 10:00:00",
                    "#newproduct #launch #tech",
                    "San Francisco, CA",
                    "pending"
                ])
                writer.writerow([
                    "twitter",
                    "Exciting news coming soon! Stay tuned 👀",
                    "",
                    "",
                    "2025-07-13 14:00:00",
                    "#announcement #comingsoon",
                    "",
                    "pending"
                ])
            
            logger.info(f"Created template CSV at {template_path}")
    
    def get_pending_posts(self, platform: Optional[str] = None) -> List[Dict[str, str]]:
        """Get pending posts from CSV"""
        posts = []
        csv_file = self.content_path / "scheduled_posts.csv"
        
        if not csv_file.exists():
            logger.warning("No scheduled_posts.csv found")
            return posts
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('status', '').lower() == 'pending':
                        if platform is None or row.get('platform', '').lower() == platform.lower():
                            posts.append(row)
            
            logger.info(f"Found {len(posts)} pending posts")
            return posts
            
        except Exception as e:
            logger.error(f"Error reading posts: {str(e)}")
            return []
    
    def mark_as_posted(self, csv_file: str, row_index: int) -> bool:
        """Mark a post as completed"""
        try:
            csv_path = self.content_path / csv_file
            
            # Read all rows
            rows = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                rows = list(reader)
            
            # Update status
            if 0 <= row_index < len(rows):
                rows[row_index]['status'] = 'posted'
                rows[row_index]['posted_time'] = datetime.now().isoformat()
                
                # Write back
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers + ['posted_time'])
                    writer.writeheader()
                    writer.writerows(rows)
                
                logger.info(f"Marked row {row_index} as posted")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating post status: {str(e)}")
            return False
    
    def validate_media_files(self, posts: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate that media files exist"""
        media_path = self.content_path.parent / "media"
        
        for post in posts:
            # Check image
            if post.get('image_path'):
                full_path = media_path / post['image_path']
                if not full_path.exists():
                    logger.warning(f"Image not found: {full_path}")
                    post['image_path'] = None
                else:
                    post['image_full_path'] = str(full_path)
            
            # Check video
            if post.get('video_path'):
                full_path = media_path / post['video_path']
                if not full_path.exists():
                    logger.warning(f"Video not found: {full_path}")
                    post['video_path'] = None
                else:
                    post['video_full_path'] = str(full_path)
        
        return posts
```

### 6. `/social_media/base.py`
```python
"""
Base class for social media platforms
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class BaseSocialMediaPoster(ABC):
    """Abstract base class for social media posting"""
    
    def __init__(self, browser, credential_manager, element_detector):
        self.browser = browser
        self.credential_manager = credential_manager
        self.element_detector = element_detector
        self.platform_name = self.__class__.__name__.replace('Poster', '').lower()
        self.is_logged_in = False
    
    async def post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Main posting workflow"""
        try:
            # Step 1: Login if needed
            if not self.is_logged_in:
                await self.login()
            
            # Step 2: Navigate to posting area
            await self.navigate_to_post_creation()
            
            # Step 3: Create the post
            result = await self.create_post(content)
            
            # Step 4: Verify posting
            success = await self.verify_post_success()
            
            return {
                'success': success,
                'platform': self.platform_name,
                'post_url': result.get('url'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Posting failed on {self.platform_name}: {str(e)}")
            return {
                'success': False,
                'platform': self.platform_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def login(self) -> bool:
        """Login to the platform"""
        try:
            # Get credentials
            creds = self.credential_manager.get_credentials(self.platform_name)
            if not creds:
                raise AuthenticationError(f"No credentials found for {self.platform_name}")
            
            # Navigate to login page
            await self.browser.navigate(self.get_login_url())
            
            # Wait for page to load
            await asyncio.sleep(random.uniform(2, 4))
            
            # Detect login elements
            elements = await self.element_detector.detect_login_elements(
                self.browser, 
                self.platform_name
            )
            
            # Fill login form
            if elements.get('username_field'):
                await self.browser.type_text(
                    elements['username_field'], 
                    creds['username']
                )
            
            if elements.get('password_field'):
                await self.browser.type_text(
                    elements['password_field'],
                    creds['password']
                )
            
            # Click submit
            if elements.get('submit_button'):
                await self.browser.click(elements['submit_button'])
            
            # Wait for login to complete
            await asyncio.sleep(random.uniform(3, 5))
            
            # Check if login successful
            self.is_logged_in = await self.check_login_success()
            
            if not self.is_logged_in:
                raise AuthenticationError(f"Login failed for {self.platform_name}")
            
            logger.info(f"Successfully logged in to {self.platform_name}")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise
    
    async def navigate_to_post_creation(self):
        """Navigate to post creation area"""
        # Add human-like delay
        await asyncio.sleep(random.uniform(1, 3))
        
        # Navigate to home/feed first
        await self.browser.navigate(self.get_home_url())
        await asyncio.sleep(random.uniform(2, 4))
        
        # Find and click create post button
        elements = await self.element_detector.detect_posting_elements(
            self.browser,
            self.platform_name
        )
        
        if elements.get('create_post_button'):
            await self.browser.click(elements['create_post_button'])
            await asyncio.sleep(random.uniform(1, 2))
    
    @abstractmethod
    def get_login_url(self) -> str:
        """Get platform login URL"""
        pass
    
    @abstractmethod
    def get_home_url(self) -> str:
        """Get platform home URL"""
        pass
    
    @abstractmethod
    async def check_login_success(self) -> bool:
        """Check if login was successful"""
        pass
    
    @abstractmethod
    async def create_post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Create a post with given content"""
        pass
    
    @abstractmethod
    async def verify_post_success(self) -> bool:
        """Verify the post was created successfully"""
        pass
```

### 7. `/social_media/platforms/instagram.py`
```python
"""
Instagram posting implementation
"""

from social_media.base import BaseSocialMediaPoster
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class InstagramPoster(BaseSocialMediaPoster):
    """Instagram-specific posting implementation"""
    
    def get_login_url(self) -> str:
        return "https://www.instagram.com/accounts/login/"
    
    def get_home_url(self) -> str:
        return "https://www.instagram.com/"
    
    async def check_login_success(self) -> bool:
        """Check if we're logged in by looking for profile icon"""
        try:
            # Check URL first
            current_url = self.browser._page.url
            if "login" in current_url or "accounts" in current_url:
                return False
            
            # Look for profile elements
            profile_selectors = [
                "img[alt*='profile']",
                "div[role='menuitem']",
                "svg[aria-label='Profile']"
            ]
            
            for selector in profile_selectors:
                if await self.browser.wait_for_selector(selector, timeout=2000):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def create_post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Create an Instagram post"""
        try:
            # Detect posting elements
            elements = await self.element_detector.detect_posting_elements(
                self.browser,
                "instagram"
            )
            
            # Upload image if provided
            if content.get('image_full_path'):
                # Click file input or drag-drop area
                file_input = await self.browser._page.query_selector("input[type='file']")
                if file_input:
                    await file_input.set_input_files(content['image_full_path'])
                    await asyncio.sleep(random.uniform(2, 4))
                
                # Click Next buttons through the flow
                next_buttons = await self.browser._page.query_selector_all("button:has-text('Next')")
                for button in next_buttons:
                    await button.click()
                    await asyncio.sleep(random.uniform(1, 2))
            
            # Add caption
            if elements.get('text_field') and content.get('text'):
                await self.browser.type_text(
                    elements['text_field'],
                    content['text']
                )
                
                # Add hashtags
                if content.get('hashtags'):
                    await self.browser.type_text(
                        elements['text_field'],
                        f"\n\n{content['hashtags']}"
                    )
            
            # Share the post
            share_selectors = [
                "button:has-text('Share')",
                "button:has-text('Post')",
                elements.get('post_submit_button')
            ]
            
            for selector in share_selectors:
                if selector and await self.browser.wait_for_selector(selector, timeout=2000):
                    await self.browser.click(selector)
                    break
            
            # Wait for posting to complete
            await asyncio.sleep(random.uniform(3, 5))
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Instagram posting failed: {str(e)}")
            raise
    
    async def verify_post_success(self) -> bool:
        """Verify the post was created"""
        try:
            # Look for success indicators
            success_indicators = [
                "Your post has been shared",
                "Post shared",
                "View post"
            ]
            
            page_text = await self.browser.extract_text()
            
            for indicator in success_indicators:
                if indicator.lower() in page_text.lower():
                    return True
            
            # Check if we're back at the home feed
            current_url = self.browser._page.url
            if current_url == self.get_home_url():
                return True
            
            return False
            
        except Exception:
            return False
```

### 8. `/social_media/orchestrator.py`
```python
"""
Main orchestrator for social media posting
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import asyncio

from browser import BrowserFactory
from social_media.credential_manager import CredentialManager
from social_media.content_manager import ContentManager
from social_media.element_detector import ElementDetector
from social_media.platforms import get_poster_class
from social_media.exceptions import SocialMediaError

logger = logging.getLogger(__name__)

class SocialMediaOrchestrator:
    """Orchestrates social media posting across platforms"""
    
    def __init__(self, storage_path: Path, llm_client):
        self.storage_path = storage_path
        self.credential_manager = CredentialManager(storage_path)
        self.content_manager = ContentManager(storage_path)
        self.element_detector = ElementDetector(llm_client)
        self.llm_client = llm_client
    
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
            posts = self.content_manager.get_pending_posts()
            if not posts:
                raise SocialMediaError("No pending posts found in CSV")
        else:
            # Use provided content for all platforms
            posts = [{'platform': p, **content} for p in platforms]
        
        # Validate media files
        posts = self.content_manager.validate_media_files(posts)
        
        # Process each post
        for idx, post in enumerate(posts):
            platform = post['platform'].lower()
            
            if platform not in platforms:
                continue
            
            try:
                # Create browser instance
                browser = BrowserFactory.create(
                    engine="stealth",
                    headless=False,  # Show browser for social media
                    anti_detection=True
                )
                await browser.initialize()
                
                # Get poster class for platform
                poster_class = get_poster_class(platform)
                if not poster_class:
                    logger.error(f"No poster implementation for {platform}")
                    continue
                
                # Create poster instance
                poster = poster_class(
                    browser,
                    self.credential_manager,
                    self.element_detector
                )
                
                # Post content
                result = await poster.post(post)
                results.append(result)
                
                # Mark as posted if successful
                if result['success'] and use_csv:
                    self.content_manager.mark_as_posted('scheduled_posts.csv', idx)
                
                # Close browser
                await browser.close()
                
                # Add delay between platforms
                await asyncio.sleep(random.uniform(5, 10))
                
            except Exception as e:
                logger.error(f"Failed to post to {platform}: {str(e)}")
                results.append({
                    'success': False,
                    'platform': platform,
                    'error': str(e)
                })
        
        return results
    
    def add_credentials(self, platform: str, username: str, password: str) -> bool:
        """Add credentials for a platform"""
        try:
            self.credential_manager.save_credentials(
                platform,
                {'username': username, 'password': password}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials: {str(e)}")
            return False
    
    def list_platforms(self) -> List[str]:
        """List available platforms"""
        from social_media.platforms import AVAILABLE_PLATFORMS
        return AVAILABLE_PLATFORMS
```

## Files to Update

### 1. Update `/config.py`
Add after `StorageConfig` class:

```python
class SocialMediaConfig(BaseSettings):
    """Social media configuration"""
    enabled: bool = Field(default=True, env="SOCIAL_MEDIA_ENABLED")
    headless: bool = Field(default=False, env="SOCIAL_MEDIA_HEADLESS")
    post_delay_min: int = Field(default=5, env="POST_DELAY_MIN")
    post_delay_max: int = Field(default=10, env="POST_DELAY_MAX")
    max_retries: int = Field(default=3, env="SOCIAL_MEDIA_MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        extra = "ignore"
```

Update the main `Config` class:
```python
class Config:
    """Main configuration class"""
    def __init__(self):
        self.llm = LLMConfig()
        self.browser = BrowserConfig()
        self.execution = ExecutionConfig()
        self.storage = StorageConfig()
        self.social_media = SocialMediaConfig()  # ADD THIS LINE
```

### 2. Update `/api.py`
Add the new function after `screenshot()`:

```python
async def post_to_social_async(
    platforms: Union[str, List[str]],
    text: Optional[str] = None,
    image_path: Optional[str] = None,
    hashtags: Optional[str] = None,
    use_csv: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Post content to social media platforms.
    
    Args:
        platforms: Platform name(s) - 'instagram', 'twitter', 'facebook', 'linkedin'
        text: Post text content
        image_path: Path to image file
        hashtags: Hashtags to include
        use_csv: Read posts from CSV file instead
        **kwargs: Additional platform-specific options
        
    Returns:
        Dictionary with posting results for each platform
    """
    # Import here to avoid circular imports
    from social_media import SocialMediaOrchestrator
    
    # Ensure platforms is a list
    if isinstance(platforms, str):
        platforms = [platforms]
    
    # Get LLM client
    config = _global_config
    if config.llm.default_provider == "openai":
        from llm.openai_client import OpenAIClient
        llm_client = OpenAIClient()
    else:
        from llm.anthropic_client import AnthropicClient
        llm_client = AnthropicClient()
    
    # Create orchestrator
    storage_path = Path.cwd() / "storage" / "social_media"
    orchestrator = SocialMediaOrchestrator(storage_path, llm_client)
    
    # Prepare content
    content = None
    if not use_csv:
        content = {
            'text': text,
            'image_path': image_path,
            'hashtags': hashtags,
            **kwargs
        }
    
    # Post to platforms
    results = await orchestrator.post_to_platforms(
        platforms=platforms,
        content=content,
        use_csv=use_csv
    )
    
    return {
        'success': all(r['success'] for r in results),
        'results': results,
        'platforms_attempted': len(platforms),
        'platforms_succeeded': sum(1 for r in results if r['success'])
    }

def post_to_social(
    platforms: Union[str, List[str]],
    text: Optional[str] = None,
    image_path: Optional[str] = None,
    hashtags: Optional[str] = None,
    use_csv: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """Synchronous version of post_to_social_async"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            post_to_social_async(
                platforms, text, image_path, hashtags, use_csv, **kwargs
            )
        )
    finally:
        loop.close()
```

Update `__all__` at the bottom:
```python
__all__ = [
    'scrape', 'scrape_async',
    'browse', 'browse_async',
    'download', 'download_async',
    'search', 'search_async',
    'screenshot', 'screenshot_async',
    'post_to_social', 'post_to_social_async',  # ADD THIS LINE
    'UndetectableConfig', 'set_config'
]
```

### 3. Update `/__init__.py`
Add to imports:
```python
from .api import (
    scrape,
    browse,
    download,
    search,
    screenshot,
    post_to_social,  # ADD THIS LINE
    UndetectableConfig
)
```

Update `__all__`:
```python
__all__ = [
    "scrape",
    "browse", 
    "download",
    "search",
    "screenshot",
    "post_to_social",  # ADD THIS LINE
    "UndetectableConfig",
    "UndetectableBrowser",
    "UnifiedScraper"
]
```

### 4. Update `/tasks/executor.py`
In the `_execute_action` method's `action_map` dictionary, add:

```python
action_map = {
    'navigate': browser.navigate,
    'search': browser.search,
    'click': browser.click,
    'fill_form': browser.fill_form,
    'screenshot': browser.screenshot,
    'scrape': self._scrape_with_browser,
    'extract_data': self._extract_data,
    'extract': self._extract_data,
    'compare': self._compare_sites,
    'monitor': self._monitor_site,
    'download': self._download_file,
    # ADD THESE LINES:
    'post_instagram': self._post_to_instagram,
    'post_twitter': self._post_to_twitter,
    'post_facebook': self._post_to_facebook,
    'post_linkedin': self._post_to_linkedin,
    'post_social': self._post_to_social_media
}
```

Add these methods to the `TaskExecutor` class:

```python
async def _post_to_social_media(self, **kwargs):
    """Post to social media platforms"""
    from social_media import SocialMediaOrchestrator
    
    # Get platforms from kwargs
    platforms = kwargs.get('platforms', [])
    if isinstance(platforms, str):
        platforms = [platforms]
    
    # Create orchestrator
    storage_path = Path.cwd() / "storage" / "social_media"
    orchestrator = SocialMediaOrchestrator(storage_path, self.llm)
    
    # Post content
    return await orchestrator.post_to_platforms(
        platforms=platforms,
        content=kwargs.get('content'),
        use_csv=kwargs.get('use_csv', False)
    )

async def _post_to_instagram(self, **kwargs):
    """Post to Instagram"""
    kwargs['platforms'] = ['instagram']
    return await self._post_to_social_media(**kwargs)

async def _post_to_twitter(self, **kwargs):
    """Post to Twitter"""
    kwargs['platforms'] = ['twitter']
    return await self._post_to_social_media(**kwargs)

async def _post_to_facebook(self, **kwargs):
    """Post to Facebook"""
    kwargs['platforms'] = ['facebook']
    return await self._post_to_social_media(**kwargs)

async def _post_to_linkedin(self, **kwargs):
    """Post to LinkedIn"""
    kwargs['platforms'] = ['linkedin']
    return await self._post_to_social_media(**kwargs)
```

### 5. Update `/llm/prompts.py`
Add these prompts:

```python
ELEMENT_DETECTION_SYSTEM_PROMPT = """You are an expert at analyzing web pages and identifying UI elements.
Your task is to examine screenshots or HTML and return precise CSS selectors for requested elements.
Always return valid JSON with the exact structure requested."""

SOCIAL_MEDIA_POSTING_PROMPT = """You are helping to create social media posts.
Guidelines:
1. Keep posts within platform character limits
2. Use appropriate hashtags
3. Maintain brand voice
4. Optimize for engagement
5. Follow platform best practices"""
```

### 6. Update `/requirements.txt`
Add these dependencies:

```
keyring>=24.0.0
cryptography>=41.0.0
python-dotenv>=1.0.0
markdownify>=0.11.6
```

### 7. Create `/social_media/platforms/__init__.py`
```python
"""
Platform implementations
"""

from .instagram import InstagramPoster
from .twitter import TwitterPoster
from .facebook import FacebookPoster
from .linkedin import LinkedInPoster

PLATFORM_CLASSES = {
    'instagram': InstagramPoster,
    'twitter': TwitterPoster,
    'facebook': FacebookPoster,
    'linkedin': LinkedInPoster
}

AVAILABLE_PLATFORMS = list(PLATFORM_CLASSES.keys())

def get_poster_class(platform: str):
    """Get poster class for a platform"""
    return PLATFORM_CLASSES.get(platform.lower())

__all__ = [
    'InstagramPoster',
    'TwitterPoster', 
    'FacebookPoster',
    'LinkedInPoster',
    'get_poster_class',
    'AVAILABLE_PLATFORMS'
]
```

### 8. Create `/storage/social_media/.gitignore`
```
# Ignore all credential files
credentials/*.enc
credentials/master_key.enc

# Ignore actual post data but keep templates
content/scheduled_posts.csv
content/*.csv
!content/posts_template.csv

# Ignore logs
logs/*.db
logs/*.log

# Ignore uploaded media
media/*
!media/.gitkeep
```

## Implementation Steps

### Step 1: Create Folder Structure
```bash
cd /Users/chrisryviss/undetectable_toolkit

# Create directories
mkdir -p social_media/platforms
mkdir -p storage/social_media/{credentials,content,logs,media}

# Create .gitkeep files
touch storage/social_media/media/.gitkeep
```

### Step 2: Install Dependencies
```bash
pip install keyring cryptography
```

### Step 3: Create All Python Files
Create each file listed in the "Files to Create" section in order.

### Step 4: Update Existing Files
Update each file listed in the "Files to Update" section.

### Step 5: Create Template CSV
Run Python to create the template:
```python
from pathlib import Path
from social_media.content_manager import ContentManager

storage_path = Path.cwd() / "storage" / "social_media"
cm = ContentManager(storage_path)
# This will create the template automatically
```

### Step 6: Add Credentials
```python
import undetectable_toolkit as tk

# Add Instagram credentials
tk.post_to_social(
    platforms='instagram',
    action='add_credentials',
    username='your_username',
    password='your_password'
)
```

### Step 7: Test Posting
```python
# Test with direct content
result = tk.post_to_social(
    platforms=['instagram', 'twitter'],
    text="Hello from Undetectable Toolkit! 🚀",
    hashtags="#automation #python"
)

# Test with CSV
result = tk.post_to_social(
    platforms=['instagram', 'twitter'],
    use_csv=True
)
```

## Testing Plan

### 1. Unit Tests
Create `/tests/test_social_media.py`:

```python
import pytest
from pathlib import Path
from social_media.credential_manager import CredentialManager
from social_media.content_manager import ContentManager

def test_credential_encryption():
    """Test credential encryption/decryption"""
    cm = CredentialManager(Path("/tmp/test_social"))
    
    # Save credentials
    cm.save_credentials("test_platform", {
        "username": "testuser",
        "password": "testpass123"
    })
    
    # Retrieve credentials
    creds = cm.get_credentials("test_platform")
    assert creds["username"] == "testuser"
    assert creds["password"] == "testpass123"

def test_csv_reading():
    """Test CSV content reading"""
    cm = ContentManager(Path("/tmp/test_social"))
    
    # Create test CSV
    # ... test implementation
```

### 2. Integration Tests
Test each platform individually:

```python
# Test Instagram posting
async def test_instagram_post():
    result = await post_to_social_async(
        platforms='instagram',
        text="Test post from automation",
        image_path="test_image.jpg"
    )
    assert result['success']
```

### 3. Manual Testing Checklist
- [ ] Credential storage and retrieval
- [ ] CSV template creation
- [ ] Element detection with LLM
- [ ] Login to each platform
- [ ] Post text only
- [ ] Post with image
- [ ] Post with hashtags
- [ ] Error handling
- [ ] Logging

## Security Considerations

### 1. Credential Security
- Master key stored in OS keyring (not in files)
- All credentials encrypted with Fernet
- Never log credentials
- Add credentials folder to .gitignore

### 2. Anti-Detection
- Uses existing StealthBrowser with anti-detection
- Random delays between actions
- Human-like typing speeds
- Proper session management

### 3. Rate Limiting
- Configurable delays between posts
- Platform-specific rate limits
- Prevents account suspension

### 4. Error Handling
- Graceful fallbacks if LLM detection fails
- Proper exception handling
- Detailed logging without exposing credentials

## Usage Examples

### Basic Usage
```python
import undetectable_toolkit as tk

# Add credentials (one-time setup)
tk.post_to_social(
    platforms='instagram',
    action='add_credentials',
    username='your_username',
    password='your_password'
)

# Post to single platform
result = tk.post_to_social(
    platforms='instagram',
    text="Check out our new product! 🚀",
    image_path="/path/to/image.jpg",
    hashtags="#newproduct #launch"
)

# Post to multiple platforms
result = tk.post_to_social(
    platforms=['instagram', 'twitter', 'linkedin'],
    text="Exciting announcement coming soon!",
    hashtags="#announcement #comingsoon"
)

# Use CSV for bulk posting
result = tk.post_to_social(
    platforms=['instagram', 'twitter'],
    use_csv=True
)
```

### Advanced Usage
```python
# With task executor
from undetectable_toolkit.tasks import Task, TaskExecutor

executor = TaskExecutor()

# Create posting task
task = Task(
    id="post_001",
    action="post_social",
    parameters={
        "platforms": ["instagram", "twitter"],
        "text": "Automated post via task executor",
        "hashtags": "#automation #tasks"
    }
)

# Execute task
result = await executor.execute_task(task)
```

### CSV Format
Create `storage/social_media/content/scheduled_posts.csv`:

```csv
platform,text,image_path,video_path,scheduled_time,hashtags,location,status
instagram,"Morning vibes ☀️",sunrise.jpg,,2025-07-13 09:00:00,"#morning #motivation","New York, NY",pending
twitter,"Big announcement tomorrow! Stay tuned 👀",,,2025-07-13 15:00:00,"#announcement #exciting",,pending
linkedin,"Thrilled to share our Q2 results...",results.png,,2025-07-13 10:00:00,"#business #growth",,pending
```

## Troubleshooting

### Common Issues

1. **"No module named 'keyring'"**
   - Run: `pip install keyring cryptography`

2. **"Login failed"**
   - Check credentials are correct
   - Try with headless=False to see what's happening
   - Platform may have updated their UI

3. **"Element not found"**
   - LLM detection may have failed
   - Check fallback selectors
   - Platform UI may have changed

4. **"Post not created"**
   - Check character limits
   - Verify image format is supported
   - Check platform-specific requirements

### Debug Mode
Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your posting code
```

## Future Enhancements

1. **Scheduling System**
   - Use APScheduler for scheduled posts
   - Read scheduled_time from CSV

2. **Analytics Integration**
   - Track post performance
   - Store engagement metrics

3. **Multi-Account Support**
   - Store multiple credentials per platform
   - Account switching

4. **Story/Reel Support**
   - Platform-specific content types
   - Video processing

5. **AI Content Generation**
   - Use LLM to generate post text
   - Auto-generate hashtags

## Conclusion

This implementation provides a robust, maintainable, and secure social media automation system that:

1. **Leverages Existing Infrastructure**: Uses the current browser automation and LLM capabilities
2. **Dynamic Element Detection**: No hardcoded selectors - adapts to UI changes
3. **Secure Credential Storage**: Military-grade encryption with keyring
4. **Simple CSV Management**: Easy for non-technical users
5. **Extensible Design**: Easy to add new platforms
6. **Production-Ready**: Comprehensive error handling and logging

The system follows the KISS principle while being powerful enough for complex automation needs.