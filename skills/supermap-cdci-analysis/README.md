# supermap:cdci-analysis Skill

TeamCity CI/CD 构建分析 Skill，智能诊断构建失败原因并提供解决方案。

## 功能特性

- **智能动态分析**: 不依赖预定义错误类型，由 LLM 动态识别任何构建失败
- **渐进式日志分析**: 先分析日志尾部，不足再获取完整日志
- **双轨解决方案**: 明确区分临时方案（快速恢复）和长期方案（根本解决）
- **跨平台兼容**: 自动检测 Windows/Linux/Mac，提供对应平台命令

## 文件结构

```
supermap-cdci-analysis/
├── SKILL.md                      # Skill 定义和使用说明
├── README.md                     # 本文件
├── evals/                        # 测试用例目录
├── scripts/                      # 核心脚本模块
│   ├── parse-url.js             # URL 解析器
│   ├── api-client.js            # TeamCity API 客户端
│   ├── platform-detector.js     # 平台检测器
│   ├── log-analyzer.js          # 日志分析器
│   └── analyze-build.js         # 主分析流程
```

## 使用前提

1. **环境变量**: 根据 CI 服务器地址设置对应的环境变量

   | CI 服务器地址 | 环境变量 | 说明 |
   |--------------|----------|------|
   | cdci.ispeco.com:90 | SUPERMAP_CDCI_TOKEN | iSpeco CDCI |
   | ci.iserver.com:90 | SUPERMAP_CI_TOKEN | iServer CI |
   | ci.ispeco.com:90 | SUPERMAP_CI_TOKEN | iSpeco CI |

   ```bash
   # Windows
   set SUPERMAP_CDCI_TOKEN=your_token_here
   set SUPERMAP_CI_TOKEN=your_token_here

   # Linux/Mac
   export SUPERMAP_CDCI_TOKEN=your_token_here
   export SUPERMAP_CI_TOKEN=your_token_here
   ```

2. **工具依赖**: 需要 Node.js 环境（使用原生 https 模块，无需 curl）

## 使用方法

### 方式一：通过 Claude Skill 调用（推荐）

当 Claude 检测到你提供 TeamCity 构建 URL 时，会自动触发此 skill。

**示例输入：**
```
http://cdci.ispeco.com:90/buildConfiguration/ICloudNative_DistributeISpecoDashboardUi_11DeployTestISpecoDashboardUi
```

### 方式二：直接运行脚本

**1. 快速检查构建状态**
```bash
node scripts/analyze-build.js <TeamCity URL> [token]
```

**参数说明：**
- `<TeamCity URL>` - TeamCity 构建配置 URL
- `[token]` - 可选，TeamCity API Token（默认从环境变量读取）

**环境变量配置：**
```bash
# Windows
set SUPERMAP_CDCI_TOKEN=your_token_here

# Linux/Mac
export SUPERMAP_CDCI_TOKEN=your_token_here
```

**示例：**
```bash
# 使用环境变量中的 token
node scripts/analyze-build.js http://cdci.ispeco.com:90/buildConfiguration/MyProject_Build --raw

# 直接传入 token
node scripts/analyze-build.js http://cdci.ispeco.com:90/buildConfiguration/MyProject_Build my-token-here --raw

# 查看帮助
node scripts/analyze-build.js --help
```

**原始数据模式输出示例：**
```json
{
  "build": {
    "id": 12345,
    "number": "100",
    "status": "FAILURE",
    "statusText": "Tests failed: 2",
    "webUrl": "http://cdci.ispeco.com:90/viewLog.html?buildId=12345"
  },
  "logContent": "...",
  "failedTests": {...},
  "changes": [...]
}
```

**2. 作为模块引入**

```javascript
const { analyzeBuild, getBuildStatus } = require('./scripts/analyze-build');

// 完整分析
const result = await analyzeBuild('http://cdci.ispeco.com:90/buildConfiguration/MyProject_Build', {
    token: 'your-token',
    llmQuery: async (prompt) => {
        // 你的 LLM 调用函数
        return await callYourLLM(prompt);
    }
});

// 仅获取状态
const status = await getBuildStatus('http://cdci.ispeco.com:90/buildConfiguration/MyProject_Build');
```

### 示例输出（构建失败）
```
✗ 构建 #4694 失败

【临时解决方案】（立即执行）
1. 增加 Node.js 内存限制：
   Windows: set NODE_OPTIONS=--max-old-space-size=4096
   Linux/Mac: export NODE_OPTIONS=--max-old-space-size=4096

2. 重新运行构建

【长期解决方案】（根本解决）
1. 修改 package.json 永久增加内存配置
2. 拆分测试批次，减少单批次内存占用
3. 升级 CI 构建节点内存配置

【关键错误】（仅参考）
FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory
```

## 模块说明

### parse-url.js
解析 TeamCity URL，提取 baseUrl 和 buildTypeId。

### api-client.js
TeamCity REST API 客户端，支持：
- 获取最新构建状态
- 下载构建日志（支持部分/完整）
- 获取测试失败详情

### platform-detector.js
检测操作系统平台，提供平台特定的命令格式。

### log-analyzer.js
生成 LLM 分析 Prompt，解析分析结果，格式化输出。

### analyze-build.js
主分析流程，整合所有模块。

## 工作流程

1. 解析 URL 提取构建配置信息
2. 调用 TeamCity API 获取最新构建状态
3. 构建成功 → 返回简洁成功信息
4. 构建失败 → 渐进式获取日志
5. LLM 智能分析日志
6. 生成临时方案 + 长期方案
7. 格式化输出结果

## 支持的构建失败类型

- JavaScript/Node.js 内存不足
- Java/JVM 内存不足
- 单元测试/集成测试失败
- 编译错误
- 依赖下载失败
- Docker 镜像构建失败
- 超时/网络问题
- 环境配置问题
- ... 以及任何其他类型（动态识别）

## 平台兼容性

| 平台 | 环境变量设置 | 状态 |
|------|-------------|------|
| Windows | `set VAR=value` | ✅ 支持 |
| macOS | `export VAR=value` | ✅ 支持 |
| Linux | `export VAR=value` | ✅ 支持 |

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| SUPERMAP_CDCI_TOKEN / SUPERMAP_CI_TOKEN 未设置 | 根据 CI 服务器地址提示设置对应环境变量 |
| Token 无效 (401) | 提示检查 Token 是否过期 |
| 构建配置不存在 (404) | 提示检查 URL 是否正确 |
| 服务器不可达 | 提示检查网络连接 |
| 日志下载失败 | 降级为显示基本失败信息 |

## 开发计划

- [x] URL 解析器
- [x] API 客户端
- [x] 平台检测器
- [x] 日志分析器
- [x] 主分析流程
- [x] 多 CI 服务器支持（SUPERMAP_CDCI_TOKEN / SUPERMAP_CI_TOKEN）
- [x] Sonar 失败联动分析
- [ ] 测试用例
- [ ] 描述优化

## 版本历史

### v1.0.0 (2026-03-09)
- 初始版本
- 支持渐进式日志分析
- 支持动态错误识别
- 支持跨平台命令

## License

MIT
