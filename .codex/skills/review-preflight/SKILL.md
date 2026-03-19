---
name: review-preflight
description: merge 前 review の検査と報告を標準化する skill。修正は行わず、観点に沿った検査結果を報告する。
---

# review-preflight

Codex CLI adapter for [`docs/skills/review-preflight.md`](../../../docs/skills/review-preflight.md).
Follow the canonical skill doc for mission, review axes, output format, and base constraints.
Use [`docs/CODEX_RUNBOOK.md`](../../../docs/CODEX_RUNBOOK.md) Appendix B only for Codex-specific execution detail.

## Codex-specific notes

- `base branch` is optional. When omitted, prefer upstream; otherwise use `main`.
- If a PR number is not provided, skip `gh pr diff` and use the local git diff for the current task.
- Codex may execute the preflight commands needed to gather evidence for the canonical procedure.
- Keep execution read-only with respect to repo-tracked files. Do not auto-fix or retry beyond evidence gathering.
