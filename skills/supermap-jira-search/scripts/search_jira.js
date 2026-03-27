#!/usr/bin/env node
/**
 * Supermap Jira Search Script (Node.js Version)
 *
 * Searches the Supermap Jira system and returns results as a markdown table.
 * Uses the SUPERMAP_JIRA_TOKEN environment variable for authentication.
 */

const https = require('https');

const JIRA_BASE_URL = 'jira.supermap.work';
const API_ENDPOINT = '/rest/quicksearch/1.0/productsearch/search';

function getToken() {
    const token = process.env.SUPERMAP_JIRA_TOKEN;
    if (!token) {
        console.error('Error: SUPERMAP_JIRA_TOKEN environment variable is not set.');
        console.error('Please set it with:');
        console.error('  Linux/macOS: export SUPERMAP_JIRA_TOKEN=\'your-token-here\'');
        console.error('  Windows (cmd): set SUPERMAP_JIRA_TOKEN=your-token-here');
        console.error('  Windows (PowerShell): $env:SUPERMAP_JIRA_TOKEN=\'your-token-here\'');
        process.exit(1);
    }
    return token;
}

function makeRequest(url, token) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: JIRA_BASE_URL,
            path: url,
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json',
                'User-Agent': 'Supermap-Jira-Search/1.0'
            },
            timeout: 30000,
            rejectUnauthorized: false // Allow self-signed certificates
        };

        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        const jsonData = JSON.parse(data);
                        resolve(jsonData);
                    } catch (e) {
                        reject(new Error(`Failed to parse response: ${e.message}`));
                    }
                } else if (res.statusCode === 401) {
                    reject(new Error('Authentication failed. Please check your SUPERMAP_JIRA_TOKEN.'));
                } else if (res.statusCode === 403) {
                    reject(new Error('Access forbidden. You may not have permission to search.'));
                } else {
                    reject(new Error(`HTTP ${res.statusCode}`));
                }
            });
        });

        req.on('error', (err) => {
            reject(new Error(`Network error: ${err.message}`));
        });

        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        req.end();
    });
}

async function searchJira(query, token) {
    const encodedQuery = encodeURIComponent(query);
    const url = `${API_ENDPOINT}?q=${encodedQuery}`;

    try {
        const response = await makeRequest(url, token);
        return response;
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

function extractIssues(response) {
    if (!Array.isArray(response)) {
        return [];
    }

    for (const section of response) {
        if (section && section.id === 'quick-search-issues') {
            return section.items || [];
        }
    }

    return [];
}

function formatAsMarkdownTable(items) {
    if (!items || items.length === 0) {
        return 'No issues found.';
    }

    const lines = ['| 标题 | 链接 |', '| --- | --- |'];

    for (const item of items) {
        const title = item.title || 'N/A';
        const url = item.url || '';

        if (url) {
            lines.push(`| ${title} | ${url} |`);
        } else {
            lines.push(`| ${title} | N/A |`);
        }
    }

    return lines.join('\n');
}

function printHelp() {
    console.log(`Supermap Jira Search (Node.js Version)

Usage: node search_jira.js <search-query>

Description:
    Search the Supermap Jira system and return matching issues as a markdown table.

Environment Variables:
    SUPERMAP_JIRA_TOKEN  - Required. Your Jira API token for authentication.

Examples:
    node search_jira.js iServer
    node search_jira.js "bug fix"
    node search_jira.js --help

Output:
    Results are displayed as a markdown table with issue titles and links.
`);
}

async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
        printHelp();
        process.exit(0);
    }

    const query = args.join(' ');
    const token = getToken();

    const response = await searchJira(query, token);
    const issues = extractIssues(response);

    const output = formatAsMarkdownTable(issues);
    console.log(output);
}

main().catch(err => {
    console.error(`Unexpected error: ${err.message}`);
    process.exit(1);
});
