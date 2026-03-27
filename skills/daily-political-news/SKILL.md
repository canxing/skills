---
name: daily-political-news
description: 每日定时收集国内外时政、经济、社会、军事新闻，通过飞书消息推送。支持每天早上8点自动执行。
---

# 每日时政新闻收集

自动收集国内外时政新闻，通过飞书消息推送。

## 触发条件

当用户表达以下意图时调用：
- "收集今天的新闻"
- "获取时政新闻"
- "运行新闻收集"
- "daily-political-news"

## 快速开始

### 1. 配置环境变量（可选）

```bash
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
```

如果不配置，将只输出到控制台。

### 2. 手动执行

```bash
python3 scripts/collect_news_v6.py
```

### 3. 设置定时任务

**方式一：使用 OpenClaw Cron (推荐)**

```bash
# 查看当前任务
openclaw cron list

# 添加 daily-news 任务（已配置在 cron.yaml 中）
openclaw cron add --name daily-news --schedule "0 8 * * *" --command "python3 /home/test/.openclaw/workspace/skills/daily-political-news/scripts/collect_news_v6.py"
```

**方式二：使用系统 crontab**

```bash
# 编辑 crontab
crontab -e

# 添加行（每天上午8点执行）
0 8 * * * cd /home/test/.openclaw/workspace/skills/daily-political-news && python3 scripts/collect_news_v6.py >> logs/cron.log 2>&1
```

## 数据源

### 国内媒体
- **联合早报-中国** (via RSSHub)
- **CNA-两岸** (via RSSHub)

### 国际媒体
- **BBC World** (via RSSHub)
- **Reuters World** (via RSSHub)

## 新闻范围

- 时政
- 经济
- 社会
- 军事

## 处理流程

1. **RSS抓取**：通过 RSSHub 聚合各媒体 RSS 源
2. **内容解析**：XML 解析提取新闻标题、链接、摘要
3. **关键词过滤**：根据预设关键词筛选时政相关新闻
4. **消息推送**：通过飞书 Webhook 发送格式化消息

## 输出格式

飞书消息格式：

```
📰 每日新闻简报 - YYYY-MM-DD

🇨🇳 国内新闻
━━━━━━━━━━━━━━━
1. 【新闻标题】
   来源：媒体名称
   链接：原文链接
   📝 新闻摘要...

🇺🇸 国际新闻
━━━━━━━━━━━━━━━
1. 【新闻标题】
   来源：媒体名称
   链接：原文链接
   📝 新闻摘要...
```

## 配置说明

### 可选配置

| 环境变量 | 说明 | 获取方式 |
|---------|------|---------|
| `FEISHU_WEBHOOK` | 飞书机器人 Webhook | 飞书群设置 → 添加自定义机器人 |

### 脚本内配置

| 配置项 | 默认值 | 说明 |
|---------|--------|------|
| `max_retries` | 3 | RSS获取失败重试次数 |
| `retry_delay` | 5 | 重试间隔（秒） |
| `KEYWORDS` | 见代码 | 新闻过滤关键词列表 |

## 文件结构

```
daily-political-news/
├── SKILL.md                    # 技能文档
├── cron.yaml                   # 定时任务配置
└── scripts/
    ├── collect_news_v2.py      # 旧版本 (已弃用)
    ├── collect_news_v5.py      # 国际新闻专版
    └── collect_news_v6.py      # 当前主程序 (合并版：国际+AI科技+国内)
```

## 依赖

仅使用 Python 标准库，无需额外安装：
- `urllib.request` - HTTP请求
- `xml.etree.ElementTree` - XML解析
- `json` - JSON处理
- `datetime` - 日期时间

## 注意事项

1. **网络访问**：需要能访问 RSSHub 服务
2. **RSS稳定性**：RSSHub 作为第三方服务，可能存在不稳定情况
3. **内容合规**：仅抓取公开新闻，遵守各媒体的使用条款
4. **无AI处理**：本版本不使用 AI 翻译或摘要，直接输出原始新闻内容

## 故障排查

| 问题 | 解决方法 |
|-----|---------|
| RSS获取失败 | 检查网络连接，增加重试次数 |
| 飞书发送失败 | 检查 FEISHU_WEBHOOK 是否正确 |
| 无新闻内容 | 检查关键词过滤规则是否过于严格 |
| 403 Forbidden | RSSHub 可能被限制，尝试更换 User-Agent 或使用代理 |

## 更新日志

### v2.0.0 (2026-03-03)
- 移除 DeepSeek API 依赖
- 简化处理流程，直接输出原始新闻
- 减少外部依赖，仅使用 Python 标准库

### v1.0.0 (2026-03-01)
- 初始版本发布
- 支持国内外新闻收集
- 集成 DeepSeek AI 翻译和摘要
- 支持飞书消息推送
- 支持定时任务

## 相关文件

- `scripts/collect_news_v6.py` - 核心收集脚本（当前版本）
- `cron.yaml` - OpenClaw 定时任务配置
- `scripts/collect_news_v5.py` - V5 版本（仅国际新闻）
- `scripts/collect_news_v2.py` - V2 版本（旧版）
