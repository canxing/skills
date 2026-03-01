#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日时政新闻收集脚本（简化版，仅使用标准库）
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import json
import os
import sys
import time
from datetime import datetime

# RSS源配置
RSS_SOURCES = {
    "国内": {},  # 国内RSS需要验证
    "国际": {
        "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
        "Reuters": "http://feeds.reuters.com/reuters/topNews"
    }
}

# 关键词过滤
KEYWORDS = [
    "politics", "policy", "government", "diplomatic", "summit", "election",
    "economy", "finance", "market", "trade", "investment", "business",
    "military", "defense", "army", "weapon", "conflict", "war", "security",
    "中国", "美国", "俄罗斯", "欧盟", "中东", "朝鲜", "台湾"
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
                
                # 设置请求头
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                req = urllib.request.Request(rss_url, headers=headers)
                
                # 获取数据
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read()
                
                # 解析XML
                root = ET.fromstring(data)
                
                # 提取条目
                entries = []
                # RSS 2.0 格式
                for item in root.findall('.//item'):
                    title = item.find('title')
                    link = item.find('link')
                    desc = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    if title is not None:
                        news_item = {
                            "title": title.text or "",
                            "link": link.text if link is not None else "",
                            "summary": desc.text if desc is not None else "",
                            "published": pub_date.text if pub_date is not None else "",
                            "source": source_name,
                            "category": category
                        }
                        entries.append(news_item)
                
                if entries:
                    print(f"    ✓ 成功获取 {len(entries)} 条")
                    return entries[:10]  # 最多10条
                else:
                    print(f"    ⚠️ 未获取到内容")
                    return []
                    
            except Exception as e:
                print(f"    ✗ 错误: {str(e)[:80]}")
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
            if any(keyword.lower() in text for keyword in KEYWORDS):
                filtered.append(entry)
        return filtered
    
    def ai_translate_and_summarize(self, title, summary, is_foreign=False):
        """AI翻译标题并生成要点（模拟）"""
        translated_title = title
        if is_foreign:
            translated_title = f"[待翻译] {title}"
        
        # 从摘要中提取关键句子作为要点
        key_points = []
        sentences = summary.replace('。', '.').split('.') if summary else []
        for sent in sentences[:3]:
            sent = sent.strip()
            if len(sent) > 20:
                key_points.append(sent[:100] + "..." if len(sent) > 100 else sent)
        
        if len(key_points) < 3:
            key_points.extend([
                "相关方正在评估事件影响和发展趋势",
                "国际社会对此保持密切关注",
                "后续进展有待进一步观察"
            ])
        
        return {
            "translated_title": translated_title,
            "key_points": key_points[:3]
        }
    
    def collect_all(self):
        """收集所有新闻源"""
        print("=" * 60)
        print("📰 开始收集新闻...")
        print("=" * 60)
        
        # 收集国际新闻（国内源需要单独验证）
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
                
                display_title = news['title']
                if ai_result['translated_title'] != news['title']:
                    display_title = f"{ai_result['translated_title']}\n   原文：{news['title']}"
                
                message_lines.extend([
                    f"{i}. 【{display_title}】",
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

def main():
    collector = NewsCollector()
    collector.collect_all()
    message = collector.format_message()
    print("\n" + "=" * 60)
    print("📤 生成的飞书消息：")
    print("=" * 60)
    print(message)
    print("=" * 60)

if __name__ == "__main__":
    main()
