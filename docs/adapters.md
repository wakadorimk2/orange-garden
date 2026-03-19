# Adapters

Adapters translate between external protocols and `personal_mcp.core` functions.
Current external input surfaces are not all adapters: some integrations are
implemented as tool-layer CLI entry points instead.

## Naming convention

```
src/personal_mcp/adapters/<name>.py
```

Each adapter file should expose a single public function named `get_<name>_context()`
or similar. Keep adapters thin — no business logic, only protocol translation.

## Current adapters

| Adapter | File | Status |
|---------|------|--------|
| MCP (base) | `adapters/mcp_server.py` | Placeholder |
| HTTP (mobile log form) | `adapters/http_server.py` | MVP (Issue #145) |

These are the only runtime adapters currently shipped.

## Current external input surfaces

| Surface | Entry point | Implementation | Status |
|---|---|---|---|
| MCP context | internal | `adapters/mcp_server.py` | Placeholder |
| HTTP mobile log form | `web-serve` | `adapters/http_server.py` | MVP |
| GitHub manual sync MVP | `github-sync` | `tools/github_sync.py` | Implemented |
| GitHub richer ingest | `github-ingest` | `tools/github_ingest.py` | Implemented |
| Local client log watcher | `poe2-watch` | `tools/poe2_client_watcher.py` | Implemented |

GitHub ingest is intentionally listed here as an external input surface rather
than an adapter. In the current runtime, GitHub is handled by tool-layer CLI
commands that fetch and normalize events before writing through the storage
boundary.

## Frontend build artifact handoff contract

`pnpm build` in `frontend/` outputs artifacts to `src/personal_mcp/web/app/`
(configured in `frontend/vite.config.ts`).

| 項目 | 値 |
|------|-----|
| Vite `outDir` | `../src/personal_mcp/web/app` |
| Python package 内パス | `personal_mcp/web/app/` |
| Git 管理 | 除外（`.gitignore: src/personal_mcp/web/app/`） |
| package-data | `pyproject.toml: "web/app/**"` |
| Vite `base` | `/app/` |
| `emptyOutDir` | `true`（ビルドごとに outDir 配下をクリアし stale artifact を除去する） |

**`web/app/` は generated artifact** — 以下の制約に注意:

- `pip wheel` / `python -m build` 前に必ず `pnpm build` を実行すること
- ビルド未実施のまま `pip wheel` / `python -m build` / non-editable な `pip install .` を実行すると、packaging は `run pnpm build in frontend/ first` を含む明示的エラーで停止する
- `make frontend-check` でビルド成果物の存在を事前確認できる

Python 側で `/app/` を配信する際は `importlib.resources.files("personal_mcp").joinpath("web/app")` を起点として読む。
`/app/` 配信ロジックの runtime 実装はこのドキュメントのスコープ外（将来の別 PR で実装）。

## Adding a new adapter

1. Create `src/personal_mcp/adapters/<name>.py`
2. Implement the interface function (see template below)
3. Add an entry to the table above
4. Wire it into `server.py` if needed

### Template

```python
# src/personal_mcp/adapters/<name>.py
from personal_mcp.core.guide import load_ai_guide


def get_<name>_context() -> str:
    """
    Context payload for <name> integration.
    Extend this function as the adapter grows.
    """
    return load_ai_guide()
```

## Planned adapters

- **poe2**: Path of Exile 2 session context (character state, current goals)
- **daily-log**: Daily log entry template and routing
- **habit**: Habit tracking app integration

These are placeholders. Implement only when the need is concrete.
