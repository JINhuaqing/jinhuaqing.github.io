#!/usr/bin/env python3
"""Merge bibliography/*.bib + _data/pub_*.yml -> _data/publications_generated.yml for Jekyll."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import bibtexparser
import yaml

ROOT = Path(__file__).resolve().parents[1]
BIB_DIR = ROOT / "bibliography"
DATA = ROOT / "_data"
OUT = DATA / "publications_generated.yml"


def initials(given: str) -> str:
    given = given.strip()
    if not given:
        return ""
    # Treat hyphens as word separators (e.g. Mi-Ok -> M.O.)
    tokens = [t for t in re.split(r"[\s\-]+", given) if t]
    return "".join(t[0] + "." for t in tokens)


def format_one_author(author: str) -> str:
    author = author.strip()
    co = False
    cor = False
    m = re.match(r"^(.+?)\+,\s*(.+)$", author)
    if m:
        family, given = m.group(1).strip(), m.group(2).strip()
        co = True
    else:
        m = re.match(r"^(.+?)\*,\s*(.+)$", author)
        if m:
            family, given = m.group(1).strip(), m.group(2).strip()
            cor = True
        else:
            m = re.match(r"^([^,]+),\s*(.+)$", author)
            if not m:
                return html.escape(author)
            family, given = m.group(1).strip(), m.group(2).strip()

    ini = initials(given)
    is_jin = family.lower() == "jin" and given.lower().startswith("huaqing")
    if is_jin:
        body = "<strong>Jin, H.</strong>"
    else:
        body = f"{html.escape(family)}, {html.escape(ini)}"
    if co:
        body += "<sup>+</sup>"
    if cor:
        body += "<sup>*</sup>"
    return body


def format_authors(raw: str) -> str:
    parts = re.split(r"\s+and\s+", raw.replace("\n", " "))
    return ", ".join(format_one_author(p) for p in parts if p.strip())


def venue_parts(entry: dict) -> tuple[str, str]:
    """Return (journal_or_booktitle, volume_pages_suffix)."""
    et = entry.get("ENTRYTYPE", "").lower()
    if et == "inproceedings":
        j = entry.get("booktitle", "").strip()
    else:
        j = entry.get("journal", "").strip()
    j = re.sub(r"\{([^}]+)\}", r"\1", j)
    vol = entry.get("volume", "").strip()
    num = entry.get("number", "").strip()
    pages = entry.get("pages", "").strip()
    bits = []
    if vol:
        bits.append(vol + (f"({num})" if num else ""))
    if pages:
        bits.append(pages)
    suffix = ", ".join(bits) if bits else ""
    return j, suffix


def load_all_entries() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name in ("publications.bib", "manuscripts.bib"):
        path = BIB_DIR / name
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            db = bibtexparser.loads(
                f.read(),
                bibtexparser.bparser.BibTexParser(
                    common_strings=True, ignore_nonstandard_types=False
                ),
            )
        for e in db.entries:
            out[e["ID"].lower()] = e
    return out


def build_item(key: str, entries: dict[str, dict], overrides: dict) -> dict | None:
    k = key.lower()
    if k not in entries:
        print(f"Warning: missing bib entry for key {key!r}", file=sys.stderr)
        return None
    e = entries[k]
    ovr = overrides.get(k, overrides.get(key, {}))
    auth = format_authors(e.get("author", ""))
    title = html.escape(re.sub(r"\{([^}]+)\}", r"\1", e.get("title", "").replace("\n", " ")))
    journal, volpages = venue_parts(e)
    journal_esc = html.escape(journal)
    year = str(e.get("year", "")).strip()
    title_url = ovr.get("title_url") or e.get("url") or e.get("doi")
    if title_url and str(title_url).startswith("10."):
        title_url = "https://doi.org/" + str(title_url)
    status = ovr.get("status", "").strip()

    links: list[dict[str, str]] = []
    if ovr.get("pdf"):
        links.append({"label": "PDF", "url": str(ovr["pdf"])})
    if ovr.get("supp"):
        links.append({"label": "Supp", "url": str(ovr["supp"])})
    if ovr.get("code"):
        links.append({"label": "Code", "url": str(ovr["code"])})
    for extra in ovr.get("links") or []:
        if isinstance(extra, dict) and extra.get("url"):
            links.append({"label": str(extra.get("label", "link")), "url": str(extra["url"])})

    venue_html = f"<em>{journal_esc}</em>"
    if volpages:
        venue_html += f", {html.escape(volpages)}"
    if year:
        venue_html += f", {html.escape(year)}"

    return {
        "id": k,
        "authors_html": auth,
        "title": title,
        "title_url": title_url or None,
        "venue_html": venue_html,
        "status": status or None,
        "links": links,
    }


def main() -> None:
    entries = load_all_entries()
    with open(DATA / "pub_categories.yml", encoding="utf-8") as f:
        cats = yaml.safe_load(f)
    ovr_path = DATA / "pub_overrides.yml"
    overrides_all = {}
    if ovr_path.exists():
        with open(ovr_path, encoding="utf-8") as f:
            overrides_all = {str(k).lower(): v for k, v in yaml.safe_load(f).items()}

    manuscripts = []
    for key in cats.get("manuscripts", []):
        item = build_item(key, entries, overrides_all)
        if item:
            manuscripts.append(item)

    pub_sections = []
    for block in cats.get("publications", []):
        title = block.get("title", "")
        items = []
        for key in block.get("keys", []):
            item = build_item(key, entries, overrides_all)
            if item:
                items.append(item)
        pub_sections.append({"title": title, "items": items})

    out_doc = {"manuscripts": manuscripts, "publications": pub_sections}
    with open(OUT, "w", encoding="utf-8") as f:
        yaml.dump(
            out_doc,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=4096,
        )
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(manuscripts)} manuscripts, {len(pub_sections)} publication sections)")


if __name__ == "__main__":
    main()
