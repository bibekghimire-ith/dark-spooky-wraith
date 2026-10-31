"""Home page components added in the redesign: hero extras, stats, focus, timeline, contact, 404."""
import re

from app import create_app, validate


def extras(full_data):
    full_data["owner"].update(location="Nowhere", availability="Open to work", cta_title="Say hi", cta="Write me.")
    full_data["hero_console"] = ["$ whoami", "test owner"]
    full_data["stats"] = [{"value": "6+", "label": "years"}, {"value": "50%", "label": "faster"}]
    full_data["focus"] = [{"title": "Backend", "text": "Services."}]
    full_data["projects"][0]["impact"] = "Cut time by half"
    return full_data


def test_optional_components_render_when_data_is_given(full_data, render):
    html = render(extras(full_data))
    for text in ["Nowhere", "Open to work", "Say hi", "Write me.", "$ whoami", "years", "50%",
                 "What I do", "Backend", "Cut time by half"]:
        assert text in html, text
    assert 'href="#about"' in html


def test_optional_components_are_absent_without_data(render):
    html = render()
    for marker in ['class="console"', 'class="stats"', 'id="about"', 'class="impact"', 'class="status"']:
        assert marker not in html, marker
    assert 'href="#about"' not in html


def test_console_command_lines_are_styled_apart_from_output(full_data, render):
    html = render(extras(full_data))
    assert '<span class="cmd">$ whoami</span>' in html
    assert '<span class="out">test owner</span>' in html


def test_current_role_is_tagged(full_data, render):
    html = render(full_data)
    assert 'class="tag">current<' in html  # "2024 - Present"
    assert html.count('class="tag">current<') == 1


def test_experience_is_an_ordered_timeline(render):
    assert '<ol class="timeline">' in render()


def test_credentials_section_needs_education_or_certifications(full_data, render):
    assert 'id="credentials"' not in render()
    full_data["education"] = [{"degree": "BSc", "school": "Uni", "dates": "2010"}]
    assert 'id="credentials"' in render(full_data)


def test_latest_posts_section_only_when_posts_exist(full_data):
    post = {"slug": "hello", "title": "Hello post", "date": __import__("datetime").date(2026, 1, 2),
            "summary": "Sum.", "html": "", "draft": False}
    with_posts = create_app(full_data, posts=[post]).test_client().get("/").get_data(as_text=True)
    without = create_app(full_data, posts=[]).test_client().get("/").get_data(as_text=True)
    assert 'id="writing"' in with_posts and "Hello post" in with_posts
    assert 'id="writing"' not in without


def test_contact_section_has_defaults(render):
    html = render()
    assert 'id="contact"' in html
    assert "Let&#39;s build something reliable." in html


def test_custom_404_page_links_home(full_data):
    r = create_app(full_data).test_client().get("/nope")
    body = r.get_data(as_text=True)
    assert r.status_code == 404
    assert "Nothing here." in body and 'href="/"' in body


def test_blog_pages_link_back_to_home_sections(full_data):
    post = {"slug": "hello", "title": "Hello post", "date": __import__("datetime").date(2026, 1, 2),
            "summary": "", "html": "", "draft": False}
    html = create_app(full_data, posts=[post]).test_client().get("/blog").get_data(as_text=True)
    assert 'href="/#projects"' in html
    assert 'aria-current="page"' in html


def test_validation_of_new_keys(full_data):
    full_data["stats"] = [{"value": 3, "label": "x"}]
    full_data["focus"] = [{"title": "only title"}]
    full_data["hero_console"] = "not a list"
    errors = validate(full_data)
    assert any(e.startswith("stats[0]") for e in errors)
    assert any(e.startswith("focus[0]") for e in errors)
    assert any(e.startswith("hero_console") for e in errors)


def test_new_keys_are_valid_when_well_formed(full_data):
    assert validate(extras(full_data)) == []
