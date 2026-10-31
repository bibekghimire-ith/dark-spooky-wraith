"""T8/T9 (route level): the page links Bootstrap safely and carries the grid and theme hooks."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "static" / "css" / "retro.css"


def test_bootstrap_is_linked_with_integrity_and_crossorigin(render):
    html = render()
    tag = re.search(r'<link[^>]+bootstrap[^>]*>', html)
    assert tag, "no Bootstrap stylesheet link"
    assert 'integrity="sha384-' in tag.group(0)
    assert 'crossorigin="anonymous"' in tag.group(0)
    assert "@5.3." in tag.group(0)  # pinned version, never "latest"


def test_retro_stylesheet_is_linked_after_bootstrap(render):
    html = render()
    assert '/static/css/retro.css' in html
    assert html.index("bootstrap") < html.index("retro.css")


def test_stylesheet_defines_the_design_tokens():
    css = CSS.read_text(encoding="utf-8")
    for token in ["--page-bg: #E5E5E5", "--panel-bg: #F0F0F0", "--ink: #000",
                  "--border: 2px solid", "--shadow: 4px 4px 0 #000"]:
        assert token.lower() in css.lower(), token
    assert "Courier New" in css and "monospace" in css
    assert "border-radius: 0" in css


def test_projects_use_a_responsive_column_grid(render):
    html = render()
    assert re.search(r'class="row[^"]*row-cols-1[^"]*row-cols-md-2[^"]*row-cols-lg-3', html)


def test_project_thumbnails_use_a_fixed_ratio_frame(render):
    html = render()
    assert "ratio-16x9" in html or "thumb" in html
    assert CSS.read_text(encoding="utf-8").count("aspect-ratio: 16 / 9") >= 1


def test_viewport_meta_present(render):
    assert 'name="viewport"' in render()
