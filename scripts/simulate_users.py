#!/usr/bin/env python3
"""
User behavior simulation script
Simulates virtual user personas browsing content and records interactions
"""
import os
import random
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(url, key)

# Define virtual user personas based on user requirements
PERSONAS = [
    {
        'name': '一线都市白领女',
        'description': '25-35岁，关注时尚美妆、通勤装扮、品质生活',
        'interest_weights': {
            '美妆': 0.4,
            '服饰': 0.3,
            '家居': 0.2,
            '食品': 0.1
        },
        'price_sensitivity': 0.3,  # 0-1, lower = less sensitive
        'preferred_price_ranges': ['100-300', '300-500'],
        'interaction_tendency': {
            'like_rate': 0.6,
            'save_rate': 0.4,
            'comment_rate': 0.2
        }
    },
    {
        'name': '美妆重度用户',
        'description': '20-30岁，精致女孩，主要关注美妆产品和教程',
        'interest_weights': {
            '美妆': 0.7,
            '服饰': 0.2,
            '数码': 0.1
        },
        'price_sensitivity': 0.5,
        'preferred_price_ranges': ['50-100', '100-300'],
        'interaction_tendency': {
            'like_rate': 0.8,
            'save_rate': 0.6,
            'comment_rate': 0.4
        }
    },
    {
        'name': '三线城市性价比男',
        'description': '25-40岁，关注数码、运动，价格敏感',
        'interest_weights': {
            '数码': 0.5,
            '运动': 0.3,
            '食品': 0.2
        },
        'price_sensitivity': 0.8,
        'preferred_price_ranges': ['<50', '50-100'],
        'interaction_tendency': {
            'like_rate': 0.3,
            'save_rate': 0.5,
            'comment_rate': 0.1
        }
    }
]

def initialize_personas():
    """Initialize user personas in database"""
    for persona in PERSONAS:
        try:
            supabase.table('user_personas').insert(persona).execute()
            print(f"Created persona: {persona['name']}")
        except Exception as e:
            print(f"Persona {persona['name']} may already exist: {e}")

def simulate_browse(persona_id, persona_data):
    """Simulate a persona browsing content"""
    # Get content profiles
    response = supabase.table('content_profile').select('*, content_raw(*)').limit(50).execute()
    content_profiles = response.data
    
    if not content_profiles:
        print("No content available to simulate")
        return
    
    for content in content_profiles:
        category = content.get('category', '')
        price_range = content.get('price_range', '')
        
        # Calculate interest score
        interest_score = persona_data['interest_weights'].get(category, 0)
        
        # Adjust for price sensitivity
        if price_range in persona_data['preferred_price_ranges']:
            interest_score += 0.2
        
        # Decide action based on interest score
        if random.random() < interest_score:
            # Simulate interaction
            actions = []
            
            if random.random() < persona_data['interaction_tendency']['like_rate']:
                actions.append('like')
            if random.random() < persona_data['interaction_tendency']['save_rate']:
                actions.append('save')
            if random.random() < persona_data['interaction_tendency']['comment_rate']:
                actions.append('comment')
            
            # Record interaction
            for action in actions:
                interaction = {
                    'persona_id': persona_id,
                    'content_id': content['content_id'],
                    'action': action,
                    'dwell_time': random.randint(5, 60)  # seconds
                }
                supabase.table('interactions').insert(interaction).execute()
            
            print(f"Persona {persona_data['name']} interacted with content {content['content_id']}: {actions}")

def run_simulation():
    """Run user behavior simulation"""
    # Initialize personas first
    initialize_personas()
    
    # Get all personas from database
    response = supabase.table('user_personas').select('*').execute()
    db_personas = response.data
    
    print(f"\nSimulating {len(db_personas)} personas browsing content...\n")
    
    for db_persona in db_personas:
        # Find matching persona definition
        persona_def = next((p for p in PERSONAS if p['name'] == db_persona['name']), None)
        if persona_def:
            print(f"\nSimulating: {db_persona['name']}")
            simulate_browse(db_persona['id'], persona_def)
    
    print("\nSimulation completed!")

if __name__ == '__main__':
    run_simulation()
