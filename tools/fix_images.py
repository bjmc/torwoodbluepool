#!/usr/bin/env python3
"""
Fix image references in extracted posts:
1. Convert raw <img> HTML tags to Markdown syntax
2. Strip WordPress size suffixes (-300x225 etc.)
3. Handle special-case images (rename, remove if unavailable)
4. Fix broken markdown artifacts
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"
IMG_DIR = ROOT / "static" / "img"

# Images we don't have (Wayback placeholders or unarchived)
UNAVAILABLE = {
    "Brick-arch-exposed",      # no archive copy
    "overflowsw",              # was suspendedpage_005.cgi (Wayback placeholder)
    "overflowse",              # was suspendedpage_006.cgi (Wayback placeholder)
    "pipe",                    # no matching original found
}

# Manual remaps for specific WordPress → original filename
REMAP = {
    "Brick-arch-exposed": "arch",   # Use arch.jpg instead
}


def fix_post(filepath):
    """Fix all image issues in a single post file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = []

    # 1. Fix broken markdown artifact: [/img/3brick.jpg](<img src="/img/..."/>)
    #    This happens when WordPress caption HTML gets mangled
    content = re.sub(
        r'\[/img/[^]]*\]\(<img[^>]*src="([^"]*)"[^>]*/>\)',
        r'![](\1)',
        content
    )

    # 2. Convert raw <img> tags to Markdown - handle alt/src in any order
    def img_to_md(match):
        tag = match.group(0)
        # Extract src
        src_m = re.search(r'src="([^"]*)"', tag)
        # Extract alt
        alt_m = re.search(r'alt="([^"]*)"', tag)
        src = src_m.group(1) if src_m else ""
        alt = alt_m.group(1) if alt_m else ""
        return f'![{alt}]({src})'

    content = re.sub(
        r'<img[^>]*/?>',
        img_to_md,
        content
    )

    # 3. Fix WordPress thumbnail sizes: strip -300x225, -150x150 etc.
    def fix_filename(match):
        prefix = match.group(1)
        name = match.group(2)
        suffix = match.group(3) if match.group(3) else ""
        ext = match.group(4)

        # Handle remaps
        if name in REMAP:
            name = REMAP[name]

        # If the image is unavailable, return a comment
        if name in UNAVAILABLE:
            changes.append(f"  🚫 Removed unavailable image: {name}")
            return f'*[Image: {name} — not available in archives]*'

        # Try exact match first
        exact = f"{name}{suffix}{ext}"
        if (IMG_DIR / exact).exists():
            return f"{prefix}{exact}"

        # Try without suffix
        no_suffix = f"{name}{ext}"
        if (IMG_DIR / no_suffix).exists():
            changes.append(f"  📎 {name}{suffix}{ext} → {no_suffix}")
            return f"{prefix}{no_suffix}"

        changes.append(f"  ❓ {name}{suffix}{ext} — not found in img/")
        return f"{prefix}{exact}"

    content = re.sub(
        r'(/img/)([a-zA-Z0-9_-]+?)(-[0-9]+x[0-9]+)?(\.[a-z]+)',
        fix_filename,
        content
    )

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, changes
    return False, changes


def main():
    print("=" * 72)
    print("Fixing image references in extracted posts")
    print("=" * 72)

    total_fixed = 0
    for md_file in sorted(POSTS_DIR.glob("*.md")):
        fixed, changes = fix_post(md_file)
        if fixed:
            print(f"\n📄 {md_file.name}")
            for c in changes:
                print(c)
            total_fixed += 1

    print(f"\nFixed {total_fixed} post(s)")
    print("Done!")


if __name__ == "__main__":
    main()
