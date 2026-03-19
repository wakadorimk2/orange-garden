# 候補タグ ingest 由来ポリシー

> Issue #429 の成果物。
> 外部自動取込み（GitHub 活動・ゲームデータ等）から派生した候補タグの扱いを事前に定義する。

## 背景

現行の候補タグソースはすべてユーザー自身が記録したイベントから抽出されている。

| ソース | 説明 |
|--------|------|
| `recent` | 直近のイベントから抽出 |
| `today_frequent` | 当日の頻出テキスト |
| `7d_frequent` | 過去 7 日間の頻出テキスト |
| `fixed` | 固定候補（`FIXED_CANDIDATES`） |

「ingest 由来」とは、GitHub 活動・ゲームデータなど外部自動取込みデータから派生した候補を指す。
これは将来の機能であり、現時点では実装されていない。

## 実装基盤（既存）

- `Candidate { text: string; source?: string }` — `source` フィールドで候補の出所を区別可能
- `resolveCandidateSource()` — telemetry に `candidate_source` を渡す仕組み済み
- バックエンド `list_candidates()` — `source` 付きで候補を返却

現行実装の source 順は `recent` → `today_frequent` → `7d_frequent` → `fixed` であり、
この文書はその動作変更を含まない。

## ポリシー定義

| 観点 | 方針 |
|------|------|
| **含めるか** | 含める（ただし低優先度） |
| **表示順** | ingest を導入する場合も既存 source 群より後ろに置く（末尾）。既存 source 同士の順序変更はこの spec の対象外 |
| **視覚的区別** | `source="ingest:*"` を持つタグは UI 側でスタイル差異を付与可能とする（実装は別 issue） |
| **上限** | `MAX_CANDIDATES`（8 件）内で扱う。ingest 由来は最大 2 件に制限推奨 |
| **命名規則** | `source` 値は `"ingest:<domain>"` 形式（例: `"ingest:github"`, `"ingest:poe2"`） |
| **実装タイミング** | この spec 完了後、必要になった時点で実装 issue を別途起こす |

## source 命名例

```
"ingest:github"   # GitHub イベント（PR, commit, issue など）
"ingest:poe2"     # Path of Exile 2 セッションデータ
```

## 非対象・除外事項

- ingest 由来候補のフィルタリング UI（スタイル差異の具体的な実装は別 issue）
- ingest ソースの追加・削除の手順（各 ingest 実装 issue で定義）
- 上限超過時の優先度計算アルゴリズム（必要になった時点で設計）
