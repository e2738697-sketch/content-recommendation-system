#!/usr/bin/env python3
"""
Generate recommendations based on user interactions
"""
import os
from supabase import create_client, Client
from collections import defaultdict

# Initialize Supabase
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(url, key)

def calculate_recommendation_score(persona, content, interactions):
    """
    Calculate recommendation score based on:
    - Persona interests
    - Past interactions
    - Content attributes
    """
    score = 0.0
    
    # Base score from category match
    category = content.get('category', '')
    interest_weight = persona.get('interest_weights', {}).get(category, 0)
    score += interest_weight * 10
    
    # Boost from past interactions
    content_id = content.get('content_id')
    similar_interactions = [i for i in interactions if i['content_id'] == content_id]
    score += len(similar_interactions) * 2
    
    # Adjust for price sensitivity
    price_range = content.get('price_range', '')
    if price_range in persona.get('preferred_price_ranges', []):
        score += 5
    
    return min(score, 100)  # Cap at 100

def generate_recommendations_for_persona(persona):
    """
    Generate recommendations for a single persona
    """
    persona_id = persona['id']
    persona_name = persona['name']
    
    # Get all interactions for this persona
    interactions_response = supabase.table('interactions').select('*').eq('persona_id', persona_id).execute()
    interactions = interactions_response.data
    
    # Get all content profiles
    content_response = supabase.table('content_profile').select('*').execute()
    content_profiles = content_response.data
    
    if not content_profiles:
        print(f"No content available for persona {persona_name}")
        return
    
    recommendations = []
    
    for content in content_profiles:
        score = calculate_recommendation_score(persona, content, interactions)
        
        if score > 0:
            recommendation = {
                'persona_id': persona_id,
                'persona_name': persona_name,
                'content_id': content['content_id'],
                'score': score,
                'category': content.get('category'),
                'reason': f"基于{persona_name}的兴趣倾向和历史行为"
            }
            recommendations.append(recommendation)
    
    # Sort by score and take top 20
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    top_recommendations = recommendations[:20]
    
    # Save to database
    for rec in top_recommendations:
        try:
            supabase.table('recommendations').insert(rec).execute()
        except Exception as e:
            print(f"Error saving recommendation: {e}")
    
    print(f"Generated {len(top_recommendations)} recommendations for {persona_name}")

def generate_all_recommendations():
    """
    Generate recommendations for all personas
    """
    # Get all personas
    personas_response = supabase.table('user_personas').select('*').execute()
    personas = personas_response.data
    
    if not personas:
        print("No personas found. Please run simulate_users.py first.")
        return
    
    print(f"\nGenerating recommendations for {len(personas)} personas...\n")
    
    for persona in personas:
        generate_recommendations_for_persona(persona)
    
    print("\nRecommendation generation completed!")

if __name__ == '__main__':
    generate_all_recommendations()
