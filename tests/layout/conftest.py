"""Browser fixtures. Skipped when Playwright or Chromium is not installed.

The site loads nothing from the internet, so no network stubbing is needed.
"""
import threading

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from app import create_app  # noqa: E402


@pytest.fixture(scope="session")
def server(request):
    from tests.conftest import FULL_DATA
    import copy

    from tests.test_home_components import extras

    data = extras(copy.deepcopy(FULL_DATA))
    data["education"] = [{"degree": "BSc Test", "school": "Test Uni", "dates": "2010 - 2014"}]
    # three projects so the 3-column case is meaningful
    data["projects"].append({"title": "Gamma Project", "description": "Third.", "tech_stack": ["C"]})
    srv = make_server("127.0.0.1", 0, create_app(data))
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as exc:  # browser binary missing
            pytest.skip(f"Chromium not available: {exc}")
        yield b
        b.close()


@pytest.fixture
def open_page(browser, server):
    pages = []

    def _open(width, height=900, path="/", **context):
        page = browser.new_page(viewport={"width": width, "height": height}, **context)
        page.goto(server + path, wait_until="load")
        pages.append(page)
        return page

    yield _open
    for p in pages:
        p.close()
