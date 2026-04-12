#!/usr/bin/env python3
"""
Check Docs Hook
===============
在 git commit 时检查文档是否有更新。

如果检测到技能目录下有 README.md 变更但没有同步更新根目录的 README.md，
则输出警告信息并以退出码 2 阻止 commit（除非用户强制跳过）。
"""

import sys
import json
import subprocess
from pathlib import Path

DOCS_FILES = ["README.md", "SKILL.md", "CLAUDE.md"]


def get_changed_docs_from_index():
    """
    获取已暂存文档变更中，属于 skills/*/ 子目录的文件列表。

    Returns:
        set: 变更的技能目录名集合，如 {"skill-name", "another-skill"}
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return set()

    changed_files = result.stdout.strip().split("\n")
    skills_dirs = set()

    for f in changed_files:
        if not f:
            continue
        parts = Path(f).parts
        # 匹配 skills/<skill-name>/<doc-file> 结构
        if len(parts) >= 3 and parts[0] == "skills" and parts[2] in DOCS_FILES:
            skills_dirs.add(parts[1])

    return skills_dirs


def get_skills_without_readme_update(skills_dirs):
    """
    检查每个变更了文档的技能目录，看其 README.md 是否有变更。

    如果技能的 README.md 有变更但根目录 README.md 中没有列出该技能，则返回该技能名。

    Returns:
        list: 需要更新根 README.md 的技能名列表
    """
    root_readme = Path("README.md")
    if not root_readme.exists():
        return []

    root_content = root_readme.read_text(encoding="utf-8")
    missing_skills = []

    for skill in skills_dirs:
        skill_readme = Path(f"skills/{skill}/README.md")
        if skill_readme.exists():
            # 检查根 README.md 是否包含该技能的链接
            # 简单检查：是否包含 skills/{skill} 或 [{skill}]
            if f"skills/{skill}" not in root_content and f"[{skill}]" not in root_content:
                missing_skills.append(skill)

    return missing_skills


def main():
    stdin_content = sys.stdin.read().strip()
    if not stdin_content:
        sys.exit(0)

    try:
        input_data = json.loads(stdin_content)
    except json.JSONDecodeError:
        sys.exit(0)

    hook_event_name = input_data.get("hook_event_name", "")
    tool_name = input_data.get("tool_name", "")

    # 只在 PreToolUse 的 Bash 命令中拦截 git commit
    if hook_event_name != "PreToolUse" or tool_name != "Bash":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # 检查是否是 git commit 命令（排除 git commit --dry-run 等）
    if "git" not in command or "commit" not in command:
        sys.exit(0)

    # 获取已暂存的文档变更
    changed_skills = get_changed_docs_from_index()
    if not changed_skills:
        sys.exit(0)

    # 检查是否有技能的 README.md 变更但未同步到根 README.md
    missing_updates = get_skills_without_readme_update(changed_skills)

    if missing_updates:
        skills_list = ", ".join(f"`{s}`" for s in missing_updates)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"以下技能的文档已更新，请同步到根目录 README.md：{skills_list}"
                ),
            }
        }
        print(json.dumps(output, ensure_ascii=False))
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
