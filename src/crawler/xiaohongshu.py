#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书内容爬虫适配器
基于 MediaCrawler 架构，适配 Supabase 存储
"""

import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import sys

# Supabase 客户端
try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase package not installed. Run: pip install supabase")
    sys.exit(1)


class XiaohongshuCrawler:
    """
    小红书内容爬虫
    
    功能:
    1. 搜索指定关键词的笔记
    2. 获取笔记详情和评论
    3. 存储到 Supabase 数据库
    """
    
    def __init__(self):
        """初始化爬虫"""
        # 从环境变量获取 Supabase 配置
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
        
        # 初始化 Supabase 客户端
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # 搜索关键词（可从配置文件读取）
        self.keywords = self._load_keywords()
        
        print(f"✅ 小红书爬虫初始化成功")
        print(f"📌 搜索关键词: {self.keywords}")
    
    def _load_keywords(self) -> List[str]:
        """
        从环境变量或配置加载搜索关键词
        """
        # 尝试从环境变量加载
        keywords_str = os.getenv('SEARCH_KEYWORDS', '')
        if keywords_str:
            return [k.strip() for k in keywords_str.split(',')]
        
        # 默认关键词
        return ['居家好物', '数码测评', '美食探店']
    
    async def crawl(self):
        """
        执行爬取任务
        """
        print("\n🚀 开始爬取小红书内容...")
        
        try:
            # 这里需要集成 MediaCrawler 的实际爬虫逻辑
            # 由于 GitHub Actions 环境限制，这里提供示例数据结构
            sample_data = self._generate_sample_data()
            
            # 存储到 Supabase
            await self._save_to_database(sample_data)
            
            print(f"\n✅ 爬取完成！共采集 {len(sample_data)} 条内容")
            
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            raise
    
    def _generate_sample_data(self) -> List[Dict[str, Any]]:
        """
        生成示例数据（实际使用时应替换为真实爬取逻辑）
        """
        sample_data = []
        
        for keyword in self.keywords[:2]:  # 每个关键词爬取2条示例
            for i in range(2):
                sample_data.append({
                    'source': 'xiaohongshu',
                    'raw_data': {
                        'note_id': f'xhs_{keyword}_{i}_{datetime.now().timestamp()}',
                        'title': f'{keyword} 相关笔记 {i+1}',
                        'content': f'这是关于 {keyword} 的精彩内容...',
                        'author': f'用户{i+1}',
                        'likes': 1000 + i * 100,
                        'comments': 50 + i * 10,
                        'collected_at': datetime.now().isoformat(),
                        'tags': [keyword, '推荐'],
                        'images': [f'https://example.com/image_{i}.jpg']
                    }
                })
        
        return sample_data
    
    async def _save_to_database(self, data: List[Dict[str, Any]]):
        """
        保存数据到 Supabase
        """
        print(f"\n💾 开始存储数据到 Supabase...")
        
        for idx, item in enumerate(data, 1):
            try:
                # 插入到 content_raw 表
                result = self.supabase.table('content_raw').insert(item).execute()
                print(f"  [{idx}/{len(data)}] ✓ 已存储: {item['raw_data']['title']}")
            
            except Exception as e:
                print(f"  [{idx}/{len(data)}] ✗ 存储失败: {str(e)}")
        
        print(f"\n💾 数据存储完成")


async def main():
    """
    主函数
    """
    print("="*60)
    print("   小红书内容爬虫 - Supabase 适配版")
    print("="*60)
    
    try:
        crawler = XiaohongshuCrawler()
        await crawler.crawl()
    except Exception as e:
        print(f"\n❌ 程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    # 运行异步主函数
    asyncio.run(main())
