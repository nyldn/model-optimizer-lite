#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
REFERENCE="$ROOT/skills/claude-model-optimizer/references/fable-review-gates.md"
validator="$(sed -n '/# fable-review-validator:start/,/# fable-review-validator:end/p' "$REFERENCE" | sed '1d;$d')"

if [[ -z "$validator" ]]; then
  echo "could not extract the published Fable review validator" >&2
  exit 1
fi

valid_stream='{"type":"assistant","message":{"model":"claude-fable-5","content":[{"type":"thinking","thinking":""}]}}
{"type":"assistant","message":{"model":"claude-fable-5","content":[{"type":"text","text":"Review complete.\n\nVERDICT: APPROVE\n\nBLOCKERS\n- None."}]}}
{"type":"result","subtype":"success","is_error":false,"modelUsage":{"claude-haiku-4-5-20251001":{"outputTokens":10},"claude-fable-5":{"outputTokens":257}},"result":"Review complete.\n\nVERDICT: APPROVE\n\nBLOCKERS\n- None."}'

fallback_stream='{"type":"assistant","message":{"model":"claude-sonnet-5","content":[{"type":"text","text":"VERDICT: APPROVE"}]}}
{"type":"result","subtype":"success","is_error":false,"modelUsage":{"claude-sonnet-5":{"outputTokens":257}},"result":"VERDICT: APPROVE"}'

incomplete_stream='{"type":"assistant","message":{"model":"claude-fable-5","content":[{"type":"tool_use","name":"Read"}]}}'

error_stream='{"type":"assistant","message":{"model":"claude-fable-5","content":[{"type":"text","text":"VERDICT: APPROVE"}]}}
{"type":"result","subtype":"error_during_execution","is_error":true,"result":"VERDICT: APPROVE"}'

if ! jq -s -e "$validator" <<<"$valid_stream" >/dev/null; then
  echo "completed Fable review was rejected" >&2
  exit 1
fi

if jq -s -e "$validator" <<<"$fallback_stream" >/dev/null; then
  echo "fallback model was accepted as Fable" >&2
  exit 1
fi

if jq -s -e "$validator" <<<"$incomplete_stream" >/dev/null; then
  echo "incomplete tool-use run was accepted" >&2
  exit 1
fi

if jq -s -e "$validator" <<<"$error_stream" >/dev/null; then
  echo "error result was accepted" >&2
  exit 1
fi

echo "OK: published Fable validator accepts Fable and rejects fallback, incomplete, or error runs"
