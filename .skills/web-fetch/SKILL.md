---
name: web-fetch
description: Fetch a URL and convert it to clean markdown. Use when you need to read a webpage, article, or link.
---

# Web Fetch

Fetch any URL and get clean markdown back. Good for reading articles, blog posts, documentation, etc.

## When to use

- Someone shares a link and you want to read it
- You need to check what's at a URL
- Research task that requires reading web content

## Usage

```bash
uv run --project scripts/web-fetch scripts/web-fetch/main.py "<url>"
```

Run from the lettabot project root (`/home/mlf/projects/lettabot`).

## Examples

```bash
# Read a blog post
uv run --project scripts/web-fetch scripts/web-fetch/main.py "https://example.com/article"

# Read an arxiv paper abstract page
uv run --project scripts/web-fetch scripts/web-fetch/main.py "https://arxiv.org/abs/2401.00001"
```

## Notes

- Uses `html-to-markdown` (Rust-based, fast) via uv-managed Python
- ATX-style headings (# not underlines)
- Metadata extraction disabled for cleaner output
- 30 second timeout, follows redirects
- Outputs clean markdown to stdout
