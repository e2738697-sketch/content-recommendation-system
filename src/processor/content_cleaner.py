import re
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentCleaner:
    """Content cleaner for removing duplicates, spam, and normalizing content"""
    
    def __init__(self):
        self.processed_ids = set()
        self.duplicate_patterns = [
            r'[\u4e00-\u9fff]+\1{2,}',  # Chinese character repetition
            r'[a-zA-Z0-9]+\1{2,}',  # English repetition
        ]
    
    def remove_duplicates(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate posts"""
        unique_posts = []
        seen_ids = set()
        
        for post in posts:
            post_id = f"{post.get('platform')}_{post.get('post_id')}"
            if post_id not in seen_ids:
                seen_ids.add(post_id)
                unique_posts.append(post)
            else:
                logger.debug(f"Duplicate post removed: {post_id}")
        
        return unique_posts
    
    def remove_spam(self, content: str) -> bool:
        """Check if content is spam"""
        # Check for excessive repetition
        for pattern in self.duplicate_patterns:
            if re.search(pattern, content):
                return True
        
        # Check for common spam keywords
        spam_keywords = ['??', '\\u200b', '\\u200c', '\\u200d']
        if any(keyword in content for keyword in spam_keywords):
            return True
        
        # Check for excessive punctuation
        punctuation_ratio = len(re.findall(r'[!?]+', content)) / (len(content) + 1)
        if punctuation_ratio > 0.3:
            return True
        
        return False
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special Unicode characters
        text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
        
        # Normalize punctuation
        text = re.sub(r'\n{2,}', '\n', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def normalize_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and clean a single post"""
        try:
            # Check for spam
            if self.remove_spam(post.get('content', '')):
                logger.info(f"Spam post removed: {post.get('post_id')}")
                return None
            
            # Clean text fields
            post['title'] = self.clean_text(post.get('title', ''))
            post['content'] = self.clean_text(post.get('content', ''))
            
            # Remove short content
            if len(post['content']) < 5:
                logger.info(f"Short content removed: {post.get('post_id')}")
                return None
            
            # Add processing timestamp
            post['clean_time'] = datetime.now().isoformat()
            post['cleaned'] = True
            
            return post
        except Exception as e:
            logger.error(f"Error normalizing post {post.get('post_id')}: {e}")
            return None
    
    def clean_batch(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and process batch of posts"""
        # Remove duplicates
        unique_posts = self.remove_duplicates(posts)
        logger.info(f"Removed {len(posts) - len(unique_posts)} duplicates")
        
        # Normalize individual posts
        cleaned_posts = []
        for post in unique_posts:
            cleaned = self.normalize_post(post)
            if cleaned:
                cleaned_posts.append(cleaned)
        
        logger.info(f"Cleaned {len(cleaned_posts)} posts from {len(posts)} total")
        
        return cleaned_posts
    
    def get_statistics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the posts"""
        stats = {
            'total': len(posts),
            'platforms': {},
            'avg_likes': 0,
            'avg_comments': 0,
            'avg_shares': 0
        }
        
        total_likes = 0
        total_comments = 0
        total_shares = 0
        
        for post in posts:
            platform = post.get('platform')
            stats['platforms'][platform] = stats['platforms'].get(platform, 0) + 1
            
            total_likes += post.get('likes', 0)
            total_comments += post.get('comments', 0)
            total_shares += post.get('shares', 0)
        
        if len(posts) > 0:
            stats['avg_likes'] = total_likes / len(posts)
            stats['avg_comments'] = total_comments / len(posts)
            stats['avg_shares'] = total_shares / len(posts)
        
        return stats
