/**
 * 日志分析器模块
 * 负责生成 LLM 分析 Prompt 和格式化输出
 */

/**
 * 生成日志片段分析的 LLM Prompt
 * @param {string} logSnippet - 日志片段
 * @param {Object} buildInfo - 构建信息
 * @returns {string} LLM Prompt
 */
function createSnippetAnalysisPrompt(logSnippet, buildInfo) {
    return `你是一位 CI/CD 构建故障排查专家。请分析以下 TeamCity 构建日志片段，判断是否能确定失败原因和解决方案。

【构建信息】
- 构建编号: #${buildInfo.number}
- 构建状态: ${buildInfo.status}
- 失败摘要: ${buildInfo.statusText || 'N/A'}

【日志片段】（最后 300 行）
\`\`\`
${logSnippet.slice(-8000)}
\`\`\`

请用 JSON 格式回复：
{
    "confidence": "high" | "medium" | "low",
    "reason": "判断理由（简要说明）",
    "errorType": "错误类型（如：JavaScript内存不足、测试失败、编译错误、Docker构建失败等）",
    "rootCause": "根本原因分析（1-2句话）",
    "tempSolutions": ["临时解决方案1", "临时解决方案2"],
    "longTermSolutions": ["长期解决方案1", "长期解决方案2"],
    "keyErrors": ["关键错误信息1（1-2行）", "关键错误信息2（可选）"]
}

说明：
- confidence: high=能确定原因和方案, medium=可能确定但需要更多信息, low=信息不足需要完整日志
- tempSolutions: 能立即执行恢复构建的方案（2-3条，具体可操作）
- longTermSolutions: 能预防问题再次发生的方案（2-3条）
- keyErrors: 提取 1-2 行最重要的错误信息作为参考

请确保 JSON 格式正确，可以被直接解析。`;
}

/**
 * 生成完整日志分析的 LLM Prompt
 * @param {string} fullLog - 完整日志
 * @param {Object} buildInfo - 构建信息
 * @returns {string} LLM Prompt
 */
function createFullLogAnalysisPrompt(fullLog, buildInfo) {
    // 限制日志大小，避免超出 token 限制
    const truncatedLog = fullLog.length > 50000
        ? fullLog.slice(0, 25000) + '\n... [中间日志省略] ...\n' + fullLog.slice(-25000)
        : fullLog;

    return `你是一位 CI/CD 构建故障排查专家。请分析以下完整的 TeamCity 构建日志，提供解决方案。

【构建信息】
- 构建编号: #${buildInfo.number}
- 构建状态: ${buildInfo.status}
- 失败摘要: ${buildInfo.statusText || 'N/A'}

【完整构建日志】
\`\`\`
${truncatedLog}
\`\`\`

请用 JSON 格式回复：
{
    "errorType": "错误类型",
    "rootCause": "根本原因分析（2-3句话）",
    "tempSolutions": ["临时解决方案1", "临时解决方案2", "临时解决方案3"],
    "longTermSolutions": ["长期解决方案1", "长期解决方案2", "长期解决方案3"],
    "keyErrors": ["关键错误信息1", "关键错误信息2"]
}

要求：
- errorType: 具体的错误类型名称
- rootCause: 解释为什么会发生这个错误
- tempSolutions: 能立即执行恢复当前构建的方案（具体可操作，包含具体命令或操作步骤）
- longTermSolutions: 能预防问题再次发生的方案（从根本上解决）
- keyErrors: 提取最重要的错误信息作为参考

请确保 JSON 格式正确，可以被直接解析。`;
}

/**
 * 解析 LLM 分析结果
 * @param {string} llmResponse - LLM 返回的文本
 * @returns {Object} 解析后的分析结果
 */
function parseAnalysisResult(llmResponse) {
    try {
        // 尝试从文本中提取 JSON
        const jsonMatch = llmResponse.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]);
        }
        throw new Error('无法从 LLM 响应中解析 JSON');
    } catch (error) {
        // 如果解析失败，返回一个默认结构
        return {
            confidence: 'low',
            errorType: '未知错误',
            rootCause: '无法解析分析结果',
            tempSolutions: ['请手动查看构建日志获取详细信息'],
            longTermSolutions: ['建议联系开发团队协助排查'],
            keyErrors: [llmResponse.slice(0, 200)]
        };
    }
}

/**
 * 格式化分析结果为输出文本
 * @param {Object} analysis - 分析结果
 * @param {string} platform - 当前平台
 * @returns {string} 格式化输出
 */
function formatAnalysisOutput(analysis, platform) {
    const { formatEnvCommand } = require('./platform-detector');

    let output = '';

    // 临时解决方案
    output += `【临时解决方案】（立即执行）\n`;
    if (analysis.tempSolutions && analysis.tempSolutions.length > 0) {
        analysis.tempSolutions.forEach((solution, index) => {
            // 替换环境变量占位符
            let formattedSolution = solution;

            // 处理 NODE_OPTIONS
            if (solution.includes('NODE_OPTIONS') && solution.includes('max-old-space-size')) {
                const match = solution.match(/(--max-old-space-size=\d+)/);
                if (match) {
                    const envCmd = formatEnvCommand('NODE_OPTIONS', match[1], platform);
                    formattedSolution = solution.replace(/export\s+NODE_OPTIONS=[^\s]+/, envCmd)
                                                .replace(/set\s+NODE_OPTIONS=[^\s]+/, envCmd);
                }
            }

            // 处理 JAVA_OPTS
            if (solution.includes('JAVA_OPTS') || solution.includes('-Xmx')) {
                const match = solution.match(/(-Xmx\d+[mg])/i);
                if (match) {
                    const envCmd = formatEnvCommand('JAVA_OPTS', match[1], platform);
                    formattedSolution = solution.replace(/export\s+JAVA_OPTS=[^\s]+/, envCmd)
                                                .replace(/set\s+JAVA_OPTS=[^\s]+/, envCmd);
                }
            }

            output += `${index + 1}. ${formattedSolution}\n`;
        });
    } else {
        output += '1. 请查看构建日志获取详细信息\n';
    }
    output += '\n';

    // 长期解决方案
    output += `【长期解决方案】（根本解决）\n`;
    if (analysis.longTermSolutions && analysis.longTermSolutions.length > 0) {
        analysis.longTermSolutions.forEach((solution, index) => {
            output += `${index + 1}. ${solution}\n`;
        });
    } else {
        output += '1. 建议联系开发团队协助排查\n';
    }
    output += '\n';

    // 关键错误（参考）
    output += `【关键错误】（仅参考）\n`;
    if (analysis.keyErrors && analysis.keyErrors.length > 0) {
        analysis.keyErrors.forEach(error => {
            output += `${error}\n`;
        });
    } else if (analysis.rootCause) {
        output += `${analysis.rootCause}\n`;
    }

    return output;
}

/**
 * 格式化成功构建的输出
 * @param {Object} buildInfo - 构建信息
 * @returns {string}
 */
function formatSuccessOutput(buildInfo) {
    const finishDate = buildInfo.finishOnAgentDate
        ? new Date(buildInfo.finishOnAgentDate).toLocaleString('zh-CN')
        : '未知';

    return `✓ 构建 #${buildInfo.number} 成功\n  完成时间: ${finishDate}`;
}

/**
 * 格式化错误输出
 * @param {string} errorMessage - 错误信息
 * @returns {string}
 */
function formatErrorOutput(errorMessage) {
    return `✗ 分析失败\n\n错误信息: ${errorMessage}`;
}

/**
 * 生成降级分析的 LLM Prompt
 * 用于无法获取完整日志时的分析
 * @param {string} fallbackInfo - 降级信息
 * @param {Object} buildInfo - 构建信息
 * @returns {string} LLM Prompt
 */
function createFallbackAnalysisPrompt(fallbackInfo, buildInfo) {
    return `你是一位 CI/CD 构建故障排查专家。由于无法获取完整构建日志，请基于以下可用信息分析失败原因。

【构建信息】
- 构建编号: #${buildInfo.number}
- 构建状态: ${buildInfo.status}
- 失败摘要: ${buildInfo.statusText || 'N/A'}

【可用信息】
${fallbackInfo}

请用 JSON 格式回复：
{
    "confidence": "medium",
    "errorType": "错误类型（基于状态文本推断）",
    "rootCause": "基于可用信息的根因分析（1-2句话）",
    "tempSolutions": ["临时解决方案1", "临时解决方案2"],
    "longTermSolutions": ["长期解决方案1", "长期解决方案2"],
    "keyErrors": ["关键错误信息"]
}

说明：
- 由于信息有限，confidence 固定为 medium
- 基于 statusText 推断最可能的错误类型
- 提供通用的排查建议
- 建议用户直接访问 TeamCity 查看完整日志

请确保 JSON 格式正确，可以被直接解析。`;
}

module.exports = {
    createSnippetAnalysisPrompt,
    createFullLogAnalysisPrompt,
    createFallbackAnalysisPrompt,
    parseAnalysisResult,
    formatAnalysisOutput,
    formatSuccessOutput,
    formatErrorOutput
};
