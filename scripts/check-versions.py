#!/usr/bin/env python3
"""Enforce scripts/release-facts.json against src/content/docs/.

    python3 scripts/check-versions.py

Every rule here is deterministic and file-scoped. The script never decides whether
a sentence is qualified enough or whether a version has a good reason to stay —
those judgements live in release-facts.json, which is the artifact a human reviews.
Exit status is the number of failing checks.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "src" / "content" / "docs"
FACTS = json.loads((ROOT / "scripts" / "release-facts.json").read_text())

# A trailing period ends a sentence far more often than it continues a version, so the
# lookahead rejects only a fourth numeric component — "shipped in 0.4.2." must be caught.
VERSION_RE = re.compile(r"(?<![\w.])v?(\d+\.\d+\.\d+)(?!\.?\d)(?!\w)")
NOT_PRODUCT = [re.compile(p) for p in FACTS["not_a_product_version"]]
FENCE_RE = re.compile(r"^\s*```")

failures: list[str] = []


def fail(check: str, detail: str) -> None:
    failures.append(f"{check}: {detail}")


def pages() -> dict[str, str]:
    return {p.relative_to(DOCS).as_posix(): p.read_text() for p in sorted(DOCS.rglob("*.mdx"))}


def split_fences(text: str) -> tuple[str, str]:
    """(prose, fenced) — every line of the file, partitioned by fenced code block."""
    prose, fenced, inside = [], [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            inside = not inside
            continue
        (fenced if inside else prose).append(line)
    return "\n".join(prose), "\n".join(fenced)


def norm(text: str) -> str:
    return " ".join(text.split())


def product_versions(text: str) -> set[str]:
    """Every product-version occurrence, skipping the environment a transcript prints."""
    found = set()
    for line in text.splitlines():
        for match in VERSION_RE.finditer(line):
            before = line[: match.start()]
            if any(rule.search(before) for rule in NOT_PRODUCT):
                continue
            found.add(match.group(1))
    return found


def main() -> int:
    docs = pages()
    current = FACTS["current_release"]
    split = {name: split_fences(body) for name, body in docs.items()}

    # a. Transcripts state the current release, and nothing else.
    for name, (_, fenced) in split.items():
        for found in sorted(product_versions(fenced)):
            if found != current:
                fail("a. transcripts", f"{name}: fenced block states {found}, not {current}")
    for name in FACTS["current_transcripts"]:
        if name not in split:
            fail("a. transcripts", f"{name}: listed in current_transcripts but does not exist")
        elif current not in split[name][1]:
            fail(
                "a. transcripts",
                f"{name}: no captured transcript states {current} — recapture it",
            )

    # b. Every product-version occurrence in prose is allowlisted.
    allowed: dict[str, set[str]] = {}
    for entry in FACTS["version_allowlist"]:
        if entry["tracks_current"] and entry["value"] != current:
            fail(
                "b. allowlist",
                f"{entry['file']}: entry pinned to {entry['value']} tracks the current "
                f"release, which is {current} — update the allowlist and the page",
            )
        allowed.setdefault(entry["file"], set()).add(entry["value"])
    for name, (prose, _) in split.items():
        for found in sorted(product_versions(prose)):
            if found not in allowed.get(name, set()):
                fail(
                    "b. allowlist",
                    f"{name}: {found} in prose with no allowlist entry",
                )
    for name, values in allowed.items():
        if name not in split:
            fail("b. allowlist", f"{name}: allowlisted but does not exist")
            continue
        for value in values:
            if value not in product_versions(split[name][0]):
                fail("b. allowlist", f"{name}: allowlists {value}, which the page no longer uses")

    # c. Evidence links stay pinned.
    for entry in FACTS["pinned_links"]:
        body = docs.get(entry["file"], "")
        if entry["must_contain"] not in body:
            fail("c. pinned links", f"{entry['file']}: lost {entry['must_contain']}")

    # d. The controlled-replay paragraph is complete wherever its figures appear.
    paragraph = norm(FACTS["replay_paragraph"])
    for name, body in docs.items():
        hits = [f for f in FACTS["replay_figures"] if f in body]
        if hits and paragraph not in norm(body):
            fail(
                "d. replay paragraph",
                f"{name}: carries {hits} without the complete paragraph verbatim",
            )

    # e. Measured timing and cost figures live on the Measurements page only.
    permitted = set(FACTS["timing_figure_pages"])
    patterns = [re.compile(p) for p in FACTS["timing_figure_patterns"]]
    for name, (prose, _) in split.items():
        if name in permitted:
            continue
        for pattern in patterns:
            for hit in pattern.findall(prose):
                fail("e. timing figures", f"{name}: {hit!r} belongs on {sorted(permitted)[0]}")

    # f. PubMed: the known misleading phrasing is gone, the not-built fact is present.
    for name in FACTS["pubmed_pages"]:
        body = docs.get(name)
        if body is None:
            fail("f. pubmed", f"{name}: listed but does not exist")
            continue
        for phrase in FACTS["pubmed_forbidden"]:
            if phrase in body:
                fail("f. pubmed", f"{name}: carries forbidden phrasing {phrase!r}")
        if not any(phrase in body for phrase in FACTS["pubmed_required_any"]):
            fail("f. pubmed", f"{name}: never states that PubMed retrieval is not built")

    labels = [
        "a. transcripts state the current release",
        "b. prose versions are allowlisted",
        "c. evidence links stay pinned",
        "d. the replay paragraph is complete",
        "e. timing figures are centralized",
        "f. PubMed is not presented as retrieval",
    ]
    print(f"checking src/content/docs/ against release-facts.json, current_release = {current}\n")
    for label in labels:
        hit = [f for f in failures if f.startswith(label[:2])]
        print(f"{label}: {len(hit)} problem(s)")
        for problem in hit:
            print(f"    {problem}")
    print()
    print("all checks passed" if not failures else f"{len(failures)} problem(s)")
    return len(failures)


if __name__ == "__main__":
    sys.exit(main())
