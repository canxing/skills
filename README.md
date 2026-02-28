# My Skills

自制 Agent Skills 集合，支持通过 [skills.sh](https://skills.sh) 安装。

## 快速开始

### 安装技能

```bash
# 安装单个技能
npx skills add canxing/skills --skill cve-vulnerability-analysis -y

# 安装多个技能
npx skills add canxing/skills --skill skill-a --skill skill-b -y

# 查看已安装技能
npx skills list
```

## 技能列表

| 技能名称 | 描述 | 适用场景 |
|---------|------|---------|
| [cve-vulnerability-analysis](./cve-vulnerability-analysis/) | 分析 Java/JavaScript 组件的 CVE 漏洞，判断误报并提供升级建议 | 安全审计、依赖检查 |

## 开发指南

### 新增技能

1. **创建技能目录**
   ```bash
   cd ~/code/skills
   mkdir my-new-skill
   cd my-new-skill
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
   ln -s $(pwd)/my-new-skill ~/.openclaw/workspace/.agents/skills/my-new-skill
   
   # 验证安装
   npx skills list
   ```

5. **提交到 Git**
   ```bash
   cd ~/code/skills
   git add my-new-skill/
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
rm -rf skill-name/

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
cd ~/code/skills/skill-name
# 编辑 SKILL.md 或其他文件

# 2. 本地测试
# 重新链接或重启 Agent

# 3. 提交更新
cd ~/code/skills
git add skill-name/
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
npx skills add canxing/skills --skill cve-vulnerability-analysis -y
```

### Claude Code / Codex / Cursor
```bash
# 这些 Agent 也支持 skills.sh 标准
npx skills add canxing/skills --skill cve-vulnerability-analysis -y
```

## 注意事项

- 技能通过 Git 子目录方式组织，每个子目录是一个独立技能
- 提交前确保 SKILL.md 格式正确，否则可能无法被识别
- 避免在技能目录中包含敏感信息（密码、密钥等）
- 定期更新技能以修复问题和改进功能

## 参考

- [skills.sh](https://skills.sh) - Skills 生态官网
- [Vercel Labs Skills](https://github.com/vercel-labs/skills) - 官方示例
