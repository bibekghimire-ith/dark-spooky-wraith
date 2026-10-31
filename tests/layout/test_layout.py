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


# ---- R2-2: print view -------------------------------------------------------

def test_cv_hides_screen_only_elements_when_printing(open_page):
    page = open_page(800, path="/cv")
    assert page.evaluate("getComputedStyle(document.querySelector('.no-print')).display") != "none"
    page.emulate_media(media="print")
    assert page.evaluate("getComputedStyle(document.querySelector('.no-print')).display") == "none"


def test_cv_prints_black_on_white_without_shadows(open_page):
    page = open_page(800, path="/cv", color_scheme="dark")
    page.emulate_media(media="print", color_scheme="dark")
    colors = page.evaluate(
        "(() => {const s = getComputedStyle(document.body);"
        "return [s.backgroundColor, s.color]})()"
    )
    assert colors == ["rgb(255, 255, 255)", "rgb(0, 0, 0)"]


def test_cv_has_no_sideways_scroll_on_a_phone(open_page):
    page = open_page(360, path="/cv")
    assert page.evaluate("document.documentElement.scrollWidth") <= 360


# ---- R2-4: dark mode --------------------------------------------------------

CONTRAST_JS = """
(selector) => {
  const lum = (rgb) => {
    const [r, g, b] = rgb.match(/[\\d.]+/g).slice(0, 3).map(Number).map(v => {
      v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const el = document.querySelector(selector);
  let bg = null, node = el;
  while (node && !bg) {
    const c = getComputedStyle(node).backgroundColor;
    if (c && !c.startsWith('rgba(0, 0, 0, 0')) bg = c;
    node = node.parentElement;
  }
  const fg = getComputedStyle(el).color;
  const [a, b] = [lum(fg), lum(bg)].sort((x, y) => y - x);
  return (a + 0.05) / (b + 0.05);
}
"""


def test_dark_scheme_changes_the_page_background(open_page):
    light = open_page(1280).evaluate("getComputedStyle(document.body).backgroundColor")
    dark = open_page(1280, color_scheme="dark").evaluate("getComputedStyle(document.body).backgroundColor")
    assert light != dark
    assert dark == "rgb(26, 26, 26)"


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("selector", ["body", ".badge-list li", ".panel p", ".btn-retro", "h2"])
def test_text_contrast_is_at_least_4_5_to_1(open_page, scheme, selector):
    page = open_page(1280, color_scheme=scheme)
    ratio = page.evaluate(CONTRAST_JS, selector)
    assert ratio >= 4.5, f"{selector} in {scheme}: {ratio:.2f}"


def test_dark_cards_keep_a_visible_hard_shadow(open_page):
    page = open_page(1280, color_scheme="dark")
    shadow = page.evaluate("getComputedStyle(document.querySelector('.project')).boxShadow")
    assert "4px 4px 0px" in shadow and "rgb(0, 0, 0)" not in shadow
