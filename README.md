# Torwood Blue Pool

A reconstruction of the former [Torwood Blue Pool](https://torwoodbluepool.co.uk) investigation website, originally created by Nigel Turnbull and hosted on ntgraphics.co.uk. The site is rebuilt from [Internet Archive](https://web.archive.org) snapshots using [Hugo](https://gohugo.io).

## Build

```shell
hugo server      # development server at localhost:1313
hugo             # production build to ./public/
```

## Deploy

Pushes to the `main` branch are automatically built and deployed to GitHub Pages via `.github/workflows/hugo.yaml`. See [Hugo's GitHub Pages docs](https://gohugo.io/host-and-deploy/host-on-github-pages/) for details.

## Structure

```
content/
  _index.md              — "What We Know" (home)
  posts/                 — dated investigation updates (2009–2011)
  words-of-condolence.md — Nigel's passing
  guestbook.md           — 166 community comments
  contact.md
data/
  guestbook.yaml         — extracted from Wayback Machine
  condolences.yaml
static/img/              — 100+ photos from the original site
archives/                — raw Wayback Machine HTML snapshots
```

## Verification

```shell
python3 tools/verify_content.py
```

Compares all content against the original archives to catch transcription errors.
