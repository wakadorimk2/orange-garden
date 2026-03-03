---
name: minimal-safe-impl
description: Repo の MVP 互換性ポリシーに従って issue や実装依頼を最小差分で実装する。既存構造と CLI パターンを踏襲し、投機的リファクタや恒久互換レイヤを入れないときに使う。
argument-hint: "[issue-url-or-number-or-implementation-request]"
disable-model-invocation: true
---

# minimal-safe-impl（Claude アダプタ）

> このファイルは Claude Code 用のアダプタです。
> **正本（AI非依存）**: [`docs/skills/minimal-safe-impl.md`](../../../docs/skills/minimal-safe-impl.md)
>
> Mission / Rules / Output テンプレは正本を参照してください。
> このファイルには Claude 固有の制約・呼び出し方法のみ記載します。

---

## Claude 固有の制約

- 入力は `$ARGUMENTS`（issue番号 / URL / 実装依頼文）
- Issue がある場合は先に本文から Goal / Scope / 完了条件を取得する
- 近い既存実装を確認し、構造と CLI パターンを揃えてから編集する
- README / AI_GUIDE の MVP 互換性ポリシーと矛盾する互換レイヤは追加しない
- データ形式変更が必要なら `schema_version` とワンタイム移行スクリプト要否を必ず確認する

## Invocation Examples

- `/minimal-safe-impl 15`
- `/minimal-safe-impl "Implement issue #15 following repo conventions."`
- `/minimal-safe-impl "Apply a minimal fix respecting the MVP compatibility policy."`
