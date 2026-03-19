---
name: review-diff
description: Review a diff in a fixed order, list findings before summary by risk, and return Markdown that can be pasted into a PR or issue comment.
---

# review-diff

Codex CLI adapter for [`docs/skills/review-diff.md`](../../../docs/skills/review-diff.md).
Follow the canonical skill doc for mission, inputs, procedure, output format, and constraints.
Use [`docs/CODEX_RUNBOOK.md`](../../../docs/CODEX_RUNBOOK.md) Appendix A only for Codex-specific execution detail.

## Codex-specific notes

- If the diff source is not explicitly provided, inspect the local git diff for the current task.
- When local validation context includes `ruff` or `pytest` failures, include the minimal next action in `Next Step` as defined by the canonical doc.
- Do not expand the review beyond the current diff and task context.
