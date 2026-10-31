"""T10/T11: accessibility and hardening assertions."""
import re


def _tags(html, name):
    return re.findall(rf"<{name}\b[^>]*>", html)


def test_exactly_one_h1(render):
    assert len(re.findall(r"<h1\b", render())) == 1


def test_every_image_has_non_empty_alt(render):
    imgs = _tags(render(), "img")
    assert imgs
    for tag in imgs:
        m = re.search(r'alt="([^"]*)"', tag)
        assert m and m.group(1).strip(), tag


def test_external_links_open_safely(render):
    html = render()
    anchors = [a for a in _tags(html, "a") if re.search(r'href="https?://', a)]
    assert anchors
    for tag in anchors:
        rel = re.search(r'rel="([^"]*)"', tag)
        assert rel and "noopener" in rel.group(1), tag


def test_internal_and_mailto_links_do_not_open_new_tabs(render):
    for tag in _tags(render(), "a"):
        if re.search(r'href="(#|mailto:)', tag):
            assert "target=" not in tag, tag


def test_skip_link_is_first_focusable_and_targets_main(render):
    html = render()
    first_a = re.search(r"<a\b[^>]*>", html).group(0)
    assert 'href="#main"' in first_a and "skip-link" in first_a
    assert 'id="main"' in html


def test_landmarks_present(render):
    html = render()
    for tag in ["<header", "<nav", "<main", "<footer"]:
        assert tag in html, tag


def test_nav_has_an_accessible_name(render):
    assert re.search(r"<nav[^>]*aria-label=\"[^\"]+\"", render())


def test_html_lang_and_meta_tags(render):
    html = render()
    assert '<html lang="en">' in html
    assert 'name="description"' in html
    assert 'name="theme-color"' in html


def test_project_images_are_lazy_and_sized(render):
    for tag in _tags(render(), "img"):
        assert 'loading="lazy"' in tag, tag
        assert "width=" in tag and "height=" in tag, tag


def test_stylesheet_has_focus_styles_and_skip_link_rule():
    from pathlib import Path
    css = (Path(__file__).resolve().parent.parent / "static/css/retro.css").read_text()
    assert ":focus-visible" in css
    assert ".skip-link" in css
    assert "prefers-reduced-motion" in css
