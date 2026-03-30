#!/usr/bin/env python
"""集成测试：模拟真实 hook 流程"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = ".claude/hooks/scripts/skill-reminder-hook.py"
REMINDER_TEXT = "***重要***: 请按照已加载的 skill 流程进行"


def run_hook(event_json):
    """运行 hook 脚本，传入 stdin，返回 (stdout, returncode)"""
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH],
        input=json.dumps(event_json),
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent.parent  # repo root
    )
    return result.stdout, result.returncode


def read_state_file():
    """读取状态文件"""
    state_path = Path(".claude/hooks/state/skill-sessions.json")
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def clear_state_file():
    """清除状态文件"""
    state_path = Path(".claude/hooks/state/skill-sessions.json")
    if state_path.exists():
        state_path.unlink()


def test_posttooluse_skill_marks_session():
    """PostToolUse + Skill -> 记录 session 状态"""
    try:
        clear_state_file()
        session_id = "test-session-posttooluse"

        event = {
            "hook_event_name": "PostToolUse",
            "session_id": session_id,
            "tool_name": "Skill",
            "tool_input": {"skill": "superpowers:brainstorming"}
        }

        stdout, code = run_hook(event)
        assert code == 0, "Hook should exit with 0"

        states = read_state_file()
        assert session_id in states, "Session should be marked"
        assert states[session_id]["used_skill"]
    finally:
        clear_state_file()


def test_userpromptsubmit_without_skill_no_reminder():
    """UserPromptSubmit + 未使用 skill -> 无提醒"""
    try:
        clear_state_file()
        session_id = "test-session-no-skill"

        event = {
            "hook_event_name": "UserPromptSubmit",
            "session_id": session_id,
            "prompt": "Hello"
        }

        stdout, code = run_hook(event)
        assert stdout == "", "Should not output reminder for session without skill"
    finally:
        clear_state_file()


def test_userpromptsubmit_with_skill_injects_reminder():
    """PostToolUse + Skill 后 UserPromptSubmit -> 注入提醒"""
    try:
        clear_state_file()
        session_id = "test-session-with-skill"

        # 1. 先调用 Skill
        skill_event = {
            "hook_event_name": "PostToolUse",
            "session_id": session_id,
            "tool_name": "Skill",
            "tool_input": {"skill": "superpowers:brainstorming"}
        }
        run_hook(skill_event)

        # 2. 再提交 prompt
        prompt_event = {
            "hook_event_name": "UserPromptSubmit",
            "session_id": session_id,
            "prompt": "Hello"
        }
        stdout, code = run_hook(prompt_event)

        assert REMINDER_TEXT in stdout, f"Should inject reminder, got: {stdout}"
    finally:
        clear_state_file()


def test_postcompact_with_skill_injects_reminder():
    """PostToolUse + Skill 后 PostCompact -> 注入提醒"""
    try:
        clear_state_file()
        session_id = "test-session-postcompact"

        # 1. 先调用 Skill
        skill_event = {
            "hook_event_name": "PostToolUse",
            "session_id": session_id,
            "tool_name": "Skill",
            "tool_input": {"skill": "superpowers:brainstorming"}
        }
        run_hook(skill_event)

        # 2. 再执行 PostCompact
        compact_event = {
            "hook_event_name": "PostCompact",
            "session_id": session_id,
            "compact_summary": "..."
        }
        stdout, code = run_hook(compact_event)

        assert REMINDER_TEXT in stdout, f"Should inject reminder after PostCompact, got: {stdout}"
    finally:
        clear_state_file()


def test_multiple_sessions_isolated():
    """多 session 隔离测试"""
    try:
        clear_state_file()

        session_a = "test-session-a"
        session_b = "test-session-b"

        # Session A 调用 Skill
        run_hook({
            "hook_event_name": "PostToolUse",
            "session_id": session_a,
            "tool_name": "Skill",
            "tool_input": {"skill": "superpowers:brainstorming"}
        })

        # Session B 不调用 Skill
        # Session A 提交 prompt -> 应有提醒
        stdout_a, _ = run_hook({
            "hook_event_name": "UserPromptSubmit",
            "session_id": session_a,
            "prompt": "Hello A"
        })
        assert REMINDER_TEXT in stdout_a

        # Session B 提交 prompt -> 应无提醒
        stdout_b, _ = run_hook({
            "hook_event_name": "UserPromptSubmit",
            "session_id": session_b,
            "prompt": "Hello B"
        })
        assert stdout_b == "", f"Session B should not have reminder, got: {stdout_b}"
    finally:
        clear_state_file()


def test_instructionsloaded_marks_session():
    """InstructionsLoaded -> 记录 session 状态（slash command 加载 skill）"""
    try:
        clear_state_file()
        session_id = "test-session-instructionsloaded"

        event = {
            "hook_event_name": "InstructionsLoaded",
            "session_id": session_id
        }

        stdout, code = run_hook(event)
        assert code == 0, "Hook should exit with 0"

        states = read_state_file()
        assert session_id in states, "Session should be marked via InstructionsLoaded"
        assert states[session_id]["used_skill"]
    finally:
        clear_state_file()


if __name__ == "__main__":
    test_posttooluse_skill_marks_session()
    test_userpromptsubmit_without_skill_no_reminder()
    test_userpromptsubmit_with_skill_injects_reminder()
    test_postcompact_with_skill_injects_reminder()
    test_multiple_sessions_isolated()
    test_instructionsloaded_marks_session()
    print("All integration tests passed!")