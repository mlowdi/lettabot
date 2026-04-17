---
name: research-memory
description: Persistent research database. Ingest URLs, full-text search later. Use when you want to save or recall web content.
---

# Research Memory

A personal research database backed by SQLite + FTS5. Ingest URLs, search them later.

## When to use

- You read an interesting article and want to remember it
- Someone shares a link worth saving for later
- You want to recall something you've read before
- During heartbeats when reviewing RSS feeds

## Usage

All commands run from the lettabot project root. The Python wrapper is managed by uv.

```bash
# Ingest a URL (fetch, convert to markdown, store)
uv run --project scripts/research-memory python scripts/research-memory/main.py ingest "<url>"

# Search stored pages (full-text search with highlighting)
uv run --project scripts/research-memory python scripts/research-memory/main.py search "<query>"

# Get a specific page by ID (full markdown output)
uv run --project scripts/research-memory python scripts/research-memory/main.py get <id>

# List all stored pages
uv run --project scripts/research-memory python scripts/research-memory/main.py list
```

## Database location

Default: `~/.local/share/lettabot/research.db`

Override with `--db /path/to/custom.db` on any command.

## Examples

```bash
# Save an interesting blog post
uv run --project scripts/research-memory python scripts/research-memory/main.py ingest "https://example.com/article"

# Search for something you remember reading
uv run --project scripts/research-memory python scripts/research-memory/main.py search "agent runtime architecture"

# Re-ingest to update stale content (upserts automatically)
uv run --project scripts/research-memory python scripts/research-memory/main.py ingest "https://example.com/article"
```

## Notes

- Re-ingesting a URL updates the existing entry (upsert behavior)
- Full-text search uses SQLite FTS5 with snippet highlighting
- Markdown conversion uses the same `html-to-markdown` as web-fetch
- The database is a single file — easy to back up or migrate
