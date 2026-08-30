#!/usr/bin/env bash
# The committed always-on template must be byte-identical to the block
# install.sh generates from the lightweight policy source.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
SKILL="$ROOT/skills/claude-model-optimizer/SKILL.md"
POLICY="$ROOT/claude-md/POLICY.md"
TEMPLATE="$ROOT/claude-md/CLAUDE.md"
CODEX_WORKFLOWS="$ROOT/skills/claude-model-optimizer/references/codex-workflows.md"
FABLE_REVIEW_GATES="$ROOT/skills/claude-model-optimizer/references/fable-review-gates.md"
README="$ROOT/README.md"
INSTALL_GUIDE="$ROOT/INSTALL.md"

if ! diff -u <("$ROOT/install.sh" claude-md-print) "$TEMPLATE"; then
  echo "claude-md/CLAUDE.md is out of date. Regenerate with:" >&2
  echo "  ./install.sh claude-md-print > claude-md/CLAUDE.md" >&2
  exit 1
fi

ANCHORS=(
  "Opus 5"
  "Fable 5"
  "GPT-5.6 Sol"
  "Codex"
  "acceptance criteria"
  "sandbox"
  "Fable-Led Delegation"
  "Fable Review Gate"
  "actual model metadata"
  "resolution ledger"
  "small slice"
)

for anchor in "${ANCHORS[@]}"; do
  if ! grep -qi -- "$anchor" "$SKILL"; then
    echo "missing anchor '$anchor' in $SKILL" >&2
    exit 1
  fi
done

if grep -q '^version:' "$SKILL"; then
  echo "non-standard version field found in $SKILL; use Git release tags instead" >&2
  exit 1
fi

POLICY_ANCHORS=(
  "Opus 5"
  "Fable 5"
  "GPT-5.6 Sol"
  "Codex"
  "independent, verifiable work packets"
  "actual model metadata"
  "/claude-model-optimizer"
)

for anchor in "${POLICY_ANCHORS[@]}"; do
  if ! grep -qi -- "$anchor" "$POLICY"; then
    echo "missing anchor '$anchor' in $POLICY" >&2
    exit 1
  fi
done

if [[ ! -f "$FABLE_REVIEW_GATES" ]]; then
  echo "missing Fable review-gate reference: $FABLE_REVIEW_GATES" >&2
  exit 1
fi

FABLE_GATE_ANCHORS=(
  "claude -p --model claude-fable-5"
  "stream-json"
  "final text-bearing assistant message"
  "fable-review-validator:start"
  "VERDICT: APPROVE"
  "three rounds"
  "normal completion"
)

for anchor in "${FABLE_GATE_ANCHORS[@]}"; do
  if ! grep -qi -- "$anchor" "$FABLE_REVIEW_GATES"; then
    echo "missing anchor '$anchor' in $FABLE_REVIEW_GATES" >&2
    exit 1
  fi
done

WORKFLOW_ANCHORS=(
  "Claude dynamic-workflow agents are Claude sessions"
  "configured default"
  "two consecutive rounds make no progress"
)

for anchor in "${WORKFLOW_ANCHORS[@]}"; do
  if ! grep -qi -- "$anchor" "$CODEX_WORKFLOWS"; then
    echo "missing anchor '$anchor' in $CODEX_WORKFLOWS" >&2
    exit 1
  fi
done

if [[ ! -f "$INSTALL_GUIDE" ]]; then
  echo "missing public installation guide: $INSTALL_GUIDE" >&2
  exit 1
fi

README_INSTALL_ANCHORS=(
  "Quick start"
  "INSTALL.md"
  "Fable review gate"
  "raw.githubusercontent.com/nyldn/claude-model-optimizer/main/install.sh"
)

for anchor in "${README_INSTALL_ANCHORS[@]}"; do
  if ! grep -qi -- "$anchor" "$README"; then
    echo "missing install anchor '$anchor' in $README" >&2
    exit 1
  fi
done

GUIDE_ANCHORS=(
  "bash -s -- skill-project"
  "bash -s -- claude-md"
  "fable5-optimizer"
  "claude-model-optimizer"
  "CLAUDE_MODEL_OPTIMIZER_"
  "Update"
  "Remove"
  "Troubleshooting"
)

for anchor in "${GUIDE_ANCHORS[@]}"; do
  if ! grep -qi -- "$anchor" "$INSTALL_GUIDE"; then
    echo "missing install anchor '$anchor' in $INSTALL_GUIDE" >&2
    exit 1
  fi
done

if ! grep -q 'github.com/nyldn/claude-model-optimizer.git' "$ROOT/install.sh"; then
  echo "installer does not use the renamed canonical repository" >&2
  exit 1
fi

policy_words="$(wc -w < "$POLICY" | tr -d ' ')"
if [[ "$policy_words" -gt 500 ]]; then
  echo "$POLICY is too large for always-on context: $policy_words words (max 500)" >&2
  exit 1
fi

for marker in "claude-model-optimizer:start" "claude-model-optimizer:end"; do
  if ! grep -q -- "$marker" "$TEMPLATE"; then
    echo "missing managed-block marker '$marker' in $TEMPLATE" >&2
    exit 1
  fi
done

ACTIVE_NAME_FILES=(
  "$ROOT/README.md"
  "$ROOT/CONTRIBUTING.md"
  "$ROOT/CLAUDE.md"
  "$ROOT/claude-md/POLICY.md"
  "$ROOT/claude-md/CLAUDE.md"
  "$ROOT/.github/ISSUE_TEMPLATE/bug_report.yml"
  "$ROOT/.github/ISSUE_TEMPLATE/config.yml"
  "$ROOT/.github/workflows/test.yml"
  "$ROOT/tests/trigger-cases.md"
)

if grep -nE 'fable5-optimizer|Fable 5 Optimizer' "${ACTIVE_NAME_FILES[@]}"; then
  echo "active public files still use the retired project name" >&2
  exit 1
fi

echo "OK: always-on template matches the lightweight policy ($policy_words words)"
