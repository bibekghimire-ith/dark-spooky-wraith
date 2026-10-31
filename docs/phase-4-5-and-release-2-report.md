# Phases 4 and 5 and Release 2 report

Status: **everything in the plan is built and tested in the cloud workspace; four checks need your Mac or your host** (see "Not verified").

Final run: **167 passed, 1 skipped** (the live-site smoke test, which needs `SMOKE_URL`). Tests were written first for every item and failed before the code existed.

## Phase 4: harden (T10, T11)

| Item | Result |
| --- | --- |
| T10 | Skip link first on the page; landmarks (`header`, `nav` with a label, `main#main`, `footer`); one `h1`; every image has non-empty `alt`; every external link has `target="_blank"` with `rel="noopener noreferrer"`, mailto and anchor links do not open tabs; visible `:focus-visible` outline; reduced-motion rule. Tests in `tests/test_a11y.py`. |
| T11 | Images are lazy-loaded with width and height set; `theme-color` and `color-scheme` meta tags. The Lighthouse score itself was not run (see below). |

## Phase 5: deploy (T12, T13)

| Item | Result |
| --- | --- |
| T12 | `gunicorn app:app` in a `Procfile` (2 workers, `$PORT`); `gunicorn==23.0.0` pinned; `/healthz`; security headers (`nosniff`, `Referrer-Policy`, `X-Frame-Options: DENY`); 404 test; a live-site smoke test that runs when `SMOKE_URL` is set. |
| T13 | README rewritten: run, edit content, add images, write posts, test, deploy, rollback. |

## Release 2

| ID | Result |
| --- | --- |
| R2-1 YAML | Content moved to `content.yaml`; `load_content(path)` uses `yaml.safe_load`; errors name the file and line; a dict and its YAML form give identical `validate()` results; the dev reloader watches the file; `CONTENT_FILE` env var overrides the path. |
| R2-6 Lighthouse CI | `lighthouserc.json` (mobile, three URLs, 0.95 gates, 3 runs) and `.gitlab-ci.yml` (test, layout, lighthouse, smoke stages). |
| R2-2 CV | `/cv` with its own template, no navbar, print CSS (black on white, no shadows, screen-only items hidden); footer link on the home page; education and certifications from the content are shown here. |
| R2-4 Dark mode | Colours are custom properties with a dark set under `prefers-color-scheme`. Playwright checks that the background changes and that body text, badges, buttons, panel text and headings reach 4.5:1 contrast in both schemes. |
| R2-3 Blog | `blog.py` (about 130 lines, a blueprint, as the plan allowed): front matter, draft hiding, bad dates and bad slugs rejected with the file name, newest first, Pygments highlighting (`static/css/pygments.css`), `/blog`, `/blog/<slug>`, 404 for unknown and draft slugs. One sample post is included. |
| R2-5 Analytics | Optional `analytics: {script_src, domain}`; no script when empty or incomplete; exactly one `defer` script when set; `https://` enforced; values escaped. |

## Decisions and deviations

- **No `nh3`.** The plan names the `nh3` sanitiser, which could not be installed here. Instead, raw HTML in posts is switched off in the Markdown renderer (it is shown as text), and a post-processing step removes any link or image address whose scheme is not http, https or mailto (it ignores case and hidden whitespace). Tests cover script tags, `img onerror`, iframes, `javascript:`, `data:` and `vbscript:`. If you later want to allow some raw HTML, add `nh3` then.
- Post HTML is marked safe in Python (`Markup`) after that step, so the templates still contain no `|safe`, and the escaping guard test stays valid.
- Templates were split into `_head.html`, `_site_header.html`, `_site_footer.html` so the blog and CV share one head.
- `tests/__init__.py` was added so the layout fixtures can reuse the shared test data.
- No git commands were run. No placeholder content was changed: email and social links are still placeholders.

## Not verified

1. **Bootstrap from the real CDN.** The layout tests here ran against a small stand-in for Bootstrap's grid. Run them on your Mac with internet access. The Bootstrap integrity hash was written from memory and could not be checked; if the page looks unstyled, replace it in `templates/_head.html`.
2. **Lighthouse scores.** `lhci` could not be installed here. The config is written and tested for shape only. Run it once and record the scores in the README. The 0.95 performance target is unproven.
3. **gunicorn and the live deploy.** `gunicorn` could not be installed here, so `Procfile` was not run. The WSGI object `app:app` was exercised with the Flask test client. No host is chosen, so the live smoke test has not run.
4. **`.gitlab-ci.yml`** has not run on a runner.
