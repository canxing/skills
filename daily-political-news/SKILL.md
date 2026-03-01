---
name: daily-political-news
description: 每日定时收集国内外时政、经济、社会、军事新闻，AI翻译外文并生成3-5个要点摘要，通过飞书消息推送。支持每天早上8点自动执行。
---

# 每日时政新闻收集

自动收集国内外时政新闻，AI翻译外文标题，生成3-5个要点摘要，通过飞书消息推送。

## 触发条件

当用户表达以下意图时调用：
- "收集今天的新闻"
- "获取时政新闻"
- "运行新闻收集"
- "daily-political-news"

## 快速开始

### 1. 配置环境变量

```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
```

### 2. 手动执行

```bash
python3 scripts/collect_news_v2.py
```

### 3. 设置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加行（每天上午8点执行）
0 8 * * * cd /path/to/daily-political-news && python3 scripts/collect_news_v2.py >> logs/cron.log 2>&1
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

## AI处理

1. **外文翻译**：使用 DeepSeek API 将英文标题翻译为中文
2. **要点提取**：AI 从新闻内容中提取3-5个关键要点
3. **内容过滤**：根据关键词筛选时政相关新闻

## 输出格式

飞书消息格式：

```
📰 每日新闻简报 - YYYY-MM-DD

🇨🇳 国内新闻
━━━━━━━━━━━━━━━
1. 【新闻标题】
   来源：媒体名称
   链接：原文链接
   
   📋 要点：
   • 要点一
   • 要点二
   • 要点三

🇺🇸 国际新闻
━━━━━━━━━━━━━━━
1. 【中文翻译 / 英文原文】
   来源：媒体名称
   链接：原文链接
   
   📋 要点：
   • 要点一
   • 要点二
   • 要点三
```

## 技术实现

1. **RSS抓取**：通过 RSSHub 聚合各媒体 RSS 源
2. **内容解析**：XML 解析提取新闻标题、链接、摘要
3. **AI处理**：调用 DeepSeek API 进行翻译和摘要
4. **消息推送**：通过飞书 Webhook 发送格式化消息

## 配置说明

### 必需配置

| 环境变量 | 说明 | 获取方式 |
|---------|------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | https://platform.deepseek.com/ |
| `FEISHU_WEBHOOK` | 飞书机器人 Webhook | 飞书群设置 → 添加自定义机器人 |

### 可选配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `MAX_RETRIES` | 3 | RSS获取失败重试次数 |
| `RETRY_DELAY` | 5 | 重试间隔（秒） |
| `NEWS_LIMIT` | 5 | 每类别最多显示条数 |

## 文件结构

```
daily-political-news/
├── SKILL.md                    # 技能文档
├── requirements.txt            # Python依赖
├── config.sh                   # 配置检查脚本
└── scripts/
    ├── collect_news_v2.py      # 主程序
    └── demo_output.py          # 演示输出
```

## 依赖安装

```bash
pip3 install feedparser requests
```

或使用系统自带库（标准库版本）。

## 注意事项

1. **网络访问**：需要能访问 RSSHub 和 DeepSeek API
2. **API限制**：DeepSeek API 有速率限制，注意控制调用频率
3. **RSS稳定性**：RSSHub 作为第三方服务，可能存在不稳定情况
4. **内容合规**：仅抓取公开新闻，遵守各媒体的使用条款

## 故障排查

| 问题 | 解决方法 |
|-----|---------|
| RSS获取失败 | 检查网络连接，增加重试次数 |
| AI翻译失败 | 检查 DEEPSEEK_API_KEY 是否有效 |
| 飞书发送失败 | 检查 FEISHU_WEBHOOK 是否正确 |
| 无新闻内容 | 检查关键词过滤规则是否过于严格 |

## 更新日志

### v1.0.0 (2026-03-01)
- 初始版本发布
- 支持国内外新闻收集
- 集成 DeepSeek AI 翻译和摘要
- 支持飞书消息推送
- 支持定时任务

## 相关文件

- `scripts/collect_news_v2.py` - 核心收集脚本
