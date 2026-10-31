# Phase 3 report: style

Status: **done, with one check left for your Mac** (see below). Gate: layout tests green at three widths and three column counts.

## What was built

| Ticket | Result |
| --- | --- |
| T8 | `static/css/retro.css` holds the design tokens as custom properties (page `#E5E5E5`, panel `#F0F0F0`, 2px black borders, hard `4px 4px 0 #000` shadow, square corners, Courier New stack). Bootstrap 5.3.3 loads from the CDN with an `integrity` hash and `crossorigin`, before `retro.css`. Nav, hero, skill groups, project cards and jobs use the panel style. |
| T9 | Projects sit in `row row-cols-1 row-cols-md-2 row-cols-lg-3`. Thumbnails sit in a `.thumb` frame fixed at 16:9; the placeholder fills the same frame. |

## How it was built (test first)

1. `tests/test_style.py` (route level: SRI present, pinned version, CSS order, tokens, grid classes) and `tests/layout/` (Playwright: no sideways scroll at 360, 768, 1280 px; 1, 2, 3 columns at 390, 800, 1280 px; Bootstrap really applied; theme colours; shadow and square corners; 16:9 thumbnails) were written first and failed.
2. CSS and template changes made them pass.
3. Final run: **79 passed** (63 earlier, 16 new).

## What to do on your Mac

- This cloud workspace cannot reach the Bootstrap CDN, so the browser tests here ran against a small stand-in for the Bootstrap 5 grid (not shipped, SRI attribute stripped in that mode only). On your Mac, run `python -m playwright install chromium` and then `python -m pytest` with no extra settings, so the real Bootstrap is used.
- I could not check the Bootstrap SRI hash against the CDN. If the page loads unstyled in a browser, the hash is wrong: copy the current `integrity` value for Bootstrap 5.3.3 CSS from the Bootstrap download page into `templates/index.html`.
- Project images still need to be added to `static/img/` (404 until then).

## Decisions

- `BOOTSTRAP_CSS_FILE` env var lets the layout tests use a local Bootstrap copy offline.
- `tests/__init__.py` added so the layout fixtures can reuse `FULL_DATA`.
- No git commands were run.

## Next: Phase 4 (harden)

T10 `rel="noopener"` on links, one `h1`, non-empty `alt`, skip link, focus styles. T11 Lighthouse run and README scores.
