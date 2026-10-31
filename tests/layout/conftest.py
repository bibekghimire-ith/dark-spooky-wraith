"""Browser fixtures. Skipped when Playwright or Chromium is not installed.

If the machine cannot reach the Bootstrap CDN, point BOOTSTRAP_CSS_FILE at a local
copy of bootstrap.min.css and the CDN request is answered from it.
"""
import os
import re
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

    data = copy.deepcopy(FULL_DATA)
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
    local_css = os.environ.get("BOOTSTRAP_CSS_FILE")

    def _open(width, height=900, path="/", **context):
        page = browser.new_page(viewport={"width": width, "height": height}, **context)
        if local_css:
            # A substitute file cannot match the real SRI hash, so drop the
            # attribute from the HTML in this mode only.
            def _page(route):
                response = route.fetch()
                body = re.sub(r'\s+integrity="[^"]*"', "", response.text())
                route.fulfill(response=response, body=body)

            page.route(server + path, _page)
            page.route(
                "**/bootstrap*.css",
                lambda route: route.fulfill(path=local_css, content_type="text/css"),
            )
        page.goto(server + path, wait_until="load")
        pages.append(page)
        return page

    yield _open
    for p in pages:
        p.close()
