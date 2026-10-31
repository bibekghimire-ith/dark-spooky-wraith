"""T12: deploy surface. The live smoke test only runs when SMOKE_URL is set."""
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_wsgi_entry_point_app_app_is_a_flask_app():
    import app as module
    assert callable(module.app)
    assert module.app.test_client().get("/").status_code == 200


def test_health_endpoint(render):
    from app import create_app
    from tests.conftest import FULL_DATA
    r = create_app(FULL_DATA).test_client().get("/healthz")
    assert r.status_code == 200 and r.get_data(as_text=True) == "ok"


def test_security_headers_are_set(render):
    from app import create_app
    from tests.conftest import FULL_DATA
    r = create_app(FULL_DATA).test_client().get("/")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_unknown_path_is_404(render):
    from app import create_app
    from tests.conftest import FULL_DATA
    assert create_app(FULL_DATA).test_client().get("/nope").status_code == 404


def test_gunicorn_is_a_runtime_dependency_and_procfile_uses_it():
    assert "gunicorn" in (ROOT / "requirements.txt").read_text().lower()
    assert "gunicorn app:app" in (ROOT / "Procfile").read_text()


@pytest.mark.skipif(not os.environ.get("SMOKE_URL"), reason="set SMOKE_URL to run against the live site")
def test_live_site_smoke():
    import urllib.request
    from app import PORTFOLIO_DATA
    with urllib.request.urlopen(os.environ["SMOKE_URL"], timeout=15) as resp:
        body = resp.read().decode("utf-8")
        assert resp.status == 200
    assert PORTFOLIO_DATA["owner"]["name"] in body
