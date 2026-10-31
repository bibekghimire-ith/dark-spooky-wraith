"""T8 and T9: what only a real browser can show."""
import pytest

pytestmark = pytest.mark.layout


@pytest.mark.parametrize("width", [360, 768, 1280])
def test_no_horizontal_scroll(open_page, width):
    page = open_page(width)
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    assert scroll_width <= width, f"page is {scroll_width}px wide at {width}px"


def test_stylesheet_actually_loaded(open_page):
    page = open_page(1280)
    assert page.evaluate("getComputedStyle(document.querySelector('.project-grid')).display") == "grid"


def test_theme_is_applied(open_page):
    page = open_page(1280)
    body = page.evaluate(
        "(() => {const s = getComputedStyle(document.body);"
        "return [s.backgroundColor, s.fontFamily]})()"
    )
    assert body[0] == "rgb(246, 247, 249)"
    assert "system-ui" in body[1] or "Segoe" in body[1] or "sans" in body[1].lower()


def test_cards_are_rounded_with_a_border(open_page):
    page = open_page(1280)
    s = page.evaluate(
        "(() => {const c = document.querySelector('.project');const s = getComputedStyle(c);"
        "return [s.borderRadius, s.borderTopWidth]})()"
    )
    assert s[0] == "12px" and s[1] == "1px"


@pytest.mark.parametrize("width,columns", [(390, 1), (800, 2), (1280, 2)])
def test_project_grid_columns(open_page, width, columns):
    page = open_page(width)
    lefts = page.evaluate(
        "[...document.querySelectorAll('#projects .project')]"
        ".map(e => Math.round(e.getBoundingClientRect().left))"
    )
    assert len(set(lefts)) == min(columns, len(lefts)), lefts


def test_odd_last_project_spans_the_full_row(open_page):
    page = open_page(1280)  # the fixture has three projects
    widths = page.evaluate(
        "[...document.querySelectorAll('#projects .project')]"
        ".map(e => Math.round(e.getBoundingClientRect().width))"
    )
    assert widths[2] > widths[0] * 1.8, widths


def test_nav_stays_visible_when_scrolling_on_desktop(open_page):
    page = open_page(1280, height=700)
    page.evaluate("window.scrollTo(0, 1500)")
    top = page.evaluate("document.querySelector('.site-nav').getBoundingClientRect().top")
    assert top == 0


def test_theme_toggle_switches_and_remembers(open_page):
    page = open_page(1280, color_scheme="light")
    toggle = page.locator("#theme-toggle")
    assert toggle.is_visible()
    toggle.click()
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(14, 17, 22)"
    page.reload()
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"


def test_scrollspy_marks_the_section_in_view(open_page):
    page = open_page(1280, height=700)
    page.evaluate("document.querySelector('#projects').scrollIntoView()")
    page.wait_for_selector('.site-nav nav a[href="#projects"][aria-current]', timeout=3000)


def test_empty_covers_are_a_slim_banner_not_a_tall_block(open_page):
    page = open_page(1280)  # the fixture projects have no image on disk
    ratios = page.evaluate(
        "[...document.querySelectorAll('#projects .thumb')]"
        ".map(e => {const r = e.getBoundingClientRect(); return r.width / r.height})"
    )
    assert ratios
    for ratio in ratios:
        assert ratio >= 16 / 9, ratio


def test_image_thumbnails_are_16_by_9():
    from pathlib import Path
    css = (Path(__file__).resolve().parent.parent.parent / "static/css/site.css").read_text()
    assert "aspect-ratio: 16 / 9" in css


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
    assert dark == "rgb(14, 17, 22)"


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize(
    "selector",
    ["body", ".lead", ".chip-list li", ".card p", "main .btn:not(.btn-ghost)", "main .btn-ghost", "h2",
     ".eyebrow", ".stat-value", ".stat-label", ".impact", ".company", ".dates", ".site-nav nav a",
     ".site-footer", ".meta"],
)
def test_text_contrast_is_at_least_4_5_to_1(open_page, scheme, selector):
    page = open_page(1280, color_scheme=scheme)
    ratio = page.evaluate(CONTRAST_JS, selector)
    assert ratio >= 4.5, f"{selector} in {scheme}: {ratio:.2f}"


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_console_text_is_readable(open_page, scheme):
    page = open_page(1280, color_scheme=scheme)
    for selector in (".console .cmd", ".console .out", ".console-bar"):
        assert page.evaluate(CONTRAST_JS, selector) >= 4.5, selector
