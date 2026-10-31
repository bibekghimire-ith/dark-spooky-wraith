# Personal portfolio (Flask, "ops console" theme)

A one-page portfolio, a print-friendly CV and a small Markdown blog. No framework and no third-party requests: one stylesheet (`static/css/site.css`) and one optional script (`static/js/site.js`, theme toggle and nav highlight). All content comes from `content.yaml` and `posts/`; there is no database.

Needs Python 3.10 or newer.

## Run it

```text
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py
```

Open http://127.0.0.1:5000. Set `FLASK_DEBUG=1` to reload when files (including `content.yaml`) change.

Pages: `/` (home), `/cv` (print view), `/blog`, `/blog/<slug>`, `/healthz` (returns `ok`).

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
- `hero_console`: lines in the career.log card (a line starting with `$` is styled as a command).
- `stats`: `{value, label}` tiles. Quote values such as `"3"`.
- `focus`: `{title, text}` cards under "What I do".
- `projects[].impact`: one-line result shown on the project card.

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

## Deploy

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
- Lighthouse scores: **not yet recorded.** Run `npx @lhci/cli autorun` once with Chrome installed and paste the scores here.

## Project docs

`Portfolio-PRD.md`, `Portfolio-Implementation-Plan.md`, `Portfolio-Profile-Data.md`, and the per-phase reports in `docs/`.
