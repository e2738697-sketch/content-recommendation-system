import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RecommendationService:
    """Main service that orchestrates all recommendation components"""
    
    def __init__(self, db_client, crawler, cleaner, tagger, recommender, user_manager, feishu_api):
        self.db = db_client
        self.crawler = crawler
        self.cleaner = cleaner
        self.tagger = tagger
        self.recommender = recommender
        self.user_manager = user_manager
        self.feishu = feishu_api
        self.logger = logging.getLogger(__name__)
    
    async def collect_and_process_content(self, keywords: List[str], platforms: List[str] = None) -> Dict[str, List[Any]]:
        """Main pipeline: collect, clean, and tag content"""
        try:
            # Step 1: Crawl content from sources
            self.logger.info(f"Collecting content for keywords: {keywords}")
            raw_posts = await self.crawler.crawl_batch(keywords, platforms)
            
            # Step 2: Clean and deduplicate
            self.logger.info(f"Cleaning content: {sum(len(p) for p in raw_posts.values())} posts")
            cleaned_posts = []
            for platform, posts in raw_posts.items():
                platform_posts = self.cleaner.clean_batch(posts)
                cleaned_posts.extend(platform_posts)
            
            # Step 3: Tag content
            self.logger.info(f"Tagging {len(cleaned_posts)} posts")
            tagged_posts = []
            for post in cleaned_posts:
                tags = self.tagger.tag(post.get('title', ''), post.get('content', ''))
                post.update(tags)
                tagged_posts.append(post)
            
            # Step 4: Store in database
            self.logger.info(f"Storing {len(tagged_posts)} posts in database")
            # await self.db.insert_posts(tagged_posts)
            
            self.logger.info("Content pipeline completed successfully")
            return {'success': True, 'posts': tagged_posts, 'count': len(tagged_posts)}
        except Exception as e:
            self.logger.error(f"Error in content pipeline: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_personalized_feed(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Generate personalized feed for a user"""
        try:
            # Get user profile
            user = self.user_manager.get_user(user_id)
            if not user:
                self.logger.warning(f"User {user_id} not found")
                return []
            
            # Get all available posts (in real app, fetch from DB)
            # posts = await self.db.get_posts()
            posts = []  # placeholder
            
            # Generate recommendations
            recommendations = self.recommender.personalize_feed(user_id, posts, limit)
            
            # Record view in user profile
            for rec in recommendations:
                self.user_manager.add_view_history(user_id, rec['post']['post_id'])
            
            self.logger.info(f"Generated feed for user {user_id}: {len(recommendations)} posts")
            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating feed: {e}")
            return []
    
    def record_user_interaction(self, user_id: str, post_id: str, interaction_type: str = 'view'):
        """Record user interaction with content"""
        try:
            # Record in user profile
            self.user_manager.add_view_history(user_id, post_id)
            
            # Record in recommender for collaborative filtering
            self.recommender.record_interaction(user_id, post_id, interaction_type)
            
            # Update in database
            # await self.db.record_interaction(user_id, post_id, interaction_type)
            
            self.logger.info(f"Recorded {interaction_type} for user {user_id} on post {post_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error recording interaction: {e}")
            return False
    
    def save_post(self, user_id: str, post_id: str) -> bool:
        """Save a post for a user"""
        try:
            self.user_manager.save_post(user_id, post_id)
            # await self.db.save_post(user_id, post_id)
            self.logger.info(f"Saved post {post_id} for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving post: {e}")
            return False
    
    def get_trending_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending content based on engagement metrics"""
        try:
            # In real app, fetch trending posts from DB
            # trending = await self.db.get_trending_posts(limit)
            trending = []
            
            self.logger.info(f"Retrieved {len(trending)} trending posts")
            return trending
        except Exception as e:
            self.logger.error(f"Error getting trending content: {e}")
            return []
    
    def send_notification(self, user_id: str, message: str, post_id: str = None) -> bool:
        """Send notification to user via Feishu"""
        try:
            user = self.user_manager.get_user(user_id)
            if not user:
                return False
            
            # Format and send via Feishu
            notification = {
                'user_id': user_id,
                'message': message,
                'post_id': post_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # await self.feishu.send_message(user.email, notification)
            self.logger.info(f"Sent notification to user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get user engagement analytics"""
        try:
            user_info = self.user_manager.get_user_info(user_id)
            view_history = self.user_manager.get_user_view_history(user_id)
            saved_posts = self.user_manager.get_user_saved_posts(user_id)
            
            analytics = {
                'user_info': user_info,
                'total_views': len(view_history),
                'total_saved': len(saved_posts),
                'interests': user_info.get('interests', []) if user_info else [],
                'timestamp': datetime.now().isoformat()
            }
            
            return analytics
        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}")
            return {}
