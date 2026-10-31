"""The page links its own stylesheet and script, makes no third-party requests, and carries the theme hooks."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "static" / "css" / "site.css"
JS = ROOT / "static" / "js" / "site.js"


def test_page_makes_no_third_party_requests(render):
    html = render()
    for tag in re.findall(r"<(?:link|script|img)\b[^>]*>", html):
        for url in re.findall(r'(?:href|src)="([^"]+)"', tag):
            assert not url.startswith(("http://", "https://")) or "cdn.example.com" in url, tag


def test_stylesheet_and_script_are_linked(render):
    html = render()
    assert "/static/css/site.css" in html
    assert re.search(r'<script defer src="/static/js/site.js"', html)


def test_stylesheet_defines_tokens_and_both_colour_schemes():
    css = CSS.read_text(encoding="utf-8")
    for token in ["--bg:", "--surface:", "--ink:", "--accent:", "--radius:", "--space-4:"]:
        assert token in css, token
    assert "prefers-color-scheme: dark" in css
    assert ':root[data-theme="dark"]' in css


def test_projects_use_a_responsive_grid(render):
    assert 'class="project-grid"' in render()
    assert "grid-template-columns" in CSS.read_text(encoding="utf-8")


def test_project_thumbnails_use_a_fixed_ratio_frame(render):
    assert 'class="thumb"' in render()
    assert CSS.read_text(encoding="utf-8").count("aspect-ratio: 16 / 9") >= 1


def test_viewport_meta_present(render):
    assert 'name="viewport"' in render()


def test_theme_toggle_is_hidden_until_the_script_runs(render):
    assert re.search(r'<button id="theme-toggle"[^>]*\bhidden\b', render())


def test_script_stores_only_a_theme_choice():
    js = JS.read_text(encoding="utf-8")
    assert "localStorage" in js and "try" in js  # storage access is guarded
