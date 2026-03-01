#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日时政新闻收集脚本 V3
- 使用 RSSHub 作为统一源
- 使用内置AI翻译和摘要（不依赖外部API）
- 支持飞书消息推送
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import json
import os
import sys
import time
from datetime import datetime

# ============ 配置区域 ============

# RSS 源配置
RSS_SOURCES = {
    "国内": {},
    "国际": {
        "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "Reuters": "http://feeds.reuters.com/reuters/topNews"
    }
}

# 关键词过滤
KEYWORDS = [
    "China", "US", "Russia", "Iran", "Israel", "Middle East", "Taiwan",
    "politics", "economy", "military", "diplomatic", "trade", "war", "conflict",
    "president", "prime minister", "election", "sanctions", "nuclear"
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
                print(f"  [{category}] {source_name} - 尝试 {attempt}/{self.max_retries}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                req = urllib.request.Request(rss_url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = response.read()
                
                root = ET.fromstring(data)
                entries = []
                
                for item in root.findall('.//item'):
                    title = item.find('title')
                    link = item.find('link')
                    desc = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    if title is not None and title.text:
                        entries.append({
                            "title": title.text.strip(),
                            "link": link.text.strip() if link is not None else "",
                            "summary": desc.text.strip() if desc is not None and desc.text else "",
                            "published": pub_date.text if pub_date is not None else "",
                            "source": source_name,
                            "category": category
                        })
                
                if entries:
                    print(f"    ✓ 成功获取 {len(entries)} 条")
                    return entries[:8]
                else:
                    print(f"    ⚠️ 未获取到内容")
                    return []
                    
            except Exception as e:
                print(f"    ✗ 错误: {str(e)[:60]}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    print(f"    ✗ 跳过")
                    return []
        
        return []
    
    def filter_news(self, entries):
        """根据关键词过滤新闻"""
        filtered = []
        for entry in entries:
            text = f"{entry['title']} {entry['summary']}".lower()
            if any(keyword.lower() in text for keyword in KEYWORDS):
                filtered.append(entry)
        return filtered
    
    def collect_all(self):
        """收集所有新闻源"""
        print("=" * 60)
        print("📰 开始收集新闻...")
        print("=" * 60)
        
        for category in ["国际"]:  # 暂时只收集国际
            print(f"\n【{category}新闻源】")
            for name, url in RSS_SOURCES[category].items():
                entries = self.fetch_rss_with_retry(name, url, category)
                if entries:
                    filtered = self.filter_news(entries)
                    print(f"   过滤后保留 {len(filtered)} 条")
                    self.news_data[category].extend(filtered)
        
        total = len(self.news_data['国内']) + len(self.news_data['国际'])
        print(f"\n{'=' * 60}")
        print(f"✓ 收集完成：共 {total} 条")
        print("=" * 60)
    
    def format_message(self):
        """格式化消息（简化版，待AI处理）"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        lines = [
            f"📰 每日新闻简报 - {today}",
            "",
            "🇺🇸 国际新闻",
            "━━━━━━━━━━━━━━━",
            ""
        ]
        
        if self.news_data["国际"]:
            for i, news in enumerate(self.news_data["国际"][:5], 1):
                lines.extend([
                    f"{i}. 【{news['title']}】",
                    f"   来源：{news['source']}",
                    f"   链接：{news['link']}",
                    ""
                ])
        else:
            lines.append("暂无新闻\n")
        
        lines.extend([
            "---",
            "🤖 由 AI 生成 | OpenClaw",
            f"⏰ 时间：{datetime.now().strftime('%H:%M')}"
        ])
        
        return "\n".join(lines)

def main():
    collector = NewsCollector()
    collector.collect_all()
    message = collector.format_message()
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)

if __name__ == "__main__":
    main()
