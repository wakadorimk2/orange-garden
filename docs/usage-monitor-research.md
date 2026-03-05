# Usage Monitor Research — Issue #120

> 種別: 調査・提案（実装前）
> 対象 Issue: #120
> 更新日: 2026-03-05

---

## 目的

最小の CLI モニターで「Claude Code トークン / Codex セッション / モデル別使用量」を
5 分間隔で表示できるかを調査する。
この文書は調査結果と提案案の記録であり、実装の開始指示ではない。

---

## 表示対象項目

| 表示項目 | 説明 |
|----------|------|
| Claude tokens today | 当日の入力・出力トークン合計 |
| model usage | モデル別（opus / sonnet 等）のトークン内訳 |
| Codex sessions today | 当日起動したセッション数 |

### 集計境界（today の定義）

- `today` は **モニター実行環境のローカルタイムゾーン** で日付判定する（例: JST 環境なら 00:00-23:59 JST）
- UTC 固定ではないため、異なるタイムゾーン環境間では日次集計値が一致しない場合がある

---

## 依存方針（M1 反映）

モニタースクリプト本体は **Python 標準ライブラリのみ** を使用し、新規依存は追加しない。

`ccusage` は外部オプションとして位置づける:

- `ccusage` がインストール済みであれば優先利用する（集計ロジックを外部に委ねる）
- 未インストールまたはコマンド失敗時は `~/.claude/projects/` 直接読取に自動フォールバックする
- どちらの経路でも、モニタースクリプト自体が新たなパッケージを要求しない

| 経路 | 条件 | モニター側の追加依存 |
|------|------|----------------------|
| ccusage 経由 | `ccusage` コマンドが実行可能 | なし（subprocess 呼び出しのみ） |
| 直接読取 | ccusage 不在または失敗 | なし（標準ライブラリのみ） |

---

## データ取得元比較

### A. Claude Code usage

#### A-1: `ccusage` CLI 利用（外部オプション）

| 項目 | 内容 |
|------|------|
| 取得元 | npm パッケージ `ccusage`（任意インストール） |
| コマンド例 | `ccusage daily --json` または `npx ccusage@latest` |
| 出力形式 | JSON（日別トークン集計、モデル別内訳を含む可能性あり） |
| 更新方法 | 5 分ごとにコマンド実行、結果を parse して表示 |
| 依存 | Node.js / npm が必要（モニター本体の依存ではない） |
| 長所 | 集計ロジック外部化、edge case 処理済み |
| 短所 | 外部依存、出力 schema が変更される可能性あり |

**不確実点:**
- `--json` フラグの有無と正確な出力 schema は未確認（要手元で `ccusage --help` 確認）
- 当日フィルタのフラグ名（`--today` / `--date` 等）は未確認

#### A-2: `~/.claude/projects/` 直接読取（標準フォールバック）

| 項目 | 内容 |
|------|------|
| 取得元 | `~/.claude/projects/<hash>/*.jsonl` |
| データ形式 | JSONL 各行に `message.usage.{input_tokens, output_tokens}` を含む |
| 更新方法 | 5 分ごとにファイルを glob して当日タイムスタンプのレコードを集計 |
| 依存 | Python 標準ライブラリのみ（`json`, `glob`, `datetime`） |
| 長所 | 外部依存なし、ccusage 不在でも動作する |
| 短所 | ファイル形式が非公式・変更リスクあり、glob 対象が多いと遅い |

**不確実点:**
- JSONL の正確なフィールド構造は Claude Code バージョンで異なる可能性あり
- モデル名のフィールドパス（`message.model` 等）が安定しているか未確認
- キャッシュトークン（`cache_read_input_tokens` 等）の扱いは要方針決定

---

### B. Codex CLI usage

#### B-1: `~/.codex/` セッションログ解析

| 項目 | 内容 |
|------|------|
| 取得元 | `~/.codex/` 配下のセッションログ（存在する場合） |
| データ形式 | 未確認（JSONL / プレーンテキスト等の可能性） |
| 更新方法 | 5 分ごとにファイル更新時刻を確認し、当日セッションをカウント |
| 依存 | Python 標準ライブラリのみ |
| 長所 | 外部依存なし |
| 短所 | ログの存在・形式が未確認、Codex バージョンで構造が変わる可能性 |

**不確実点（高）:**
- `~/.codex/` に当日セッションを識別できるログが存在するか未確認
- ファイル名・ディレクトリ構造が未確認
- トークン情報がログに含まれるかどうか不明

#### B-2: Codex 組み込みコマンド（`/status` 代替）

| 項目 | 内容 |
|------|------|
| 取得元 | Codex CLI の組み込みレポートコマンド（存在する場合） |
| 出力形式 | 未確認 |
| 更新方法 | コマンド実行（現在セッション情報のみの可能性） |
| 長所 | 公式経路であれば安定性が高い |
| 短所 | 現セッションのみで履歴集計ができない可能性あり |

**不確実点（高）:**
- このようなコマンドが Codex CLI に存在するかどうか未確認
- 存在する場合も、当日集計か現セッションのみかが不明

---

## 最小 CLI モニター案

### 設計方針

- Python スクリプト 1 ファイル、標準ライブラリのみ（新規依存追加なし）
- `ccusage` は任意外部ツール: 利用可能であれば A-1 を採用し、そうでなければ A-2 に自動フォールバック
- Codex データが取得できない場合は `N/A` を表示し、`0` で誤魔化さない（M2）
- `os.system("clear")` + `print()` のみ（curses / rich 等不使用）
- 5 分（300 秒）ごとに自動更新、更新時刻のみ表示（カウントダウン・進捗バー等は不使用）

### 欠測値の表示方針（M2 反映）

データが取得できなかった場合の表示ルール:

| 状況 | 表示 |
|------|------|
| ccusage / 直接読取のどちらも失敗 | `N/A` |
| `~/.codex/` が存在しない | `N/A` |
| ログは存在するが解析失敗 | `N/A (parse error)` |
| 当日レコードが 0 件（実際に使用なし） | `0`（これは正常値） |

「0 件で使用なし」と「取得失敗」は区別して表示する。

### 表示レイアウト案

Codex データが取得できない場合:

```
AI Usage Monitor  (updated: 14:30)

Claude tokens (today)
  total:              142,384
  claude-opus-4-6:     98,234
  claude-sonnet-4-6:   44,150
  source:             ccusage

Codex sessions (today): N/A
  (log source unavailable — see ~/.codex/)
```

Codex データが取得できた場合:

```
AI Usage Monitor  (updated: 14:30)

Claude tokens (today)
  total:              142,384
  claude-opus-4-6:     98,234
  claude-sonnet-4-6:   44,150
  source:             direct (~/.claude/)

Codex sessions (today): 3
  latest:             14:12
```

### 疑似コード構造

```python
# 疑似コード（実装コードではない）

SENTINEL = "N/A"

def get_claude_usage() -> dict:
    # 1. ccusage が利用可能か試みる
    #    subprocess.run(["ccusage", ...], capture_output=True, timeout=10)
    #    成功: JSON parse して返す、source="ccusage"
    # 2. 失敗（FileNotFoundError / returncode != 0）:
    #    ~/.claude/projects/*/*.jsonl を glob
    #    当日タイムスタンプのレコードを集計して返す、source="direct"
    # 3. どちらも失敗: {"total": SENTINEL, "by_model": {}, "source": SENTINEL}
    pass

def get_codex_sessions() -> dict:
    # ~/.codex/ が存在しなければ {"count": SENTINEL, "latest": SENTINEL} を返す
    # 存在する場合: 当日セッションファイルを探して集計
    # parse 失敗: {"count": SENTINEL, "latest": "N/A (parse error)"}
    pass

def render(claude: dict, codex: dict) -> None:
    # os.system("clear")
    # 各項目を print()
    # SENTINEL 値はそのまま文字列として表示（0 に変換しない）
    pass

# メインループ
# while True:
#   render(get_claude_usage(), get_codex_sessions())
#   time.sleep(300)
```

---

## personal-mcp-core 統合の可能性

将来的には以下が考えられる（現時点では実装しない）:

- usage イベントを JSONL に記録し、event-contract-v1 形式で蓄積する
- `domain: "ai_usage"`, `kind: "token_summary"` 等のイベントとして append-only で保存
- MCP ツールとして `get_ai_usage_today` を expose する

これらは Issue #120 スコープ外であり、別 Issue として検討する。

---

## 実装に進む場合の追加確認事項

1. `ccusage --help` の出力を確認し、`--json` フラグと当日フィルタのフラグ名を特定する
2. `~/.claude/projects/` 配下の実際のファイル構造とフィールド名を確認する
3. `~/.codex/` が存在するか、ディレクトリ構造とファイル形式を確認する
4. キャッシュトークンの扱い方針を決定する（表示に含めるか）

---

## Blockers

| Blocker | 内容 | 影響度 | 対応案 |
|---------|------|--------|--------|
| `ccusage` JSON スキーマ未確認 | `--json` フラグ・出力フィールド名が不明 | 中 | Codex が `ccusage --help` を実行して確認 |
| `~/.claude/projects/` フォーマット未確認 | JSONL フィールド名・ネスト構造が非公式 | 中 | Codex が実ファイル先頭行を確認 |
| `~/.codex/` ログ存在未確認 | ディレクトリ自体が存在しない可能性あり | 高 | 存在しない場合は Codex 側を `N/A` 固定で実装開始、後から追加 |
| キャッシュトークン扱い未決定 | `cache_read_input_tokens` を合算するか方針決定が必要 | 低 | 実装時に Maintainer に確認 |
