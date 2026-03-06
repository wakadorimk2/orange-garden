# 短文投稿候補 Contract v1

> スコープ: 日々のログから「知見共有・研究ノート・開発メモ」寄りの短文投稿候補を生成するための最小仕様
> 関連 Issue: #129

## 目的

この文書は、日々のログ（event / issue / PR / commit / 手動メモ / 日次まとめ）を入力源として短文投稿候補を生成する運用フローと、後続実装（skill / CLI / interface）が参照すべき入力・出力の契約を定義する。

実装ではなく仕様を定める文書である。自動投稿実装・API 連携・secrets 設計はスコープ外とする。

---

## 1. 入力源と取り込み単位

| 入力源 | 取り込み単位 | 取り込み方法 | 備考 |
|--------|--------------|--------------|------|
| event (JSONL) | 1 イベントレコード | reader の正規化後 `data.text` を本文として参照（legacy `payload.text` も受理） | Event Contract v1 形式（`docs/event-contract-v1.md`）に準拠 |
| issue | 1 Issue | タイトル + 本文（抜粋） | GitHub Issue の URL または番号で参照 |
| PR | 1 Pull Request | タイトル + 概要（抜粋） | GitHub PR の URL または番号で参照 |
| commit | 1 コミットメッセージ | コミットメッセージ本文 | SHA または短縮 SHA で参照 |
| 手動メモ | 1 段落またはメモ単位 | 自由テキスト | 構造化不要。raw text として受け取る |
| 日次まとめ | 1 日分のまとめテキスト | 日付＋まとめ本文 | 複数 event を集約した自然言語要約 |

取り込み単位は「投稿候補を 1 件生成するのに必要な最小コンテキスト」を基準とする。
複数 event を横断するまとめは「日次まとめ」入力として扱う。
event JSONL は生読みせず、既存 reader の正規化層を通した入力を前提にする。
legacy record（`payload` 形式）が残る期間は `payload.text` を `data.text` 相当として扱う。

---

## 2. 最小入力 Contract

### 2.1 必須フィールド

| フィールド | 型 | 説明 | 例 |
|---|---|---|---|
| `source_type` | string | 入力源の種別 | `"event"` / `"issue"` / `"pr"` / `"commit"` / `"memo"` / `"daily"` |
| `content` | string | 投稿候補生成の元となる本文テキスト | `"JSONL の最低契約を先に固定したい"` |

### 2.2 任意フィールド

| フィールド | 型 | 説明 | 例 |
|---|---|---|---|
| `ts` | string | 入力源のタイムスタンプ（ISO 8601） | `"2026-03-06T18:00:00+09:00"` |
| `domain` | string | event 由来の場合の domain | `"eng"` |
| `kind` | string | event 由来の場合の kind | `"note"` |
| `ref` | string | issue / PR / commit 番号・SHA | `"#129"` |
| `tags` | array of string | 分類・フィルタ補助情報 | `["docs", "design"]` |

### 2.3 入力 I/O 例

#### event 由来

```json
{
  "source_type": "event",
  "content": "reader-first な設計だと writer の制約を後から緩めやすい",
  "ts": "2026-03-06T18:00:00+09:00",
  "domain": "eng",
  "kind": "note",
  "ref": "#94",
  "tags": ["design", "schema"]
}
```

#### 手動メモ由来

```json
{
  "source_type": "memo",
  "content": "reader-first な設計をすると、writer の制約を後から緩められることがわかった"
}
```

#### 日次まとめ由来

```json
{
  "source_type": "daily",
  "content": "今日は event contract の cleanup と kind taxonomy の草案を進めた。docs-first で進めると可逆性が保ちやすい。",
  "ts": "2026-03-06T23:59:00+09:00"
}
```

---

## 3. 出力 Contract

### 3.1 1案の構造

| フィールド | 型 | 必須 | 説明 | 文字量目安 |
|---|---|---|---|---|
| `hook` | string | 必須 | 投稿の掴みになる冒頭文 | 20〜50字 |
| `body` | string | 必須 | 知見・メモ・気づきの本文 | 60〜150字 |
| `tags` | array of string | 任意 | 投稿時に付与するハッシュタグ候補 | 0〜3件 |

**合計文字量レンジ**: hook + body 合計で **80〜200字**（スペース・改行を含む）

- 80字未満は内容が薄すぎる可能性がある
- 200字超は短文投稿媒体の性質に合わない
- tags は本文文字数カウントに含めない

### 3.2 1回実行あたりの候補数

**2〜3案** を返す。

- 2案は最低限の選択肢を保証する
- 3案は角度違いのバリエーションを提供する
- 4案以上は選択コストが増え、Human-in-the-loop の負担になる

### 3.3 出力 I/O 例

```json
[
  {
    "hook": "JSONL の reader-first 設計で気づいたこと。",
    "body": "writer に制約を持たせつつ reader を寛容にすると、後から writer 制約を緩めるときに互換を壊さずに済む。schema の変化に対して「壊れにくい読み取り」が先に来る設計は、append-only ログとの相性がいい。",
    "tags": ["設計メモ", "JSONL"]
  },
  {
    "hook": "append-only ログに schema 進化をどう持たせるか。",
    "body": "legacy record と v1 record を reader が吸収する方式なら、writer の出力形式を変えても既存データを壊さない。reader tolerant / writer strict の分離が鍵。",
    "tags": ["設計メモ", "ログ設計"]
  }
]
```

---

## 4. トーン方針

### 4.1 基本方針

- **知見共有・研究ノート・開発メモ寄り**: 「こういうことがわかった」「こう考えた」という一人称の気づきを基本とする
- **断定より気づき**: 「〜すべき」より「〜が向いていそう」「〜と感じた」を優先する
- **再現性のある抽象化**: 固有名詞・文脈に過度に依存せず、読み手が自分のケースに引用できる表現を選ぶ
- **過度な宣伝・自己 PR・行動誘導を避ける**: 「フォローしてね」「いいねしてね」等の行動促進フレーズは入れない

### 4.2 避けるべき表現

- 比較・ランキング表現（「最強の」「一番の」）
- 緊急性・煽り（「今すぐ」「絶対に」）
- 未検証の定量表現（「効率が3倍に」等）
- 宣伝主体の文体（「〜をリリースしました！」単独では投稿候補として不適切）

---

## 5. 最小運用フロー

```
[収集]
  ↓  event JSONL / issue / PR / commit / 手動メモ / 日次まとめ を入力として準備する
[候補生成]
  ↓  skill または CLI に入力を渡す → 2〜3案を受け取る
[人間が選択]
  ↓  候補から1案を選ぶ（または全案を棄却してもよい）
[軽微修正]
  ↓  表現・タグ・文字数を手で調整する（必須ではない）
[投稿]
     人間が手動で投稿プラットフォームに投稿する
```

**自動投稿は行わない。** 投稿の最終実行は常に人間が手動で行う。
この境界は本 contract の不変条件であり、後続実装でも変更しない。

---

## 6. repo 内責務分離

| 層 | 配置場所 | 責務 | 状態 |
|---|---|---|---|
| docs | `docs/post-candidate-contract-v1.md`（この文書） | 入力・出力・運用フロー・トーン方針の正本 | 本 Issue で定義 |
| skill | `docs/skills/post-candidate.md` + `.codex/skills/post-candidate/SKILL.md` | 候補生成の手順・プロンプト構造 | 本PRで Codex adapter を追加（Claude adapter は後続候補） |
| CLI | `src/personal_mcp/tools/post_candidate.py` | JSONL event を入力にとり候補を stdout 出力するツール | 後続候補 |
| interface | TBD（MCP adapter 等） | 外部ツール・アプリとの連携 | 後続候補（スコープ外） |

**正本はこの docs 文書のみ。** skill / CLI / interface は、この文書の定義と整合する範囲で実装する。
docs 文書を変更せずに実装側の動作を変えてはならない。

---

## 7. 後続候補タスク（このIssueでは実装しない）

| タスク | 説明 |
|---|---|
| Claude adapter 追加 | `.claude/skills/post-candidate/SKILL.md` を定義し、Claude が手動実行できる形にする |
| CLI 化 | `src/personal_mcp/tools/post_candidate.py` として JSONL event → 候補テキスト出力の最小 CLI を実装する |
| interface 化 | MCP tool または HTTP adapter として expose する |
| 入力自動収集 | GitHub Webhook・JSONL reader との連携で入力取り込みを自動化する |

---

## 8. 非スコープ

このIssueでやらないこと:

- X/Twitter 自動投稿実装
- API 連携・secrets / 認証設計
- 予約投稿・効果測定・分析基盤
- 投稿後の反応集計・改善ループ
