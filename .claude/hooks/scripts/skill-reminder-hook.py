#!/usr/bin/env python3
"""
Skill Reminder Hook
====================
当加载 skill 后，在用户每次提问时提醒按照 skill 流程进行。

跨平台支持：Linux 使用 fcntl，Windows 使用 msvcrt
"""

import sys
import json
import time
import os
import traceback
from pathlib import Path

# 跨平台文件锁
try:
    import fcntl  # Linux/Unix/Mac
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

try:
    import msvcrt  # Windows only
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

STATE_FILE = "skill-sessions.json"
REMINDER_TEXT = "***重要***: 请按照已加载的 skill 流程进行"


def get_state_path():
    script_dir = Path(__file__).parent
    hooks_dir = script_dir.parent
    return hooks_dir / "state" / STATE_FILE


def load_session_states():
    state_path = get_state_path()
    if not state_path.exists():
        return {}
    for _ in range(10):  # 重试直到成功
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                # 跨平台文件锁（共享锁）
                try:
                    if HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    elif HAS_MSVCRT:
                        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                except (IOError, OSError):
                    # 锁失败时继续，仅打印警告
                    pass

                data = json.load(f)

                # 解锁
                try:
                    if HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    elif HAS_MSVCRT:
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except:
                    pass

                return data
        except (json.JSONDecodeError, IOError, OSError):
            time.sleep(0.01)
    return {}


def save_session_states(states):
    state_path = get_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_path.parent / f".{state_path.name}.tmp"

    try:
        # 先写临时文件
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(states, f, ensure_ascii=False, indent=2)
            f.flush()
            # 跨平台文件锁（排他锁）
            try:
                if HAS_FCNTL:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                elif HAS_MSVCRT:
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
            except (IOError, OSError):
                # 锁失败时继续
                pass
        # atomic rename
        tmp_path.replace(state_path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def mark_session_used_skill(session_id):
    states = load_session_states()
    states[session_id] = {"used_skill": True}
    save_session_states(states)


def has_session_used_skill(session_id):
    states = load_session_states()
    return states.get(session_id, {}).get("used_skill", False)


def main():
    try:
        stdin_content = sys.stdin.read().strip()
        if not stdin_content:
            sys.exit(0)

        input_data = json.loads(stdin_content)
        event_name = input_data.get("hook_event_name", "")
        session_id = input_data.get("session_id", "")

        if not session_id:
            sys.exit(0)

        # PostToolUse + Skill tool -> 记录该 session 已调用 skill
        # (直接使用 Skill 工具时触发)
        if event_name == "PostToolUse":
            tool_name = input_data.get("tool_name", "")
            if tool_name == "Skill":
                mark_session_used_skill(session_id)
                sys.exit(0)

        # InstructionsLoaded -> 记录该 session 已加载 skill
        # (通过 slash command 加载 skill 时触发，如 /superpowers:brainstorm)
        if event_name == "InstructionsLoaded":
            # InstructionsLoaded 事件表示 skill/指令已加载
            mark_session_used_skill(session_id)
            sys.exit(0)

        # UserPromptSubmit -> 检查并注入提醒
        if event_name == "UserPromptSubmit":
            if has_session_used_skill(session_id):
                sys.stdout.write(REMINDER_TEXT)
                sys.stdout.flush()
            sys.exit(0)

        # PostCompact -> 检查并注入提醒
        if event_name == "PostCompact":
            if has_session_used_skill(session_id):
                sys.stdout.write(REMINDER_TEXT)
                sys.stdout.flush()
            sys.exit(0)

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON input: {e}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
