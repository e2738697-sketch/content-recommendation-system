import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class UserProfile:
    """Represents a user profile in the system"""
    
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = datetime.now().isoformat()
        self.preferences = {}
        self.interests = set()
        self.blocked_keywords = set()
        self.followed_tags = set()
        self.view_history = []
        self.saved_posts = set()
        self.profile_complete = False
    
    def update_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences"""
        allowed_keys = ['language', 'notification', 'privacy', 'theme', 'recommendation_level']
        for key, value in preferences.items():
            if key in allowed_keys:
                self.preferences[key] = value
    
    def add_interest(self, interest: str):
        """Add an interest to user profile"""
        self.interests.add(interest.lower())
    
    def remove_interest(self, interest: str):
        """Remove an interest from user profile"""
        self.interests.discard(interest.lower())
    
    def set_interests(self, interests: List[str]):
        """Set all interests at once"""
        self.interests = set(i.lower() for i in interests)
    
    def add_blocked_keyword(self, keyword: str):
        """Add a blocked keyword"""
        self.blocked_keywords.add(keyword.lower())
    
    def add_view_history(self, post_id: str, view_time: float = None):
        """Add post to view history"""
        self.view_history.append({
            'post_id': post_id,
            'view_time': datetime.now().isoformat(),
            'duration': view_time or 0
        })
    
    def save_post(self, post_id: str):
        """Save a post"""
        self.saved_posts.add(post_id)
    
    def unsave_post(self, post_id: str):
        """Unsave a post"""
        self.saved_posts.discard(post_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'preferences': self.preferences,
            'interests': list(self.interests),
            'blocked_keywords': list(self.blocked_keywords),
            'followed_tags': list(self.followed_tags),
            'saved_posts_count': len(self.saved_posts),
            'view_history_count': len(self.view_history)
        }

class UserProfileManager:
    """Manages user profiles in the system"""
    
    def __init__(self):
        self.profiles = {}
        self.email_index = {}
    
    def create_user(self, user_id: str, username: str, email: str) -> UserProfile:
        """Create a new user profile"""
        if user_id in self.profiles:
            logger.warning(f"User {user_id} already exists")
            return self.profiles[user_id]
        
        if email in self.email_index:
            logger.warning(f"Email {email} already registered")
            return None
        
        profile = UserProfile(user_id, username, email)
        self.profiles[user_id] = profile
        self.email_index[email] = user_id
        
        logger.info(f"User created: {user_id}")
        return profile
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self.profiles.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user profile by email"""
        user_id = self.email_index.get(email)
        if user_id:
            return self.profiles.get(user_id)
        return None
    
    def update_user_interests(self, user_id: str, interests: List[str]) -> bool:
        """Update user interests"""
        user = self.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        user.set_interests(interests)
        logger.info(f"Updated interests for user {user_id}")
        return True
    
    def add_view_history(self, user_id: str, post_id: str, view_time: float = None) -> bool:
        """Record user view of a post"""
        user = self.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        user.add_view_history(post_id, view_time)
        return True
    
    def save_post(self, user_id: str, post_id: str) -> bool:
        """Save a post for user"""
        user = self.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        user.save_post(post_id)
        return True
    
    def get_user_saved_posts(self, user_id: str) -> set:
        """Get all saved posts for a user"""
        user = self.get_user(user_id)
        if not user:
            return set()
        return user.saved_posts
    
    def get_user_view_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user view history"""
        user = self.get_user(user_id)
        if not user:
            return []
        return user.view_history[-limit:]
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        user = self.get_user(user_id)
        if not user:
            return None
        return user.to_dict()
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user profile"""
        user = self.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        email = user.email
        del self.profiles[user_id]
        del self.email_index[email]
        
        logger.info(f"User deleted: {user_id}")
        return True
