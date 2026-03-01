#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日时政新闻收集脚本
收集国内外时政、经济、社会、军事新闻，AI翻译并生成要点
"""

import feedparser
import requests
import json
import os
import sys
from datetime import datetime
from urllib.parse import urljoin

# RSS源配置
RSS_SOURCES = {
    "国内": {
        "澎湃新闻": "https://www.thepaper.cn/rss.xml",
        "财新网": "https://www.caixin.com/rss.xml"
    },
    "国际": {
        "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
        "Reuters": "https://www.reuters.com/tools/rss",
        "Associated Press": "https://apnews.com/hub/rss"
    }
}

# 关键词过滤（时政、经济、社会、军事相关）
KEYWORDS = [
    # 时政
    "政治", "政策", "政府", "会议", "领导人", "外交", "关系",
    "politics", "policy", "government", "diplomatic", "summit",
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
        
    def fetch_rss(self, source_name, rss_url, category):
        """获取RSS源内容"""
        try:
            print(f"正在获取: {source_name}...")
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                print(f"  ⚠️ {source_name} RSS解析警告: {feed.bozo_exception}")
            
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
            
            print(f"  ✓ 获取到 {len(entries)} 条新闻")
            return entries
            
        except Exception as e:
            print(f"  ✗ {source_name} 获取失败: {str(e)}")
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
        这里使用简单的模拟实现，实际使用时调用LLM API
        """
        # TODO: 集成DeepSeek/OpenAI API进行翻译和摘要
        # 当前返回模拟数据用于演示
        
        translated_title = title
        if is_foreign:
            # 模拟翻译（实际应调用API）
            translated_title = f"[译文] {title}"
        
        # 模拟生成要点（实际应从正文提取）
        key_points = [
            "要点一：事件背景和影响范围",
            "要点二：相关方态度和反应",
            "要点三：后续发展和可能趋势"
        ]
        
        return {
            "translated_title": translated_title,
            "key_points": key_points
        }
    
    def collect_all(self):
        """收集所有新闻源"""
        print("=" * 50)
        print("开始收集新闻...")
        print("=" * 50)
        
        # 收集国内新闻
        print("\n【国内新闻源】")
        for name, url in RSS_SOURCES["国内"].items():
            entries = self.fetch_rss(name, url, "国内")
            filtered = self.filter_news(entries)
            self.news_data["国内"].extend(filtered)
        
        # 收集国际新闻
        print("\n【国际新闻源】")
        for name, url in RSS_SOURCES["国际"].items():
            entries = self.fetch_rss(name, url, "国际")
            filtered = self.filter_news(entries)
            self.news_data["国际"].extend(filtered)
        
        print("\n" + "=" * 50)
        print(f"收集完成：国内 {len(self.news_data['国内'])} 条，国际 {len(self.news_data['国际'])} 条")
        print("=" * 50)
    
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
            for i, news in enumerate(self.news_data["国内"][:5], 1):  # 最多显示5条
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
            for i, news in enumerate(self.news_data["国际"][:5], 1):  # 最多显示5条
                ai_result = self.ai_translate_and_summarize(
                    news["title"], news["summary"], is_foreign=True
                )
                
                message_lines.extend([
                    f"{i}. 【{ai_result['translated_title']}】",
                    f"   原文：{news['title']}",
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
        
        return "\n".join(message_lines)
    
    def send_to_feishu(self, message):
        """发送消息到飞书"""
        # TODO: 集成飞书API发送消息
        # 当前仅打印到控制台
        print("\n" + "=" * 50)
        print("飞书消息内容：")
        print("=" * 50)
        print(message)
        print("=" * 50)
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
