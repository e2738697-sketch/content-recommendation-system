# 内容推荐系统 - 架构文档

## 系统概述

该系统是一个完整的内容推荐平台，集成了内容采集、AI标注、用户画像构建、行为模拟和飞书数据同步等核心功能。

## 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                            │
│  - content_analysis.html (内容分析UI)                       │
│  - index.html (主页)                                        │
│  - login_interface.js (登录管理)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  - app.py (FastAPI主应用)                                   │
│    - /api/content/upload (上传内容)                         │
│    - /api/content/list (列表查询)                           │
│    - /api/tagging/auto-tag (自动标注)                       │
│    - /api/persona/create (创建人群)                         │
│    - /api/crawler/start (启动爬虫)                          │
│    - /api/feishu/sync (飞书同步)                            │
│    - /api/stats (统计信息)                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer                              │
│  ├── src/db/supabase_client.py (数据库抽象层)              │
│  ├── src/integration/feishu_api.py (飞书API集成)           │
│  ├── src/ai/tagging_engine.py (AI标注引擎)                │
│  ├── src/crawler/content_crawler.py (网络爬虫)            │
│  └── src/scoring/score_calculator.py (评分计算)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              External Services Integration                  │
│  ├── Supabase (PostgreSQL数据库)                            │
│  ├── Feishu (飞书多维表)                                   │
│  ├── GitHub Actions (自动化工作流)                         │
│  └── Small Red Book / Douyin (内容爬虫)                    │
└─────────────────────────────────────────────────────────────┘
```

## 数据流架构

### 第一环节：内容采集与清洗

**输入**: 小红书/抖音关键词  
**过程**:
1. 网络爬虫采集原始数据
2. 数据字段清洗和标准化
3. 存储到 `content_raw` 表

**输出**: 清洗后的内容数据

### 第二环节：内容画像构建

**输入**: 清洗后的内容  
**过程**:
1. AI模型自动标注（LLM）
2. 提取维度标签：
   - 品类(category)
   - 价格带(price_band)
   - 场景(scenario)
   - 风格(style)
   - 情绪分(sentiment_score)
3. 向量化存储

**输出**: 标注完成的内容记录

### 第三环节：用户人群画像设计

**输入**: 目标用户特征  
**表**:
- `persona_profile`: 人群基础信息
  - demographics（人口统计）
  - price_sensitivity（价格敏感度）
  - interaction_pref（互动偏好）
  - interests（兴趣权重）
- `persona_interest_weights`: 兴趣权重详情

**输出**: 完整的人群画像配置

### 第四环节：行为模拟与评分

**输入**: 人群画像 + 内容标签  
**计算维度**:
- match_score: 内容与人群的匹配度
- p_view: 浏览概率
- p_click: 点击概率
- p_like: 点赞概率
- p_collect: 收藏概率
- p_comment: 评论概率
- p_convert: 转化概率
- overall_score: 综合评分

**输出**: `persona_content_score` 表

### 第五环节：飞书数据同步

**流程**:
1. 从 Supabase 读取处理完的数据
2. 转换为飞书API格式
3. 批量写入飞书多维表
4. 支持实时查看和进一步分析

## 已实现模块

### 1. Backend API (app.py)

**核心功能**:
- FastAPI框架
- CORS中间件
- 8个RESTful端点
- 后台任务支持

**依赖**:
```
fastapi>=0.104
uvicorn>=0.24
pydantic>=2.0
requests>=2.31
```

### 2. 数据库客户端 (src/db/supabase_client.py)

**功能**:
- 数据库连接管理
- CRUD操作
- 批量操作
- 计数操作

**方法**:
- insert(): 单条插入
- select(): 查询数据
- update(): 更新数据
- delete(): 删除数据
- batch_insert(): 批量插入
- count(): 统计记录

### 3. 飞书API集成 (src/integration/feishu_api.py)

**功能**:
- 获取租户级访问令牌
- 写入数据到飞书多维表
- 同步所有数据

**方法**:
- get_tenant_access_token(): 获取token
- write_to_table(): 写入记录
- sync_all_data(): 全量同步

## 待实现模块

### 1. AI标注引擎 (src/ai/tagging_engine.py)

需要实现:
```python
class TaggingEngine:
    def tag(self, title, description, hashtags):
        # 使用LLM进行标注
        # 返回: {category, price_band, scenario, style, sentiment_score}
```

### 2. 内容爬虫 (src/crawler/content_crawler.py)

需要实现:
```python
class ContentCrawler:
    def crawl(self, platform, keywords, count, max_pages):
        # 爬取平台内容
        # 支持: xiaohongshu, douyin
```

### 3. 评分计算 (src/scoring/score_calculator.py)

需要实现:
```python
class ScoreCalculator:
    def calculate(self, persona, content):
        # 计算匹配度和各概率
```

### 4. GitHub Actions工作流

需要创建:
- `.github/workflows/crawler.yml` - 定期爬虫
- `.github/workflows/tagging.yml` - 自动标注
- `.github/workflows/scoring.yml` - 评分计算
- `.github/workflows/feishu_sync.yml` - 飞书同步

## 部署步骤

### 1. 环境变量配置

```bash
# .env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
FEISHU_APP_TOKEN=your_app_token
FEISHU_TABLE_ID=your_table_id
```

### 2. 依赖安装

```bash
pip install -r requirements.txt
```

### 3. 启动API服务

```bash
python app.py
# 或
uvicorn app:app --reload
```

## 数据库表设计

```sql
-- 原始内容表
CREATE TABLE content_raw (
    content_id UUID PRIMARY KEY,
    platform VARCHAR(50),
    title TEXT,
    description TEXT,
    author_id VARCHAR(255),
    author_name VARCHAR(255),
    like_count INT,
    comment_count INT,
    collect_count INT,
    share_count INT,
    media_urls JSONB,
    hashtags JSONB,
    publish_time TIMESTAMP,
    fetch_time TIMESTAMP
);

-- 清洗后的内容表
CREATE TABLE content_clean (
    content_id UUID PRIMARY KEY,
    category VARCHAR(50),
    price_band VARCHAR(50),
    scenario JSONB,
    style VARCHAR(50),
    sentiment_score FLOAT,
    tags JSONB,
    embedding VECTOR(1536)
);

-- 人群画像表
CREATE TABLE persona_profile (
    persona_id UUID PRIMARY KEY,
    name VARCHAR(255),
    demographics JSONB,
    price_sensitivity FLOAT,
    interaction_pref VARCHAR(50),
    interests JSONB,
    created_at TIMESTAMP
);

-- 评分矩阵表
CREATE TABLE persona_content_score (
    persona_id UUID,
    content_id UUID,
    match_score FLOAT,
    p_view FLOAT,
    p_click FLOAT,
    p_like FLOAT,
    p_collect FLOAT,
    p_comment FLOAT,
    p_convert FLOAT,
    overall_score FLOAT,
    PRIMARY KEY (persona_id, content_id)
);
```

## API文档

### 健康检查
```
GET /health
```

### 上传内容
```
POST /api/content/upload
Body: ContentItem
```

### 自动标注
```
POST /api/tagging/auto-tag
Body: TaggingRequest
```

### 创建人群
```
POST /api/persona/create
Body: PersonaProfile
```

### 启动爬虫
```
POST /api/crawler/start
Body: CrawlerConfig
```

### 飞书同步
```
POST /api/feishu/sync
```

### 获取统计
```
GET /api/stats
```

## 下一步

1. 完成AI标注引擎实现
2. 完成网络爬虫实现
3. 完成评分计算逻辑
4. 创建GitHub Actions工作流
5. 前端UI优化和集成
6. 端到端测试
