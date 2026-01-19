# Content Recommendation System - Testing Setup Guide

## 鲜明概述 | Quick Overview

This guide explains how to set up and test the Content Recommendation System with automatic keyword-based content crawling and scheduled delivery.

## 前置要求 | Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git
- Text editor or IDE

## 1. 环境配置 | Environment Configuration

### 1.1 复制环境变量 | Copy Environment Variables

```bash
cp .env.example .env
```

### 1.2 修改 .env 文件 | Edit .env File

The `.env` file has been configured for local testing with the following key settings:

```
# FastAPI Configuration
FAST_API_HOST=0.0.0.0
FAST_API_PORT=8000
DEBUG=True
ENVIRONMENT=development

# Database (using SQLite for testing)
DATABASE_URL=sqlite:///./test.db
```

**Note:** For production use with Supabase, update the database configuration accordingly.

## 2. 安装依赖 | Install Dependencies

### 2.1 创建虚拟环境 | Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.2 安装所需包 | Install Required Packages

```bash
pip install -r requirements.txt
```

## 3. 启动后端服务 | Start Backend Service

### 3.1 运行 FastAPI 服务器 | Run FastAPI Server

```bash
python app.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3.2 验证服务健康状况 | Verify Service Health

Open your browser and visit:
- Health check: `http://localhost:8000/health`
- API documentation: `http://localhost:8000/docs`

## 4. 自动爬虫配置 | Automatic Crawler Configuration

### 4.1 使用测试配置 | Using Test Configuration

The system provides a test crawler configuration file: `test_crawler_config.json`

This configuration includes:

#### **小红书 (Xiaohongshu) 爬虫配置**

Keywords: Python编程, Web开发, 数据分析, 机器学习, 前端框架

Schedule: Every 6 hours automatically

#### **抖音 (Douyin) 爬虫配置**

Keywords: 编程教程, 开发工具, 技术分享, 代码片段, 项目分享

Schedule: Every 12 hours automatically

### 4.2 启动爬虫 | Start Crawler

#### Option A: 使用 API 端点 | Using API Endpoint

```bash
curl -X POST "http://localhost:8000/api/crawler/start" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "xiaohongshu",
    "keywords": ["Python编程", "Web开发"],
    "count": 50,
    "max_pages": 2
  }'
```

#### Option B: 使用 Swagger UI | Using Swagger UI

1. Open `http://localhost:8000/docs`
2. Find the "POST /api/crawler/start" endpoint
3. Click "Try it out"
4. Enter the configuration and click "Execute"

## 5. 测试数据流 | Test Data Flow

### 5.1 查看爬取的内容 | View Crawled Content

```bash
curl "http://localhost:8000/api/content/list?platform=xiaohongshu&limit=10"
```

### 5.2 获取系统统计 | Get System Statistics

```bash
curl "http://localhost:8000/api/stats"
```

### 5.3 自动标签生成 | Auto-Tagging

```bash
curl -X POST "http://localhost:8000/api/tagging/auto-tag" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "test_001",
    "title": "Python Web Development Tutorial",
    "description": "Learn Django and FastAPI",
    "hashtags": ["python", "web", "tutorial"]
  }'
```

## 6. 访问测试界面 | Access Testing UI

### 6.1 打开测试仪表板 | Open Testing Dashboard

Access the web interface at:
```
http://localhost:8080/content_analysis.html
```

### 6.2 主要功能 | Main Features

- **内容输入面板 | Content Input Panel**: Enter keywords for manual crawling
- **爬虫配置 | Crawler Configuration**: Set up scheduling and sources
- **内容预览 | Content Preview**: View fetched content
- **标签管理 | Tag Management**: Manage content tags
- **统计仪表板 | Statistics Dashboard**: View system metrics

## 7. 计划任务配置 | Scheduled Task Configuration

### 7.1 启用定时爬虫 | Enable Scheduled Crawling

The test configuration includes automatic scheduling:

```json
{
  "schedule": {
    "enabled": true,
    "interval_hours": 6,
    "description": "每6小时自动爬取一次"
  }
}
```

### 7.2 自定义计划 | Customize Schedule

Edit `test_crawler_config.json` to change:
- `interval_hours`: Schedule interval in hours
- `keywords`: Content keywords to crawl
- `platform`: Target platform (xiaohongshu, douyin, etc.)

## 8. 故障排查 | Troubleshooting

### 问题1：连接被拒绝 | Connection Refused

**症状：** `ERR_CONNECTION_REFUSED`

**解决方案：**
1. Ensure backend is running: `python app.py`
2. Check if port 8000 is available
3. Verify `.env` configuration

### 问题2：数据库错误 | Database Errors

**症状：** Database connection errors

**解决方案：**
1. Delete old `test.db` file: `rm test.db`
2. Restart the backend
3. Database will be created automatically

### 问题3：爬虫未启动 | Crawler Not Starting

**症状：** Crawler returns `status: started` but no content appears

**解决方案：**
1. Check crawler logs in the backend console
2. Verify API credentials if using real platforms
3. Try with test keywords first

## 9. API 端点参考 | API Endpoints Reference

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/api/content/upload` | 上传内容 |
| GET | `/api/content/list` | 获取内容列表 |
| POST | `/api/tagging/auto-tag` | 自动标签 |
| POST | `/api/persona/create` | 创建人群画像 |
| POST | `/api/crawler/start` | 启动爬虫 |
| POST | `/api/feishu/sync` | 同步到飞书 |
| GET | `/api/stats` | 获取统计信息 |

## 10. 下一步 | Next Steps

1. ✅ Environment configuration complete
2. ✅ Backend service running
3. ✅ Test crawler configuration ready
4. 🔄 Run initial crawl with keywords
5. 🔄 Monitor scheduled tasks
6. 🔄 Integrate with Feishu for notifications

## 支持 | Support

For issues or questions:
1. Check `TESTING_GUIDE.md` for detailed testing procedures
2. Review `API.md` for API documentation
3. Check backend logs for errors
4. Refer to `QUICK_START.md` for quick setup
