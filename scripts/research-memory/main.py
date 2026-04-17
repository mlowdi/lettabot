"""Research memory — ingest URLs, search them later.

A persistent SQLite + FTS5 database for storing and searching web content.
Liv uses this to remember interesting articles, blog posts, and research.

Usage:
    uv run --project scripts/research-memory research-memory ingest <url>
    uv run --project scripts/research-memory research-memory search <query>
    uv run --project scripts/research-memory research-memory get <id>
    uv run --project scripts/research-memory research-memory list
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import click
import httpx
from html_to_markdown import ConversionOptions, convert

# Default DB location — lettabot data dir or local fallback
DEFAULT_DB = Path.home() / ".local" / "share" / "lettabot" / "research.db"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

MD_OPTS = ConversionOptions(
    heading_style="atx",
    extract_metadata=False,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    fetched_at TEXT NOT NULL,
    raw_markdown TEXT NOT NULL,
    metadata_json TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_pages USING fts5(
    title,
    raw_markdown,
    content=pages,
    content_rowid=id
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages BEGIN
    INSERT INTO fts_pages (rowid, title, raw_markdown)
    VALUES (new.id, new.title, new.raw_markdown);
END;

CREATE TRIGGER IF NOT EXISTS pages_ad AFTER DELETE ON pages BEGIN
    INSERT INTO fts_pages (fts_pages, rowid, title, raw_markdown)
    VALUES ('delete', old.id, old.title, old.raw_markdown);
END;

CREATE TRIGGER IF NOT EXISTS pages_au AFTER UPDATE ON pages BEGIN
    INSERT INTO fts_pages (fts_pages, rowid, title, raw_markdown)
    VALUES ('delete', old.id, old.title, old.raw_markdown);
    INSERT INTO fts_pages (rowid, title, raw_markdown)
    VALUES (new.id, new.title, new.raw_markdown);
END;
"""


def _get_db(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _fetch_url(url: str) -> tuple[str, str, dict | None]:
    """Fetch URL, convert to markdown. Returns (title, markdown, metadata)."""
    resp = httpx.get(
        url,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()

    result = convert(resp.text, MD_OPTS)
    md = result.content

    # Try to extract title from metadata or first heading
    title = None
    if result.metadata and hasattr(result.metadata, "title"):
        title = result.metadata.title
    if not title:
        for line in md.split("\n"):
            line = line.strip()
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if not title:
        title = url.split("/")[-1] or url

    metadata = None
    if result.metadata:
        try:
            metadata = {
                k: str(v)
                for k, v in result.metadata.__dict__.items()
                if v is not None
            }
        except Exception:
            pass

    return title, md, metadata


@click.group()
@click.option("--db", "db_path", type=Path, default=None, help="Database path")
@click.pass_context
def cli(ctx: click.Context, db_path: Path | None) -> None:
    """Research memory — ingest URLs, search them later."""
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db_path


@cli.command()
@click.argument("url")
@click.pass_context
def ingest(ctx: click.Context, url: str) -> None:
    """Fetch a URL and store it in the research database."""
    conn = _get_db(ctx.obj.get("db_path"))

    # Check if already stored
    existing = conn.execute("SELECT id FROM pages WHERE url = ?", (url,)).fetchone()
    if existing:
        # Update existing entry
        try:
            title, md, metadata = _fetch_url(url)
            fetched_at = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "UPDATE pages SET title=?, fetched_at=?, raw_markdown=?, metadata_json=? WHERE url=?",
                (title, fetched_at, md, json.dumps(metadata) if metadata else None, url),
            )
            conn.commit()
            click.echo(f"Updated page {existing['id']}: {title}")
        except Exception as e:
            click.echo(f"Error updating {url}: {e}", err=True)
            raise SystemExit(1)
    else:
        try:
            title, md, metadata = _fetch_url(url)
            fetched_at = datetime.now(timezone.utc).isoformat()
            cursor = conn.execute(
                "INSERT INTO pages (url, title, fetched_at, raw_markdown, metadata_json) VALUES (?, ?, ?, ?, ?)",
                (url, title, fetched_at, md, json.dumps(metadata) if metadata else None),
            )
            conn.commit()
            click.echo(f"Ingested page {cursor.lastrowid}: {title}")
        except Exception as e:
            click.echo(f"Error ingesting {url}: {e}", err=True)
            raise SystemExit(1)

    conn.close()


@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=10, help="Max results")
@click.pass_context
def search(ctx: click.Context, query: str, limit: int) -> None:
    """Full-text search across stored pages."""
    conn = _get_db(ctx.obj.get("db_path"))

    results = conn.execute(
        """
        SELECT p.id, p.url, p.title, p.fetched_at, snippet(fts_pages, 1, '>>>', '<<<', '...', 30) as snippet
        FROM fts_pages f
        JOIN pages p ON p.id = f.rowid
        WHERE fts_pages MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()

    if not results:
        click.echo("No results found.")
        conn.close()
        return

    for row in results:
        click.echo(f"---\nID: {row['id']}")
        click.echo(f"Title: {row['title']}")
        click.echo(f"URL: {row['url']}")
        click.echo(f"Fetched: {row['fetched_at']}")
        click.echo(f"Snippet: {row['snippet']}")

    click.echo(f"\n{len(results)} result(s) found.")
    conn.close()


@cli.command()
@click.argument("page_id", type=int)
@click.pass_context
def get(ctx: click.Context, page_id: int) -> None:
    """Retrieve a stored page by ID."""
    conn = _get_db(ctx.obj.get("db_path"))

    row = conn.execute("SELECT * FROM pages WHERE id = ?", (page_id,)).fetchone()
    if not row:
        click.echo(f"Page {page_id} not found.", err=True)
        raise SystemExit(1)

    click.echo(f"ID: {row['id']}")
    click.echo(f"Title: {row['title']}")
    click.echo(f"URL: {row['url']}")
    click.echo(f"Fetched: {row['fetched_at']}")
    click.echo(f"---")
    click.echo(row["raw_markdown"])
    conn.close()


@cli.command("list")
@click.option("--limit", "-n", default=20, help="Max results")
@click.pass_context
def list_pages(ctx: click.Context, limit: int) -> None:
    """List all stored pages."""
    conn = _get_db(ctx.obj.get("db_path"))

    results = conn.execute(
        "SELECT id, url, title, fetched_at FROM pages ORDER BY fetched_at DESC LIMIT ?",
        (limit,),
    ).fetchall()

    if not results:
        click.echo("No pages stored yet.")
        conn.close()
        return

    for row in results:
        click.echo(f"  {row['id']:>4}  {row['title'][:60]:<60}  {row['fetched_at'][:10]}")

    click.echo(f"\n{len(results)} page(s).")
    conn.close()


if __name__ == "__main__":
    cli()
