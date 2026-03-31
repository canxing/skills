# My Skills

自制 Agent Skills 集合，支持通过 [skills.sh](https://skills.sh) 安装。

## 快速开始

### 安装技能

```bash
# 安装单个技能（普通技能使用目录名）
npx skills add canxing/skills --skill daily-political-news -y

# 安装 Supermap 系列技能（使用 supermap: 前缀）
npx skills add canxing/skills --skill supermap:cdci-analysis -y
npx skills add canxing/skills --skill supermap:cve-analysis -y
npx skills add canxing/skills --skill supermap:jira-read -y
npx skills add canxing/skills --skill supermap:jira-search -y
npx skills add canxing/skills --skill supermap:search -y
npx skills add canxing/skills --skill supermap:sonar-error-analysis -y
npx skills add canxing/skills --skill supermap:wiki-read -y
npx skills add canxing/skills --skill supermap:wiki-search -y
npx skills add canxing/skills --skill supermap:wiki-writer -y
npx skills add canxing/skills --skill supermap:youtrack-search -y
npx skills add canxing/skills --skill supermap:youtrack-work-report -y

# 安装多个技能
npx skills add canxing/skills --skill skill-a --skill skill-b -y

# 查看已安装技能
npx skills list
```

## 技能列表

| 技能名称 | 描述 | 适用场景 |
|---------|------|---------|
| [bug-fixing](./skills/bug-fixing/) | 指导按照特定7步流程修复bug：分析→设计测试→确保UT通过→添加失败UT→修复代码→验证→最终通过 | Bug修复、代码调试 |
| [quickly-thinking](./skills/quickly-thinking/) | 确认对任务的理解，列出任务拆解 | 任务理解、需求澄清 |
| [daily-political-news](./skills/daily-political-news/) | 每日定时收集国内外时政新闻，AI翻译并生成要点摘要 | 新闻资讯、信息收集 |
| [supermap-cdci-analysis](./skills/supermap-cdci-analysis/) | 分析 TeamCity CI/CD 构建失败原因并提供解决方案 | CI/CD 故障排查、构建分析 |
| [supermap-cve-analysis](./skills/supermap-cve-analysis/) | 分析 Java/JavaScript 组件的 CVE 漏洞，判断误报并提供升级建议 | 安全审计、依赖检查 |
| [supermap-jira-read](./skills/supermap-jira-read/) | 读取 Supermap Jira 问题的详情，包括描述、附件、评论等 | 问题详情查询 |
| [supermap-jira-search](./skills/supermap-jira-search/) | 搜索 Supermap Jira 系统中的 issues、bug 报告或任务 | 问题追踪、Bug 查询 |
| [supermap-search](./skills/supermap-search/) | 统一搜索 Supermap wiki、Jira 和 YouTrack，整合展示结果 | 信息检索、知识查询 |
| [supermap-sonar-error-analysis](./skills/supermap-sonar-error-analysis/) | 分析 SonarQube 质量门失败原因并提供改进建议 | 代码质量检查、质量门分析 |
| [supermap-wiki-read](./skills/supermap-wiki-read/) | 完整读取 wiki 页面内容，包括图片、评论和递归解析引用页面 | 文档阅读、内容获取 |
| [supermap-wiki-search](./skills/supermap-wiki-search/) | 搜索 Supermap Confluence wiki，查找公司文档和技术资料 | 文档查询、知识库检索 |
| [supermap-wiki-writer](./skills/supermap-wiki-writer/) | 向 Supermap Wiki 写入内容，支持创建新页面或修改现有页面 | Wiki 内容编写、文档维护 |
| [supermap-youtrack-search](./skills/supermap-youtrack-search/) | 搜索 Supermap YouTrack 系统中的 issues、任务或缺陷报告 | 任务查询、缺陷跟踪 |
| [supermap-youtrack-work-report](./skills/supermap-youtrack-work-report/) | 从 YouTrack 获取工作时间记录并生成工作报告 | 工作汇报、时间统计 |

## 开发指南

### 新增技能

1. **创建技能目录**
   ```bash
   cd ~/code/skills
   mkdir skills/my-new-skill
   cd skills/my-new-skill
   ```

2. **创建 SKILL.md**
   ```bash
   cat > SKILL.md << 'SKILL'
   ---
   name: my-new-skill
   description: 描述这个技能的功能
   agents: [OpenClaw, Claude Code, Codex]
   ---
   
   # My New Skill
   
   ## When to Use
   描述在什么场景下使用这个技能。
   
   ## How to Use
   提供具体的使用指导。
   SKILL
   ```

3. **添加辅助文件（可选）**
   - `scripts/` - 可执行脚本
   - `references/` - 参考文档
   - `assets/` - 资源文件

4. **本地测试**
   ```bash
   # 链接到 Agent 进行测试
   ln -s $(pwd)/skills/my-new-skill ~/.openclaw/workspace/.agents/skills/my-new-skill
   
   # 验证安装
   npx skills list
   ```

5. **提交到 Git**
   ```bash
   cd ~/code/skills
   git add skills/my-new-skill/
   git commit -m "Add my-new-skill"
   git push
   ```

6. **安装测试**
   ```bash
   # 从 GitHub 安装验证
   npx skills add canxing/skills --skill my-new-skill -y
   ```

### 删除技能

```bash
# 1. 本地移除技能目录
cd ~/code/skills
rm -rf skills/skill-name/

# 2. 提交变更
git add -A
git commit -m "Remove skill-name"
git push

# 3. 用户端卸载
npx skills remove skill-name -y
```

### 更新技能

```bash
# 1. 修改技能文件
cd ~/code/skills/skills/skill-name
# 编辑 SKILL.md 或其他文件

# 2. 本地测试
# 重新链接或重启 Agent

# 3. 提交更新
cd ~/code/skills
git add skills/skill-name/
git commit -m "Update skill-name: 描述变更内容"
git push

# 4. 用户端更新
npx skills check          # 检查更新
npx skills update         # 更新所有技能
# 或重新安装特定技能
npx skills add canxing/skills --skill skill-name -y
```

## 技能规范

### SKILL.md 头部格式

```yaml
---
name: skill-name                    # 技能标识符（小写+连字符）
description: 简短描述功能           # 一句话说明用途
agents: [OpenClaw, Claude Code]     # 支持的 Agent 列表（可选）
---
```

### 目录结构

```
skill-name/
├── SKILL.md              # 必需：技能定义和使用说明
├── README.md             # 可选：详细文档
├── requirements.txt      # 可选：Python 依赖
├── scripts/              # 可选：可执行脚本
│   └── script.py
├── references/           # 可选：参考文档
│   └── guide.md
└── assets/               # 可选：资源文件
    └── template.md
```

### 最佳实践

1. **命名规范**：使用小写字母和连字符，如 `cve-analysis`
2. **描述清晰**：一句话说明技能的核心价值
3. **When to Use**：明确触发条件，帮助 Agent 判断何时调用
4. **版本控制**：重大变更时更新说明，考虑用户迁移成本
5. **测试充分**：本地测试通过后再提交发布

## 安装到不同 Agent

### OpenClaw
```bash
# 普通技能
npx skills add canxing/skills --skill bug-fixing -y
npx skills add canxing/skills --skill daily-political-news -y

# Supermap 系列技能（使用 supermap: 前缀）
npx skills add canxing/skills --skill supermap:cdci-analysis -y
npx skills add canxing/skills --skill supermap:cve-analysis -y
npx skills add canxing/skills --skill supermap:jira-read -y
npx skills add canxing/skills --skill supermap:jira-search -y
npx skills add canxing/skills --skill supermap:search -y
npx skills add canxing/skills --skill supermap:sonar-error-analysis -y
npx skills add canxing/skills --skill supermap:wiki-read -y
npx skills add canxing/skills --skill supermap:wiki-search -y
npx skills add canxing/skills --skill supermap:wiki-writer -y
npx skills add canxing/skills --skill supermap:youtrack-search -y
npx skills add canxing/skills --skill supermap:youtrack-work-report -y
```

### Claude Code / Codex / Cursor
```bash
# 这些 Agent 也支持 skills.sh 标准
# 普通技能
npx skills add canxing/skills --skill bug-fixing -y

# Supermap 系列技能（使用 supermap: 前缀）
npx skills add canxing/skills --skill supermap:cdci-analysis -y
npx skills add canxing/skills --skill supermap:cve-analysis -y
npx skills add canxing/skills --skill supermap:jira-read -y
npx skills add canxing/skills --skill supermap:jira-search -y
npx skills add canxing/skills --skill supermap:search -y
npx skills add canxing/skills --skill supermap:sonar-error-analysis -y
npx skills add canxing/skills --skill supermap:wiki-read -y
npx skills add canxing/skills --skill supermap:wiki-search -y
npx skills add canxing/skills --skill supermap:wiki-writer -y
npx skills add canxing/skills --skill supermap:youtrack-search -y
npx skills add canxing/skills --skill supermap:youtrack-work-report -y
```

## 注意事项

- 技能通过 Git 子目录方式组织，每个子目录是一个独立技能
- 提交前确保 SKILL.md 格式正确，否则可能无法被识别
- 避免在技能目录中包含敏感信息（密码、密钥等）
- 定期更新技能以修复问题和改进功能

## 参考

- [skills.sh](https://skills.sh) - Skills 生态官网
- [Vercel Labs Skills](https://github.com/vercel-labs/skills) - 官方示例
