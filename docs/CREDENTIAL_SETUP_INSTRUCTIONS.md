# Social Media Credential Setup Instructions

## Quick Start

1. **Copy the template**:
   ```bash
   cp storage/social_media/credentials_template.json storage/social_media/credentials_filled.json
   ```

2. **Edit credentials_filled.json** with your actual credentials:
   ```json
   {
     "platforms": {
       "instagram": {
         "username": "your_actual_instagram_username",
         "password": "your_actual_password"
       },
       // ... other platforms
     }
   }
   ```

3. **Run the setup script**:
   ```bash
   python setup_credentials.py
   ```
   Choose option 1 when prompted.

4. **Delete the filled template** (IMPORTANT for security):
   ```bash
   rm storage/social_media/credentials_filled.json
   ```

## How It Works

- Credentials are encrypted using Fernet encryption
- The master key is stored in your OS keyring (not in files)
- Each platform's credentials are stored in separate encrypted files
- The system will automatically use these credentials when posting

## Using the System

Once credentials are set up, you can use natural language commands in the CLI:

- `post to instagram` - Posts the next pending Instagram post from CSV
- `publish on twitter` - Posts the next pending Twitter post
- `share on facebook` - Posts the next pending Facebook post
- `post on linkedin` - Posts the next pending LinkedIn post

## Adding Content

Edit `storage/social_media/content/scheduled_posts.csv`:

```csv
platform,text,image_path,video_path,scheduled_time,hashtags,location,status
instagram,Good morning! ☀️,sunrise.jpg,,2025-07-13 09:00:00,#morning #motivation,New York,pending
twitter,Big news coming soon!,,,2025-07-13 10:00:00,#announcement,,pending
```

- Set `status` to `pending` for new posts
- Add images to `storage/social_media/media/` folder
- The system will automatically mark posts as `completed` after posting

## Security Notes

- NEVER commit credentials_filled.json to git
- The template file is safe to commit (contains no real data)
- Credentials are never logged or displayed
- All credential files are git-ignored by default

## Troubleshooting

**"No posts available"**
- Check that scheduled_posts.csv has posts with status="pending"
- Ensure the platform column matches exactly (lowercase: instagram, twitter, facebook, linkedin)

**"No credentials found"**
- Run setup_credentials.py to set up credentials
- Check that the platform name matches exactly

**Login fails**
- Verify credentials are correct
- Check if 2FA is enabled (not yet supported)
- Try with headless=False to see what's happening