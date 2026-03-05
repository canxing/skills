#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻收集脚本 V6 (合并版)
- 国际新闻：BBC、Reuters
- AI科技：36氪、阮一峰博客、量子位
- 国内时政：新华网
- 自动推送到飞书
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import json
import os
import sys
import time
from datetime import datetime

# ============ RSS 源配置 ============

RSS_SOURCES = {
    "国际": {
        "BBC World": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "Reuters": "http://feeds.reuters.com/reuters/topNews"
    },
    "AI科技": {
        "阮一峰博客": "https://www.ruanyifeng.com/blog/atom.xml",
        "量子位": "https://www.qbitai.com/feed",
        "机器之心": "https://www.jiqizhixin.com/rss",
        "InfoQ AI": "https://www.infoq.cn/feed/ai"
    },
    "国内": {
        "新华网-时政": "http://www.xinhuanet.com/politics/news_politics.xml",
        "人民日报": "http://paper.people.com.cn/rmrb/rss.xml"
    }
}

# ============ 关键词配置 ============

KEYWORDS = {
    "国际": [
        "China", "Chinese", "Beijing", "Taiwan", "Hong Kong", "Asia",
        "US", "USA", "America", "Washington", "Biden", "Trump",
        "Russia", "Putin", "Ukraine", "Moscow",
        "Iran", "Israel", "Middle East", "Gaza", "Palestine",
        "Europe", "EU", "NATO",
        "politics", "government", "election", "president", "minister",
        "economy", "trade", "market", "finance", "business",
        "military", "war", "conflict", "attack", "defense",
        "diplomatic", "sanctions", "treaty", "summit",
        "crisis", "security"
    ],
    "AI科技": [
        "人工智能", "AI", "大模型", "ChatGPT", "DeepSeek", "Claude", "Gemini",
        "机器学习", "深度学习", "神经网络", "算法", "算力",
        "芯片", "GPU", "NPU", "OpenAI", "LLM", "AIGC",
        "生成式AI", "多模态", "智能体", "Agent",
        "自动驾驶", "机器人", "人形机器人", "具身智能",
        "artificial intelligence", "machine learning", "deep learning",
        "large language model", "generative AI", "multimodal",
        "autonomous driving", "robotics", "tech", "technology"
    ],
    "国内": [
        "中国", "习近平", "李克强", "国务院", "全国人大",
        "政治", "经济", "社会", "军事", "外交",
        "疫情", "防控", "疫苗", "健康",
        "发展", "改革", "政策", "会议"
    ]
}

# ============ 核心类 ============

class NewsCollector:
    def __init__(self):
        self.news_data = {"国际": [], "AI科技": [], "国内": []}
        self.max_retries = 3
        self.retry_delay = 5
        
    def fetch_rss(self, source_name, rss_url, category):
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
                
                # 解析XML
                root = ET.fromstring(data)
                entries = []
                
                # RSS 2.0 格式
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
                
                # Atom 格式 (如阮一峰博客)
                atom_ns = '{http://www.w3.org/2005/Atom}'
                for entry in root.findall(f'.//{atom_ns}entry'):
                    title = entry.find(f'{atom_ns}title')
                    link = entry.find(f'{atom_ns}link')
                    summary = entry.find(f'{atom_ns}summary')
                    content = entry.find(f'{atom_ns}content')
                    updated = entry.find(f'{atom_ns}updated')
                    
                    if title is not None and title.text:
                        link_url = link.get('href') if link is not None else ""
                        desc_text = ""
                        if summary is not None and summary.text:
                            desc_text = summary.text.strip()
                        elif content is not None and content.text:
                            desc_text = content.text.strip()[:300]
                        
                        entries.append({
                            "title": title.text.strip(),
                            "link": link_url,
                            "summary": desc_text,
                            "published": updated.text if updated is not None else "",
                            "source": source_name,
                            "category": category
                        })
                
                if entries:
                    print(f"    ✓ 成功获取 {len(entries)} 条")
                    return entries[:10]
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
    
    def filter_news(self, entries, category):
        """根据关键词过滤新闻"""
        keywords = KEYWORDS.get(category, [])
        filtered = []
        for entry in entries:
            text = f"{entry['title']} {entry['summary']}".lower()
            if any(kw.lower() in text for kw in keywords):
                filtered.append(entry)
        return filtered
    
    def collect_all(self):
        """收集所有新闻源"""
        print("=" * 60)
        print("📰 开始收集新闻...")
        print("=" * 60)
        
        for category in RSS_SOURCES.keys():
            print(f"\n【{category}新闻源】")
            for name, url in RSS_SOURCES[category].items():
                entries = self.fetch_rss(name, url, category)
                if entries:
                    filtered = self.filter_news(entries, category)
                    print(f"   过滤后保留 {len(filtered)} 条")
                    self.news_data[category].extend(filtered)
        
        # 去重
        for category in self.news_data:
            seen = set()
            unique = []
            for news in self.news_data[category]:
                if news['title'] not in seen:
                    seen.add(news['title'])
                    unique.append(news)
            self.news_data[category] = unique
        
        total = sum(len(v) for v in self.news_data.values())
        print(f"\n{'=' * 60}")
        print(f"✓ 收集完成：共 {total} 条")
        print(f"  - 国际: {len(self.news_data['国际'])} 条")
        print(f"  - AI科技: {len(self.news_data['AI科技'])} 条")
        print(f"  - 国内: {len(self.news_data['国内'])} 条")
        print("=" * 60)
    
    def format_message(self):
        """格式化飞书消息"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        lines = [f"📰 每日新闻简报 - {today}", ""]
        
        # 国内新闻
        domestic = self.news_data.get("国内", [])
        if domestic:
            lines.extend(["🇨🇳 国内要闻", "━━━━━━━━━━━━━━━", ""])
            for i, news in enumerate(domestic[:5], 1):
                lines.extend([
                    f"{i}. 【{news['title']}】",
                    f"   来源：{news['source']}",
                    f"   链接：{news['link']}",
                    ""
                ])
        
        # 国际新闻
        international = self.news_data.get("国际", [])
        if international:
            lines.extend(["🌍 国际要闻", "━━━━━━━━━━━━━━━", ""])
            for i, news in enumerate(international[:8], 1):
                lines.extend([
                    f"{i}. 【{news['title']}】",
                    f"   来源：{news['source']}",
                    f"   链接：{news['link']}",
                    ""
                ])
        
        # AI科技新闻 - 按来源分组，每个来源最多3条
        ai_tech = self.news_data.get("AI科技", [])
        if ai_tech:
            lines.extend(["🔬 AI科技", "━━━━━━━━━━━━━━━", ""])
            
            # 按来源分组
            from collections import defaultdict
            source_groups = defaultdict(list)
            for news in ai_tech:
                source_groups[news['source']].append(news)
            
            # 每个来源最多显示3条
            for source_name, news_list in source_groups.items():
                lines.append(f"📌 {source_name}")
                for i, news in enumerate(news_list[:3], 1):
                    lines.extend([
                        f"  {i}. 【{news['title']}】",
                        f"     链接：{news['link']}",
                        ""
                    ])
                    if news['summary']:
                        summary = news['summary'].replace('<p>', '').replace('</p>', '').replace('<br>', '\n').replace('&quot;', '"')[:120]
                        if summary:
                            lines.append(f"     📝 {summary}...")
                            lines.append("")
        
        lines.extend([
            "---",
            "🤖 由 OpenClaw 自动生成",
            f"⏰ 时间：{datetime.now().strftime('%H:%M')}"
        ])
        
        return "\n".join(lines)

def main():
    collector = NewsCollector()
    collector.collect_all()
    message = collector.format_message()
    
    # 输出到控制台（供OpenClaw捕获并发送）
    print("\n" + "="*60)
    print("FEISHU_MESSAGE_START")
    print(message)
    print("FEISHU_MESSAGE_END")
    print("="*60)

if __name__ == "__main__":
    main()
