"""PreToolUse hook: project boundary gate — block writes outside project directory.
No CLAUDE.md → deny (project boundary not declared, complete S1-S2 first).
Adapted from hook-development's validate-write.sh path traversal / system dir checks.
Fail-open: any error → exit 0 (allow operation)."""
import sys
import json
import os
import re


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
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        if not file_path:
            print("{}")
            sys.exit(0)

        abs_path = os.path.abspath(file_path).replace("\\", "/")

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if not project_dir:
            print("{}")
            sys.exit(0)

        claude_md = os.path.join(project_dir, "CLAUDE.md")

        # CLAUDE.md and .claude/ always exempt
        if abs_path == os.path.abspath(claude_md).replace("\\", "/"):
            print("{}")
            sys.exit(0)
        claude_dir = os.path.join(project_dir, ".claude")
        if abs_path.startswith(os.path.abspath(claude_dir).replace("\\", "/") + "/"):
            print("{}")
            sys.exit(0)

        # Gate 1: No CLAUDE.md → no boundary declared → deny
        if not os.path.exists(claude_md):
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                },
                "systemMessage": (
                    "No CLAUDE.md found — project boundary not declared. "
                    "Complete S2 (project boundary) and write CLAUDE.md before "
                    "writing any code file outside .claude/."
                ),
            }
            print(json.dumps(result))
            sys.exit(2)

        with open(claude_md, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Extract project directory from CLAUDE.md
        m = re.search(r"项目目录[：:]\s*(\S+)", content)
        if not m:
            m = re.search(r"操作范围[：:]\s*限定\s+(\S+)", content)
        if not m:
            print("{}")
            sys.exit(0)

        declared_dir = m.group(1).rstrip("/").replace("\\", "/")

        if abs_path.endswith("/CLAUDE.md") or "/CLAUDE.d/" in abs_path:
            print("{}")
            sys.exit(0)

        if not abs_path.startswith(declared_dir + "/"):
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                },
                "systemMessage": (
                    f"Write denied: {abs_path} is outside project directory "
                    f"{declared_dir}. All writes must stay within the declared "
                    f"project boundary. Use the project directory for all files."
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
