"""PreToolUse hook: project boundary gate — block writes outside project directory.
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
        # Extract file path from write operations
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        if not file_path:
            print("{}")
            sys.exit(0)

        # Resolve to absolute path
        abs_path = os.path.abspath(file_path).replace("\\", "/")

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if not project_dir:
            print("{}")
            sys.exit(0)

        # Read CLAUDE.md to find the declared project directory
        claude_md = os.path.join(project_dir, "CLAUDE.md")
        if not os.path.exists(claude_md):
            print("{}")
            sys.exit(0)

        with open(claude_md, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Extract project directory from CLAUDE.md
        # Pattern 1: "项目目录：d:/path/"
        m = re.search(r"项目目录[：:]s*(S+)", content)
        if not m:
            # Pattern 2: "操作范围：限定 d:/path/"
            m = re.search(r"操作范围[：:]s*限定s+(S+)", content)
        if not m:
            # No boundary defined → allow
            print("{}")
            sys.exit(0)

        declared_dir = m.group(1).rstrip("/").replace("\\", "/")

        # Allow writes to CLAUDE.md and CLAUDE.d/ even if boundary is otherwise
        # (these are the skill's own config files)
        if abs_path.endswith("/CLAUDE.md") or "/CLAUDE.d/" in abs_path:
            print("{}")
            sys.exit(0)

        # Check if write target is within declared project directory
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
