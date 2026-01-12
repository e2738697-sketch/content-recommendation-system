# 配置指南

本文档详细说明如何配置和启动内容推荐系统。

## 前置条件

- GitHub账号
- Supabase账号
- 飞书开发者账号
- OpenAI API密钥（可选）

## 第一步：Supabase配置

### 1. 创建Supabase项目

访问 [Supabase](https://supabase.com)，创建新项目。

当前项目ID: `qxtsitaebqmiphnwmvky`

### 2. 创建数据表

在SQL Editor中执行以下SQL语句创建所需的数据表：

```sql
-- 原始内容表
CREATE TABLE content_raw (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    raw_data JSONB NOT NULL,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 内容画像表
CREATE TABLE content_profile (
    id BIGSERIAL PRIMARY KEY,
    content_id BIGINT REFERENCES content_raw(id),
    category TEXT,
    price_range TEXT,
    scenarios TEXT[],
    style TEXT,
    emotion TEXT,
    keywords TEXT[],
    tagged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 虚拟用户画像表
CREATE TABLE user_personas (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    interest_weights JSONB,
    price_sensitivity FLOAT,
    interaction_tendency JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户行为模拟记录表
CREATE TABLE interactions (
    id BIGSERIAL PRIMARY KEY,
    persona_id BIGINT REFERENCES user_personas(id),
    content_id BIGINT REFERENCES content_raw(id),
    action TEXT NOT NULL,
    dwell_time INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 推荐结果表
CREATE TABLE recommendations (
    id BIGSERIAL PRIMARY KEY,
    persona_id BIGINT REFERENCES user_personas(id),
    persona_name TEXT,
    content_id BIGINT REFERENCES content_raw(id),
    score FLOAT NOT NULL,
    category TEXT,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. 获取API凭证

在项目设置中找到：
- **Project URL**: 用作 `SUPABASE_URL`
- **anon public key**: 用作 `SUPABASE_KEY`

## 第二步：飞书配置

### 1. 创建飞书应用

1. 访问 [飞书开发者后台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 记录 **App ID** 和 **App Secret**

### 2. 授予权限

在应用权限页面，添加以下权限：
- `bitable:app` - 访问多维表格应用
- `bitable:app:readonly` - 只读访问

### 3. 获取多维表格信息

1. 创建或打开目标多维表格
2. 从URL中提取：
   - Base ID (类似 `Z7RTbVpleamDjlsrBX7cBCConEb`)
   - Table ID (类似 `tbl1mUkTnmdx0W1u`)

## 第三步：GitHub Secrets配置

在GitHub仓库的 **Settings** > **Secrets and variables** > **Actions** 中添加以下Secrets：

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key
OPENAI_API_KEY=sk-xxx  # 可选，用于智能标签生成
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_BASE_ID=your_base_id
FEISHU_TABLE_ID=your_table_id
```

## 第四步：测试运行

### 手动触发工作流

1. 进入GitHub仓库的 **Actions** 页面
2. 选择要测试的工作流（如 `Content Crawler`）
3. 点击 **Run workflow** 按钮
4. 查看运行日志确认是否成功

### 建议测试顺序

1. **crawler.yml** - 测试数据采集
2. **tagging.yml** - 测试内容标签
3. **simulation.yml** - 测试用户模拟
4. **feishu_sync.yml** - 测试飞书同步

## 第五步：查看结果

### Supabase

访问Supabase Dashboard查看各表数据：
- `content_raw` - 原始采集数据
- `content_profile` - 标签化内容
- `recommendations` - 推荐结果

### 飞书

打开配置的飞书多维表格，查看同步的推荐结果。

## 常见问题

### 工作流运行失败

1. 检查GitHub Secrets是否正确配置
2. 查看Actions日志中的错误信息
3. 确认Supabase和飞书的权限设置

### 数据未同步到飞书

1. 确认飞书应用已发布并启用
2. 检查飞书表格ID是否正确
3. 验证飞书API权限范围

### Supabase连接失败

1. 确认项目URL和密钥正确
2. 检查Supabase项目是否处于活动状态
3. 验证网络连接

## 下一步

系统配置完成后，可以：

1. **实现爬虫逻辑** - 在 `scripts/crawler.py` 中实现具体的小红书/抖音爬虫
2. **优化标签策略** - 在 `scripts/tag_content.py` 中完善标签分类规则
3. **设计用户画像** - 创建符合业务场景的虚拟用户画像
4. **开发推荐算法** - 实现个性化推荐算法逻辑
5. **定期监控** - 查看GitHub Actions运行日志，确保系统正常运行

## 技术支持

如遇到问题，可以：
- 查看GitHub Issues
- 参考 [Supabase文档](https://supabase.com/docs)
- 参考 [飞书开放平台文档](https://open.feishu.cn/document/)
