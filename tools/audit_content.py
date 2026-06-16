#!/usr/bin/env python3
"""
Audit: compare our Hugo content against the two original hand-coded HTML pages.
Finds:
1. Sections of text in the originals not present in any Hugo page/post
2. Introductory/home content that should be on the main page
3. Image references in originals that have no match in static/img/
4. Thumbnail images where a full-size original might exist
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
ARCHIVES = ROOT / "archives"
CONTENT = ROOT / "content"
IMG = ROOT / "static" / "img"

PAGE1 = ARCHIVES / (
    "Torwood Blue Pool — Investigation of a round brick lined "
    "blue pool at Torwood near Dunipace and Larbert.html"
)
PAGE2 = ARCHIVES / (
    "Torwood Blue Pool page 2 — Investigation of a round brick lined "
    "blue pool at Torwood near Dunipace and Larbert.html"
)


def load_text(path):
    try:
        return path.read_text("utf-8", errors="replace")
    except FileNotFoundError:
        return None


def strip_html(html):
    """Remove tags, return clean text blocks."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n")


def get_all_our_text():
    """Return all the text content we have across all Hugo files."""
    texts = []
    for md_file in sorted(CONTENT.rglob("*.md")):
        text = md_file.read_text("utf-8", errors="replace")
        # Strip front matter
        text = re.sub(r"^(---|\+\+\+)\n.*?\n\1\n", "", text, flags=re.DOTALL)
        # Strip markdown formatting
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", text)  # images
        text = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", text)  # links
        text = re.sub(r"^[#>*-]\s*", "", text, flags=re.MULTILINE)  # markers
        text = re.sub(r"\*\*|__|\*|_", "", text)
        texts.append(text)
    return "\n".join(texts)


def get_image_refs_from_html(html, page_label):
    """Extract all image filenames referenced in an HTML page."""
    soup = BeautifulSoup(html, "lxml")
    refs = set()
    for img in soup.find_all("img"):
        src = img.get("src", "")
        # Extract just the filename
        fname = src.split("/")[-1]
        if fname and not fname.startswith("suspendedpage") and not fname.endswith(".cgi"):
            refs.add(fname)
    return refs


def get_image_refs_from_markdown():
    """Extract all /img/ references from our markdown."""
    refs = set()
    for md_file in sorted(CONTENT.rglob("*.md")):
        text = md_file.read_text("utf-8", errors="replace")
        for m in re.finditer(r'/img/([^")\s]+)', text):
            refs.add(m.group(1))
    return refs


def find_text_segments(html, our_text, min_len=40):
    """
    Find text segments from the HTML that are NOT present in our content.
    Splits the HTML text into paragraphs and checks each one.
    """
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    missing = []
    # Find all paragraph-like elements
    for p in soup.find_all(["p", "li", "td"]):
        text = p.get_text(strip=True)
        if len(text) < min_len:
            continue
        # Skip known navigation/sidebar patterns
        skip_patterns = [
            "return to HOME", "tell a friend", "email the author",
            "return to TOP", "Page 1 of 2", "Page 2 of 2",
            "go to the latest", "you can view the earlier",
            "CAN YOU HELP", "Get onboard", "Go straight to",
            "Local Mystery", "The Torwood Blue Water Pool",
            "Investigation of a round brick lined",
            "google_ad", "comments section",
            "Copyright ©", "Theme by", "Powered by",
            "Back to Top", "Navigation",
        ]
        should_skip = False
        for pat in skip_patterns:
            if pat.lower() in text.lower():
                should_skip = True
                break
        if should_skip:
            continue

        # Check if this text exists in our content
        if text.lower() not in our_text.lower():
            # Get context: which section is this in?
            parent_text = ""
            parent = p.find_parent("td") or p.find_parent("div")
            if parent:
                parent_text = parent.get_text(strip=True)[:100]

            missing.append((text[:150], parent_text[:80]))

    return missing


def main():
    print("=" * 72)
    print("CONTENT AUDIT: Hand-coded pages vs Hugo rebuild")
    print("=" * 72)

    page1_html = load_text(PAGE1)
    page2_html = load_text(PAGE2)
    our_text = get_all_our_text()

    if not page1_html or not page2_html:
        print("ERROR: Could not load archive files")
        return

    # ---- SECTION 1: Missing text segments ----
    print("\n--- SECTION 1: Text in page 1 not found in any Hugo file ---")
    missing_p1 = find_text_segments(page1_html, our_text)
    if missing_p1:
        print(f"  Found {len(missing_p1)} potentially missing segments:\n")
        for i, (text, context) in enumerate(missing_p1[:30]):
            print(f"  [{i+1}] Context: {context}")
            print(f"       Text: {text}...")
            print()
        if len(missing_p1) > 30:
            print(f"  ... and {len(missing_p1) - 30} more")
    else:
        print("  ✅ All text segments accounted for")

    print("\n--- SECTION 2: Text in page 2 not found in any Hugo file ---")
    missing_p2 = find_text_segments(page2_html, our_text)
    if missing_p2:
        print(f"  Found {len(missing_p2)} potentially missing segments:\n")
        for i, (text, context) in enumerate(missing_p2[:30]):
            print(f"  [{i+1}] Context: {context}")
            print(f"       Text: {text}...")
            print()
        if len(missing_p2) > 30:
            print(f"  ... and {len(missing_p2) - 30} more")
    else:
        print("  ✅ All text segments accounted for")

    # ---- SECTION 3: Key introductory content ----
    print("\n--- SECTION 3: Introductory/home content (not in dated posts) ---")
    # Check if the investigation intro text is on our home page
    home_text = load_text(CONTENT / "home.md") or ""
    intro_phrases = [
        "I first came across the blue pool in 1961",
        "The blue colour, it seems, is not that big a mystery",
        "If the pool was being fed by an external source",
        "Heather Livingston from Ontario, Canada",
        "Caroline Kerr from Aberdeen, Scotland",
        "The questions:",
        "What was the function and purpose of the blue pool",
    ]
    for phrase in intro_phrases:
        if phrase.lower() in home_text.lower():
            print(f"  ✅ '{phrase[:60]}...' — on home page")
        else:
            print(f"  ⚠️  '{phrase[:60]}...' — NOT on home page")

    # Check page 2 intro content
    page2_intro = [
        "Known by Denny folk as The Blue Pool",
        "After two years of investigating",
        "The circular Pool is flush with ground level",
        "The oldest and most common theory",
    ]
    for phrase in page2_intro:
        if phrase.lower() in our_text.lower():
            print(f"  ✅ '{phrase[:60]}...' — found in content")
        else:
            print(f"  ❌ '{phrase[:60]}...' — MISSING from all content")

    # ---- SECTION 4: Image audit ----
    print("\n--- SECTION 4: Image audit ---")

    # Images referenced in page 1 HTML
    p1_imgs = get_image_refs_from_html(page1_html, "page 1")
    p2_imgs = get_image_refs_from_html(page2_html, "page 2")

    # Our markdown refs
    our_imgs = get_image_refs_from_markdown()

    print(f"\n  Images in page 1 source: {len(p1_imgs)}")
    print(f"  Images in page 2 source: {len(p2_imgs)}")
    print(f"  Images referenced in our Markdown: {len(our_imgs)}")

    # Check which images in our markdown don't exist on disk
    missing_from_disk = []
    for ref in sorted(our_imgs):
        if not (IMG / ref).exists():
            missing_from_disk.append(ref)

    if missing_from_disk:
        print(f"\n  ❌ Images referenced but NOT in static/img/ ({len(missing_from_disk)}):")
        for ref in missing_from_disk:
            print(f"     - {ref}")
    else:
        print(f"\n  ✅ All {len(our_imgs)} referenced images exist in static/img/")

    # Check for thumbnails where full-size might exist
    thumbnails = [ref for ref in our_imgs if re.search(r'-\d+x\d+\.', ref)]
    if thumbnails:
        print(f"\n  📎 Thumbnail images (WordPress -300xNNN etc.):")
        for ref in sorted(thumbnails):
            # Try to find full-size original
            base = re.sub(r'-\d+x\d+\.', '.', ref)
            if (IMG / base).exists():
                print(f"     ✅ {ref}  →  full-size {base} exists")
            else:
                # Check archives for the original
                found = False
                for archive_dir in ARCHIVES.iterdir():
                    if archive_dir.is_dir() and archive_dir.name.endswith("_files"):
                        if (archive_dir / base).exists():
                            found = True
                            break
                if found:
                    print(f"     📎 {ref}  →  full-size {base} exists in archives (not copied)")
                else:
                    print(f"     ❌ {ref}  →  no full-size original found")

    # Missing images from originals not yet in our site
    all_archive_imgs = p1_imgs | p2_imgs
    our_imgs_basename = {re.sub(r'-\d+x\d+', '', f) for f in our_imgs}
    missing_from_site = set()
    for img in sorted(all_archive_imgs):
        base = re.sub(r'-\d+x\d+', '', img)
        base_no_ext = Path(base).stem
        if base not in our_imgs_basename:
            # Check if it's a real image (not a CGI/HTML)
            if img.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                # Check if it exists on disk (might have been copied with different name)
                if not (IMG / img).exists():
                    # Check if any file with same stem exists
                    matches = list(IMG.glob(f"{base_no_ext}.*"))
                    if not matches:
                        missing_from_site.add(img)

    if missing_from_site:
        print(f"\n  📸 Images in original HTMLs not yet in our site ({len(missing_from_site)}):")
        for img in sorted(missing_from_site):
            print(f"     - {img}")
    else:
        print(f"\n  ✅ All original images accounted for")

    print("\nDone!")


if __name__ == "__main__":
    main()
