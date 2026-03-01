#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日时政新闻收集脚本 V2
- 使用 RSSHub 作为统一源
- 集成 DeepSeek API 进行翻译和摘要
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

# RSS 源配置（使用 RSSHub）
RSS_SOURCES = {
    "国内": {
        "联合早报-中国": "https://rsshub.app/zaobao/realtime/china",
        "CNA-两岸": "https://rsshub.app/cna/news/aopl"
    },
    "国际": {
        "BBC-World": "https://rsshub.app/bbc/world",
        "Reuters-World": "https://rsshub.app/reuters/world"
    }
}

# 关键词过滤
KEYWORDS = [
    # 中文
    "中国", "美国", "俄罗斯", "欧盟", "中东", "朝鲜", "台湾", "香港",
    "政治", "经济", "军事", "外交", "贸易", "战争", "冲突", "制裁",
    "总统", "首相", "主席", "选举", "会议", "协议", "条约",
    # 英文
    "China", "US", "Russia", "EU", "Middle East", "Taiwan",
    "politics", "economy", "military", "diplomatic", "trade", "war", "conflict",
    "president", "prime minister", "election", "sanctions"
]

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 飞书配置
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

# ============ 核心类 ============

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
                
                if entries:
                    print(f"    ✓ 成功获取 {len(entries)} 条")
                    return entries[:8]  # 每个源最多8条
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
    
    def call_deepseek(self, prompt, max_tokens=500):
        """调用 DeepSeek API"""
        if not DEEPSEEK_API_KEY:
            print("    ⚠️ 未配置 DEEPSEEK_API_KEY，使用模拟数据")
            return None
        
        try:
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            req = urllib.request.Request(
                DEEPSEEK_API_URL,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"    ✗ DeepSeek API 错误: {str(e)[:60]}")
            return None
    
    def translate_title(self, title):
        """翻译标题"""
        prompt = f"将以下英文新闻标题翻译成中文，保持简洁准确：\n\n{title}\n\n只返回翻译结果，不要解释。"
        result = self.call_deepseek(prompt, max_tokens=100)
        return result if result else f"[翻译失败] {title}"
    
    def generate_key_points(self, title, summary):
        """生成要点"""
        content = f"标题：{title}\n摘要：{summary}" if summary else f"标题：{title}"
        prompt = f"根据以下新闻内容，提取3个关键要点（每点不超过50字）：\n\n{content}\n\n格式：\n1. 要点一\n2. 要点二\n3. 要点三"
        
        result = self.call_deepseek(prompt, max_tokens=200)
        if result:
            # 解析要点
            points = []
            for line in result.strip().split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    point = line.lstrip('0123456789.- ').strip()
                    if point:
                        points.append(point)
            return points[:3]
        
        return ["要点生成失败", "请查看原文链接", "获取详细信息"]
    
    def process_news(self, news, is_foreign=False):
        """处理单条新闻"""
        print(f"    处理: {news['title'][:40]}...")
        
        if is_foreign:
            translated = self.translate_title(news['title'])
            key_points = self.generate_key_points(news['title'], news['summary'])
            return {
                "translated_title": translated,
                "original_title": news['title'],
                "key_points": key_points
            }
        else:
            key_points = self.generate_key_points(news['title'], news['summary'])
            return {
                "translated_title": news['title'],
                "original_title": None,
                "key_points": key_points
            }
    
    def collect_all(self):
        """收集所有新闻源"""
        print("=" * 60)
        print("📰 开始收集新闻...")
        print("=" * 60)
        
        for category in ["国内", "国际"]:
            print(f"\n【{category}新闻源】")
            for name, url in RSS_SOURCES[category].items():
                entries = self.fetch_rss_with_retry(name, url, category)
                if entries:
                    filtered = self.filter_news(entries)
                    print(f"   过滤后保留 {len(filtered)} 条")
                    self.news_data[category].extend(filtered)
        
        total = len(self.news_data['国内']) + len(self.news_data['国际'])
        print(f"\n{'=' * 60}")
        print(f"✓ 收集完成：共 {total} 条（国内 {len(self.news_data['国内'])}，国际 {len(self.news_data['国际'])}）")
        print("=" * 60)
    
    def format_message(self):
        """格式化飞书消息"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        lines = [f"📰 每日新闻简报 - {today}", ""]
        
        # 国内新闻
        lines.extend(["🇨🇳 国内新闻", "━━━━━━━━━━━━━━━", ""])
        if self.news_data["国内"]:
            for i, news in enumerate(self.news_data["国内"][:5], 1):
                processed = self.process_news(news, is_foreign=False)
                lines.extend([
                    f"{i}. 【{news['title']}】",
                    f"   来源：{news['source']}",
                    f"   链接：{news['link']}",
                    "",
                    "   📋 要点："
                ])
                for point in processed['key_points']:
                    lines.append(f"   • {point}")
                lines.append("")
        else:
            lines.append("暂无符合条件的国内新闻\n")
        
        # 国际新闻
        lines.extend(["🇺🇸 国际新闻", "━━━━━━━━━━━━━━━", ""])
        if self.news_data["国际"]:
            for i, news in enumerate(self.news_data["国际"][:5], 1):
                processed = self.process_news(news, is_foreign=True)
                display = processed['translated_title']
                if processed['original_title']:
                    display += f"\n   原文：{processed['original_title']}"
                
                lines.extend([
                    f"{i}. 【{display}】",
                    f"   来源：{news['source']}",
                    f"   链接：{news['link']}",
                    "",
                    "   📋 要点："
                ])
                for point in processed['key_points']:
                    lines.append(f"   • {point}")
                lines.append("")
        else:
            lines.append("暂无符合条件的国际新闻\n")
        
        lines.extend([
            "---",
            "🤖 由 AI 自动生成 | 每天早上8点推送",
            f"⏰ 生成时间：{datetime.now().strftime('%H:%M')}"
        ])
        
        return "\n".join(lines)
    
    def send_to_feishu(self, message):
        """发送到飞书"""
        if not FEISHU_WEBHOOK:
            print("\n⚠️ 未配置 FEISHU_WEBHOOK，仅输出到控制台")
            print("=" * 60)
            print(message)
            print("=" * 60)
            return False
        
        try:
            payload = {
                "msg_type": "text",
                "content": {"text": message}
            }
            
            headers = {"Content-Type": "application/json"}
            req = urllib.request.Request(
                FEISHU_WEBHOOK,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get('code') == 0:
                    print("\n✓ 飞书消息发送成功")
                    return True
                else:
                    print(f"\n✗ 飞书发送失败: {result}")
                    return False
                    
        except Exception as e:
            print(f"\n✗ 发送失败: {str(e)}")
            return False

def main():
    collector = NewsCollector()
    collector.collect_all()
    message = collector.format_message()
    collector.send_to_feishu(message)

if __name__ == "__main__":
    main()
