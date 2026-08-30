#!/usr/bin/env bash
# Verify the Claude CLI flags used by the Fable review template. Help-text
# probe only: no model calls, auth, or repository changes. Skips cleanly when
# Claude Code is absent, as it is on many CI runners.
set -euo pipefail

if ! command -v claude >/dev/null 2>&1; then
  echo "SKIP: claude not installed; Fable review-template flag check not run"
  exit 0
fi

status=0
help_text="$(claude --help 2>&1)"

for flag in --print --model --effort --restricted --allowed-tools --output-format --verbose; do
  if ! grep -q -- "$flag" <<<"$help_text"; then
    echo "missing flag '$flag' in claude help; Fable review template needs updating" >&2
    status=1
  fi
done

if [[ "$status" -ne 0 ]]; then
  claude --version >&2 || true
  exit 1
fi

echo "OK: claude $(claude --version 2>/dev/null | tr -d '\n') exposes all flags used by the Fable review template"
