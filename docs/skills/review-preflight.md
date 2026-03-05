# review-preflight

merge 前 review の「検査と報告」を標準化する skill。
この Issue (#114) では docs 更新のみを扱い、実装変更・contract 変更・自動修正は扱わない。
`review-preflight` は修正を行う skill ではなく、観点に沿った検査結果を報告するための skill として定義する。

## Purpose

レビュー開始前の安全確認と、4 観点の意味的整合チェックを固定する。
責務は検査と報告に限定し、修正は別 skill に委譲する。

## Input

- `pr_or_diff`（PR 番号または差分）
- `issue_ref`（対応する Issue 番号）
- base branch（例: `main`、任意）
- 現在の作業ツリー

## Fixed Procedure

以下の手順をこの順序で実施する。検査結果の報告までを本 skill の責務とする。

1. コマンドチェック（Codex が実行可能な場合）
2. 4 観点チェック（Claude / Codex 共通）
3. Output Format に沿った報告

コマンドチェックを行う場合、次の順序は固定とする。

```bash
git status --short --branch
git diff --stat
ruff check .
pytest
```

## Review Axes（4本柱）

### 1) Contract Consistency

イベント契約の照合は、次の正本のみを使う。

- A. `docs/event-contract-v1.md`（最優先）
- B. `docs/domain-extension-policy.md`（domain/allowlist の正本）
- C. `docs/kind-taxonomy-v1.md`（kind taxonomy の正本）

`docs/architecture.md` と `AI_GUIDE.md` は補助ガイドとして扱い、正本判定には使わない。

### 2) Scope Guard

Issue の Goal / Scope / Acceptance Criteria / Non-goals と差分を照合し、範囲外変更の混入を確認する。

### 3) Migration Awareness

破壊的変更や移行説明が必要な差分かを確認し、説明不足を報告する。

### 4) Docs-Impl Consistency

ドキュメント記述と実装差分の意味が一致しているかを確認する。

## Failure Handling

失敗した場合は、修正しない。次を報告する。

1. 失敗概要
2. 再現コマンド
3. 原因候補（当たり）

`ruff` / `pytest` の失敗時に自動修正・再試行ループを行わない。
修正は `minimal-safe-impl` など別 skill に委譲することを `Next Step` で明記する。

## Output Format

出力は PR コメントにそのまま貼れる Markdown とし、既存の見出し構造を維持する。
（`Summary` / `Preflight Checks` / `Failures` / `Next Step` は互換維持）

## Summary

短い結果サマリー（検査対象 / 判定 / レビュー継続可否）

## Preflight Checks

- `git status`: `PASS` / `FAIL`
- `git diff`: `PASS` / `FAIL`
- `ruff`: `PASS` / `FAIL`
- `pytest`: `PASS` / `FAIL`
- `contract`: `PASS` / `WARN` / `FAIL`
- `scope`: `PASS` / `WARN` / `FAIL`
- `migration`: `PASS` / `WARN` / `FAIL`
- `docs-impl`: `PASS` / `WARN` / `FAIL`

## Failures

失敗したチェックの詳細。失敗がない場合も `None` と明記する。
失敗がある場合は各項目に以下を含める。

- `Failure`: 失敗概要
- `Repro`: 再現コマンド
- `Likely Cause`: 原因候補（当たり）

## Next Step

修正指示は書かず、委譲先のみを 1 行で書く。

- 失敗あり: `修正は別 skill（minimal-safe-impl など）へ委譲。review-preflight は報告のみ。`
- 失敗なし: `レビュー開始可。`

## Review Prompt (Claude / Codex 共通)

```text
あなたは merge 前 review の検査担当です。修正は行わず、検査と報告だけを実施してください。

確認観点:
1) Contract Consistency
2) Scope Guard
3) Migration Awareness
4) Docs-Impl Consistency

制約:
- 実装変更しない
- contract 変更しない
- 自動修正しない
- 再試行ループしない
- 報告は Summary / Preflight Checks / Failures / Next Step の順で出力する
```

## Docs-only Note

この Issue (#114) は docs-only で仕様を確定する。
`.codex/skills/review-preflight/SKILL.md` と `docs/CODEX_RUNBOOK.md` の同期は別 Issue で扱う。
フォローアップ: `#126`
