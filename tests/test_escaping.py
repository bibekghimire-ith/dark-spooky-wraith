"""T7: content is escaped; the template never marks data as safe."""
from pathlib import Path

PAYLOAD = "<script>alert(1)</script>"
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def test_script_in_a_description_is_escaped(full_data, render):
    full_data["projects"][0]["description"] = PAYLOAD
    html = render(full_data)
    assert PAYLOAD not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_markup_in_every_text_field_is_escaped(full_data, render):
    full_data["owner"]["name"] = "<b>Name</b>"
    full_data["owner"]["bio"] = "<i>Bio</i>"
    full_data["skills"]["Languages"] = ["<u>Skill</u>"]
    full_data["experience"][0]["highlights"] = ["<em>High</em>"]
    html = render(full_data)
    for raw in ["<b>Name</b>", "<i>Bio</i>", "<u>Skill</u>", "<em>High</em>"]:
        assert raw not in html, raw


def test_quote_in_a_title_cannot_break_out_of_an_attribute(full_data, render):
    full_data["projects"][0]["title"] = 'x" onerror="alert(1)'
    html = render(full_data)
    assert 'onerror="alert(1)' not in html


def test_templates_never_use_the_safe_filter_or_disable_autoescape():
    for path in TEMPLATES.glob("*.html"):
        source = path.read_text(encoding="utf-8")
        assert "|safe" not in source.replace(" ", ""), path.name
        assert "autoescape false" not in source, path.name
