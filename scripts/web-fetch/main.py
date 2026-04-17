"""Fetch a URL and convert it to clean markdown.

Usage: uv run main.py <url>
"""

import sys

import httpx
from html_to_markdown import ConversionOptions, convert


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

MD_OPTS = ConversionOptions(
    heading_style="atx",
    extract_metadata=False,
)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run main.py <url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]

    try:
        resp = httpx.get(
            url,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=30,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = convert(resp.text, MD_OPTS)
    except Exception as e:
        print(f"Error converting to markdown: {e}", file=sys.stderr)
        sys.exit(1)

    print(result.content)


if __name__ == "__main__":
    main()
