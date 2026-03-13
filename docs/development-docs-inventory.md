# Development Docs Inventory and Consolidation Baseline

> Issue: #416
> Parent epic: #415
> Purpose: docs 再編時の current baseline と統合判断を短く固定する
> Updated: 2026-03-14

## 1. Why this file still exists

`#416` の役割は、再編前に `docs/` の責務と重複候補を見える化することだった。
ただし、行単位の巨大 inventory table は再編途中で drift しやすく、
`#417` 完了後の実 tree とずれ始めていた。

この文書は詳細な全件台帳ではなく、
**current baseline / overlap cluster / immediate action**
だけを残す軽量 inventory として扱う。

## 2. Current baseline

2026-03-14 時点の `docs/**/*.md` は 59 files。

| group | count | note |
|---|---:|---|
| `docs/` top-level | 41 | architecture / runbook / spec / record を含む |
| `docs/skills/` | 12 | canonical skill docs |
| `docs/infra/` | 5 | infra / notification / backup docs |
| `docs/architecture/` | 1 | AI development system parent doc |

前版の 56-file inventory から漏れていたもの:

- `docs/architecture/ai-development-system.md`
- `docs/development-docs-inventory.md`
- `docs/heatmap-metric-derivation-spec.md`

## 3. Current ownership decisions

### 3.1 Keep as canonical

以下は削減対象ではなく、canonical として維持する。

- `AGENTS.md`
- `AI_GUIDE.md`
- `docs/architecture/ai-development-system.md`
- `docs/AI_ROLE_POLICY.md`
- `docs/AI_WORKFLOW.md`
- `docs/PLAYBOOK.md`
- `docs/WORKER_POLICY.md`
- `docs/RUNBOOK_BASELINE.md`
- worker protocol docs
- contract / spec docs

### 3.2 Absorb into existing docs

以下は独立 file よりも、既存 canonical doc の section / appendix に寄せる方が自然である。

- `docs/git-branch-cleanup-cheatsheet.md`
- `docs/skills/issue-create.md`
- `docs/skills/issue-project-meta.md`
- `docs/skills/minimal-safe-impl.md`
- `docs/skills/review-diff.md`
- `docs/skills/review-preflight.md`
- `docs/unified-input-ui-187.md`
- `docs/migration.md`
- `docs/infra/restore-mvp-draft.md`

### 3.3 Retire after absorption or reference cleanup

- `docs/issue-79-proposal-review.md`
- `docs/issue-213-daily-log-input-frictions.md`
- `docs/infra/ai-cli-discord-smoke-log.md`

## 4. Overlap clusters

| cluster | decision | main issue |
|---|---|---|
| `ai-system-core` | parent doc + thin adapters を維持する。file 数より line 数を減らす | `#417` follow-up |
| `ai-runbook-skill` | `CODEX_RUNBOOK` と既存 runbook へ吸収する | `#418` |
| `skill-github-ops` | runbook appendix へ吸収する | `#418` |
| `skill-review` | `CODEX_RUNBOOK` の review / preflight appendix に吸収する | `#418` |
| `daily-input` | canonical UX doc へ issue memo を吸収する | follow-up |
| `storage-recovery` | `data-directory` と backup docs へ寄せる | follow-up |
| `notification-infra` | contract と wrapper doc を残し、 smoke log は retire する | follow-up |

## 5. Immediate actions

`#415` の current phase で先に進めるのは次の 3 点。

1. `#418`: runbook / skill 群を既存 runbook に統合する
2. `#419`: docs index と backlinks を追加し、探索導線を作る
3. issue memo / smoke log / old review memo を retire する

## 6. Expected reduction

高 confidence で見込める削減:

- file count: `59 -> 48` 前後
- 独立 runbook / skill docs: 6 から 7 files 削減
- issue-specific memo / log docs: 3 files 削減
- reference-only docs: 1 から 2 files 削減

補足:

- `ai-system-core` 4 docs は消すより薄くする方が安全
- `#419` で stub を恒久化しすぎると file 数は減らない
- 詳細な per-file 台帳が必要になった場合は、この文書を再肥大化させず、別 issue の一時 artifact として作る

## 7. Handoff map

| issue | role |
|---|---|
| `#416` | baseline と判断材料の記録 |
| `#417` | parent doc と priming topology の固定 |
| `#418` | runbook / skill 統合 |
| `#419` | docs index / backlinks / stub policy |
