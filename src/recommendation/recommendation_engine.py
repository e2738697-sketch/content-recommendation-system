import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict, Any, Set
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Hybrid recommendation engine using collaborative and content-based filtering"""
    
    def __init__(self, min_score: float = 0.5):
        self.min_score = min_score
        self.user_profiles = {}
        self.content_vectors = {}
        self.user_interactions = defaultdict(list)
        self.scaler = MinMaxScaler()
    
    def build_content_vector(self, post: Dict[str, Any]) -> np.ndarray:
        """Build feature vector for a post"""
        features = []
        
        # Engagement features (normalized)
        likes = post.get('likes', 0)
        comments = post.get('comments', 0)
        shares = post.get('shares', 0)
        
        features.extend([likes, comments, shares])
        
        # Category features (one-hot encoded)
        category_map = {'beauty': 1, 'fashion': 2, 'health': 3, 'tech': 4, 'lifestyle': 5}
        category = post.get('category', 'lifestyle')
        category_vector = [1 if category_map.get(category) == i else 0 for i in range(1, 6)]
        features.extend(category_vector)
        
        # Sentiment features
        sentiment = post.get('sentiment', 0.5)
        features.append(sentiment)
        
        # Price band (if applicable)
        price_band = post.get('price_band', 2)  # 1=low, 2=mid, 3=high
        features.append(price_band)
        
        return np.array(features, dtype=np.float32)
    
    def record_interaction(self, user_id: str, post_id: str, interaction_type: str = 'view', score: float = 1.0):
        """Record user interaction with a post"""
        interaction_weights = {'view': 0.5, 'like': 1.0, 'comment': 1.5, 'share': 2.0}
        weight = interaction_weights.get(interaction_type, 0.5)
        
        self.user_interactions[user_id].append({
            'post_id': post_id,
            'type': interaction_type,
            'weight': weight * score
        })
    
    def get_user_profile(self, user_id: str, posts: List[Dict[str, Any]]) -> np.ndarray:
        """Generate user profile from interactions and preferences"""
        interactions = self.user_interactions.get(user_id, [])
        
        if not interactions:
            # Default profile if no interactions
            return np.ones(len(self.build_content_vector(posts[0] if posts else {}))) * 0.5
        
        profile_vector = np.zeros(len(self.build_content_vector(posts[0] if posts else {})))
        total_weight = 0
        
        for interaction in interactions:
            post_id = interaction['post_id']
            weight = interaction['weight']
            
            # Find post in list
            post = next((p for p in posts if p.get('post_id') == post_id), None)
            if post:
                content_vector = self.build_content_vector(post)
                profile_vector += content_vector * weight
                total_weight += weight
        
        if total_weight > 0:
            profile_vector /= total_weight
        
        self.user_profiles[user_id] = profile_vector
        return profile_vector
    
    def content_based_recommendation(self, user_id: str, posts: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Content-based recommendation using cosine similarity"""
        if user_id not in self.user_profiles:
            user_profile = self.get_user_profile(user_id, posts)
        else:
            user_profile = self.user_profiles[user_id]
        
        scores = []
        for post in posts:
            post_id = post.get('post_id')
            
            # Skip already seen posts
            if post_id in [i['post_id'] for i in self.user_interactions.get(user_id, [])]:
                continue
            
            content_vector = self.build_content_vector(post)
            similarity = cosine_similarity([user_profile], [content_vector])[0][0]
            
            scores.append({
                'post': post,
                'score': float(similarity),
                'method': 'content-based'
            })
        
        # Sort and return top-k
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:top_k]
    
    def collaborative_recommendation(self, user_id: str, posts: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Collaborative filtering recommendation"""
        scores = defaultdict(float)
        user_ids = set(self.user_interactions.keys())
        
        # Find similar users
        similar_users = []
        for other_user in user_ids:
            if other_user == user_id:
                continue
            
            other_interactions = set(i['post_id'] for i in self.user_interactions[other_user])
            user_interactions = set(i['post_id'] for i in self.user_interactions.get(user_id, []))
            
            # Jaccard similarity
            if len(other_interactions | user_interactions) > 0:
                similarity = len(other_interactions & user_interactions) / len(other_interactions | user_interactions)
                if similarity > 0.1:
                    similar_users.append((other_user, similarity))
        
        # Get recommendations from similar users
        results = []
        for other_user, similarity in similar_users:
            for interaction in self.user_interactions[other_user]:
                post_id = interaction['post_id']
                
                # Skip already seen
                if post_id in [i['post_id'] for i in self.user_interactions.get(user_id, [])]:
                    continue
                
                scores[post_id] += interaction['weight'] * similarity
        
        # Get post objects and create results
        results = []
        for post_id, score in scores.items():
            post = next((p for p in posts if p.get('post_id') == post_id), None)
            if post:
                results.append({
                    'post': post,
                    'score': float(score),
                    'method': 'collaborative'
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def hybrid_recommendation(self, user_id: str, posts: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """Hybrid recommendation combining content and collaborative filtering"""
        # Get recommendations from both methods
        content_recs = self.content_based_recommendation(user_id, posts, top_k=top_k)
        collab_recs = self.collaborative_recommendation(user_id, posts, top_k=top_k)
        
        # Combine and normalize scores
        all_recs = {}
        for rec in content_recs:
            post_id = rec['post']['post_id']
            all_recs[post_id] = {'post': rec['post'], 'score': rec['score'] * 0.6, 'methods': ['content-based']}
        
        for rec in collab_recs:
            post_id = rec['post']['post_id']
            if post_id in all_recs:
                all_recs[post_id]['score'] += rec['score'] * 0.4
                all_recs[post_id]['methods'].append('collaborative')
            else:
                all_recs[post_id] = {'post': rec['post'], 'score': rec['score'] * 0.4, 'methods': ['collaborative']}
        
        # Sort and return
        results = sorted(all_recs.values(), key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def personalize_feed(self, user_id: str, posts: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
        """Generate personalized feed for user"""
        recommendations = self.hybrid_recommendation(user_id, posts, top_k=limit)
        
        # Filter by minimum score
        recommendations = [r for r in recommendations if r['score'] >= self.min_score]
        
        return recommendations
