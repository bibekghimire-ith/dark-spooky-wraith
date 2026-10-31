"""T8 and T9: what only a real browser can show."""
import pytest

pytestmark = pytest.mark.layout


@pytest.mark.parametrize("width", [360, 768, 1280])
def test_no_horizontal_scroll(open_page, width):
    page = open_page(width)
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    assert scroll_width <= width, f"page is {scroll_width}px wide at {width}px"


def test_bootstrap_actually_loaded(open_page):
    page = open_page(1280)
    assert page.evaluate("getComputedStyle(document.querySelector('.row')).display") == "flex"


def test_theme_is_applied(open_page):
    page = open_page(1280)
    body = page.evaluate(
        "(() => {const s = getComputedStyle(document.body);"
        "return [s.backgroundColor, s.fontFamily]})()"
    )
    assert body[0] == "rgb(229, 229, 229)"
    assert "Courier New" in body[1] or "monospace" in body[1]


def test_cards_have_hard_shadow_and_square_corners(open_page):
    page = open_page(1280)
    s = page.evaluate(
        "(() => {const c = document.querySelector('.project');const s = getComputedStyle(c);"
        "return [s.boxShadow, s.borderRadius, s.borderTopWidth]})()"
    )
    assert "4px 4px 0px" in s[0]
    assert s[1] == "0px"
    assert s[2] == "2px"


@pytest.mark.parametrize("width,columns", [(390, 1), (800, 2), (1280, 3)])
def test_project_grid_columns(open_page, width, columns):
    page = open_page(width)
    lefts = page.evaluate(
        "[...document.querySelectorAll('#projects .project')]"
        ".map(e => Math.round(e.getBoundingClientRect().left))"
    )
    assert len(set(lefts)) == min(columns, len(lefts)), lefts


def test_thumbnails_are_16_by_9(open_page):
    page = open_page(1280)
    boxes = page.evaluate(
        "[...document.querySelectorAll('#projects .thumb')]"
        ".map(e => {const r = e.getBoundingClientRect(); return r.width / r.height})"
    )
    assert boxes
    for ratio in boxes:
        assert abs(ratio - 16 / 9) < 0.02, ratio
