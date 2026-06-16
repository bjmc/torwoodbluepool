#!/usr/bin/env python3
"""
Find images that exist in static/img/ but are never referenced in content,
and images referenced in original HTML pages but missing from our site.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "static" / "img"
CONTENT = ROOT / "content"
THEME = ROOT / "themes" / "torwood"
ARCHIVES = ROOT / "archives"

PAGE1 = ARCHIVES / (
    "Torwood Blue Pool — Investigation of a round brick lined "
    "blue pool at Torwood near Dunipace and Larbert.html"
)
PAGE2 = ARCHIVES / (
    "Torwood Blue Pool page 2 — Investigation of a round brick lined "
    "blue pool at Torwood near Dunipace and Larbert.html"
)


def all_img_refs_in_content():
    """Return set of image filenames referenced in our Markdown."""
    refs = set()
    for md_file in sorted(CONTENT.rglob("*.md")):
        text = md_file.read_text("utf-8", errors="replace")
        for m in re.finditer(r'/img/([^")\s]+)', text):
            refs.add(m.group(1))
    # Also check theme CSS
    for css_file in THEME.rglob("*.css"):
        text = css_file.read_text("utf-8", errors="replace")
        for m in re.finditer(r'url\(["\']?\.\./img/([^"\')\s]+)', text):
            refs.add(m.group(1))
    return refs


def all_static_images():
    """Return set of all image filenames in static/img/."""
    return {f.name for f in IMG.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif')}


def images_in_archive(html):
    """Return set of image filenames referenced in an archive HTML file."""
    refs = set()
    soup = BeautifulSoup(html, "lxml")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        fname = src.split("/")[-1]
        # Skip Wayback placeholders and non-image files
        if fname.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            refs.add(fname)
    return refs


def main():
    content_refs = all_img_refs_in_content()
    static_imgs = all_static_images()

    print("=" * 72)
    print("IMAGE AUDIT")
    print("=" * 72)

    # ---- Unused images in static/img/ ----
    unused = static_imgs - content_refs
    # Exclude the stone background (used in CSS)
    unused = {f for f in unused if f != "stone_background2.jpg"}

    if unused:
        print(f"\n📦 Images in static/img/ but NEVER referenced in content ({len(unused)}):")
        for f in sorted(unused):
            print(f"     - {f}")
    else:
        print(f"\n✅ All images in static/img/ are referenced somewhere")

    # ---- Images in page 1 not yet in our content ----
    p1 = images_in_archive(PAGE1.read_text("utf-8", errors="replace"))
    p2 = images_in_archive(PAGE2.read_text("utf-8", errors="replace"))
    all_archive = p1 | p2

    # For matching, strip WordPress size suffixes
    def basename(f):
        return re.sub(r'-\d+x\d+', '', Path(f).stem)

    content_basenames = {basename(f) for f in content_refs}

    missing_from_content = set()
    for f in sorted(all_archive):
        base = basename(f)
        if base not in content_basenames and f not in content_refs:
            missing_from_content.add(f)

    if missing_from_content:
        print(f"\n📸 Images in original HTML pages but NOT in our content ({len(missing_from_content)}):")
        for f in sorted(missing_from_content):
            # Check if it exists in static/img/ (copied but not referenced)
            exists = "✅ exists in static/img/" if f in static_imgs else "❌ not in static/img/"
            print(f"     - {f}  ({exists})")
    else:
        print(f"\n✅ All images from original pages are accounted for in our content")

    print()


if __name__ == "__main__":
    main()
