# Skill Trigger Cases

Manual evaluation set for the `fable5-optimizer` skill description. After changing the frontmatter description, check each case in a fresh Claude Code session and confirm the load behavior matches.

## Should trigger

1. "Should Opus 5 handle this feature, or is it worth escalating to Fable?"
2. "Have GPT-5.6 Sol review this Opus implementation for edge cases."
3. "Use Codex browser automation to verify the checkout screenshots."
4. "Which model should plan and implement this repository-wide migration?"
5. "Should Fable orchestrate Sol, Terra, or Luna workers for this migration?"

## Should not trigger

6. "Review this diff." (no model-routing intent)
7. "Rewrite this marketing prompt." (prompt rewriting, not routing or orchestration)
