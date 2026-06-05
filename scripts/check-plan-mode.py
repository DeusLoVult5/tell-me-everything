"""PreToolUse hook: scale declaration gate — block writes without 【规模：】declaration.
Any mode (PLAN or IMPLEMENT) without a scale declaration → deny.
CLAUDE.md writes are exempted so Agent can add scale declarations.
Adapted from hookify's pretooluse.py and hook-development's validate-write.sh.
Fail-open: any error → exit 0 (allow operation)."""
import sys
import json
import os


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        print("{}")
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        print("{}")
        sys.exit(0)

    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if not project_dir:
            print("{}")
            sys.exit(0)

        claude_md = os.path.join(project_dir, "CLAUDE.md")
        if not os.path.exists(claude_md):
            print("{}")
            sys.exit(0)

        # Check if target is CLAUDE.md → exempt (Agent needs to write scale declarations)
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        if file_path:
            abs_path = os.path.abspath(file_path).replace("\\", "/")
            claude_abs = os.path.abspath(claude_md).replace("\\", "/")
            if abs_path == claude_abs:
                print("{}")
                sys.exit(0)

        with open(claude_md, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Gate: no scale declaration → deny (any mode)
        # Scale declaration is the only pass. Mode is auxiliary info.
        if "【规模：" not in content:
            current_mode = "PLAN" if "【当前模式：PLAN】" in content else "IMPLEMENT"
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                },
                "systemMessage": (
                    f"No scale declaration found (current mode: {current_mode}). "
                    "Before writing any non-CLAUDE.md file, add a scale declaration: "
                    "【规模：微量/小改动/中改动/大改动】+ 【预计改动：file1 / file2】+ 【验证方式：...】. "
                    "This prevents Agent from silently skipping the scale confirmation step."
                ),
            }
            print(json.dumps(result))
            sys.exit(2)

        print("{}")
        sys.exit(0)

    except Exception:
        print("{}")
        sys.exit(0)


if __name__ == "__main__":
    main()
