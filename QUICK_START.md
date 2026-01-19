# 快速开始指南 - 3分钟上手

## 🚀 一行命令安装

```bash
# 1. 克隆且进入
git clone https://github.com/e2738697-sketch/content-recommendation-system.git
cd content-recommendation-system

# 2. 创建虚拟环境
python3.11 -m venv venv && source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境
cp .env.example .env
# 编辑 .env ，添加 Supabase 凭证

# 5. 启动 API
python app.py
```

---

## 📄 十秒内了解

### 整个系统流程

```
输入关键词 (e.g., "美妆")
       ⬇️
爬取演示界面 (keyword_crawler_demo.html)
       ⬇️
Supabase 数据库
       ⬇️
爬取 + 保存内容
       ⬇️
AI 标注 + 推荐
       ⬇️
飞书同步 (Feishu)
```

---

## 🖫️ 接下来做什么

1. 在 Supabase 中创建数据库表（参考 TESTING_GUIDE.md）
2. 打开 `http://localhost:8000/keyword_crawler_demo.html`
3. 添加第一个关键词
4. 检查数据是否保存到 Supabase
5. 在 Supabase 中查询数据验证

---

## 📚 完整指南

详细配置需求，请查看 TESTING_GUIDE.md

---

## 🥷 像不到？

```bash
# 检查环境变量
echo $SUPABASE_URL

# 重新安装依赖
pip install --force-reinstall -r requirements.txt

# 查看日志 - API 应有输出
```

---

## 🌟 下一步

系统定时爬取内容 → AI 自动标注 → 推荐一上人群 → 飞书同步

祝测试顺利! 🚀
