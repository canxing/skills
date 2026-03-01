#!/bin/bash
# 配置脚本

echo "=== 每日新闻简报配置 ==="
echo ""

# 检查 DeepSeek API Key
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️ 请设置 DeepSeek API Key:"
    echo "   export DEEPSEEK_API_KEY=your_key_here"
else
    echo "✓ DeepSeek API Key 已配置"
fi

# 检查飞书 Webhook
if [ -z "$FEISHU_WEBHOOK" ]; then
    echo ""
    echo "⚠️ 请设置飞书 Webhook:"
    echo "   export FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
    echo ""
    echo "获取方式："
    echo "1. 在飞书群聊中添加自定义机器人"
    echo "2. 复制 Webhook 地址"
    echo "3. 设置环境变量"
else
    echo "✓ 飞书 Webhook 已配置"
fi

echo ""
echo "=== 定时任务配置 ==="
echo "添加到 crontab:"
echo "0 8 * * * cd $(pwd) && python3 scripts/collect_news_v2.py >> logs/cron.log 2>&1"
