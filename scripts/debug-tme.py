"""Debug module helper for tell-me-everything.

Usage:
    python debug-tme.py init full              # Create timestamp dir + 5 placeholder files
    python debug-tme.py init session           # Create timestamp dir + 2 placeholder files
    python debug-tme.py init compliance        # Create timestamp dir + 2 placeholder files
    python debug-tme.py init files             # Create timestamp dir + 2 placeholder files
    python debug-tme.py init state             # Create timestamp dir + 2 placeholder files
    python debug-tme.py validate <dir>         # Check required files exist and are non-empty
"""

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path.cwd()
DEBUG_DIR = PROJECT_ROOT / ".claude" / "debug"

MODE_FILES = {
    "full": ["session.md", "raw.md", "compliance.md", "files.md", "state-snapshot.md"],
    "session": ["session.md", "raw.md"],
    "compliance": ["compliance.md", "raw.md"],
    "files": ["files.md", "raw.md"],
    "state": ["state-snapshot.md", "raw.md"],
}

PLACEHOLDER = "<!-- debug-tme: content pending -->\n"


def cmd_init(mode: str) -> None:
    if mode not in MODE_FILES:
        print(f"ERROR: unknown mode '{mode}'. Valid: {', '.join(MODE_FILES)}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out_dir = DEBUG_DIR / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    for filename in MODE_FILES[mode]:
        filepath = out_dir / filename
        filepath.write_text(PLACEHOLDER, encoding="utf-8")

    print(f"DEBUG_DIR={out_dir}")
    for filename in MODE_FILES[mode]:
        print(f"  {filename}")


def cmd_validate(dir_path: str) -> None:
    target = Path(dir_path)
    if not target.is_dir():
        print(f"FAIL: directory not found: {dir_path}")
        sys.exit(1)

    expected = MODE_FILES["full"]
    missing = []
    empty = []

    for filename in expected:
        fp = target / filename
        if not fp.is_file():
            missing.append(filename)
        elif fp.stat().st_size <= len(PLACEHOLDER.encode("utf-8")):
            empty.append(filename)

    if missing:
        print(f"FAIL: missing files: {missing}")
    if empty:
        print(f"FAIL: empty/placeholder files: {empty}")

    if not missing and not empty:
        print(f"PASS: all {len(expected)} files present and populated")
        sys.exit(0)
    else:
        sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]

    if action == "init":
        mode = sys.argv[2] if len(sys.argv) > 2 else "full"
        cmd_init(mode)
    elif action == "validate":
        if len(sys.argv) < 3:
            print("ERROR: validate requires a directory path")
            sys.exit(1)
        cmd_validate(sys.argv[2])
    else:
        print(f"ERROR: unknown action '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
