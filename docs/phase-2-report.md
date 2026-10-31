# Phase 2 report: sections

Status: **done**. Gate met: every section renders from the data, and adding an entry needs no template edit.

## What was built

| Ticket | Result |
| --- | --- |
| T3 | `templates/index.html` loops over skills, projects and experience. Order written in the data is kept. |
| T4 | `image_src()` registered as a Jinja global. Hosted http(s) URLs pass through; other values become `/static/...`. Empty values, `..` segments, backslashes and other schemes return nothing. |
| T5 | Optional fields are guarded. No empty Demo/Code buttons, no `href=""`, no `src=""`. A project without a usable image gets `<div class="project-placeholder">`. Empty sections and their nav links disappear. |
| T6 | Nav links are generated only for sections with data (Contact is always present). Social links come from the data. Footer has a mailto link and `(c) <year> <name>`. |
| T7 | Everything is auto-escaped. A test fails if a template uses `|safe` or turns autoescape off. |

## How it was built (test first)

1. Wrote `tests/conftest.py`, `test_sections.py`, `test_images.py` and `test_escaping.py` first. First run failed at import (red).
2. Added `image_src()` and the full template.
3. Final run: **63 tests passed** (29 from Phase 1, 34 new).

## Decisions and notes

- Tests were run in the cloud workspace; run `python -m pytest` locally once to confirm.
- The page is still unstyled. Class names (`project`, `project-placeholder`, `tech-badges`, `job`, `skill-group`) are the hooks for Phase 3.
- Project images in the shipped data point to files not yet in `static/img/`; add them or the placeholder will not appear (the broken link will). 
- No git commands were run.

## Next: Phase 3 (style)

T8 Bootstrap CDN with SRI and retro design tokens; T9 Playwright layout tests.
