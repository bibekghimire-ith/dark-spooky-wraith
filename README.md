# Personal portfolio (Flask, "ops console" theme)

A one-page portfolio, a print-friendly CV and a small Markdown blog. No framework and no third-party requests: one stylesheet (`static/css/site.css`) and one optional script (`static/js/site.js`, theme toggle and nav highlight). All content comes from `content.yaml` and `posts/`; there is no database.

Needs Python 3.10 or newer.

## Two versions of the site

| | Static version | Flask version |
| --- | --- | --- |
| What it is | One self-contained `index.html` (CSS and JS inlined), no server | The Flask app: home, `/cv`, `/blog`, `/healthz` |
| Needs at run time | Any static host, or just open the file | Python, gunicorn |
| Build or run | `python build.py` | `python app.py` |
| Contains | Everything on the home page, case studies, linked dev.to posts | All of that, plus the print-view CV and the local blog |
| Best for | Showing your work: fast, free, nothing to maintain | Local editing, the blog and CV pages, a live Python demo |

Both are generated from the same `content.yaml` and templates, so they never drift apart.

### Static version

```text
python build.py              # writes build/index.html (+ build/static/img if you have project images)
python build.py --out public # choose the folder; it is deleted and recreated on every run
python build.py --full       # also export /cv and the blog as separate pages (add --base-path /name for a sub-path)
```

Upload the folder to GitHub Pages, GitLab Pages, Netlify, Cloudflare Pages or any web server. The single page uses only relative links, so it also works from a sub-path or from a double-clicked file. It leaves out the links to `/cv` and the local blog, because those pages are not in it; posts you link or import from dev.to stay. Rebuild after you edit `content.yaml` or add posts. The build refuses to delete a folder that is not empty and does not already hold a build.

## Run it (Flask version)

```text
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py
```

Open http://127.0.0.1:5000. Set `FLASK_DEBUG=1` to reload when files (including `content.yaml`) change.

Flask pages: `/` (home), `/cv` (print view), `/blog`, `/blog/<slug>`, `/healthz` (returns `ok`).

## Edit the content

Open `content.yaml`. Field names are listed in the docstring at the top of `app.py`.

- Add a project, a job or a skill by copying an existing entry. No template change is needed.
- Quote values that YAML could read as something else, for example `dates: "2024"` and `version: "3.10"`. An unquoted number where text is expected fails the check at startup.
- A broken file stops the app at startup with a message naming the file, line or field. Fix it and start again.
- Links must start with `http://`, `https://` or `mailto:`. Empty links are simply not shown.
- Replace the placeholder email and social links before publishing.

### Home page extras (all optional)

Remove a key to hide its section. Everything below is dummy text drawn from the CV; edit freely.

- `owner.location`, `owner.availability`, `owner.cta_title`, `owner.cta`: hero badge and contact card.
- `hero_console`: lines in the profile.txt card (a line starting with `$` is styled as a command).
- `stats`: `{value, label}` tiles. Quote values such as `"3"`.
- `focus`: `{title, text}` cards under "What I do".
- `projects[].impact`: one-line result shown on the project card.

### Page order

Hero, highlights, About, Experience, Projects, Tech Stack, Credentials, Writing, Contact. Experience comes before Projects because work history is the strongest proof for an experienced engineer. Section numbers and the nav follow whichever sections have data.

- `experience[].tech`: optional tags shown under each role.
- `experience_visible`: how many of the newest roles are expanded (default 3). Older roles sit under "Earlier roles"; `0` shows all.

### Availability badge

`owner.availability` in `content.yaml` is the badge in the hero. Use plain text, or choose the colour:

```text
owner:
  availability:
    text: Booked until March, open to talk
    status: limited      # open (green), limited (amber) or closed (grey)
```

Remove the key (or leave it empty) to hide the badge.

### Featured project and case studies

Each project can be expanded in place under "Read the case study" (the page stays a single page).

```text
projects:
- title: My project
  featured: true            # optional: wide card with the cover beside the text
  impact: One-line result   # optional
  case_study:               # optional; show only the fields you fill in
    problem: What needed solving.
    role: What you did.
    approach: How you did it.
    result: What changed.
    diagram: img/my-diagram.png     # optional image in static/img/ or an https:// URL
    diagram_alt: Describe the diagram for screen readers
```

A link ending in `#case-my-project` (the project title in lowercase with dashes) opens that case study. The case-study text in `content.yaml` is dummy copy written from your CV: rewrite it in your own words.

### Link your dev.to posts

Posts published elsewhere appear in "Latest posts" and on `/blog` beside your local posts, newest first, and open in a new tab.

```text
writing:
  devto_username: your-username     # optional: import your dev.to posts when the app starts
  links:                            # optional: link any post by hand
  - title: My post
    url: https://dev.to/your-username/my-post
    date: 2026-01-31                # optional
    summary: One line (optional)
    source: dev.to                  # optional label, defaults to the site's host
```

The import runs once at startup with a 5 second limit; restart the app to pick up new posts. If dev.to cannot be reached the site starts anyway and logs a warning, and your hand-written links still show. A hand-written link replaces an imported post with the same address.

### Add images

Put files in `static/img/` and set `image_url: img/your-file.png`. A full `https://` address also works. Use 16:9 images (for example 1280 x 720); anything else is cropped to fit. A project without a usable image shows a striped placeholder.

### Write a blog post

Create `posts/my-post-title.md`. The file name (lowercase letters, digits, dashes) becomes the address.

```text
---
title: My post title
date: 2026-11-01
summary: One line for the list page (optional)
draft: true      (optional: hides the post)
---
Markdown text. Fenced code blocks are highlighted.
```

Raw HTML in a post is shown as plain text, and links may only use http, https, mailto or relative addresses.

### Analytics (optional)

Add to `content.yaml` to switch on a privacy-friendly analytics script (for example a Plausible-style tool):

```text
analytics:
  script_src: https://plausible.io/js/script.js
  domain: your-domain.example
```

Leave it out or empty and no script is added. If you add a Content-Security-Policy header at your host, allow that one origin in `script-src`. Check that your chosen tool honours Do Not Track.

## Test it

```text
python -m pytest                  # everything
python -m pytest -m "not layout"  # fast tests only (no browser)
```

Browser tests (`tests/layout/`) need Chromium (the site itself loads nothing from the internet):

```text
python -m playwright install chromium
```

If Chromium is missing they skip themselves. They check: no sideways scroll at 360, 768 and 1280 px; 1 and 2 project columns; sticky nav, theme toggle, scroll highlight; print view; text contrast in light and dark.

## Deploy the Flask version

The app is a standard WSGI app: `gunicorn app:app`. The `Procfile` runs it with 2 workers on `$PORT`, which works on Heroku-style hosts (Render, Railway, Fly with a Procfile builder) and on any Linux server behind nginx.

1. Push the repository to your host and set the start command to the `Procfile` line.
2. Make sure the host serves HTTPS.
3. Run the smoke test against the live address:

   ```text
   SMOKE_URL=https://your-site.example/ python -m pytest tests/test_deploy.py -k live
   ```

Rollback: redeploy the previous tagged release. Content lives in the repository, so there is no data to restore.

Host chosen: **not yet decided** (open question from the PRD). Write it here once chosen.

## Quality gates

- `.gitlab-ci.yml` runs the tests, the layout tests and a Lighthouse CI check (`lighthouserc.json`, mobile, minimum 0.95 in performance, accessibility, best practices and SEO for `/`, `/cv` and `/blog`).
- Lighthouse (mobile, median of 3 runs, 2026-10-31): performance, accessibility, best practices and SEO are all **100** on `/`, `/cv` and `/blog`. Home page weight is about 32 KB (budget 150 KB). To re-run: put `.venv/bin` on `PATH`, then `npx @lhci/cli@0.14.0 autorun` with Chrome installed (set `CHROME_PATH` if it is not found).

## Project docs

`Portfolio-PRD.md`, `Portfolio-Implementation-Plan.md`, `Portfolio-Profile-Data.md`, and the per-phase reports in `docs/`.

Hosting on free services (InfinityFree, GitHub Pages, PythonAnywhere, Render): `docs/HOSTING.md`.
