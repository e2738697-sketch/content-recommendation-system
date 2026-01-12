#!/usr/bin/env python3
"""
Content crawler for collecting data from Xiaohongshu and Douyin
"""
import os
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase client
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(url, key)

def crawl_xiaohongshu():
    """Crawl content from Xiaohongshu"""
    # TODO: Implement Xiaohongshu crawler
    # This would use Playwright or similar tool
    print("Crawling Xiaohongshu...")
    return []

def crawl_douyin():
    """Crawl content from Douyin"""
    # TODO: Implement Douyin crawler
    print("Crawling Douyin...")
    return []

def clean_and_save(raw_data, source):
    """Clean data and save to Supabase"""
    for item in raw_data:
        try:
            supabase.table('content_raw').insert({
                'source': source,
                'raw_data': item,
                'collected_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error saving {item}: {e}")

if __name__ == '__main__':
    xhs_data = crawl_xiaohongshu()
    clean_and_save(xhs_data, 'xiaohongshu')
    
    dy_data = crawl_douyin()
    clean_and_save(dy_data, 'douyin')
    
    print("Crawling completed!")
