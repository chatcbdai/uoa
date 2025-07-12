# Documentation

This directory contains documentation for the Undetectable Toolkit.

## Available Documentation

### Social Media Automation
- `SOCIAL_MEDIA_IMPLEMENTATION_PLAN.md` - Original implementation plan
- `SOCIAL_MEDIA_AUTOMATION_COMPLETE_PLAN.md` - Complete implementation guide
- `CREDENTIAL_SETUP_INSTRUCTIONS.md` - Step-by-step credential setup guide

## Quick Links

- [Credential Setup](CREDENTIAL_SETUP_INSTRUCTIONS.md) - Start here to set up social media credentials
- [Implementation Details](SOCIAL_MEDIA_AUTOMATION_COMPLETE_PLAN.md) - Technical implementation details

## File Organization

```
undetectable_toolkit/
├── docs/                    # Documentation files
├── tests/                   # Test scripts
├── social_media/           # Social media automation module
└── storage/social_media/   # Data storage
    ├── credentials/        # Encrypted credentials (git-ignored)
    ├── content/           # CSV posts (scheduled_posts.csv)
    └── media/            # Images/videos for posts
```