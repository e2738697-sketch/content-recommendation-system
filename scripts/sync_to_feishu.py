#!/usr/bin/env python3
"""
Sync recommendations to Feishu Bitable (Multi-dimensional Table)
"""
import os
import requests
from supabase import create_client, Client

# Environment variables
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET')
FEISHU_BASE_ID = os.environ.get('FEISHU_BASE_ID')
FEISHU_TABLE_ID = os.environ.get('FEISHU_TABLE_ID')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_tenant_access_token():
    """Get Feishu tenant access token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json().get('tenant_access_token')

def get_recommendations():
    """Get recommendations from Supabase"""
    response = supabase.table('recommendations').select('*').order('score', desc=True).limit(100).execute()
    return response.data

def sync_record_to_feishu(token, record):
    """Sync a single record to Feishu Bitable"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE_ID}/tables/{FEISHU_TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # Map Supabase fields to Feishu fields
    fields = {
        "content_id": record.get('content_id'),
        "persona_name": record.get('persona_name'),
        "score": record.get('score'),
        "category": record.get('category'),
        "reason": record.get('reason'),
        "created_at": record.get('created_at')
    }
    
    data = {"fields": fields}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print(f"Synced record {record['id']} successfully")
        else:
            print(f"Error syncing record {record['id']}: {response.text}")
    except Exception as e:
        print(f"Exception syncing record {record['id']}: {e}")

def sync_all():
    """Sync all recommendations to Feishu"""
    token = get_tenant_access_token()
    if not token:
        print("Failed to get Feishu access token")
        return
    
    recommendations = get_recommendations()
    print(f"Found {len(recommendations)} recommendations to sync")
    
    for record in recommendations:
        sync_record_to_feishu(token, record)
    
    print("Sync completed!")

if __name__ == '__main__':
    sync_all()
