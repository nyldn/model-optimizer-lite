#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
diff -u <("$ROOT/install.sh" claude-md-print) "$ROOT/claude-md/CLAUDE.md"
python3 "$ROOT/scripts/sync-packages.py" --check
python3 "$ROOT/scripts/validate-packages.py"
python3 "$ROOT/scripts/build-distribution.py" --check
echo "OK: generated packages, links, frontmatter, and context budgets"
