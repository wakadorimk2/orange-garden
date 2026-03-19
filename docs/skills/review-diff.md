# review-diff

**種類**: review
**正本**: このファイル（`docs/skills/review-diff.md`）
**Codex用アダプタ**: `.codex/skills/review-diff/SKILL.md`
**Claude用アダプタ**: なし（no-side-effect 担当は diff を生成するが review-diff は実行しない）
**Codex 実行詳細**: [`docs/CODEX_RUNBOOK.md`](../CODEX_RUNBOOK.md) Appendix A

---

## Mission

差分をリスク順に整理し、Findings → Open Questions → Change Summary → Next Step の順で報告する。
根拠が不十分な場合は推測せず、不足している情報を Open Questions に記録する。

---

## Inputs

- PR 番号（任意）
- 差分（現在の task で提供されたもの）
- 関連 Issue 番号（任意。scope 確認に使用）

差分が明示されていない場合は、現在の task のローカル git diff を参照する。

---

## Procedure

以下の順序で実施する。順序を変更・省略・代替しない。

1. 差分のコンテキストを収集する
2. 差分を要約する（変更ファイル数・行数・目的を 2〜5 行で記述）
3. インパクトでファイルを優先順位付けする（core logic → tests → docs の順）
4. 各ファイルを 3 つの観点で確認する
   - Regression: 既存挙動を壊していないか
   - Scope deviation: Issue スコープ外の変更が混入していないか
   - Missing tests: 挙動変更に対応するテストがないか
5. Findings をリスクでソートする（HIGH → MEDIUM → LOW）
   - 根拠が不十分な場合は Open Questions に移す
6. `ruff` / `pytest` 失敗が確認できる場合は Next Step を生成する

---

## Output Format

以下のセクション順で Markdown を返す。すべてのセクションが必須。内容がない場合は `None` と記載する。

### Findings

- 存在しない場合は `None`
- リスクラベル付きで 1 Finding 1 行：`[HIGH]` / `[MEDIUM]` / `[LOW]`
- 可能な場合はファイル参照を含める

### Open Questions

- 存在しない場合は `None`
- 利用可能な根拠から判断できない項目を列挙する
- 各項目の末尾に `-> check <ファイルまたは仮定>` を付ける

### Change Summary

- Files changed: N
- Lines: +X / -Y
- Purpose: 変更の意図を 2〜5 行で記述

### Next Step

- 対応不要な場合は `None`
- `ruff` / `pytest` が失敗した場合：最小限の次アクションを 1 行で記載
- HIGH Findings がある場合：review を続行できるか停止が必要かを 1 行で記載

---

## Constraints

- push しない
- 現在の task で明示的に依頼されない限りファイルを編集しない
- 外部 web 検索・任意リモートコンテンツへのアクセスをしない
- 破壊的操作をしない
- Findings は現在の review スコープ内に限定する
- 根拠なく Finding を断定しない。根拠不足の場合は Open Questions を使う
