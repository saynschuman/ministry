#!/usr/bin/env python3
"""
Simple script to fetch a web page and print its content.

Usage:
  python3 fetch_psalm.py                          # fetch default URL, print cleaned text
  python3 fetch_psalm.py --raw                    # print raw HTML
  python3 fetch_psalm.py --selector 'main'        # extract specific CSS selector
  python3 fetch_psalm.py https://example.com      # fetch a custom URL

Dependencies:
  - requests (required)
  - beautifulsoup4 (optional; for better text extraction)
"""

import argparse
import sys
from typing import Optional

try:
    import requests
except ImportError:
    print(
        "Missing dependency: requests. Install with 'pip install requests'",
        file=sys.stderr,
    )
    sys.exit(2)


def fetch(url: str, timeout: int = 20) -> requests.Response:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0 Safari/537.36 requests-script"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en,ru;q=0.9,uk;q=0.8",
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    # Improve encoding detection
    if not resp.encoding:
        try:
            resp.encoding = resp.apparent_encoding or "utf-8"
        except Exception:
            resp.encoding = "utf-8"
    return resp


def extract_text(html: str, selector: Optional[str] = None) -> str:
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception:
        # Fallback: return raw HTML if bs4 isn't available
        return html

    soup = BeautifulSoup(html, "html.parser")
    node = None
    if selector:
        try:
            node = soup.select_one(selector)
        except Exception:
            node = None

    if node is None:
        # Try common content containers before falling back to full-page text
        for sel in ("main", "article", "[role=main]", ".content", "#content"):
            node = soup.select_one(sel)
            if node is not None:
                break

    target = node if node is not None else soup
    text = target.get_text(separator="\n", strip=True)
    # Collapse excessive blank lines
    lines = [ln for ln in (ln.strip() for ln in text.splitlines()) if ln]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a web page and print its content")
    parser.add_argument(
        "url",
        nargs="?",
        default="https://ministry.saynschuman.pp.ua/psalm/849/",
        help="URL to fetch (default: psalm 849)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw HTML instead of extracted text",
    )
    parser.add_argument(
        "--selector",
        help="Optional CSS selector to narrow content extraction",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Request timeout in seconds (default: 20)",
    )

    args = parser.parse_args()

    try:
        resp = fetch(args.url, timeout=args.timeout)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {args.url}: {e}", file=sys.stderr)
        return 1

    if args.raw:
        print(resp.text)
    else:
        content = extract_text(resp.text, selector=args.selector)
        print(content)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
