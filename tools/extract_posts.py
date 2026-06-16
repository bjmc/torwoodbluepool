#!/usr/bin/env python3
"""Extract WordPress posts from wayback HTML files and generate Hugo posts."""

import re
import yaml
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
ARCHIVES = ROOT / "archives"
POSTS_DIR = ROOT / "content" / "posts"

POSTS = [
    {
        "file": "wayback-2010-04-15-more-pipes-found.html",
        "slug": "more-pipes-found-but-archives-draw-blank",
        "date": "2010-04-15",
        "title": "More Pipes Found But Archives Draw Blank So Far",
    },
    {
        "file": "wayback-2010-01-06-water-tank-theory.html",
        "slug": "water-tank-theory-abandoned",
        "date": "2010-01-06",
        "title": "Water Tank Theory Abandoned",
    },
    {
        "file": "wayback-2009-12-01-brick-arch-2nd-pipe.html",
        "slug": "brick-arch-and-2nd-pipe-found",
        "date": "2009-12-01",
        "title": "Brick Arch And 2nd Pipe Found",
    },
    {
        "file": "wayback-2009-10-15-few-more-facts.html",
        "slug": "few-more-facts-and-speculation",
        "date": "2009-10-15",
        "title": "Few More Facts And Speculation",
    },
    {
        "file": "wayback-2009-10-13-google-map.html",
        "slug": "google-map-of-torwood-blue-pool",
        "date": "2009-10-13",
        "title": "Google Map Of Torwood Blue Pool",
    },
    {
        "file": "wayback-2009-10-06-water-analysis.html",
        "slug": "torwood-blue-pool-water-analysis",
        "date": "2009-10-06",
        "title": "Torwood Blue Pool Water Analysis",
    },
    {
        "file": "wayback-2009-08-31-bottom-visible.html",
        "slug": "torwood-blue-pool-bottom-visible",
        "date": "2009-08-31",
        "title": "Torwood Blue Pool Bottom Visible",
    },
    {
        "file": "wayback-2009-08-26-arched-opening.html",
        "slug": "brick-arched-opening-confirmed",
        "date": "2009-08-26",
        "title": "Brick Arched Opening Confirmed",
    },
    {
        "file": "wayback-2009-08-24-water-sample.html",
        "slug": "water-sample-from-torwood-blue-pool",
        "date": "2009-08-24",
        "title": "Water Sample From Torwood Blue Pool",
    },
]


def extract_entry_content(html):
    """Extract article body text from a WordPress page, targeting div.entry-content."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "nav", "form"]):
        tag.decompose()
    entry = soup.find("div", class_="entry-content")
    if entry:
        return entry
    return None


def img_to_markdown(html_str):
    """Convert <img> tags within HTML string to Markdown image syntax."""
    def repl(m):
        tag = m.group(0)
        src_m = re.search(r'src="([^"]*)"', tag)
        alt_m = re.search(r'alt="([^"]*)"', tag)
        src = src_m.group(1) if src_m else ""
        alt = alt_m.group(1) if alt_m else ""
        # Extract just the filename
        src = src.split("/")[-1]
        return f'![{alt}](/img/{src})'
    return re.sub(r'<img[^>]*/?>', repl, html_str)


def entry_to_markdown(entry):
    """Convert WordPress entry-content HTML to Markdown."""
    lines = []

    for el in entry.children:
        tag = el.name if hasattr(el, "name") else None

        if tag is None:
            text = str(el).strip()
            if text:
                lines.append(text)
            continue

        if tag in ("p", "div"):
            inner = "".join(str(c) for c in el.contents)
            inner = img_to_markdown(inner)
            lines.append(inner)
        elif tag in ("h1", "h2", "h3", "h4"):
            lines.append(f"\n## {el.get_text(strip=True)}\n")
        elif tag == "hr":
            lines.append("\n---\n")
        elif tag == "ul":
            for li in el.find_all("li", recursive=False):
                li_html = "".join(str(c) for c in li.contents)
                li_html = img_to_markdown(li_html)
                lines.append(f"- {li_html}")
        elif tag == "ol":
            for li in el.find_all("li", recursive=False):
                li_html = "".join(str(c) for c in li.contents)
                li_html = img_to_markdown(li_html)
                lines.append(f"1. {li_html}")
        elif tag == "blockquote":
            for p in el.find_all("p"):
                p_html = "".join(str(c) for c in p.contents)
                p_html = img_to_markdown(p_html)
                lines.append(f"> {p_html}")
        elif tag in ("img",):
            src = el.get("src", "")
            alt = el.get("alt", "")
            src = src.split("/")[-1]
            if alt:
                lines.append(f"\n![{alt}](/img/{src})\n")
            else:
                lines.append(f"\n![](/img/{src})\n")
        else:
            text = el.get_text(strip=True)
            if text:
                lines.append(text)

    return "\n".join(lines)


def clean_markdown(md):
    """Clean up WordPress markup into clean Hugo Markdown."""
    # Replace WordPress image URLs with local /img/ paths
    md = re.sub(
        r'https?://[^"]*?wp-content/uploads/\d+/\d+/([^"\s]+)',
        r'/img/\1',
        md
    )
    md = re.sub(
        r"https?://[^']*?wp-content/uploads/\d+/\d+/([^'\s]+)",
        r"/img/\1",
        md
    )

    # Strip <p> and </p> tags
    md = re.sub(r"</?p[^>]*>", "\n\n", md)

    # Strip other HTML tags but keep their content
    md = re.sub(r"</?strong>", "**", md)
    md = re.sub(r"</?em>", "*", md)
    md = re.sub(r"</?br\s*/?>", "\n", md)
    md = re.sub(r"</?span[^>]*>", "", md)
    md = re.sub(r"</?div[^>]*>", "\n", md)

    # Clean up WordPress caption divs
    md = re.sub(
        r'\[/?caption[^]]*\]',
        "",
        md
    )

    # Remove style attributes
    md = re.sub(r'\sstyle="[^"]*"', "", md)
    md = re.sub(r"\sstyle='[^']*'", "", md)
    md = re.sub(r'\sclass="[^"]*"', "", md)
    md = re.sub(r"\sclass='[^']*'", "", md)
    md = re.sub(r'\salign="[^"]*"', "", md)
    md = re.sub(r"\s(title|alt|width|height|id|rel|target)='[^']*'", "", md)
    md = re.sub(r'\s(title|alt|width|height|id|rel|target)="[^"]*"', "", md)

    # Remove empty links
    md = re.sub(r'<a[^>]*></a>', "", md)

    # Convert remaining <a> tags
    def convert_link(m):
        text = m.group(1)
        href = m.group(2)
        # Fix Wayback Machine links
        href = re.sub(r"https?://web\.archive\.org/web/\d+im_/", "", href)
        href = re.sub(r"https?://web\.archive\.org/web/\d+/", "", href)
        return f"[{text}]({href})"
    md = re.sub(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", convert_link, md)

    # Normalize whitespace
    md = re.sub(r"\n{4,}", "\n\n\n", md)
    md = re.sub(r" +\n", "\n", md)

    # Decode HTML entities
    md = md.replace("&nbsp;", " ").replace("&amp;", "&")
    md = md.replace("&lt;", "<").replace("&gt;", ">")
    md = md.replace("&#8211;", "–").replace("&#8212;", "—")
    md = md.replace("&#8216;", "'").replace("&#8217;", "'")
    md = md.replace("&#8220;", "\"").replace("&#8221;", "\"")
    md = md.replace("&#038;", "&")

    return md.strip()


def main():
    print("=" * 72)
    print("Generating Hugo posts from Wayback WordPress archives")
    print("=" * 72)

    for post in POSTS:
        path = ARCHIVES / post["file"]
        slug = post["slug"]
        filepath = POSTS_DIR / f"{slug}.md"

        if not path.exists():
            print(f"  ❌ Missing: {post['file']}")
            continue

        if filepath.exists():
            print(f"  ⏭️  Exists: {slug}.md")
            continue

        html = path.read_text("utf-8", errors="replace")
        entry = extract_entry_content(html)

        if entry is None:
            print(f"  ⚠️  No entry-content found in {post['file']}")
            continue

        md = entry_to_markdown(entry)
        md = clean_markdown(md)

        front_matter = f"""+++
date = {post['date']}T00:00:00+00:00
draft = false
title = '{post["title"]}'
tags = ['Torwood']
[params]
  author = 'Nigel Turnbull'
+++
"""
        content = front_matter + md + "\n"

        filepath.write_text(content, encoding="utf-8")
        print(f"  ✅ Created: {slug}.md ({len(md)} chars)")

    print("\nDone!")


if __name__ == "__main__":
    main()
