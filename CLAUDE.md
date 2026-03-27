# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供该代码库的操作指南。

## 仓库概述

这是一个 AI Agent 技能集合仓库，可通过 [skills.sh](https://skills.sh) 安装使用。每个子目录是一个独立的"技能"(skill)，提供特定功能。

## 架构说明

### 技能目录结构

每个技能遵循以下目录布局：

```
skill-name/
├── SKILL.md              # 必需：YAML 头部 + 使用说明
├── README.md             # 可选：详细文档
├── scripts/              # 可选：可执行 Python 脚本
│   └── script.py         # 脚本仅使用 Python 标准库
├── references/           # 可选：参考文档
├── assets/               # 可选：模板和资源文件
└── cron.yaml             # 可选：OpenClaw 定时任务配置
```

### SKILL.md 格式规范

所有 SKILL.md 文件必须包含 YAML 头部：

```yaml
---
name: skill-name                    # 唯一标识符（小写+连字符）
description: 一句话描述            # 该技能的功能说明
agents: [OpenClaw, Claude Code]    # 支持的 Agent 列表（可选）
---
```

对于禁用模型调用的技能（纯工具执行）：

```yaml
---
name: namespace:skill-name
description: 描述
allowed-tools: [Bash, Read]        # 该技能可使用的工具
disable-model-invocation: true     # true 表示不调用模型
---
```

### 脚本开发规范

- **语言**：Python 3.7+
- **依赖**：仅使用 Python 标准库（无需 requirements.txt）
- **执行**：脚本位于 `scripts/` 目录，通过 `python3 scripts/<script>.py` 运行
- **配置**：API Token 和设置通过环境变量传递
- **输出**：标准输出使用 Markdown 格式

### 技能分类

**Supermap 内部工具** (supermap-*)：
- `supermap-wiki-search` - 搜索 Confluence Wiki
- `supermap-wiki-read` - 读取完整 Wiki 页面并递归解析引用
- `supermap-jira-search` - 搜索 Jira Issues
- `supermap-youtrack-search` - 搜索 YouTrack Issues
- `supermap-search` - 统一搜索以上三个系统

**工作效率**：
- `youtrack-work-summary` - 从 YouTrack 生成工作时间报告
- `daily-political-news` - 定时收集新闻并通过飞书推送

**安全审计**：
- `cve-vulnerability-analysis` - 分析 CVE 漏洞、判断误报、评估升级风险

## 常用开发命令

### 本地安装和测试技能

```bash
# 本地链接技能进行测试（OpenClaw）
ln -s $(pwd)/skills/skill-name ~/.openclaw/workspace/.agents/skills/skill-name

# 从 GitHub 安装（推送后）
npx skills add canxing/skills --skill skill-name -y

# 查看已安装技能
npx skills list

# 更新技能
npx skills check && npx skills update
```

### 运行技能脚本

```bash
# 大多数技能遵循以下执行模式
python3 scripts/<script>.py "<参数>"

# 示例：
python3 scripts/search_wiki.py "部署指南"
python3 scripts/youtrack_summary.py "2026-01"
python3 scripts/collect_news_v6.py
```

### 环境变量配置

**Supermap 系列技能**：
- `SUPERMAP_WIKI_TOKEN` - Confluence API Token
- `SUPERMAP_JIRA_TOKEN` - Jira API Token
- `SUPERMAP_YOUTRACK_TOKEN` - YouTrack API Token

**daily-political-news**：
- `FEISHU_WEBHOOK` - 飞书机器人 Webhook 地址（可选）

**youtrack-work-summary**：
- Token 文件路径：`~/.supermap/youtrack`

## 技能开发流程

1. **创建技能目录**：`mkdir skills/new-skill && cd skills/new-skill`
2. **编写 SKILL.md**：包含 YAML 头部和使用说明
3. **添加脚本**：使用 Python 标准库编写功能脚本
4. **本地测试**：链接到 Agent 验证功能
5. **提交推送**：`git add new-skill/ && git commit -m "Add new-skill: 描述"`
6. **安装验证**：`npx skills add canxing/skills --skill new-skill -y`
7. **同步 README.md**：修改或新增技能后，同步更新根目录 README.md 中的技能列表

## 重要注意事项

- 技能之间相互独立，技能之间不共享依赖
- 脚本需自行处理错误情况和输出格式化
- 更新技能时需保持向后兼容，或记录破坏性变更
- 切勿将 API Token 或凭证提交到代码仓库
