#!/usr/bin/env python3
"""Refresh official HTML snapshots, index options, or read a selected section."""

import argparse
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://imagemagick.org/"
TOOLS = (
    "magick magick-script animate compare composite conjure display identify "
    "import mogrify montage stream"
).split()
TOPICS = (
    "command-line-tools command-line-processing command-line-options formats "
    "defines escape color color-management compose fx magick-vector-graphics "
    "quantize gradient clahe connected-components convex-hull color-thresholding "
    "high-dynamic-range multispectral-imagery motion-picture webp jp2 miff "
    "resources security-policy architecture porting cipher magick-cache "
    "distribute-pixel-cache openmp opencl license"
).split()


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.parts = []
        self.anchors = {}
        self.links = []
        self.tool_links = set()
        self.in_term = False
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "main":
            self.active = True
        if not self.active:
            return
        if tag in ("script", "style"):
            self.skip += 1
        if self.skip:
            return
        if tag in ("h1", "h2", "h3", "h4", "p", "div", "pre", "tr", "dt", "dd", "li", "br"):
            self.parts.append("\n")
        if tag in ("h1", "h2", "h3", "h4"):
            self.parts.append("#" * int(tag[1]) + " ")
        if "id" in attrs:
            self.anchors[attrs["id"]] = len(self.parts)
        if tag == "dt":
            self.in_term = True
        if tag in ("td", "th"):
            self.parts.append(" | ")
        if tag == "a":
            href = attrs.get("href", "")
            self.links.append(href)
            if self.in_term and href.startswith("/") and "#" not in href:
                self.tool_links.add(href.strip("/"))
        if tag == "img":
            self.parts.append(" [Image: " + attrs.get("alt", "") + " " + urljoin(BASE, attrs.get("src", "")) + "] ")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
            return
        if not self.active or self.skip:
            return
        if tag == "a" and self.links:
            href = self.links.pop()
            if href:
                self.parts.append(" [" + href + "]")
        if tag == "dt":
            self.in_term = False
        if tag in ("h1", "h2", "h3", "h4", "p", "pre", "tr", "dt", "dd", "li"):
            self.parts.append("\n")
        if tag == "main":
            self.active = False

    def handle_data(self, data):
        if self.active and not self.skip:
            self.parts.append(data)

    def text(self, anchor=None):
        start, end = 0, len(self.parts)
        if anchor:
            if anchor not in self.anchors:
                raise ValueError(f"Unknown section: {anchor}")
            start = self.anchors[anchor]
            # Sections end at the next heading, not at nested anchors or links.
            end = next((i for i in range(start + 1, end)
                        if re.fullmatch(r"#{1,4} ", self.parts[i])), end)
        return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", "".join(self.parts[start:end])).strip()


def parse(path):
    doc = Document()
    doc.feed(path.read_text(encoding="utf-8"))
    if not doc.parts:
        raise ValueError(f"No official document body in {path}")
    return doc


def refresh(no_proxy):
    target = ROOT / "references" / "official"
    # Fetch and validate every page before replacing the existing snapshot.
    with tempfile.TemporaryDirectory(prefix="imagemagick-docs-") as temporary:
        staging = Path(temporary)
        for page in TOPICS + TOOLS:
            command = ["curl", "--silent", "--show-error", "--fail", "--location", "--max-time", "45"]
            if no_proxy:
                command += ["--noproxy", "*"]
            subprocess.run(command + [BASE + page + "/", "--output", str(staging / (page + ".html"))], check=True)
            parse(staging / (page + ".html"))
            print(f"Fetched {page}", flush=True)
        found = parse(staging / "command-line-tools.html").tool_links
        if found != set(TOOLS):
            raise ValueError(f"Tool inventory differs: {sorted(found)}")
        options = parse(staging / "command-line-options.html")
        if len(options.anchors) < 200:
            raise ValueError("Incomplete option reference")
        target.mkdir(parents=True, exist_ok=True)
        for path in staging.iterdir():
            (target / path.name).write_bytes(path.read_bytes())
        lines = ["# Official Reference Index", "", f"Retrieved: {date.today().isoformat()}",
                 f"Source: {BASE}command-line-tools/", "",
                 "Official HTML is retained in full, including tables, anchors and license links.",
                 "Read one page or option with `python3 scripts/official_docs.py read PAGE [ANCHOR]`.",
                 "Arguments use page names without `.html`; anchors have no leading `#`.",
                 "Examples: `read command-line-options resize`; `read formats`; `read defines`.",
                 "Reference links inside extracted text are relative to https://imagemagick.org/.",
                 "The website may describe a newer release than the installed binary.", "", "## Tools", ""]
        lines += [f"- [{page}](official/{page}.html) | {BASE}{page}/" for page in TOOLS]
        lines += ["", "## Topics", ""]
        lines += [f"- [{page}](official/{page}.html) | {BASE}{page}/" for page in TOPICS]
        lines += ["", f"## Option Anchors ({len(options.anchors)})", ""]
        lines += [f"- `{anchor}`: [official section](official/command-line-options.html#{anchor})"
                  for anchor in options.anchors]
        (ROOT / "references" / "official-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Validated {len(TOOLS)} tools, {len(TOPICS) + len(TOOLS)} pages, {len(options.anchors)} option anchors.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    update = sub.add_parser("refresh")
    update.add_argument("--no-proxy", action="store_true")
    read = sub.add_parser("read")
    read.add_argument("page", choices=TOPICS + TOOLS)
    read.add_argument("anchor", nargs="?")
    args = parser.parse_args()
    if args.action == "refresh":
        refresh(args.no_proxy)
    else:
        print(parse(ROOT / "references" / "official" / (args.page + ".html")).text(args.anchor))


if __name__ == "__main__":
    main()
