# Phase 1 report: scaffold and data

Status: **done**. Gate met: the page renders the owner name from the dictionary.

## What was built

| Ticket | Result |
| --- | --- |
| T1 | `create_app(data=None)` factory, route `/`, bare `templates/index.html`. `GET /` returns 200 and shows the owner name, title and bio. A module-level `app` serves the shipped data. |
| T2 | `validate(data)` returns a list of readable errors, and `create_app` refuses to start when the list is not empty. The error names the field path. |

Supporting files: `requirements.txt` (Flask pinned), `requirements-dev.txt` (adds pytest), `pytest.ini`, `.gitignore`, `README.md`, `static/img/.gitkeep`.

`PORTFOLIO_DATA` sits at the top of `app.py` under a docstring that documents every field. It is filled from the profile data in `Portfolio-Profile-Data.md`.

## How it was built (test first)

1. Wrote `tests/test_data.py` and `tests/test_routes.py` before any code. First run: both files failed at import (red).
2. Wrote `app.py` and `index.html` until the suite passed.
3. Final run: **29 tests passed**.

| Test file | Covers |
| --- | --- |
| `tests/test_data.py` | Valid data; non-dict root; missing owner; each missing or empty owner field; `tech_stack` and `skills` types; project title; link schemes (allowed and rejected, plus empty links); unknown keys ignored; several errors reported together; the shipped data is valid |
| `tests/test_routes.py` | `GET /` is 200 with owner name, title and bio; `<title>` comes from data; invalid data stops `create_app`; the module-level `app` serves |

Manual checks: the dev server returned 200 with `<title>` and one `<h1>`; broken data gives this startup message:

```text
Invalid PORTFOLIO_DATA:
- owner.email is required and must be non-empty text
- projects[1].tech_stack must be a list of strings
```

## Decisions and deviations

- **Shipped-data test:** the plan says fixtures never use the real data. All content tests do use small fixtures; one extra test, `test_shipped_data_is_valid`, validates the real `PORTFOLIO_DATA` so a bad edit fails the test run instead of the live site.
- **Python version:** the plan says 3.11 or newer. The code uses nothing newer than 3.10, so it runs on the 3.10 installed on this Mac. Tests ran on Python 3.13.
- **Where tests ran:** this Mac has no Flask or pytest installed, and the session shell there could not reach the package index. The tests were run in the cloud workspace and the files copied across. Run `python -m pytest` locally once after installing the dev requirements to confirm.
- **Placeholders still in the data:** the email address, the three social links and the project GitHub link need real values (see `Portfolio-Profile-Data.md`). They are valid text, so validation passes.
- **No git commands were run.** Files were written to the folder only; staging and committing are yours.

## Next: Phase 2 (sections)

Start with failing tests for T3 to T7: skills, projects and experience loops, `image_src()`, optional-field guards, generated nav links and the escaping check.
