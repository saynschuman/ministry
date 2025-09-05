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
import re
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


def fetch_html(url: str, timeout: int = 20, force_encoding: Optional[str] = None) -> str:
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

    raw = resp.content

    # 1) If user forces an encoding, use it
    if force_encoding:
        try:
            return raw.decode(force_encoding, errors="strict")
        except Exception:
            return raw.decode(force_encoding, errors="replace")

    # 2) Try to detect from HTML meta in the first chunk
    head = raw[:4096]
    m = re.search(rb"charset\s*=\s*['\"]?([A-Za-z0-9_\-]+)", head, re.IGNORECASE)
    meta_enc = m.group(1).decode("ascii", "ignore").lower() if m else None

    # 3) Decide best encoding: prefer meta, else requests' guess, else apparent
    enc = meta_enc or (resp.encoding.lower() if resp.encoding else None)
    apparent = None
    try:
        apparent = (resp.apparent_encoding or "").lower()
    except Exception:
        apparent = None

    # 4) If server says latin-1/iso-8859-1 but apparent/ meta suggests utf-8, prefer that
    if enc in {"iso-8859-1", "latin-1", "windows-1252", "cp1252"} and apparent:
        enc = apparent

    if not enc:
        enc = apparent or "utf-8"

    try:
        return raw.decode(enc, errors="strict")
    except Exception:
        # Last resort: utf-8 with replacement
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:
            return raw.decode(errors="replace")


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
    parser.add_argument(
        "--encoding",
        type=str,
        help="Force a specific text encoding (e.g., utf-8)",
    )

    args = parser.parse_args()

    try:
        html = fetch_html(args.url, timeout=args.timeout, force_encoding=args.encoding)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {args.url}: {e}", file=sys.stderr)
        return 1

    if args.raw:
        print(html)
    else:
        content = extract_text(html, selector=args.selector)
        print(content)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
