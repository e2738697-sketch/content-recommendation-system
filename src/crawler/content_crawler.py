import asyncio
import aiohttp
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentCrawler:
    """Content crawler for fetching posts from Xiaohongshu and Douyin"""
    
    def __init__(self, proxy_list: List[str] = None):
        self.proxy_list = proxy_list or []
        self.current_proxy_idx = 0
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def init_session(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    def get_proxy(self) -> str:
        """Get next proxy from pool"""
        if not self.proxy_list:
            return None
        proxy = self.proxy_list[self.current_proxy_idx]
        self.current_proxy_idx = (self.current_proxy_idx + 1) % len(self.proxy_list)
        return proxy
    
    async def fetch_xiaohongshu(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
        """Fetch posts from Xiaohongshu"""
        try:
            url = f"https://edith.xiaohongshu.com/fe_api/biz/feed?keyword={keyword}&page={page}"
            proxy = self.get_proxy()
            
            async with self.session.get(url, headers=self.headers, proxy=proxy) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_xiaohongshu_response(data)
                else:
                    logger.warning(f"Failed to fetch Xiaohongshu: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Xiaohongshu: {e}")
            return []
    
    async def fetch_douyin(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
        """Fetch posts from Douyin"""
        try:
            url = f"https://www.douyin.com/api/v1/search?keyword={keyword}&page={page}"
            proxy = self.get_proxy()
            
            async with self.session.get(url, headers=self.headers, proxy=proxy) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_douyin_response(data)
                else:
                    logger.warning(f"Failed to fetch Douyin: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Douyin: {e}")
            return []
    
    def _parse_xiaohongshu_response(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse Xiaohongshu API response"""
        posts = []
        try:
            for item in data.get('items', []):
                post = {
                    'platform': 'xiaohongshu',
                    'post_id': item.get('id'),
                    'title': item.get('title'),
                    'content': item.get('content'),
                    'author': item.get('author', {}).get('name'),
                    'likes': item.get('interact_info', {}).get('zan_count', 0),
                    'comments': item.get('interact_info', {}).get('comment_count', 0),
                    'shares': item.get('interact_info', {}).get('share_count', 0),
                    'images': item.get('image_list', []),
                    'create_time': item.get('create_time'),
                    'crawl_time': datetime.now().isoformat()
                }
                posts.append(post)
        except Exception as e:
            logger.error(f"Error parsing Xiaohongshu response: {e}")
        return posts
    
    def _parse_douyin_response(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse Douyin API response"""
        posts = []
        try:
            for item in data.get('aweme_list', []):
                post = {
                    'platform': 'douyin',
                    'post_id': item.get('aweme_id'),
                    'title': item.get('desc'),
                    'content': item.get('desc'),
                    'author': item.get('author', {}).get('nickname'),
                    'likes': item.get('statistics', {}).get('digg_count', 0),
                    'comments': item.get('statistics', {}).get('comment_count', 0),
                    'shares': item.get('statistics', {}).get('share_count', 0),
                    'video_url': item.get('video', {}).get('play_addr', {}).get('url'),
                    'cover': item.get('video', {}).get('cover', {}).get('url'),
                    'create_time': item.get('create_time'),
                    'crawl_time': datetime.now().isoformat()
                }
                posts.append(post)
        except Exception as e:
            logger.error(f"Error parsing Douyin response: {e}")
        return posts
    
    async def crawl_batch(self, keywords: List[str], platforms: List[str] = None) -> Dict[str, List[Dict]]:
        """Crawl content from multiple sources"""
        if platforms is None:
            platforms = ['xiaohongshu', 'douyin']
        
        await self.init_session()
        results = {}
        
        try:
            tasks = []
            for platform in platforms:
                for keyword in keywords:
                    if platform == 'xiaohongshu':
                        tasks.append(self.fetch_xiaohongshu(keyword))
                    elif platform == 'douyin':
                        tasks.append(self.fetch_douyin(keyword))
            
            batch_results = await asyncio.gather(*tasks)
            for platform in platforms:
                results[platform] = []
            
            for result in batch_results:
                if result:
                    platform = result[0]['platform']
                    results[platform].extend(result)
        finally:
            await self.close_session()
        
        return results
