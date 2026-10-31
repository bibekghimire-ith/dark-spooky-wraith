# Portfolio website

A one-page personal portfolio built with Flask. All content lives in `PORTFOLIO_DATA` at the top of `app.py`.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
flask --app app run          # http://127.0.0.1:5000
```

Set `FLASK_DEBUG=1` to get the reloader while editing. Needs Python 3.10 or newer.

## Edit the content

Open `app.py` and change `PORTFOLIO_DATA`. The field list is in the docstring at the top of the file. If a field is wrong, the app refuses to start and the error names the field, for example `projects[2].tech_stack must be a list of strings`.

## Test

```bash
python -m pytest
```

## Status

Phases 1 to 3 are done: the app validates its data, renders every section from it, and is styled with Bootstrap 5.3 plus the retro theme in `static/css/retro.css`. Sections, styling, hardening and deployment follow the plan in `Portfolio-Implementation-Plan.md`.

## Layout tests (browser)

`tests/layout/` uses Playwright and Chromium and needs internet access to load Bootstrap from the CDN. One-time setup:

```text
python -m playwright install chromium
```

`python -m pytest` runs everything; `python -m pytest -m "not layout"` skips the browser tests; if Chromium is missing the layout tests skip themselves.
