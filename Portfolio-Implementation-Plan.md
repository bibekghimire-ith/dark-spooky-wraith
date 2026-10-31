# Portfolio Website — Implementation Plan

Oct 29, 2026 · Bibek Ghimire

## Approach

Build Release 1 in about 3 days as a thin vertical slice, data first and styling last, then add six Release 2 features in about 4 days, each behind a CI gate so the site never regresses. Estimates are for one developer.

Five principles drive every decision:

1. **Data is the contract.** The `PORTFOLIO_DATA` schema is frozen first; the template, tests and validator all read it and nothing else.
2. **Tests first.** Each ticket starts with a failing test (Flask test client, then Playwright for layout), then the smallest code to pass it.
3. **Boring technology.** Flask, Jinja, Bootstrap 5, PyYAML, pytest. No build step, no Node in the runtime path.
4. **Fail loudly at startup, never at render.** Bad data stops the app with a message that names the field; a request never crashes on a missing optional value.
5. **Measure from day one.** Lighthouse and the page-weight budget run in CI before the blog or analytics can land.

## Engineering decisions

| # | Decision | Choice | Why | Revisit when |
| --- | --- | --- | --- | --- |
| D1 | App shape | Flask app factory `create_app(data=None)` in `app.py`, plus a module-level `app` | Lets tests inject data; still one file as briefed | Blog code passes about 60 lines |
| D2 | Data source | Release 1: dict at top of `app.py`. Release 2: `content.yaml` through one `load_content()` | The dict meets the brief; one loader function makes the swap a one-line change | Never needed earlier |
| D3 | Validation | Plain Python function `validate(data)` returning a list of errors; no pydantic | Zero dependencies, readable messages | Schema grows past about 30 fields |
| D4 | Image resolution | Jinja global `image_src(value)`: `http(s)://` as-is, else `url_for('static', ...)` | One place to change; unit-testable | Images move to a CDN |
| D5 | CSS | Bootstrap 5.3 from a CDN with SRI, plus about 25 lines of inline CSS using custom properties | No build step; custom properties give dark mode for free in Release 2 | Offline use required |
| D6 | JavaScript | Only Bootstrap's bundle for the navbar toggler | Brief forbids heavy JS | A manual theme toggle is wanted |
| D7 | Serving | `gunicorn` with 2 workers behind the host's proxy; Flask dev server for local only | Standard and small | Traffic needs more than a small instance |
| D8 | Python and deps | Python 3.11 or newer; pinned `requirements.txt` plus `requirements-dev.txt` | Reproducible installs | Dependabot or similar added |
| D9 | Tests | `pytest` and Flask test client for logic; `playwright` for layout and responsive checks | Fast tests for behavior, one browser suite for layout | Suite takes over 1 minute |

## Repository layout and module design

Release 1 is two source files; Release 2 adds files beside them without moving anything.

```text
portfolio/
  app.py                  # PORTFOLIO_DATA, validate(), create_app(), route
  templates/
    index.html            # all six sections, Jinja loops
    cv.html               # R2-2
    blog_index.html       # R2-3
    post.html             # R2-3
  static/img/             # local project images
  posts/                  # R2-3 Markdown files
  content.yaml            # R2-1
  tests/
    test_data.py          # schema and validate()
    test_routes.py        # Flask test client
    test_images.py        # image_src() rules
    e2e/test_layout.py    # Playwright: breakpoints, no sideways scroll
  requirements.txt
  requirements-dev.txt
  lighthouserc.json       # R2-6
  README.md
```

The module has five small units. Signatures below are the skeleton to write tests against; bodies are filled test-first.

```python
# app.py
PORTFOLIO_DATA = {...}                       # frozen schema, see PRD

REQUIRED = {"owner": ["name", "title", "bio", "email"]}

def validate(data: dict) -> list[str]:
    """Return human-readable errors; empty list means valid."""

def image_src(value: str | None) -> str | None:
    """http(s) URL as-is, else static path; None when empty."""

def create_app(data: dict | None = None) -> Flask:
    """Validate data, register image_src and year globals, add route /."""

app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
```

**Validation rules** (each is one test): required owner fields are non-empty strings; `tech_stack` is a list of strings; `skills` maps strings to lists of strings; project `title` is present; link fields, when set, start with `http://`, `https://` or `mailto:`; unknown keys are allowed and ignored. Errors name the path, for example `projects[2].tech_stack must be a list`.

## Release 1 work breakdown

Each ticket is sized to under half a day. The failing test named in the third column is written and committed first.

| ID | Phase | Failing test first | Then build | Done when | Est. |
| --- | --- | --- | --- | --- | --- |
| T1 | 1 Scaffold | `GET /` returns 200 and contains the owner name | Repo, venv, `requirements*.txt`, `create_app`, bare `index.html` | Test green; app starts with `flask run` | 1 h |
| T2 | 1 Scaffold | `validate()` rejects each missing required field, with the field path in the message | `validate()` and startup call | 6 or more validation tests green | 2 h |
| T3 | 2 Sections | Page contains every project title, job role and skill from a fixture | Jinja loops for skills, projects, experience | Adding fixture entries changes output, no template edit | 3 h |
| T4 | 2 Sections | `image_src()` table test: URL, `img/x.png`, empty, `None` | `image_src()` global and placeholder block | Image rules from the PRD hold | 1 h |
| T5 | 2 Sections | Missing `demo_link`, `code_link`, `image_url`, empty `skills` render with 200 and no empty buttons | `if` guards in the template | Optional-field tests green | 1 h |
| T6 | 2 Sections | Navbar contains an anchor only for sections that have data | Generated nav links, hero social buttons, footer with year | Nav test green | 2 h |
| T7 | 2 Sections | Description containing a script tag is escaped in the response | Confirm autoescape on, no `\|safe` anywhere | Test green; grep for `safe` returns nothing | 0.5 h |
| T8 | 3 Style | Playwright: no horizontal scroll at 360, 768, 1280 px | Custom properties, borders, hard shadows, monospace stack | Layout test green at three widths | 3 h |
| T9 | 3 Style | Playwright: projects show 1, 2 and 3 columns at 390, 800, 1280 px | `row-cols-*` grid, fixed 16:9 thumbnails | Column-count test green | 1 h |
| T10 | 4 Harden | Every project link has `rel` containing `noopener`; one `h1`; every image has non-empty `alt` | Landmarks, skip link, focus styles | Accessibility assertions green | 2 h |
| T11 | 4 Harden | Lighthouse manual run reaches 95 or higher on mobile | Fix findings; image sizes, `loading="lazy"`, meta tags | Scores recorded in README | 2 h |
| T12 | 5 Deploy | Smoke test against the live URL: 200 and owner name | `gunicorn app:app`, host config, HTTPS, env vars | Live URL passes smoke test | 3 h |
| T13 | 5 Deploy | None | README: how to edit data, add images, run, test, deploy | A fresh clone runs from the README alone | 1 h |

## Release 2 work breakdown

Release 2 runs in the order the PRD fixes: YAML, then CI, then the features. Each feature is merged only when the Lighthouse gate from R2-6 stays green.

| ID | Feature | Failing test first | Implementation notes | Est. |
| --- | --- | --- | --- | --- |
| R2-1 | YAML content | Same fixture as a dict and as YAML produces identical `validate()` results; a bad YAML file raises an error naming the line | `load_content(path)` with `yaml.safe_load`; `PORTFOLIO_DATA = load_content(...)`; `extra_files` for the reloader; quote-coercion note in README | 0.5 d |
| R2-6 | Lighthouse CI | A deliberately heavy page fails the `lhci assert` step | `lighthouserc.json` with 0.95 gates on `/`, `/cv`, `/blog`; mobile preset; start app in the job; upload report | 0.5 d |
| R2-2 | CV at `/cv` | `GET /cv` returns 200 and omits the navbar; print CSS test in Playwright with `emulate_media(print)` | `cv.html`, `@media print` block, footer link | 0.5 d |
| R2-4 | Dark mode | Playwright with `color_scheme=dark`: body background differs; text contrast 4.5:1 or better for body and badges | Move colors to custom properties; add the dark set under `prefers-color-scheme` | 0.5 d |
| R2-3 | Blog | `parse_post()` tests: front matter, draft hidden, bad date rejected; route tests: list, post, unknown slug 404, script tag stripped | `blog.py` with `load_posts()` at startup; Markdown library plus `nh3` sanitiser; Pygments CSS; slug whitelist from file names | 1.5 d |
| R2-5 | Analytics | Empty `analytics` key renders no script tag; set key renders exactly one tag with the configured origin | Template guard, `rel` and CSP note, Do Not Track respected by the chosen tool | 0.25 d |

R2-3 is the only item that may split the single-file rule: if the blog code passes about 60 lines it moves to `blog.py`, and `create_app` registers it as a blueprint.

## Dependency map

> Diagram: dependency map, 11 work items. Release 1 (about 3 days) is a chain: Scaffold (T1, T2), Sections (T3 to T7), Style (T8, T9), Harden (T10, T11), Deploy (T12, T13). Release 2 (about 4 days) follows: YAML content (R2-1), then Lighthouse CI (R2-6, the gate), then CV page (R2-2) and Dark mode (R2-4) in parallel, then Blog (R2-3), then Analytics (R2-5). Arrows show merge order. After R2-6, each feature must keep Lighthouse at 0.95 or higher.

Release 1 is a straight chain, because each phase needs the one before it. In Release 2, YAML and CI come first; the CV and dark mode are independent of each other and can run in parallel, then the blog, with analytics last.

## Test strategy

Most tests are fast and run in under 5 seconds; one small browser suite covers what only a browser can show.

| Layer | Tool | Covers | Runs |
| --- | --- | --- | --- |
| Unit | `pytest` | `validate()`, `image_src()`, `load_content()`, `parse_post()` | Every save and every push |
| Route | `pytest` with Flask test client | Status codes, content present, escaping, 404s, optional-field fallbacks | Every push |
| Layout | `playwright` (Chromium) | No sideways scroll at 360, 768, 1280 px; 1, 2, 3 project columns; print and dark media | Every push |
| Performance and a11y | `lhci` (Lighthouse CI), mobile preset | Scores of 0.95 or higher on `/`, `/cv`, `/blog`; page weight under 150 KB excluding images | Every push, from R2-6 |
| Smoke | `pytest` or `curl` against the live URL | 200 and owner name | After each deploy |

Two rules keep the suite honest. Fixtures are small dictionaries built in the test, never the real `PORTFOLIO_DATA`, so editing content never breaks a test. Coverage is tracked for logic only (`app.py`, `blog.py`) with a floor of 90%; templates are covered by route and layout tests, not by a percentage.

## CI/CD and deployment

> Diagram: CI/CD pipeline, 8 stages. Commit (branch and MR), then Tests (pytest), Layout (Playwright), Lighthouse (lhci, from R2-6), Deploy (merge to main), then Smoke test (GET / is 200). Pass leads to Live (tag the release); fail leads to Rollback (last good build). A red check blocks the merge and returns to the author. Until R2-6 the pipeline runs pytest only; layout and Lighthouse jobs are added as they are written.

Deploys come only from the main branch after the gates pass. A failed smoke test triggers a rollback to the last good build.

| Item | Plan |
| --- | --- |
| Branching | Short-lived branches, merge requests into main, one reviewer even on a solo project (self-review checklist) |
| Environments | Local and production only; a preview is the branch run in CI |
| Config | Environment variables for `FLASK_DEBUG` and the analytics key; no secrets in the repo |
| Process | `gunicorn app:app` with 2 workers behind the host's HTTPS proxy |
| Rollback | Redeploy the previous tagged release; data lives in the repo, so there is no database to restore |
| Host | Open question from the PRD; the plan works on any host that runs Python and serves `static/` |

## Risks, definition of done and first day

| Risk | Impact | Mitigation in the plan |
| --- | --- | --- |
| Bad data breaks the site after an edit | High | `validate()` at startup (T2); pre-push test run; previous deploy kept for rollback |
| Playwright tests are flaky in CI | Medium | Fixed viewports, no animations, wait on selectors not timeouts; retry once, then fail |
| Lighthouse scores vary by run | Medium | Take the median of 3 runs in `lhci`; gate at 0.95 with a documented 0.02 tolerance |
| Blog scope grows (tags, RSS, pagination) | Medium | R2-3 ships list and post pages only; extras are separate tickets |
| CDN outage removes styling | Low | SRI hash plus a documented fallback: vendor Bootstrap into `static/` |
| Hosting choice delays T12 | Medium | Decide host before Phase 5; keep `gunicorn app:app` portable |

**Definition of done, per ticket:** failing test seen first, test green, no new Lighthouse regression, README updated if behavior changed, change merged to the main branch through a reviewed merge request.

**Definition of done, per release:** all gates in the PRD pass on the live URL; a fresh clone runs from the README; scores and page weight are recorded.

**First-day checklist:**

- [ ] Create the repo with `.gitignore`, `README.md`, `requirements.txt` and `requirements-dev.txt`.
- [ ] Write the data schema as the first test file (T2) and commit it red.
- [ ] Get `GET /` returning the owner name (T1) so the loop is closed end to end.
- [ ] Choose the host and note it in the README (open question from the PRD).
- [ ] Add a CI job that runs `pytest` only; Lighthouse joins in R2-6.
