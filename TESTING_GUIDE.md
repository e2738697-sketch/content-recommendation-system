# 完整测试指南 - 内容推荐系统

本指南将帮助您快速配置并测试整个系统。预计需要15-20分钟。

---

## 📋 第一步：环境准备

### 1.1 克隆项目
```bash
git clone https://github.com/e2738697-sketch/content-recommendation-system.git
cd content-recommendation-system
```

### 1.2 创建Python虚拟环境
```bash
python3.11 -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 1.3 安装依赖
```bash
pip install -r requirements.txt
```

---

## 🔐 第二步：配置凭证

### 2.1 复制环境变量文件
```bash
cp .env.example .env
```

### 2.2 编辑 `.env` 文件，填入以下信息：

#### **Supabase 配置**
- 访问 https://supabase.com
- 创建一个新项目
- 从项目设置中获取以下信息：

```env
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

#### **Feishu（飞书）配置**（可选，演示用）
```env
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
FEISHU_BASE_ID=your_feishu_base_id
FEISHU_TABLE_ID=your_feishu_table_id
```

#### **OpenAI 配置**（用于AI标注）
```env
OPENAI_API_KEY=your_openai_api_key
```

---

## 💾 第三步：数据库初始化

### 3.1 在 Supabase 中创建必要的表

登录 Supabase Dashboard → SQL Editor → 运行以下SQL：

```sql
-- 关键词表
CREATE TABLE IF NOT EXISTS keywords (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  keyword VARCHAR(255) NOT NULL,
  platform VARCHAR(50) NOT NULL,  -- 'xiaohongshu' or 'douyin'
  interval_hours INT DEFAULT 12,
  last_crawl_time TIMESTAMP,
  next_crawl_time TIMESTAMP DEFAULT NOW(),
  last_crawl_count INT DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 原始内容表
CREATE TABLE IF NOT EXISTS content_raw (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  platform VARCHAR(50),
  title TEXT,
  description TEXT,
  author_id VARCHAR(255),
  author_name VARCHAR(255),
  like_count INT,
  comment_count INT,
  collect_count INT,
  publish_time TIMESTAMP,
  fetch_time TIMESTAMP DEFAULT NOW()
);

-- 创建索引以提高查询性能
CREATE INDEX idx_keywords_active ON keywords(is_active);
CREATE INDEX idx_keywords_next_crawl ON keywords(next_crawl_time);
CREATE INDEX idx_content_platform ON content_raw(platform);
```

---

## 🚀 第四步：启动API服务

### 4.1 启动 FastAPI 服务器
```bash
python app.py
```

或使用 uvicorn：
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**预期输出：**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 4.2 验证 API 健康状态
```bash
curl http://localhost:8000/health
```

**预期响应：**
```json
{"status": "ok", "timestamp": "2024-01-19T10:00:00Z"}
```

---

## 🧪 第五步：测试关键词爬取功能

### 5.1 打开测试前端界面

在浏览器中打开：
```
http://localhost:8000/keyword_crawler_demo.html
```

或直接打开文件：
```bash
open keyword_crawler_demo.html
```

### 5.2 添加测试关键词

1. **输入关键词：** 输入 "美妆" 或 "护肤"
2. **选择平台：** 选择 "小红书"
3. **设置间隔：** 选择 "6 小时"
4. **点击添加：** 点击 "➕ 添加关键词" 按钮

**预期效果：**
- ✅ 显示成功提示："✨ 成功添加关键词"
- 📄 关键词出现在实时监测面板
- 显示添加时间和状态信息

### 5.3 测试多个关键词

```
第1个关键词："美妆产品" (小红书, 12小时)
第2个关键词："护肤" (抖音, 24小时)
第3个关键词："旅游" (小红书, 6小时)
```

---

## 📡 第六步：测试 API 端点

### 6.1 添加关键词（Python）
```python
import requests

response = requests.post('http://localhost:8000/api/keyword/add', json={
    'keyword': '美妆产品',
    'platform': 'xiaohongshu',
    'interval_hours': 12
})
print(response.json())
```

### 6.2 获取活跃关键词
```python
response = requests.get('http://localhost:8000/api/keywords/active')
print(response.json())
```

### 6.3 执行爬取任务
```python
response = requests.post('http://localhost:8000/api/keyword/crawl', json={
    'keyword_id': 'your-keyword-id-here'
})
print(response.json())
```

---

## 📊 第七步：验证数据库存储

### 7.1 检查Supabase中的数据

在 Supabase Dashboard 中：

1. 点击 "SQL Editor"
2. 运行查询检查关键词：
```sql
SELECT * FROM keywords WHERE is_active = true ORDER BY created_at DESC;
```

3. 检查爬取的内容：
```sql
SELECT COUNT(*) as total_content FROM content_raw;
```

---

## 🔄 第八步：测试定时爬取

### 8.1 模拟定时任务（开发环境）
```python
from src.crawler.keyword_manager import KeywordManager
from datetime import datetime

manager = KeywordManager()

# 获取需要爬取的关键词
due_keywords = manager.get_due_keywords()
print(f"找到 {len(due_keywords)} 个需要爬取的关键词")

# 执行爬取
for keyword in due_keywords:
    print(f"开始爬取：{keyword['keyword']}")
    result = manager.execute_crawl_for_keyword(keyword['id'])
    print(f"结果：{result}")
```

### 8.2 设置生产环境定时任务

在 GitHub Actions 中自动运行爬取脚本：
- 查看 `.github/workflows/crawler.yml`
- 脚本每12小时自动执行一次

---

## ⚠️ 常见问题排查

### 问题1："ModuleNotFoundError: No module named 'src'"
**解决方案：**
```bash
# 确保在项目根目录
cd /path/to/content-recommendation-system
pip install -e .
```

### 问题2："SUPABASE_URL not found in environment"
**解决方案：**
```bash
# 检查 .env 文件是否存在和正确配置
cat .env

# 或手动设置环境变量
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
```

### 问题3："Connection refused on localhost:8000"
**解决方案：**
```bash
# 检查端口是否被占用
lsof -i :8000

# 使用不同的端口启动
uvicorn app:app --port 8001
```

### 问题4："SyntaxError or Import Error"
**解决方案：**
```bash
# 重新安装依赖
pip install --upgrade -r requirements.txt
```

---

## ✅ 测试完成检查清单

- [ ] 环境变量正确配置
- [ ] Supabase数据库已创建表
- [ ] API服务正常运行
- [ ] 关键词爬取演示界面可访问
- [ ] 可以添加新的关键词
- [ ] Supabase中能看到关键词记录
- [ ] API端点正常响应
- [ ] 爬取任务能正常执行
- [ ] 内容正确存储到数据库
- [ ] 定时任务按计划运行

---

## 📞 支持和反馈

如遇到任何问题，请检查：
1. 环境变量配置是否正确
2. 依赖是否完全安装
3. 数据库表是否正确创建
4. 网络连接是否正常

祝测试顺利！🎉
