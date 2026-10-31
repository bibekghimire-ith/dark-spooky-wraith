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

Phase 1 (scaffold and data) is done: the app starts, validates its data, and renders the owner name, title and bio. Sections, styling, hardening and deployment follow the plan in `Portfolio-Implementation-Plan.md`.
