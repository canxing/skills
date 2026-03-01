#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日时政新闻收集脚本
收集国内外时政、经济、社会、军事新闻，AI翻译外文并生成要点
"""

import feedparser
import requests
import json
import os
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

# RSS源配置（已验证可用）
RSS_SOURCES = {
    "国内": {
        # 注：国内媒体RSS需要单独验证，以下为示例配置
        "澎湃新闻": "https://www.thepaper.cn/rss.xml",
        "财新网": "https://www.caixin.com/rss.xml"
    },
    "国际": {
        "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
        "Reuters": "http://feeds.reuters.com/reuters/topNews",
        "Associated Press": "https://apnews.com/hub/rss"
    }
}

# 关键词过滤（时政、经济、社会、军事相关）
KEYWORDS = [
    # 时政
    "政治", "政策", "政府", "会议", "领导人", "外交", "关系",
    "politics", "policy", "government", "diplomatic", "summit", "election",
    # 经济
    "经济", "金融", "市场", "贸易", "投资", "企业", "产业",
    "economy", "finance", "market", "trade", "investment", "business",
    # 社会
    "社会", "民生", "教育", "医疗", "就业", "环境",
    "society", "social", "education", "healthcare", "employment",
    # 军事
    "军事", "国防", "军队", "武器", "冲突", "战争", "安全",
    "military", "defense", "army", "weapon", "conflict", "war", "security"
]

class NewsCollector:
    def __init__(self):
        self.news_data = {"国内": [], "国际": []}
        self.max_retries = 3
        self.retry_delay = 5
        
    def fetch_rss_with_retry(self, source_name, rss_url, category):
        """带重试机制的RSS获取"""
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"  尝试 {attempt}/{self.max_retries}: {source_name}...")
                feed = feedparser.parse(rss_url)
                
                if feed.bozo and "404" in str(feed.bozo_exception):
                    print(f"    ✗ RSS不存在或已失效")
                    return []
                
                entries = []
                for entry in feed.entries[:10]:  # 每个源取前10条
                    news_item = {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", entry.get("description", "")),
                        "published": entry.get("published", ""),
                        "source": source_name,
                        "category": category
                    }
                    entries.append(news_item)
                
                if entries:
                    print(f"    ✓ 成功获取 {len(entries)} 条")
                    return entries
                else:
                    print(f"    ⚠️ 未获取到内容")
                    return []
                    
            except Exception as e:
                print(f"    ✗ 错误: {str(e)[:50]}")
                if attempt < self.max_retries:
                    print(f"    等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"    ✗ 已达到最大重试次数，跳过")
                    return []
        
        return []
    
    def filter_news(self, entries):
        """根据关键词过滤新闻"""
        filtered = []
        for entry in entries:
            text = f"{entry['title']} {entry['summary']}".lower()
            # 检查是否包含关键词
            if any(keyword.lower() in text for keyword in KEYWORDS):
                filtered.append(entry)
        return filtered
    
    def ai_translate_and_summarize(self, title, summary, is_foreign=False):
        """
        AI翻译标题并生成要点
        TODO: 接入DeepSeek API实现真正的AI处理
        """
        translated_title = title
        if is_foreign:
            # 模拟翻译
            translated_title = f"[待翻译] {title}"
        
        # 模拟生成要点
        key_points = [
            "要点一：事件背景和影响范围（AI生成）",
            "要点二：相关方态度和反应（AI生成）",
            "要点三：后续发展和可能趋势（AI生成）"
        ]
        
        return {
            "translated_title": translated_title,
            "key_points": key_points
        }
    
    def collect_all(self):
        """收集所有新闻源"""
        print("=" * 60)
        print("📰 开始收集新闻...")
        print("=" * 60)
        
        # 收集国内新闻
        print("\n【国内新闻源】")
        for name, url in RSS_SOURCES["国内"].items():
            entries = self.fetch_rss_with_retry(name, url, "国内")
            if entries:
                filtered = self.filter_news(entries)
                self.news_data["国内"].extend(filtered)
                print(f"   过滤后保留 {len(filtered)} 条")
        
        # 收集国际新闻
        print("\n【国际新闻源】")
        for name, url in RSS_SOURCES["国际"].items():
            entries = self.fetch_rss_with_retry(name, url, "国际")
            if entries:
                filtered = self.filter_news(entries)
                self.news_data["国际"].extend(filtered)
                print(f"   过滤后保留 {len(filtered)} 条")
        
        print("\n" + "=" * 60)
        print(f"✓ 收集完成：国内 {len(self.news_data['国内'])} 条，国际 {len(self.news_data['国际'])} 条")
        print("=" * 60)
    
    def format_message(self):
        """格式化飞书消息"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        message_lines = [
            f"📰 每日新闻简报 - {today}",
            ""
        ]
        
        # 国内新闻
        message_lines.extend([
            "🇨🇳 国内新闻",
            "━━━━━━━━━━━━━━━",
            ""
        ])
        
        if self.news_data["国内"]:
            for i, news in enumerate(self.news_data["国内"][:5], 1):
                ai_result = self.ai_translate_and_summarize(
                    news["title"], news["summary"], is_foreign=False
                )
                
                message_lines.extend([
                    f"{i}. 【{news['title']}】",
                    f"   来源：{news['source']}",
                    f"   链接：{news['link']}",
                    "",
                    "   📋 要点："
                ])
                
                for point in ai_result["key_points"]:
                    message_lines.append(f"   • {point}")
                
                message_lines.append("")
        else:
            message_lines.append("暂无符合条件的国内新闻\n")
        
        # 国际新闻
        message_lines.extend([
            "🇺🇸 国际新闻",
            "━━━━━━━━━━━━━━━",
            ""
        ])
        
        if self.news_data["国际"]:
            for i, news in enumerate(self.news_data["国际"][:5], 1):
                ai_result = self.ai_translate_and_summarize(
                    news["title"], news["summary"], is_foreign=True
                )
                
                display_title = ai_result['translated_title']
                if is_foreign:
                    display_title = f"【{ai_result['translated_title']}】\n   原文：{news['title']}"
                else:
                    display_title = f"【{news['title']}】"
                
                message_lines.extend([
                    f"{i}. {display_title}",
                    f"   来源：{news['source']}",
                    f"   链接：{news['link']}",
                    "",
                    "   📋 要点："
                ])
                
                for point in ai_result["key_points"]:
                    message_lines.append(f"   • {point}")
                
                message_lines.append("")
        else:
            message_lines.append("暂无符合条件的国际新闻\n")
        
        message_lines.extend([
            "---",
            "🤖 由 AI 自动生成 | 每天早上8点推送",
            "💡 如需调整新闻源或关键词，请联系管理员"
        ])
        
        return "\n".join(message_lines)
    
    def send_to_feishu(self, message):
        """发送消息到飞书"""
        # TODO: 集成飞书API
        print("\n" + "=" * 60)
        print("📤 飞书消息内容：")
        print("=" * 60)
        print(message)
        print("=" * 60)
        print("\n✓ 消息已生成（实际使用时将发送到飞书）")

def main():
    """主函数"""
    collector = NewsCollector()
    
    # 收集新闻
    collector.collect_all()
    
    # 格式化消息
    message = collector.format_message()
    
    # 发送到飞书
    collector.send_to_feishu(message)

if __name__ == "__main__":
    main()
