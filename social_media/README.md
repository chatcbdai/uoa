# Social Media Automation Module

This module provides automated posting capabilities for Instagram, Twitter/X, Facebook, and LinkedIn using the undetectable browser with anti-detection features.

## Features

- **Dynamic Element Detection**: Uses LLM to dynamically identify page elements instead of hardcoded selectors
- **Secure Credential Storage**: Credentials encrypted with Fernet and stored in OS keyring
- **CSV Content Management**: Bulk posting from CSV files
- **Anti-Detection**: Leverages existing StealthBrowser capabilities
- **Multi-Platform Support**: Instagram, Twitter/X, Facebook, LinkedIn

## Quick Start

### 1. Add Credentials

```python
from social_media import SocialMediaOrchestrator
from pathlib import Path

# Setup
storage_path = Path.cwd() / "storage" / "social_media"
orchestrator = SocialMediaOrchestrator(storage_path, llm_client)

# Add credentials
orchestrator.add_credentials(
    platform='instagram',
    username='your_username',
    password='your_password'
)
```

### 2. Post Content

```python
import undetectable_toolkit as tk

# Single platform
result = tk.post_to_social(
    platforms='instagram',
    text="Hello world! 🚀",
    image_path="/path/to/image.jpg",
    hashtags="#hello #world"
)

# Multiple platforms
result = tk.post_to_social(
    platforms=['instagram', 'twitter'],
    text="Check this out!",
    hashtags="#awesome"
)
```

### 3. CSV Posting

Create `storage/social_media/content/scheduled_posts.csv`:

```csv
platform,text,image_path,video_path,scheduled_time,hashtags,location,status
instagram,Morning vibes ☀️,sunrise.jpg,,2025-07-13 09:00:00,#morning #motivation,New York,pending
twitter,Big announcement tomorrow!,,,2025-07-13 15:00:00,#announcement,,pending
```

Then post:

```python
result = tk.post_to_social(
    platforms=['instagram', 'twitter'],
    use_csv=True
)
```

## File Structure

```
storage/social_media/
├── credentials/        # Encrypted credentials (git-ignored)
├── content/           # CSV files with posts
│   ├── posts_template.csv
│   └── scheduled_posts.csv
├── media/             # Images/videos for posts
└── logs/              # Posting history
```

## Security Notes

- Credentials are encrypted with Fernet
- Master key stored in OS keyring (not in files)
- All credential files are git-ignored
- Never commit real credentials

## Platform-Specific Notes

### Instagram
- Requires image for posts
- Supports location tagging
- Handles multi-step posting flow

### Twitter/X
- Character limit aware
- Supports media attachments
- Handles new X interface

### Facebook
- Supports photo/video posts
- Privacy settings available
- Handles post modals

### LinkedIn
- Professional content focus
- Supports article-style posts
- Company page support (future)

## Troubleshooting

1. **Login Failed**: Check credentials and 2FA settings
2. **Element Not Found**: LLM detection may need retry
3. **Post Not Created**: Check content requirements per platform
4. **Rate Limited**: Increase delays in config

## Future Enhancements

- Scheduled posting with APScheduler
- Story/Reel support
- Analytics integration
- Multi-account management
- AI content generation