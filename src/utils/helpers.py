import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DateTimeHelper:
    """DateTime utilities for handling timestamps and date operations"""
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    @staticmethod
    def get_date_range(days: int = 7) -> tuple:
        """Get date range for analytics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def parse_iso_datetime(dt_string: str) -> datetime:
        """Parse ISO format datetime string"""
        return datetime.fromisoformat(dt_string)

class TextHelper:
    """Text processing utilities"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + '...'
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-friendly slug"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)
        return text.strip('-')
    
    @staticmethod
    def extract_keywords(text: str, num_keywords: int = 5) -> List[str]:
        """Extract top keywords from text (simple word frequency)"""
        from collections import Counter
        words = text.lower().split()
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        filtered = [w for w in words if w not in common_words and len(w) > 2]
        return [word for word, _ in Counter(filtered).most_common(num_keywords)]

class HashHelper:
    """Hashing utilities for data integrity"""
    
    @staticmethod
    def generate_hash(data: str) -> str:
        """Generate SHA-256 hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def generate_short_id(prefix: str = '') -> str:
        """Generate short unique ID"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{unique_id}" if prefix else unique_id

class ValidationHelper:
    """Data validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format"""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def sanitize_input(data: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent injection attacks"""
        import re
        data = data.strip()
        data = re.sub(r'[<>\";{}]', '', data)
        return data[:max_length]

class JSONHelper:
    """JSON utilities for serialization"""
    
    @staticmethod
    def safe_json_loads(json_str: str, default: Any = None) -> Any:
        """Safely load JSON string with default fallback"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return default
    
    @staticmethod
    def to_json_serializable(obj: Any) -> Any:
        """Convert object to JSON-serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return obj

class CacheHelper:
    """Cache management utilities"""
    
    cache_store: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in cls.cache_store:
            cached = cls.cache_store[key]
            # Check if expired
            if cached['expires'] > datetime.now():
                return cached['value']
            else:
                del cls.cache_store[key]
        return None
    
    @classmethod
    def set(cls, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache with TTL"""
        cls.cache_store[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=ttl_seconds)
        }
    
    @classmethod
    def clear(cls):
        """Clear all cache"""
        cls.cache_store.clear()

class PaginationHelper:
    """Pagination utilities"""
    
    @staticmethod
    def paginate(items: List[Any], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Paginate list of items"""
        total = len(items)
        total_pages = (total + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return {
            'items': items[start_idx:end_idx],
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
