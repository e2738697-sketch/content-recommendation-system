#!/usr/bin/env python3
"""
Content tagging and profiling script
Tags content with: category, price range, scenario, style, emotion, creator level, etc.
"""
import os
import jieba
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(url, key)

# Tag definitions
CATEGORIES = ['美妆', '服饰', '食品', '数码', '家居', '母婴', '运动', '图书']
PRICE_RANGES = ['<50', '50-100', '100-300', '300-500', '>500']
SCENARIOS = ['通勤', '居家', '健身', '旅行', '聚会', '约会']
STYLES = ['种草', '测评', '晒单', '教程', '开箱']
EMOTIONS = ['兴奋', '满意', '中立', '失望', '愤怒']

def extract_keywords(text):
    """Extract keywords from text using jieba"""
    words = jieba.cut(text)
    return list(words)

def tag_category(content):
    """Tag content category"""
    # TODO: Implement category tagging logic
    # Can use keyword matching or ML model
    return CATEGORIES[0]  # Placeholder

def tag_price_range(content):
    """Extract and tag price range"""
    # TODO: Extract price from content
    return PRICE_RANGES[1]  # Placeholder

def tag_scenario(content):
    """Tag usage scenario"""
    # TODO: Implement scenario detection
    return [SCENARIOS[0], SCENARIOS[1]]  # Placeholder

def tag_style(content):
    """Tag content style"""
    # TODO: Detect content style
    return STYLES[0]  # Placeholder

def tag_emotion(content):
    """Analyze emotion"""
    # TODO: Sentiment analysis
    return EMOTIONS[1]  # Placeholder

def process_content(raw_content):
    """Process and tag a single content item"""
    text = str(raw_content.get('raw_data', {}))
    
    profile = {
        'content_id': raw_content['id'],
        'category': tag_category(text),
        'price_range': tag_price_range(text),
        'scenarios': tag_scenario(text),
        'style': tag_style(text),
        'sentiment_score': tag_emotion(text),
        'keywords': extract_keywords(text)[:10],  # Top 10 keywords
        'tagged_at': datetime.utcnow().isoformat()
    }
    
    return profile

def tag_all_untagged():
    """Tag all content that hasn't been tagged yet"""
    # Get untagged content
    response = supabase.table('content_raw').select('*').execute()
    raw_contents = response.data
    
    # Get already tagged content IDs
    tagged_response = supabase.table('content_profile').select('content_id').execute()
    tagged_ids = {item['content_id'] for item in tagged_response.data}
    
    untagged = [c for c in raw_contents if c['id'] not in tagged_ids]
    
    print(f"Found {len(untagged)} untagged content items")
    
    for content in untagged:
        try:
            profile = process_content(content)
            supabase.table('content_profile').insert(profile).execute()
            print(f"Tagged content {content['id']}")
        except Exception as e:
            print(f"Error tagging content {content['id']}: {e}")

if __name__ == '__main__':
    tag_all_untagged()
    print("Tagging completed!")
