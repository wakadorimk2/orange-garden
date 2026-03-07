# Issue #151 Boundary Phase Memo

## Purpose

Issue #151 は「境界定義フェーズ」に戻し、先行して入っていた越境差分を外す。
このメモは、レビュー指摘に対する整理結果と follow-up 分割先を記録する。

## Scope For #151

- 境界定義（責務整理・許可境界の論点整理）
- follow-up Issue への分割と追跡

## Out Of Scope For #151

- policy/runbook/skills/guide 本体の直接更新
- adapter 配布物の同期反映
- 実装運用への先行反映

## Follow-up Issues

- #154 docs: AI_ROLE_POLICY境界を導線文書へ同期する
- #155 docs/skills: codex-claude-bridgeをvNext境界へ全面同期する
- #156 docs/skills: implement-onlyの実行モード定義を一意化する
- #157 docs/runbook/policy: 境界変更反映の実施順を定義する

## Execution Order

1. #154 正本と導線の矛盾解消
2. #155 codex-claude-bridge の vNext 同期
3. #156 implement-only のモード一意化
4. #157 境界変更反映の順序定義

## Notes

- この PR では越境差分を外し、Issue 契約（Out / Non-goals）との整合を優先する。
- 実編集は follow-up Issue で段階的に行う。
