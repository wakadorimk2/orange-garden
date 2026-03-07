# post-candidate

**種類**: workflow
**正本**: このファイル（`docs/skills/post-candidate.md`）
**Codex用アダプタ**: `.codex/skills/post-candidate/SKILL.md`
**Claude用アダプタ**: なし（必要になった時点で追加）

---

## Mission

日次ログから「知見共有・研究ノート・開発メモ」寄りの短文投稿候補を 2〜3 案生成する。
I/O 契約と運用境界は `docs/post-candidate-contract-v1.md` を正本として扱う。

---

## Rules（絶対）

- 対象スコープは `docs/post-candidate-contract-v1.md` に定義された範囲に限定する
- 出力は 1 回あたり 2〜3 案とし、1 案は `hook` / `body` / `tags(optional)` で返す
- 1 案の本文長は `hook + body` 合計 80〜200 字の範囲に収める
- トーンは知見共有・研究ノート・開発メモ寄りを維持し、過度な宣伝表現は避ける
- 自動投稿は扱わない。最終投稿は常に人間が実行する
- 仕様変更が必要な場合はこの skill ではなく `docs/post-candidate-contract-v1.md` を先に更新する

---

## Inputs

- 入力レコード（`source_type`, `content` は必須）
- 任意メタデータ（`ts`, `domain`, `kind`, `ref`, `tags`）

入力項目の詳細は `docs/post-candidate-contract-v1.md` の「2. 最小入力 Contract」に従う。

---

## Procedure（作業手順）

1. 入力を正規化し、`source_type` と `content` が存在することを確認する
2. 入力内容から 2〜3 個の切り口（視点）を選ぶ
3. 各切り口について `hook` と `body` を作る
4. 文字量レンジ（80〜200 字）とトーン方針を満たすように調整する
5. `tags` は任意で 0〜3 件付与する
6. JSON 配列で候補を返し、投稿実行は人間に委ねる

---

## Output Contract

```json
[
  {
    "hook": "string",
    "body": "string",
    "tags": ["string"]
  }
]
```

- 配列要素数: 2〜3
- `tags` は省略可能
- 文字数条件: `hook + body` 合計 80〜200 字

---

## Non-goals

- X/Twitter への自動投稿
- API 連携、認証、secrets 管理
- 投稿効果測定や分析基盤の設計
