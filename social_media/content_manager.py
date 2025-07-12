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