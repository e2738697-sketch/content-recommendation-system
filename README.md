# 内容推荐系统 (Content Recommendation System)

基于 GitHub Actions + Supabase 的自动化内容推荐工作流系统，用于采集、分析小红书/抖音内容，并通过虚拟人群画像生成推荐结果，最终同步至飞书多维表格。

## 系统架构

### 核心组件

1. **GitHub Actions** - 自动化工作流调度
2. **Supabase** - 数据存储和管理
3. **飞书多维表格** - 数据资产库展示
4. **Python脚本** - 数据采集、处理、分析

### 数据库表结构 (Supabase)

- `content_raw` - 原始内容数据
- `content_profile` - 内容画像标签
- `user_personas` - 虚拟用户画像
- `interactions` - 用户行为模拟记录
- `recommendations` - 推荐结果

## 工作流说明

### 1. 内容采集与清洗 (.github/workflows/crawler.yml)

- **触发时间**: 每12小时运行一次
- **功能**: 采集小红书/抖音内容，清洗字段，统一结构
- **脚本**: `scripts/crawler.py`

### 2. 内容画像构建 (.github/workflows/tagging.yml)

- **触发时间**: 每6小时运行一次
- **功能**: 对内容打标签（品类、价格带、场景、风格、情绪等）
- **脚本**: `scripts/tag_content.py`

### 3. 用户行为模拟 (.github/workflows/simulation.yml)

- **触发时间**: 每天运行一次
- **功能**: 
  - 设计5-10个标准信息流人群画像
  - 配置兴趣权重、价格敏感度、互动倾向
  - 模拟虚拟人群的点击/停留/交互行为
  - 生成推荐结果
- **脚本**: `scripts/simulate_users.py`, `scripts/generate_recommendations.py`

### 4. 飞书同步 (.github/workflows/feishu_sync.yml)

- **触发时间**: 每12小时运行一次
- **功能**: 将推荐结果同步到飞书多维表格
- **脚本**: `scripts/sync_to_feishu.py`

## 配置说明

### GitHub Secrets

需要在 GitHub 仓库的 Settings > Secrets 中配置以下密钥：

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key  # 用于内容标签生成
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
FEISHU_BASE_ID=your_feishu_base_id
FEISHU_TABLE_ID=your_feishu_table_id
```

### Supabase 项目

项目ID: `qxtsitaebqmiphnwmvky`

运行 SQL Editor 中的建表语句创建所需表结构。

### 飞书应用

在飞书开发者后台创建应用，获取 App ID 和 App Secret，并授予多维表格读写权限。

## 使用方式

### 手动触发工作流

1. 进入 GitHub Actions 页面
2. 选择需要运行的工作流
3. 点击 "Run workflow" 按钮

### 查看运行日志

在 Actions 页面可以查看每次运行的详细日志。

### 查看数据

- Supabase Dashboard: 查看原始数据和中间结果
- 飞书多维表格: 查看最终推荐结果

## 技术栈

- Python 3.11
- Supabase (PostgreSQL)
- GitHub Actions
- 飞书开放平台 API
- OpenAI API (可选，用于智能标签生成)

## 项目结构

```
.
├── .github/
│   └── workflows/
│       ├── crawler.yml           # 内容采集工作流
│       ├── tagging.yml           # 内容标签工作流
│       ├── simulation.yml        # 用户模拟工作流
│       └── feishu_sync.yml       # 飞书同步工作流
├── scripts/
│   ├── crawler.py                # 内容采集脚本
│   ├── tag_content.py            # 内容标签脚本
│   ├── simulate_users.py         # 用户模拟脚本
│   ├── generate_recommendations.py  # 推荐生成脚本
│   └── sync_to_feishu.py         # 飞书同步脚本
├── README.md
└── requirements.txt              # Python依赖
```

## 扩展说明

本系统提供了完整的自动化工作流框架，各脚本文件中包含了基础结构，可根据具体需求扩展：

1. **爬虫实现**: 在 `crawler.py` 中使用 Playwright 或其他工具实现具体的爬虫逻辑
2. **标签策略**: 在 `tag_content.py` 中定义内容标签的分类和提取规则
3. **用户画像**: 在 `simulate_users.py` 中设计符合业务场景的虚拟用户画像
4. **推荐算法**: 在 `generate_recommendations.py` 中实现推荐算法逻辑

## License

MIT
