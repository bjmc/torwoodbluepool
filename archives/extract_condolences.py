"""Extract Words of Condolence comments from the archive HTML and save as YAML."""
import yaml
import sys
import os

# Add parent directory to path so we can import from convert.py
sys.path.insert(0, os.path.dirname(__file__))
from convert import parse_comments


if __name__ == "__main__":
    path = os.path.join(
        os.path.dirname(__file__),
        "Words of Condolence - Torwood Blue Pool.html"
    )
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    comments = parse_comments(html)
    output = {"comments": comments}

    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "condolences.yaml")
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(output, f, sort_keys=False, allow_unicode=True)

    print(f"Done. Extracted {len(comments)} comments to {out_path}")
