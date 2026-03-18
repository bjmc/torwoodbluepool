import yaml
from bs4 import BeautifulSoup
from datetime import datetime


def parse_comment_li(li):
    """Parse a single <li class='comment'> into a dict."""

    article = li.find("article", class_="comment")
    if not article:
        return None

    # --- ID ---
    comment_id = article.get("id", "").replace("comment-", "")

    # --- Author ---
    author_tag = article.select_one(".fn")
    author = author_tag.get_text(strip=True) if author_tag else None

    # --- Avatar ---
    avatar_tag = article.select_one("img.avatar")
    avatar = avatar_tag["src"] if avatar_tag and avatar_tag.has_attr("src") else None

    # --- Date ---
    time_tag = article.find("time")
    date = None
    if time_tag and time_tag.has_attr("datetime"):
        try:
            date = datetime.fromisoformat(
                time_tag["datetime"].replace("Z", "+00:00")
            ).isoformat()
        except Exception:
            date = time_tag["datetime"]

    # --- Content ---
    content_section = article.select_one(".comment-content")
    content = ""
    if content_section:
        # Convert <br> to newlines
        for br in content_section.find_all("br"):
            br.replace_with("\n")

        # Extract paragraphs cleanly
        paragraphs = [
            p.get_text(" ", strip=True)
            for p in content_section.find_all("p")
        ]
        content = "\n\n".join(paragraphs)

    # --- Replies (recursive) ---
    replies = []
    children_ol = li.find("ol", class_="children")
    if children_ol:
        for child_li in children_ol.find_all("li", recursive=False):
            parsed = parse_comment_li(child_li)
            if parsed:
                replies.append(parsed)

    return {
        "id": int(comment_id) if comment_id.isdigit() else comment_id,
        "author": author,
        "date": date,
        "avatar": avatar,
        "content": content,
        "replies": replies,
    }


def parse_comments(html):
    soup = BeautifulSoup(html, "html.parser")

    root = soup.find("ol", class_="commentlist")
    if not root:
        return []

    comments = []
    for li in root.find_all("li", recursive=False):
        parsed = parse_comment_li(li)
        if parsed:
            comments.append(parsed)

    return comments


if __name__ == "__main__":
    with open("What We Know _ Torwood Blue Pool.html", "r", encoding="utf-8") as f:
        html = f.read()

    comments = parse_comments(html)

    output = {"comments": comments}

    with open("comments.yaml", "w", encoding="utf-8") as f:
        yaml.dump(output, f, sort_keys=False, allow_unicode=True)

    print("Done. Wrote comments.yaml")