# SuperMap Sonar Error Analysis Skill

一个用于分析 SonarQube 质量门失败原因的 Claude Code Skill。

## 功能

- 自动解析 Sonar URL，提取项目信息和 PR 号
- 查询质量门状态
- 质量门通过时：显示简洁的成功信息
- 质量门失败时：
  - 分析失败的具体原因（覆盖率、重复率、问题等）
  - 统计问题分布（Blocker/Critical/Major/Minor/Info）
  - 列出主要问题详情
  - 提供针对性的改进建议

## 安装

1. 确保 skill 文件位于 Claude Code 的 skills 目录：
   ```
   ~/.claude/skills/supermap-sonar-error-analysis/
   ├── SKILL.md
   └── README.md
   ```

2. 设置环境变量：
   ```bash
   # Windows
   set SUPERMAP_SONAR_TOKEN=your_sonar_token_here

   # Linux/Mac
   export SUPERMAP_SONAR_TOKEN=your_sonar_token_here
   ```

   获取 Token：
   - 登录 SonarQube (http://sonar.ispeco.com:9001)
   - 进入 **User > My Account > Security**
   - 生成新的 User Token

## 使用方法

### 触发方式

提供以下任一形式的信息：

1. **Sonar 项目 URL**：
   ```
   http://sonar.ispeco.com:9001/dashboard?id=com.supermap.cloud:ispeco-dashboard-api
   ```

2. **Sonar PR URL**（自动识别 PR 号）：
   ```
   http://sonar.ispeco.com:9001/dashboard?id=com.supermap.cloud:ispeco-dashboard-api&pullRequest=3099
   ```

3. **纯项目 key**：
   ```
   com.supermap.cloud:ispeco-dashboard-api
   ```

4. **项目 key + PR 号**：
   ```
   com.supermap.cloud:ispeco-dashboard-api PR:3099
   ```

### 示例对话

```
User: 帮我看看这个 Sonar 检查 http://sonar.ispeco.com:9001/dashboard?id=com.supermap.cloud:ispeco-dashboard-api&pullRequest=3099

Claude: 正在分析 Sonar 质量门状态...

✗ Sonar 质量门未通过
  项目: com.supermap.cloud:ispeco-dashboard-api
  分支: PR #3099

【失败原因】
1. 新代码覆盖率 65.2% < 要求 80% （差距 14.8%）
2. 发现 3 个 Blocker 级别问题

【问题统计】
- Blocker: 3
- Critical: 5
- Major: 12

【主要问题】
1. [Blocker] 空指针异常风险
   文件: src/main/java/com/supermap/cloud/dashboard/service/AnalysisService.java:142
   规则: java:S2259

【改进建议】
1. 为新代码添加单元测试，补充缺失的 14.8% 覆盖率
2. 修复所有 Blocker 级别问题
...
```

## 技术实现

### Sonar API 调用

质量门状态查询：
```bash
curl -u "${SUPERMAP_SONAR_TOKEN}:" \
  "http://sonar.ispeco.com:9001/api/qualitygates/project_status?projectKey={key}&pullRequest={pr}"
```

指标详情查询：
```bash
curl -u "${SUPERMAP_SONAR_TOKEN}:" \
  "http://sonar.ispeco.com:9001/api/measures/component?component={key}&metricKeys=coverage,new_coverage,..."
```

问题列表查询：
```bash
curl -u "${SUPERMAP_SONAR_TOKEN}:" \
  "http://sonar.ispeco.com:9001/api/issues/search?componentKeys={key}&severities=BLOCKER,CRITICAL&statuses=OPEN"
```

### 认证方式

SonarQube 使用 Basic Auth：
- 用户名: Token 值
- 密码: 空（留空）

### 关键指标

| 指标 | API Key | 说明 |
|------|---------|------|
| 整体覆盖率 | `coverage` | 代码行覆盖率百分比 |
| 新代码覆盖率 | `new_coverage` | 新增/修改代码的覆盖率 |
| 整体重复率 | `duplicated_lines_density` | 重复代码行百分比 |
| 新代码重复率 | `new_duplicated_lines_density` | 新增/修改代码的重复率 |
| Bug 数 | `bugs` | 可靠性问题数量 |
| 漏洞数 | `vulnerabilities` | 安全问题数量 |
| 代码异味 | `code_smells` | 可维护性问题数量 |

## 输出格式

### 质量门通过
```
✓ Sonar 质量门通过
  项目: {projectKey}
  分支: {branch}
  覆盖率: {coverage}%
  重复率: {duplication}%
```

### 质量门失败
```
✗ Sonar 质量门未通过
  项目: {projectKey}
  分支: {branch}

【失败原因】
1. ...
2. ...

【问题统计】
- Blocker: X
- Critical: Y
- Major: Z
...

【主要问题】
1. [级别] 描述
   文件: 路径:行号
   规则: 规则ID

【改进建议】
1. ...
2. ...

【参考链接】
- {sonar_url}
```

## 常见问题

### Q: 提示 "SUPERMAP_SONAR_TOKEN 未设置"
确保已正确设置环境变量。Windows 用户需要重启终端或 IDE 使环境变量生效。

### Q: 提示 "Token 无效"
- 检查 Token 是否已过期（SonarQube 中可查看 Token 创建时间）
- 检查 Token 是否有项目访问权限
- 尝试重新生成 Token

### Q: 项目不存在
- 确认 project key 拼写正确
- 确认 Token 有该项目的访问权限

### Q: 无法访问 Sonar 服务器
- 检查网络连接
- 确认 Sonar 服务器地址正确（默认: http://sonar.ispeco.com:9001）

## 更新日志

### v1.0.0
- 初始版本
- 支持质量门状态查询
- 支持 PR 分析
- 支持失败原因分析和改进建议

## 维护

- 作者: SuperMap iCloud Native Team
- 问题反馈: 请联系团队或通过内部渠道反馈
