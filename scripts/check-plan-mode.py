"""PreToolUse hook: M5 state gate — block writes when PLAN mode active without scale declaration.
Adapted from hookify's pretooluse.py and hook-development's validate-write.sh.
Fail-open: any error → exit 0 (allow operation)."""
import sys
import json
import os


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        # Fail-open: can't parse input → allow
        print("{}")
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        # Not a file write operation → allow
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

        with open(claude_md, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Check: PLAN mode without scale declaration → deny
        if "【当前模式：PLAN】" in content and "【规模：" not in content:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                },
                "systemMessage": (
                    "PLAN mode active without scale declaration. "
                    "User must confirm the change scale before writing files. "
                    "Say 'implement'(实现) to switch to IMPLEMENT mode, "
                    "or the user will confirm the scale first."
                ),
            }
            print(json.dumps(result))
            sys.exit(2)

        # Allow
        print(json.dumps({}))
        sys.exit(0)

    except Exception:
        # Fail-open: any unexpected error → allow
        print(json.dumps({}))
        sys.exit(0)


if __name__ == "__main__":
    main()
