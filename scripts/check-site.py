#!/usr/bin/env python3
"""Check the built site: internal links, canonical/OpenGraph tags, sitemap, origin hygiene.

Runs against dist/ after `npm run build`, identically on a laptop and in CI:

    npm run build && python3 scripts/check-site.py

Every check reads the canonical origin from astro.config.ts through
scripts/sync-page-meta.py, so the hostname is written in exactly one place.
Exit status is the number of failing checks.
"""

from __future__ import annotations

import importlib.util
import pathlib
import posixpath
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

_spec = importlib.util.spec_from_file_location("sync_page_meta", ROOT / "scripts" / "sync-page-meta.py")
_sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sync)
SITE = _sync.site_origin()

SKIP_SCHEMES = ("mailto:", "tel:", "data:", "javascript:")
LINK_RE = re.compile(r'\b(?:href|src)="([^"]+)"')
TAG_RE = re.compile(r"<(?:link|meta)\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r'\b([a-zA-Z:-]+)="([^"]*)"')


def pages() -> list[pathlib.Path]:
    """Every built route. 404.html is not a route and carries no per-page metadata."""
    return sorted(DIST.rglob("index.html"))


def route_url(page: pathlib.Path) -> str:
    rel = page.relative_to(DIST).parent.as_posix()
    return SITE + "/" + ("" if rel == "." else rel + "/")


def tags(html: str) -> list[dict[str, str]]:
    return [dict(ATTR_RE.findall(tag)) for tag in TAG_RE.findall(html)]


def meta(parsed: list[dict[str, str]], key: str, attr: str) -> list[str]:
    return [t["content"] for t in parsed if t.get(attr) == key and "content" in t]


def resolve(target: str, page: pathlib.Path) -> pathlib.Path | None:
    """Map an internal URL path to the file that must exist in dist, or None if absent."""
    path = target if target.startswith("/") else posixpath.normpath(
        posixpath.join("/" + page.relative_to(DIST).parent.as_posix(), target)
    )
    base = DIST / path.lstrip("/")
    for candidate in (base, base / "index.html", base.with_name(base.name + ".html")):
        if candidate.is_file():
            return candidate
    return None


def check_links() -> list[str]:
    broken, checked = [], 0
    for page in sorted(DIST.rglob("*.html")):
        html = page.read_text(encoding="utf-8", errors="replace")
        for raw in LINK_RE.findall(html):
            target = raw.strip()
            if not target or target.startswith("#") or target.lower().startswith(SKIP_SCHEMES):
                continue
            if target.startswith("http://") or target.startswith("https://"):
                if not (target == SITE or target.startswith(SITE + "/")):
                    continue  # external, not ours to verify
                target = target[len(SITE):] or "/"
            target = target.split("#")[0].split("?")[0]
            if not target:
                continue
            checked += 1
            if resolve(target, page) is None:
                broken.append(f"{page.relative_to(DIST)} -> {raw}")
    print(f"a. links: {checked} internal references checked, {len(broken)} broken")
    for item in broken:
        print(f"     BROKEN {item}")
    if broken:
        return ["links: fix the hrefs above, or add the missing page, then rebuild"]
    return []


def check_metadata() -> list[str]:
    problems = []
    for page in pages():
        name = page.relative_to(DIST).parent.as_posix()
        html = page.read_text(encoding="utf-8", errors="replace")
        parsed = tags(html)
        canonicals = [t["href"] for t in parsed if t.get("rel") == "canonical" and "href" in t]
        if len(canonicals) != 1:
            problems.append(f"{name}: {len(canonicals)} <link rel=\"canonical\">, expected exactly 1")
            continue
        canonical = canonicals[0]
        if not canonical.startswith(SITE + "/"):
            problems.append(f"{name}: canonical {canonical} is not on {SITE}")
        for key in ("og:title", "og:description", "og:url", "og:image"):
            if not meta(parsed, key, "property"):
                problems.append(f"{name}: no {key}")
        if not meta(parsed, "twitter:card", "name"):
            problems.append(f"{name}: no twitter:card")
        og_url = meta(parsed, "og:url", "property")
        if og_url and og_url[0] != canonical:
            problems.append(f"{name}: og:url {og_url[0]} != canonical {canonical}")
        og_image = meta(parsed, "og:image", "property")
        if og_image:
            image = og_image[0]
            if not image.startswith(SITE + "/"):
                problems.append(f"{name}: og:image {image} is not absolute on {SITE}")
            elif not (DIST / image[len(SITE) + 1:]).is_file():
                problems.append(f"{name}: og:image {image} has no file in dist")
    print(f"b. canonical + OG: {len(pages())} pages checked, {len(problems)} problems")
    for item in problems:
        print(f"     {item}")
    if problems:
        return ["canonical/OG: run `python3 scripts/sync-page-meta.py` and rebuild"]
    return []


def check_sitemap() -> list[str]:
    index = DIST / "sitemap-index.xml"
    if not index.is_file():
        return ["sitemap: dist/sitemap-index.xml is missing — is @astrojs/sitemap registered in astro.config.ts?"]
    problems = []
    urls: set[str] = set()
    for loc in ET.parse(index).getroot().iter(f"{SITEMAP_NS}loc"):
        if not loc.text.startswith(SITE + "/"):
            problems.append(f"sitemap index entry {loc.text} is not on {SITE}")
            continue
        part = DIST / loc.text[len(SITE) + 1:]
        if not part.is_file():
            problems.append(f"sitemap index points at {loc.text}, which is not in dist")
            continue
        urls |= {u.text for u in ET.parse(part).getroot().iter(f"{SITEMAP_NS}loc")}

    off_site = sorted(u for u in urls if not u.startswith(SITE + "/"))
    problems += [f"sitemap URL {u} is not on {SITE}" for u in off_site]
    routes = {route_url(p) for p in pages()}
    problems += [f"in sitemap, not built: {u}" for u in sorted(urls - routes)]
    problems += [f"built, not in sitemap: {u}" for u in sorted(routes - urls)]

    robots = DIST / "robots.txt"
    expected = f"Sitemap: {SITE}/sitemap-index.xml"
    if not robots.is_file():
        problems.append("dist/robots.txt is missing")
    elif expected not in robots.read_text(encoding="utf-8").splitlines():
        problems.append(f"robots.txt has no `{expected}` line")

    print(f"c. sitemap: {len(urls)} URLs, {len(routes)} built routes, {len(problems)} problems")
    for item in problems:
        print(f"     {item}")
    if problems:
        return ["sitemap: rebuild; if a route is intentionally excluded, say so in astro.config.ts"]
    return []


def check_origin_hygiene() -> list[str]:
    needles = (b"vercel.app", b"localhost:4321")
    hits = []
    for base in ("src", "public", "dist"):
        for path in sorted((ROOT / base).rglob("*")):
            if not path.is_file():
                continue
            blob = path.read_bytes()
            for needle in needles:
                if needle in blob:
                    hits.append(f"{path.relative_to(ROOT)}: {needle.decode()}")
    print(f"d. origin hygiene: {len(hits)} stale-origin occurrences in src/, public/, dist/")
    for item in hits:
        print(f"     {item}")
    if hits:
        return [f"origin hygiene: replace with {SITE}; the origin is set once, in astro.config.ts"]
    return []


def main() -> int:
    if not DIST.is_dir():
        sys.exit("dist/ not found — run `npm run build` first.")
    print(f"checking {DIST.relative_to(ROOT)}/ against site = {SITE}\n")
    failures = check_links() + check_metadata() + check_sitemap() + check_origin_hygiene()
    print()
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        return len(failures)
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
