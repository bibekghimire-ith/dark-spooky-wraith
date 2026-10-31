"""T4: image_src() rules and how images render in project cards."""
import pytest

from app import create_app, image_src


@pytest.fixture
def ctx(full_data):
    with create_app(full_data).test_request_context():
        yield


@pytest.mark.usefixtures("ctx")
@pytest.mark.parametrize(
    "value,expected",
    [
        ("https://cdn.example.com/a.png", "https://cdn.example.com/a.png"),
        ("http://example.com/a.png", "http://example.com/a.png"),
        ("img/x.png", "/static/img/x.png"),
        ("/img/x.png", "/static/img/x.png"),
        ("", None),
        ("   ", None),
        (None, None),
        ("../secret.png", None),
        ("img/../../secret.png", None),
        ("javascript:alert(1)", None),
    ],
)
def test_image_src_rules(value, expected):
    assert image_src(value) == expected


def test_local_image_renders_through_static(render):
    html = render()
    assert 'src="/static/img/alpha.png"' in html


def test_hosted_image_renders_as_is(render):
    html = render()
    assert 'src="https://cdn.example.com/beta.png"' in html


def test_image_alt_text_is_the_project_title(render):
    html = render()
    assert 'alt="Alpha Project"' in html


def test_project_without_image_gets_a_placeholder_not_a_broken_img(full_data, render):
    full_data["projects"][0]["image_url"] = ""
    html = render(full_data)
    assert 'class="project-placeholder"' in html
    assert 'src=""' not in html


def test_unusable_image_value_falls_back_to_the_placeholder(full_data, render):
    full_data["projects"][0]["image_url"] = "../secret.png"
    html = render(full_data)
    assert "secret.png" not in html
    assert 'class="project-placeholder"' in html
