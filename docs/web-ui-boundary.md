# Web UI 責務境界

> この文書は Epic #442（Vite + React UI 基盤導入）完了時点の責務分離を固定する。
> 将来の auth/public shell 設計が確定した段階で更新すること。

## ルート責務マップ

| ルート | 配信元 | 技術 | 状態 |
|---|---|---|---|
| `/` | Python (inline HTML) | stdlib HTTP + vanilla JS | 現行・維持 |
| `/dashboard` | 同上 | 同上 | 現行・維持 |
| `/input` | 同上 | 同上 | 現行・維持 |
| `/api/*` | Python (JSON) | stdlib HTTP | 現行・維持 |
| `/app/*` | Python (static serve) | Vite + React build 成果物 | #442 で導入 |
| `/app/` (未 build) | Python | 503 + hint レスポンス | #442 で導入 |

## 今回の実装範囲（Epic #442）

- `frontend/` に Vite + React scaffold を導入
- `/app/` 配下への汎用 static serving + SPA fallback
- `web/app/` 未 build 時の 503 graceful degradation
- `pnpm build` → Python serve のハンドオフパス契約固定（`web/app/`）
- 未 build 時の packaging 警告（`pip wheel` 実行時）
- CI への frontend build 最小検査線追加

## 今回の非対象（明示）

以下は #442 のスコープ外であり、別 issue で判断する。

- 既存 `/` `/input` `/api/*` の React 化・移行
- 認証実装
- public hosting 構成
- multi-user / tenancy 対応
- Tailwind / shadcn / Storybook 等の UI 基盤拡張
- frontend test/lint の本格整備
- preview deploy

## 既存 UI の扱い

`/` `/input` `/api/*` は **現行・安定** として維持する。
即時移行は要求しない。React 化の時期・方式は別 issue で判断する。

## 将来の public/auth shell について

**境界の整理のみ実施済み。実装は今回のスコープ外。**

- `/app/` は local-first な React 開発面として独立配置済み
- 将来の auth/public shell は `/app/` の外側に後付けで差し込む前提を保つ
- core app に auth を直埋めしない方針は維持する
- 認証方式・public hosting 構成の決定はこの文書のスコープ外

## 混同しやすい点

| 混同されやすい組み合わせ | 正しい理解 |
|---|---|
| 「`/app/` 導入 = auth 実装済み」 | `/app/` は local-first な開発面の導入のみ。auth は未実装 |
| 「既存 UI は近々廃止される」 | 廃止計画なし。`/` `/input` は現行維持 |
| 「public 配信ができるようになった」 | local-first の運用は変わらない。public shell は将来の別実装 |
| 「`/app/` に認証をかける必要がある」 | local-first 利用では不要。将来の shell 側で差し込む設計 |
