"""T3, T5, T6: sections are rendered from data and adapt to missing data."""
import copy
from datetime import date


# ---- T3: loops render everything from the data ------------------------------

def test_page_contains_every_skill_project_and_job(render):
    html = render()
    for text in [
        "Languages", "Testing", "Python", "Go", "Playwright", "Postman",
        "Alpha Project", "Beta Project", "First project description.",
        "Flask", "Redis", "Rust",
        "Newest Role", "Newest Co", "2024 - Present", "Newest highlight two.",
        "Older Role", "Older Co", "Older highlight.",
    ]:
        assert text in html, text


def test_adding_entries_changes_output_without_a_template_edit(full_data, render):
    full_data["projects"].append(
        {"title": "Zeta Project", "description": "Added later.", "tech_stack": ["Elixir"]}
    )
    full_data["experience"].append(
        {"role": "Zed Role", "company": "Zed Co", "dates": "2018", "highlights": ["Zed."]}
    )
    full_data["skills"]["Cloud"] = ["Kubernetes"]
    html = render(full_data)
    for text in ["Zeta Project", "Elixir", "Zed Role", "Zed Co", "Cloud", "Kubernetes"]:
        assert text in html, text


def test_experience_keeps_the_order_written(render):
    html = render()
    assert html.index("Newest Role") < html.index("Older Role")


def test_sections_have_anchor_ids(render):
    html = render()
    for anchor in ["hero", "tech", "projects", "experience", "contact"]:
        assert f'id="{anchor}"' in html, anchor


def test_social_links_render_with_their_urls(render):
    html = render()
    assert 'href="https://example.com/one"' in html
    assert ">SiteOne<" in html
    assert 'href="mailto:test@example.com"' in html


def test_project_links_render_with_urls(render):
    html = render()
    assert 'href="https://example.com/alpha-demo"' in html
    assert 'href="https://example.com/alpha-code"' in html


# ---- T5: optional fields and empty sections never break the page ------------

def test_missing_demo_and_code_links_render_no_empty_buttons(full_data, render):
    for key in ("demo_link", "code_link"):
        full_data["projects"][0][key] = ""
        del full_data["projects"][1][key]
    html = render(full_data)
    assert ">Demo<" not in html
    assert ">Code<" not in html
    assert 'href=""' not in html


def test_only_the_set_link_renders(full_data, render):
    full_data["projects"][0]["demo_link"] = ""
    html = render(full_data)
    assert ">Demo<" in html  # the second project still has one
    assert 'href="https://example.com/alpha-demo"' not in html
    assert 'href="https://example.com/alpha-code"' in html


def test_empty_skills_hide_the_section_heading_and_nav_link(full_data, render):
    full_data["skills"] = {}
    html = render(full_data)
    assert 'id="tech"' not in html
    assert 'href="#tech"' not in html


def test_missing_optional_sections_still_return_200(full_data, render):
    for key in ("social_links", "skills", "projects", "experience"):
        del full_data[key]
    html = render(full_data)
    assert "Test Owner" in html
    for anchor in ["tech", "projects", "experience"]:
        assert f'id="{anchor}"' not in html


def test_project_without_tech_stack_renders(full_data, render):
    del full_data["projects"][0]["tech_stack"]
    assert "Alpha Project" in render(full_data)


def test_experience_entry_without_highlights_renders(full_data, render):
    del full_data["experience"][0]["highlights"]
    assert "Newest Role" in render(full_data)


# ---- T6: nav, hero buttons and footer come from the data --------------------

def test_nav_has_an_anchor_for_each_section_with_data(render):
    html = render()
    for anchor in ["#tech", "#projects", "#experience", "#contact"]:
        assert f'href="{anchor}"' in html, anchor


def test_nav_omits_sections_without_data(full_data, render):
    del full_data["projects"]
    html = render(full_data)
    assert 'href="#projects"' not in html
    assert 'href="#experience"' in html
    assert 'href="#contact"' in html  # contact is always present


def test_footer_has_mailto_link_and_current_year(render):
    html = render()
    assert 'href="mailto:test@example.com"' in html
    assert f"(c) {date.today().year} Test Owner" in html
