#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书瑜伽主题爬虫
搜索关键词"瑜伽"，按互动数据排序，收集高质量内容
时间范围：3个月内
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from supabase import create_client, Client

class YogaXhsCrawler:
    """
    小红书瑜伽主题爬虫
    
    功能:
    1. 搜索关键词"瑜伽"
    2. 筛选3个月内的内容
    3. 按点赞/评论/收藏/分享排序
    4. 收集完整数据并存储到Supabase
    """
    
    def __init__(self):
        """初始化爬虫"""
        # Supabase配置
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # 搜索配置
        self.keyword = "瑜伽"
        self.months_range = 3  # 3个月内
        self.sort_types = ["liked_count", "comment_count", "collected_count", "share_count"]
        
        print(f"✅ 小红书瑜伽爬虫初始化成功")
        print(f"📌 搜索关键词: {self.keyword}")
        print(f"📅 时间范围: {self.months_range}个月内")
        print(f"📊 排序维度: {', '.join(self.sort_types)}")
    
    async def crawl(self):
        """执行爬取任务"""
        print("\n🚀 开始爬取小红书瑜伽内容...")
        
        all_notes = []
        
        try:
            # 根据不同维度获取热门内容
            for sort_type in self.sort_types:
                print(f"\n🔍 按 {sort_type} 排序搜索...")
                notes = await self._search_notes_by_sort(sort_type)
                all_notes.extend(notes)
            
            # 去重
            unique_notes = self._deduplicate_notes(all_notes)
            print(f"\n✅ 去重后共 {len(unique_notes)} 条笔记")
            
            # 获取详细信息和评论
            detailed_notes = await self._fetch_note_details(unique_notes)
            
            # 存储到数据库
            await self._save_to_database(detailed_notes)
            
            print(f"\n🎉 爬取完成！共采集 {len(detailed_notes)} 条高质量瑜伽内容")
            
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            raise
    
    async def _search_notes_by_sort(self, sort_type: str) -> List[Dict[str, Any]]:
        """
        按指定维度搜索笔记
        
        TODO: 实际实现需要使用MediaCrawler或小红书API
        这里提供数据结构示例
        """
        # 生成示例数据（实际使用时替换为真实API调用）
        sample_notes = []
        timestamp = datetime.now()
        
        for i in range(5):  # 每个排序类型获取5条
            note = {
                'note_id': f'yoga_{sort_type}_{i}_{int(timestamp.timestamp())}',
                'note_url': f'https://www.xiaohongshu.com/explore/yoga_{i}',
                'title': f'瑜伽{["入门", "进阶", "塑形", "冥想", "拉伸"][i]}教程',
                'desc': f'这是一篇关于瑜伽的优质笔记，详细介绍了瑜伽{["基础动作", "进阶技巧", "塑形方法", "冥想技巧", "拉伸动作"][i]}，非常适合初学者和进阶者。',
                'nickname': f'瑜伽教练{i+1}',
                'time': (timestamp - timedelta(days=i*15)).isoformat(),
                'type': 'video' if i % 2 == 0 else 'image',
                'liked_count': 5000 + i * 1000 if sort_type == 'liked_count' else 1000 + i * 100,
                'comment_count': 500 + i * 100 if sort_type == 'comment_count' else 100 + i * 10,
                'collected_count': 800 + i * 150 if sort_type == 'collected_count' else 200 + i * 20,
                'share_count': 200 + i * 50 if sort_type == 'share_count' else 50 + i * 5,
                'tag_list': ['瑜伽', '健身', '塑形', '减脂', '健康生活'],
            }
            sample_notes.append(note)
        
        return sample_notes
    
    def _deduplicate_notes(self, notes: List[Dict]) -> List[Dict]:
        """去重笔记"""
        seen_ids = set()
        unique_notes = []
        
        for note in notes:
            note_id = note.get('note_id')
            if note_id and note_id not in seen_ids:
                seen_ids.add(note_id)
                unique_notes.append(note)
        
        return unique_notes
    
    async def _fetch_note_details(self, notes: List[Dict]) -> List[Dict]:
        """获取笔记详细信息和评论"""
        print(f"\n📥 开始获取 {len(notes)} 条笔记的详细信息和评论...")
        
        detailed_notes = []
        
        for idx, note in enumerate(notes, 1):
            try:
                # 获取评论（示例数据）
                comments = self._fetch_comments(note['note_id'])
                note['comments'] = comments
                
                detailed_notes.append(note)
                print(f"  [{idx}/{len(notes)}] ✓ 已获取: {note['title']}")
                
            except Exception as e:
                print(f"  [{idx}/{len(notes)}] ✗ 获取失败: {str(e)}")
        
        return detailed_notes
    
    def _fetch_comments(self, note_id: str) -> List[Dict]:
        """获取笔记评论（示例）"""
        comments = []
        for i in range(3):  # 每条笔记获取3条评论示例
            comment = {
                'content': f'这个瑜伽教程太棒了！第{i+1}个动作特别有效。',
                'user_name': f'用户{i+1}',
                'created_at': datetime.now().isoformat(),
                'liked_count': 10 + i * 5
            }
            comments.append(comment)
        return comments
    
    async def _save_to_database(self, notes: List[Dict]):
        """保存到Supabase数据库"""
        print(f"\n💾 开始存储数据到 Supabase...")
        
        success_count = 0
        fail_count = 0
        
        for idx, note in enumerate(notes, 1):
            try:
                # 准备content_raw表数据
                content_data = {
                    'platform': 'xiaohongshu',
                    'content_id': note['note_id'],
                    'author_name': note['nickname'],
                    'title': note['title'],
                    'text': note['desc'],
                    'hashtags': json.dumps(note.get('tag_list', [])),
                    'like_count': note['liked_count'],
                    'comment_count': note['comment_count'],
                    'collect_count': note['collected_count'],
                    'share_count': note['share_count'],
                    'publish_time': note['time'],
                    'media_urls': json.dumps([note.get('note_url', '')])
                }
                
                # 插入到content_raw表
                result = self.supabase.table('content_raw').insert(content_data).execute()
                
                # 存储评论数据（如果有comments表）
                # for comment in note.get('comments', []):
                #     comment_data = {
                #         'content_id': note['note_id'],
                #         'content': comment['content'],
                #         ...
                #     }
                #     self.supabase.table('comments').insert(comment_data).execute()
                
                print(f"  [{idx}/{len(notes)}] ✓ 已存储: {note['title']}")
                success_count += 1
                
            except Exception as e:
                print(f"  [{idx}/{len(notes)}] ✗ 存储失败: {str(e)}")
                fail_count += 1
        
        print(f"\n💾 数据存储完成 - 成功: {success_count}, 失败: {fail_count}")


async def main():
    """主函数"""
    print("="*70)
    print("  小红书瑜伽主题内容爬虫")
    print("  搜索关键词: 瑜伽 | 时间: 3个月内 | 排序: 互动数据")
    print("="*70)
    
    try:
        crawler = YogaXhsCrawler()
        await crawler.crawl()
    except Exception as e:
        print(f"\n❌ 程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
