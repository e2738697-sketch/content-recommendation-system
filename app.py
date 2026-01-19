#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容推荐系统后端API
Provides RESTful API endpoints for:
- Content data management
- AI tagging and annotation
- User persona management
- Feishu integration
- Score calculation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import json
from datetime import datetime
import logging

# Import custom modules
try:
    from src.db.supabase_client import SupabaseClient
    from src.ai.tagging_engine import TaggingEngine
    from src.integration.feishu_api import FeishuAPI
    from src.crawler.content_crawler import ContentCrawler
except ImportError as e:
    logging.warning(f"Some modules not fully initialized: {e}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Content Recommendation System API",
    description="API for content analysis, tagging, and recommendation",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Data Models ====================

class ContentItem(BaseModel):
    """原始内容模型"""
    platform: str  # xiaohongshu, douyin, etc.
    title: str
    description: Optional[str] = None
    author_id: str
    author_name: str
    like_count: int = 0
    comment_count: int = 0
    collect_count: int = 0
    share_count: int = 0
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    publish_time: Optional[str] = None

class TaggingRequest(BaseModel):
    """标签请求模型"""
    content_id: str
    title: str
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None

class PersonaProfile(BaseModel):
    """人群画像模型"""
    name: str
    demographics: Dict[str, Any]
    price_sensitivity: float
    interaction_pref: str
    interests: Dict[str, float]

class CrawlerConfig(BaseModel):
    """爬虫配置模型"""
    platform: str
    keywords: List[str]
    count: int = 50
    max_pages: int = 1

# ==================== API Endpoints ====================

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/content/upload")
async def upload_content(content: ContentItem):
    """上传内容到数据库"""
    try:
        # Initialize Supabase client
        db = SupabaseClient()
        
        # Prepare data
        data = {
            "platform": content.platform,
            "title": content.title,
            "description": content.description,
            "author_id": content.author_id,
            "author_name": content.author_name,
            "like_count": content.like_count,
            "comment_count": content.comment_count,
            "collect_count": content.collect_count,
            "share_count": content.share_count,
            "media_urls": json.dumps(content.media_urls) if content.media_urls else None,
            "hashtags": json.dumps(content.hashtags) if content.hashtags else None,
            "publish_time": content.publish_time,
            "fetch_time": datetime.now().isoformat()
        }
        
        # Insert to Supabase
        result = db.insert("content_raw", data)
        return {"status": "success", "content_id": result.get("id")}
    except Exception as e:
        logger.error(f"Error uploading content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tagging/auto-tag")
async def auto_tag_content(request: TaggingRequest):
    """自动为内容打标签"""
    try:
        tagging_engine = TaggingEngine()
        tags = tagging_engine.tag(
            title=request.title,
            description=request.description,
            hashtags=request.hashtags
        )
        
        # Save tags to database
        db = SupabaseClient()
        db.update("content_clean", {"tags": json.dumps(tags)}, f"content_id={request.content_id}")
        
        return {"status": "success", "tags": tags}
    except Exception as e:
        logger.error(f"Error tagging content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/content/list")
async def list_content(platform: Optional[str] = None, limit: int = 50, offset: int = 0):
    """获取内容列表"""
    try:
        db = SupabaseClient()
        
        query = db.client.table("content_raw").select("*")
        if platform:
            query = query.eq("platform", platform)
        
        result = query.limit(limit).offset(offset).execute()
        return {"status": "success", "data": result.data, "count": len(result.data)}
    except Exception as e:
        logger.error(f"Error listing content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/persona/create")
async def create_persona(persona: PersonaProfile):
    """创建人群画像"""
    try:
        db = SupabaseClient()
        
        data = {
            "name": persona.name,
            "demographics": json.dumps(persona.demographics),
            "price_sensitivity": persona.price_sensitivity,
            "interaction_pref": persona.interaction_pref,
            "interests": json.dumps(persona.interests),
            "created_at": datetime.now().isoformat()
        }
        
        result = db.insert("persona_profile", data)
        return {"status": "success", "persona_id": result.get("id")}
    except Exception as e:
        logger.error(f"Error creating persona: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crawler/start")
async def start_crawler(config: CrawlerConfig, background_tasks: BackgroundTasks):
    """启动内容爬虫"""
    try:
        crawler = ContentCrawler()
        
        # Run crawler in background
        background_tasks.add_task(
            crawler.crawl,
            platform=config.platform,
            keywords=config.keywords,
            count=config.count,
            max_pages=config.max_pages
        )
        
        return {"status": "started", "message": "Crawler started in background"}
    except Exception as e:
        logger.error(f"Error starting crawler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feishu/sync")
async def sync_to_feishu(background_tasks: BackgroundTasks):
    """同步数据到飞书"""
    try:
        feishu = FeishuAPI()
        background_tasks.add_task(feishu.sync_all_data)
        
        return {"status": "syncing", "message": "Feishu sync started"}
    except Exception as e:
        logger.error(f"Error syncing to Feishu: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics():
    """获取系统统计信息"""
    try:
        db = SupabaseClient()
        
        # Count contents
        contents = db.client.table("content_raw").select("count", count="exact").execute()
        tagged = db.client.table("content_clean").select("count", count="exact").execute()
        personas = db.client.table("persona_profile").select("count", count="exact").execute()
        
        return {
            "total_contents": contents.count,
            "tagged_contents": tagged.count,
            "total_personas": personas.count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
