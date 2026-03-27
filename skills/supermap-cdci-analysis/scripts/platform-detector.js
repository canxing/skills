/**
 * 平台检测器模块
 * 负责检测操作系统平台并提供平台特定的命令
 */

const os = require('os');

/**
 * 检测当前操作系统平台
 * @returns {string} 'windows' | 'macos' | 'linux' | 'unknown'
 */
function detectPlatform() {
    const platform = os.platform();

    switch (platform) {
        case 'win32':
            return 'windows';
        case 'darwin':
            return 'macos';
        case 'linux':
            return 'linux';
        default:
            return 'unknown';
    }
}

/**
 * 根据平台格式化环境变量设置命令
 * @param {string} varName - 变量名
 * @param {string} value - 变量值
 * @param {string} platform - 平台类型（可选，默认自动检测）
 * @returns {string} 格式化的命令
 */
function formatEnvCommand(varName, value, platform = null) {
    const p = platform || detectPlatform();

    switch (p) {
        case 'windows':
            return `set ${varName}=${value}`;
        case 'macos':
        case 'linux':
            return `export ${varName}=${value}`;
        default:
            // 默认使用 POSIX 格式
            return `export ${varName}=${value}`;
    }
}

/**
 * 获取平台特定的命令连接符
 * @param {string} platform - 平台类型（可选）
 * @returns {string}
 */
function getCommandSeparator(platform = null) {
    const p = platform || detectPlatform();
    // Windows 和 Unix 都支持 &&
    return ' && ';
}

/**
 * 获取平台特定的路径分隔符
 * @param {string} platform - 平台类型（可选）
 * @returns {string}
 */
function getPathSeparator(platform = null) {
    const p = platform || detectPlatform();
    return p === 'windows' ? '\\' : '/';
}

/**
 * 将路径转换为平台特定格式
 * @param {string} path - 路径
 * @param {string} platform - 平台类型（可选）
 * @returns {string}
 */
function toPlatformPath(path, platform = null) {
    const p = platform || detectPlatform();
    const separator = getPathSeparator(p);

    // 统一使用正斜杠，然后根据平台转换
    return path.replace(/[/\\]/g, separator);
}

module.exports = {
    detectPlatform,
    formatEnvCommand,
    getCommandSeparator,
    getPathSeparator,
    toPlatformPath
};
