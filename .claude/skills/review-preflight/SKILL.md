---
name: review-preflight
description: merge 前 review の検査と報告を標準化する skill。修正は行わず、観点に沿った検査結果を報告する。
---

# review-preflight

Claude Code adapter for [`docs/skills/review-preflight.md`](../../../docs/skills/review-preflight.md).
Follow the canonical skill doc for mission, review axes, output format, and base constraints.

## Claude-specific notes

- Claude does not execute commands for this skill.
- Use the provided diff, worktree state, and command results as evidence. If required evidence is missing, record that gap in `Failures` or `Preflight Checks` instead of assuming results.
- Keep the response aligned with the canonical output structure.
