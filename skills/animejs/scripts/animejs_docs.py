# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4>=4.12", "markdownify>=0.13"]
# ///
"""Read the live Anime.js documentation as Markdown.

  uv run animejs_docs.py --list              # every page path in the docs sidebar
  uv run animejs_docs.py --list timeline     # page paths containing "timeline"
  uv run animejs_docs.py scope/scope-methods/revert animation/tween-value-types
  uv run animejs_docs.py --html https://animejs.com/documentation/layout

Each page prints its breadcrumb, "Since" version, body text, parameter tables and
the JavaScript example (add --html for the example's markup too).
"""

import argparse
import sys
import urllib.request

from bs4 import BeautifulSoup
from markdownify import markdownify

BASE = "https://animejs.com/documentation"


def fetch(url: str) -> BeautifulSoup:
    request = urllib.request.Request(url, headers={"User-Agent": "regent-animejs-skill"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return BeautifulSoup(response.read(), "html.parser")


def page_url(ref: str) -> str:
    if ref.startswith("http"):
        return ref
    return f"{BASE}/{ref.strip('/').removeprefix('documentation/')}"


def list_pages(needle: str | None) -> None:
    soup = fetch(f"{BASE}/getting-started")
    seen = set()
    for link in soup.select("#docs-sidebar a.docs-link"):
        path = link["href"].removeprefix(BASE).strip("/")
        if path in seen or (needle and needle.lower() not in path):
            continue
        seen.add(path)
        print(f"{path}\t{link.get('title', '').strip()}")


def render(ref: str, with_html: bool) -> str:
    url = page_url(ref)
    soup = fetch(url)
    info = soup.select_one("#docs-info .docs-info.is-active")
    if info is None:
        raise SystemExit(f"no documentation article at {url}")

    parts = [f"<!-- {url} -->"]
    content = info.select_one(".docs-info-content")
    breadcrumb = content.select_one(".docs-breadcrumb")
    if breadcrumb:
        parts.append(" / ".join(p.get_text(" ", strip=True) for p in breadcrumb.find_all("p")))
        breadcrumb.decompose()
    parts.append(markdownify(str(content), heading_style="ATX", code_language="js").strip())

    for section in info.select("section.code-preview"):
        languages = ["js", "html"] if with_html else ["js"]
        for language in languages:
            block = section.select_one(f'pre[data-language="{language}"] code')
            if block:
                parts.append(f"```{language}\n{block.get_text().rstrip()}\n```")

    subpages = info.select("ul.links-list:not(.prev-next-links) a")
    if subpages:
        parts.append("In this section: " + ", ".join(a.get("title", "") for a in subpages))
    return "\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pages", nargs="*", help="page path under /documentation or a full URL")
    parser.add_argument("--list", nargs="?", const="", metavar="FILTER", help="list page paths")
    parser.add_argument("--html", action="store_true", help="include each example's HTML")
    args = parser.parse_args()

    if args.list is not None:
        list_pages(args.list or None)
        return
    if not args.pages:
        parser.print_help()
        sys.exit(2)
    print("\n\n---\n\n".join(render(ref, args.html) for ref in args.pages))


if __name__ == "__main__":
    main()
