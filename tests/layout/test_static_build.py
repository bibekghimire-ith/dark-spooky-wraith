"""The static single page, opened as a plain file: no server, no Flask, no network."""
import pytest

from app import PORTFOLIO_DATA, create_app
from build import build_single

pytestmark = pytest.mark.layout


@pytest.fixture(scope="module")
def page_url(tmp_path_factory):
    app = create_app(PORTFOLIO_DATA, posts=[], check_images=True, single_page=True)
    out = tmp_path_factory.mktemp("static-site")
    build_single(out, app)
    return (out / "index.html").as_uri()


@pytest.fixture
def open_file(browser, page_url):
    pages, problems = [], []

    def _open(width=1280, **context):
        page = browser.new_page(viewport={"width": width, "height": 900}, **context)
        page.on("console", lambda m: problems.append(m.text) if m.type in ("error", "warning") else None)
        page.on("requestfailed", lambda r: problems.append(f"failed: {r.url}"))
        page.on("request", lambda r: problems.append(f"network: {r.url}") if not r.url.startswith(("file:", "data:")) else None)
        page.goto(page_url)
        pages.append(page)
        return page, problems

    yield _open
    for p in pages:
        p.close()


def test_page_is_styled_with_no_requests_beyond_the_file(open_file):
    page, problems = open_file()
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(246, 247, 249)"
    assert page.evaluate("getComputedStyle(document.querySelector('.project-grid')).display") == "grid"
    assert problems == []


@pytest.mark.parametrize("width", [360, 768, 1280])
def test_no_sideways_scroll(open_file, width):
    page, _ = open_file(width)
    assert page.evaluate("document.documentElement.scrollWidth") <= width


def test_script_features_work_from_a_file(open_file):
    page, _ = open_file(color_scheme="light")
    page.locator("#theme-toggle").click()
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    page.locator("#projects .case-study summary").first.click()
    assert page.evaluate("document.querySelector('#projects .case-study').open")
    page.click('.site-nav nav a[href="#projects"]')
    page.wait_for_selector('.site-nav nav a[href="#projects"][aria-current]', timeout=3000)


def test_no_link_points_at_a_page_that_is_not_there(open_file):
    page, _ = open_file()
    hrefs = page.evaluate("[...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
    assert hrefs and all(h.startswith(("#", "https://", "mailto:")) for h in hrefs), hrefs
