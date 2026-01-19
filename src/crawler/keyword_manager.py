"""关键词管理和定时爬取模块"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.db.supabase_client import SupabaseClient
from src.crawler.content_crawler import ContentCrawler


class KeywordManager:
    """管理用户输入的关键词并执行定时爬取"""
    
    def __init__(self):
        """初始化关键词管理器"""
        self.db = SupabaseClient()
        self.crawler = ContentCrawler()
    
    def add_keyword(self, keyword: str, platform: str = "xiaohongshu", 
                    interval_hours: int = 12) -> Dict:
        """添加新的爬取关键词
        
        Args:
            keyword: 搜索关键词（例如："美妆产品", "护肤品"）
            platform: 平台（xiaohongshu 或 douyin）
            interval_hours: 爬取间隔（小时，默认12小时）
        
        Returns:
            插入的关键词记录
        """
        keyword_record = {
            'keyword': keyword,
            'platform': platform,
            'interval_hours': interval_hours,
            'last_crawl_time': None,
            'next_crawl_time': datetime.utcnow().isoformat(),
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = self.db.insert('keywords', keyword_record)
        return result
    
    def get_active_keywords(self) -> List[Dict]:
        """获取所有活跃的关键词
        
        Returns:
            关键词列表
        """
        keywords = self.db.select('keywords', 
                                 query_filter={'is_active': True})
        return keywords or []
    
    def get_due_keywords(self) -> List[Dict]:
        """获取所有应该执行爬取的关键词
        
        Returns:
            需要爬取的关键词列表
        """
        now = datetime.utcnow().isoformat()
        keywords = self.db.select('keywords',
                                 query_filter={
                                     'is_active': True,
                                     'next_crawl_time_le': now
                                 })
        return keywords or []
    
    def execute_crawl_for_keyword(self, keyword_id: str) -> Dict:
        """为指定关键词执行爬取任务
        
        Args:
            keyword_id: 关键词ID
        
        Returns:
            爬取结果
        """
        # 获取关键词详情
        keywords = self.db.select('keywords', 
                                 query_filter={'id': keyword_id})
        if not keywords:
            return {'status': 'error', 'message': '关键词不存在'}
        
        keyword_record = keywords[0]
        keyword = keyword_record['keyword']
        platform = keyword_record['platform']
        interval_hours = keyword_record['interval_hours']
        
        # 执行爬取
        try:
            crawled_content = self.crawler.crawl(
                platform=platform,
                keywords=keyword,
                count=20,
                max_pages=5
            )
            
            # 更新最后爬取时间和下次爬取时间
            now = datetime.utcnow()
            next_crawl = now + timedelta(hours=interval_hours)
            
            self.db.update(
                'keywords',
                {'id': keyword_id},
                {
                    'last_crawl_time': now.isoformat(),
                    'next_crawl_time': next_crawl.isoformat(),
                    'last_crawl_count': len(crawled_content)
                }
            )
            
            return {
                'status': 'success',
                'keyword': keyword,
                'count': len(crawled_content),
                'next_crawl_time': next_crawl.isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def disable_keyword(self, keyword_id: str) -> bool:
        """禁用关键词爬取
        
        Args:
            keyword_id: 关键词ID
        
        Returns:
            是否成功禁用
        """
        self.db.update('keywords', {'id': keyword_id}, 
                      {'is_active': False})
        return True
    
    def get_keyword_statistics(self, keyword_id: str) -> Dict:
        """获取关键词的爬取统计信息
        
        Args:
            keyword_id: 关键词ID
        
        Returns:
            统计信息
        """
        keywords = self.db.select('keywords',
                                 query_filter={'id': keyword_id})
        if not keywords:
            return {}
        
        keyword = keywords[0]
        return {
            'keyword': keyword.get('keyword'),
            'platform': keyword.get('platform'),
            'total_crawls': keyword.get('total_crawl_count', 0),
            'last_crawl_time': keyword.get('last_crawl_time'),
            'next_crawl_time': keyword.get('next_crawl_time'),
            'is_active': keyword.get('is_active')
        }


if __name__ == '__main__':
    manager = KeywordManager()
    
    # 示例：添加关键词
    # result = manager.add_keyword('美妆产品', platform='xiaohongshu', 
    #                              interval_hours=12)
    # print(f"添加关键词: {result}")
    
    # 获取活跃关键词
    active = manager.get_active_keywords()
    print(f"活跃关键词数量: {len(active)}")
