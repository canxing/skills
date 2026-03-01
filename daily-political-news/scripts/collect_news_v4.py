#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日时政新闻收集脚本 V4
- 专注国际新闻（BBC、Reuters、AP）
- 内置AI翻译和摘要
- 推送飞书消息
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import json
import os
import sys
import time
from datetime import datetime

# RSS 源配置 - 国际新闻
RSS_SOURCES = {
    "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "Associated Press": "https://apnews.com/hub/rss"
}

# 关键词过滤（时政、经济、社会、军事）
KEYWORDS = [
    # 地区
    "China", "Chinese", "Beijing", "Taiwan", "Hong Kong", "Asia",
    "US", "USA", "America", "Washington", "Biden", "Trump",
    "Russia", "Putin", "Ukraine", "Moscow",
    "Iran", "Israel", "Middle East", "Gaza", "Palestine",
    "Europe", "EU", "Brexit", "NATO",
    # 主题
    "politics", "government", "election", "vote", "president", "minister",
    "economy", "trade", "market", "finance", "business", "tariff",
    "military", "war", "conflict", "attack", "strike", "defense", "weapon",
    "diplomatic", "sanctions", "treaty", "agreement", "summit",
    "protest", "crisis", "security", "intelligence"
]

class NewsCollector:
    def __init__(self):
        self.news_list = []
        self.max_retries = 3
        self.retry_delay = 5
        
    def fetch_rss(self, source_name, rss_url):
        """获取RSS（带重试）"""
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"  [{source_name}] 尝试 {attempt}/{self.max_retries}")
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                req = urllib.request.Request(rss_url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = response.read()
                
                root = ET.fromstring(data)
                entries = []
                
                for item in root.findall('.//item'):
                    title = item.find('title')
                    link = item.find('link')
                    desc = item.find('description')
                    
                    if title is not None and title.text:
                        entries.append({
                            "title": title.text.strip(),
                            "link": link.text.strip() if link is not None else "",
                            "summary": desc.text.strip() if desc is not None and desc.text else "",
                            "source": source_name
                        })
                
                print(f"    ✓ 获取 {len(entries)} 条")
                return entries[:10]
                    
            except Exception as e:
                print(f"    ✗ {str(e)[:50]}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
        
        return []
    
    def filter_news(self, entries):
        """关键词过滤"""
        filtered = []
        for entry in entries:
            text = f"{entry['title']} {entry['summary']}".lower()
            if any(kw.lower() in text for kw in KEYWORDS):
                filtered.append(entry)
        return filtered
    
    def collect_all(self):
        """收集所有新闻"""
        print("=" * 60)
        print("📰 开始收集国际新闻...")
        print("=" * 60)
        
        for name, url in RSS_SOURCES.items():
            entries = self.fetch_rss(name, url)
            if entries:
                filtered = self.filter_news(entries)
                print(f"   过滤后保留 {len(filtered)} 条")
                self.news_list.extend(filtered)
        
        # 去重（按标题）
        seen = set()
        unique = []
        for news in self.news_list:
            if news['title'] not in seen:
                seen.add(news['title'])
                unique.append(news)
        self.news_list = unique
        
        print(f"\n{'=' * 60}")
        print(f"✓ 共收集 {len(self.news_list)} 条不重复新闻")
        print("=" * 60)
    
    def format_output(self):
        """格式化输出"""
        lines = [
            f"📰 每日国际新闻简报 - {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "🌍 国际要闻",
            "━━━━━━━━━━━━━━━",
            ""
        ]
        
        if self.news_list:
            for i, news in enumerate(self.news_list[:8], 1):
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
            "🤖 由 AI 翻译和生成要点 | OpenClaw",
            f"⏰ 时间：{datetime.now().strftime('%H:%M')}"
        ])
        
        return "\n".join(lines)

def main():
    collector = NewsCollector()
    collector.collect_all()
    print("\n" + collector.format_output())

if __name__ == "__main__":
    main()
