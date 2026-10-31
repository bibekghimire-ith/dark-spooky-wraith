"""R2-5: optional analytics script."""
import re

SRC = "https://stats.example.com/js/script.js"


def scripts(html):
    """Third-party script tags; the site's own static/js file is not analytics."""
    tags = re.findall(r"<script\b[^>]*>", html)
    return [t for t in tags if "/static/js/" not in t]


def test_no_analytics_key_renders_no_script_tag(render):
    assert scripts(render()) == []


def test_empty_analytics_renders_no_script_tag(full_data, render):
    full_data["analytics"] = {}
    assert scripts(render(full_data)) == []
    full_data["analytics"] = {"script_src": "", "domain": ""}
    assert scripts(render(full_data)) == []


def test_configured_analytics_renders_exactly_one_tag(full_data, render):
    full_data["analytics"] = {"script_src": SRC, "domain": "example.com"}
    tags = scripts(render(full_data))
    assert len(tags) == 1
    assert f'src="{SRC}"' in tags[0] and 'data-domain="example.com"' in tags[0]
    assert "defer" in tags[0]


def test_analytics_only_needs_both_values(full_data, render):
    full_data["analytics"] = {"script_src": SRC}
    assert scripts(render(full_data)) == []


def test_analytics_values_are_escaped(full_data, render):
    full_data["analytics"] = {"script_src": SRC, "domain": 'x" onload="alert(1)'}
    assert 'onload="alert(1)' not in render(full_data)


def test_validate_rejects_non_https_script_source():
    from app import validate
    from tests.conftest import FULL_DATA
    import copy
    d = copy.deepcopy(FULL_DATA)
    d["analytics"] = {"script_src": "http://insecure.example.com/a.js", "domain": "example.com"}
    assert any("analytics.script_src" in e for e in validate(d))
    d["analytics"] = {"script_src": "javascript:alert(1)", "domain": "example.com"}
    assert any("analytics.script_src" in e for e in validate(d))
    d["analytics"] = "on"
    assert any("analytics" in e for e in validate(d))


def test_cv_page_has_no_analytics_script(full_data):
    from app import create_app
    full_data["analytics"] = {"script_src": SRC, "domain": "example.com"}
    html = create_app(full_data).test_client().get("/cv").get_data(as_text=True)
    assert len(scripts(html)) <= 1
