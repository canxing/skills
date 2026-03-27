/**
 * URL 解析器模块
 * 负责解析 TeamCity 构建 URL
 */

/**
 * 解析 TeamCity URL，提取 baseUrl、buildTypeId 和分支信息
 * @param {string} url - TeamCity 构建 URL
 * @returns {Object} { baseUrl, buildTypeId, branch }
 * @throws {Error} 当 URL 格式不正确时抛出
 */
function parseTeamcityUrl(url) {
    try {
        const urlObj = new URL(url);
        const baseUrl = `${urlObj.protocol}//${urlObj.host}`;

        // 从路径提取 buildTypeId
        // 支持的格式:
        // - /buildConfiguration/{buildTypeId}
        // - /viewType.html?buildTypeId={buildTypeId}
        // - /buildConfiguration/{buildTypeId}?focusLine=xxx

        let buildTypeId = null;

        // 尝试从路径匹配
        const pathMatch = urlObj.pathname.match(/\/buildConfiguration\/([^/?]+)/);
        if (pathMatch) {
            buildTypeId = pathMatch[1];
        }

        // 尝试从查询参数匹配
        if (!buildTypeId) {
            buildTypeId = urlObj.searchParams.get('buildTypeId');
        }

        if (!buildTypeId) {
            throw new Error('无法从 URL 提取 Build Type ID，请确保 URL 格式正确。\n' +
                '支持的格式：\n' +
                '- http://host/buildConfiguration/BUILD_TYPE_ID\n' +
                '- http://host/viewType.html?buildTypeId=BUILD_TYPE_ID');
        }

        // 提取分支信息
        let branch = null;
        const branchParam = urlObj.searchParams.get('branch');
        if (branchParam) {
            // URL 解码分支名称
            branch = decodeURIComponent(branchParam);
        }

        return { baseUrl, buildTypeId, branch };
    } catch (error) {
        if (error.message.startsWith('无法从 URL')) {
            throw error;
        }
        throw new Error(`URL 解析失败: ${error.message}`);
    }
}

module.exports = { parseTeamcityUrl };
