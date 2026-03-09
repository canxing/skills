#!/usr/bin/env python3
"""
YouTrack 工作总结生成器
从 YouTrack API 获取工作时间记录并生成结构化报告
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timedelta
from collections import defaultdict


class YouTrackSummary:
    """YouTrack 工作报告生成器"""

    def __init__(self, token=None, base_url=None):
        """初始化，读取配置"""
        self.token = token or os.getenv('SUPERMAP_YOUTRACK_TOKEN')
        if not self.token:
            print("错误: 未设置 SUPERMAP_YOUTRACK_TOKEN 环境变量")
            print("请设置环境变量: export SUPERMAP_YOUTRACK_TOKEN='your-token-here'")
            sys.exit(1)
        self.base_url = base_url or os.getenv('YOUTRACK_URL', 'http://yt.ispeco.com:8099')
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
    
    def parse_time_range(self, time_range_str):
        """解析时间范围字符串"""
        time_range_str = time_range_str.strip()
        now = datetime.now()
        
        # 处理相对时间
        if time_range_str == '本月':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
            return start, end
        
        elif time_range_str == '上个月':
            first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = first_day_this_month
            if end.month == 1:
                start = end.replace(year=end.year - 1, month=12)
            else:
                start = end.replace(month=end.month - 1)
            return start, end
        
        elif time_range_str == '上周':
            today = now.date()
            monday = today - timedelta(days=today.weekday() + 7)
            sunday = monday + timedelta(days=6)
            start = datetime.combine(monday, datetime.min.time())
            end = datetime.combine(sunday, datetime.max.time())
            return start, end
        
        # 处理月份格式：2026-01 或 2026年1月
        import re
        month_match = re.match(r'(\d{4})[\-年](\d{1,2})月?$', time_range_str)
        if month_match:
            year = int(month_match.group(1))
            month = int(month_match.group(2))
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
            return start, end
        
        # 处理日期范围：2026-01-01到2026-01-31
        range_match = re.match(r'(\d{4}-\d{2}-\d{2})[到~\-](\d{4}-\d{2}-\d{2})', time_range_str)
        if range_match:
            start = datetime.strptime(range_match.group(1), '%Y-%m-%d')
            end = datetime.strptime(range_match.group(2), '%Y-%m-%d') + timedelta(days=1)
            return start, end
        
        raise ValueError(f"无法解析时间范围: {time_range_str}")
    
    def get_current_user_id(self):
        """获取当前用户ID"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/me",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            user_data = response.json()
            return user_data.get('id', '1-61')  # 默认使用已知ID
        except Exception as e:
            print(f"获取用户信息失败，使用默认ID: {e}")
            return '1-61'
    
    def fetch_work_items(self, start_date, end_date):
        """从 YouTrack API 获取工作项"""
        # 转换为毫秒时间戳
        start_ms = int(start_date.timestamp() * 1000)
        end_ms = int(end_date.timestamp() * 1000)
        
        # 获取当前用户ID
        author_id = self.get_current_user_id()
        
        fields = "id,date,duration(minutes,presentation),issue(id,idReadable,summary),text"
        all_items = []
        skip = 0
        page_size = 50
        
        while True:
            params = {
                "author": author_id,
                "fields": fields,
                "$top": page_size,
                "$skip": skip,
                "start": start_ms,
                "end": end_ms
            }
            
            try:
                response = requests.get(
                    f"{self.base_url}/api/workItems",
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                items = response.json()
                
                if not items:
                    break
                
                all_items.extend(items)
                
                if len(items) < page_size:
                    break
                    
                skip += page_size
                
            except requests.exceptions.RequestException as e:
                print(f"API 调用失败: {e}")
                sys.exit(1)
        
        return all_items
    
    def get_task_parent(self, task_id):
        """从 API 获取任务的父任务"""
        url = f"{self.base_url}/api/issues/{task_id}/links"
        params = {
            "fields": "id,direction,linkType(id,directed,sourceToTarget,targetToSource,aggregation),trimmedIssues(id,idReadable,summary)"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            links = response.json()
            
            for link in links:
                link_type = link.get('linkType', {})
                direction = link.get('direction', '')
                trimmed_issues = link.get('trimmedIssues', [])
                
                source_to_target = link_type.get('sourceToTarget', '')
                target_to_source = link_type.get('targetToSource', '')
                
                # 检查父子关系
                is_parent_child = ("parent for" in source_to_target or 
                                  "subtask of" in target_to_source)
                
                if is_parent_child and direction == 'INWARD' and trimmed_issues:
                    return {
                        'id': trimmed_issues[0].get('idReadable', ''),
                        'summary': trimmed_issues[0].get('summary', '')
                    }
            
            return None
            
        except Exception as e:
            print(f"获取任务 {task_id} 的父任务失败: {e}")
            return None
    
    def analyze_parent_tasks(self, task_ids):
        """分析多个任务的父任务，返回最常见的父任务"""
        parent_counts = defaultdict(lambda: {'count': 0, 'info': None})
        
        for task_id in task_ids:
            parent = self.get_task_parent(task_id)
            if parent:
                parent_id = parent['id']
                parent_counts[parent_id]['count'] += 1
                parent_counts[parent_id]['info'] = parent
        
        if not parent_counts:
            return None
        
        # 选择出现次数最多的父任务
        most_common = max(parent_counts.items(), key=lambda x: x[1]['count'])
        return most_common[1]['info']
    
    def group_by_task(self, work_items):
        """按任务分组工作项"""
        tasks = defaultdict(lambda: {
            'work_items': [],
            'dates': set(),
            'total_minutes': 0
        })
        
        for item in work_items:
            issue = item.get('issue', {})
            task_id = issue.get('idReadable', '')
            
            if not task_id:
                continue
            
            duration = item.get('duration', {})
            minutes = duration.get('minutes', 0)
            date_ts = item.get('date', 0)
            date = datetime.fromtimestamp(date_ts / 1000).strftime('%Y-%m-%d')
            
            tasks[task_id]['work_items'].append({
                'date': date,
                'minutes': minutes,
                'text': item.get('text', '')
            })
            tasks[task_id]['dates'].add(date)
            tasks[task_id]['total_minutes'] += minutes
            tasks[task_id]['summary'] = issue.get('summary', '')
            tasks[task_id]['id'] = task_id
        
        return tasks
    
    def generate_report(self, time_range_str, work_items):
        """生成工作报告"""
        if not work_items:
            return "指定时间范围内无工作记录。"
        
        # 按任务分组
        tasks = self.group_by_task(work_items)
        
        # 分析父任务
        task_ids = list(tasks.keys())
        parent_task = self.analyze_parent_tasks(task_ids)
        
        # 生成报告
        lines = []
        lines.append("# YouTrack 工作内容总结")
        lines.append("")
        lines.append(f"**时间范围**: {time_range_str}")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        
        # 父任务标题
        if parent_task:
            lines.append(f"**{parent_task['id']}: {parent_task['summary']}**:")
        else:
            lines.append("**工作任务汇总**:")
        lines.append("")
        
        # 子任务详情
        total_hours = 0
        total_days = set()
        
        for task_id, task_data in sorted(tasks.items()):
            hours = task_data['total_minutes'] / 60
            total_hours += hours
            days = sorted(task_data['dates'])
            total_days.update(days)
            
            lines.append(f"  **{task_id}: {task_data['summary']}**")
            lines.append(f"    - 工作时间: {hours:.1f}小时")
            lines.append(f"    - 工作天数: {len(days)}天 ({', '.join(days)})")
            lines.append(f"    - 工作项数: {len(task_data['work_items'])}个")
            lines.append(f"    - 任务链接: {self.base_url}/issue/{task_id}")
            
            # 工作内容（取第一个非空的）
            texts = [wi['text'] for wi in task_data['work_items'] if wi['text']]
            if texts:
                lines.append(f"    - 工作内容: {texts[0]}")
            lines.append("")
        
        # 汇总
        lines.append("## 📊 汇总信息")
        lines.append("")
        if parent_task:
            lines.append(f"- **父任务**: {parent_task['id']}: {parent_task['summary']}")
        lines.append(f"- **子任务数**: {len(tasks)} 个")
        lines.append(f"- **工作项数**: {len(work_items)} 个")
        lines.append(f"- **总工作时间**: {total_hours:.1f} 小时")
        lines.append(f"- **工作天数**: {len(total_days)} 天")
        
        return '\n'.join(lines)
    
    def run(self, time_range_str):
        """运行总结流程"""
        print(f"正在分析时间范围: {time_range_str}")
        
        # 解析时间
        start_date, end_date = self.parse_time_range(time_range_str)
        print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        
        # 获取数据
        print("正在获取工作项数据...")
        work_items = self.fetch_work_items(start_date, end_date)
        print(f"获取到 {len(work_items)} 个工作项")
        
        # 生成报告
        report = self.generate_report(time_range_str, work_items)
        
        return report


def main():
    parser = argparse.ArgumentParser(description='YouTrack 工作报告生成器')
    parser.add_argument('time_range', help='时间范围，如 "2026-01"、"本月"、"上周"')
    parser.add_argument('--token', help='API Token (默认从 SUPERMAP_YOUTRACK_TOKEN 环境变量获取)')
    parser.add_argument('--base-url', help='YouTrack API 地址')

    args = parser.parse_args()

    summary = YouTrackSummary(
        token=args.token,
        base_url=args.base_url
    )

    report = summary.run(args.time_range)
    print(report)


if __name__ == '__main__':
    main()
