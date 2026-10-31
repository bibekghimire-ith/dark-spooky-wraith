"""Section order, numbering and the experience-first layout (see README, "Page order")."""
import re

import pytest

from app import validate


def extras(full_data, roles=5):
    full_data["focus"] = [{"title": "T", "text": "Text."}]
    full_data["education"] = [{"degree": "BSc", "school": "Uni", "dates": "2010"}]
    full_data["certifications"] = [{"name": "Cert", "issuer": "Issuer", "date": "2020"}]
    full_data["experience"] = [
        {"role": f"Role {i}", "company": f"Co {i}", "dates": f"{2030 - i}", "highlights": [f"Did {i}."],
         "tech": [f"Tech{i}"]} for i in range(roles)
    ]
    return full_data


def ids(html):
    """Section ids in page order. "writing" depends on which posts exist, so it is left out."""
    return [i for i in re.findall(r'<section id="([a-z]+)"', html) if i != "writing"]


def test_sections_run_about_experience_projects_tech_credentials_contact(full_data, render):
    html = render(extras(full_data))
    assert ids(html) == ["hero", "about", "experience", "projects", "tech", "credentials", "contact"]


def test_nav_follows_the_page_order(full_data, render):
    html = render(extras(full_data))
    nav = re.search(r'<nav aria-label="Sections">(.*?)</nav>', html, re.S).group(1)
    assert re.findall(r'href="#([a-z]+)"', nav) == ["about", "experience", "projects", "tech", "contact"]


def test_section_numbers_are_sequential_even_when_sections_are_missing(full_data, render):
    del full_data["skills"]
    html = render(extras(full_data))
    numbers = re.findall(r'<p class="eyebrow">(\d\d) / ', html)
    assert numbers == [f"{i:02d}" for i in range(1, len(numbers) + 1)]
    assert "Toolbox" not in html


def test_primary_hero_button_leads_to_experience(full_data, render):
    html = render(extras(full_data))
    first_btn = re.search(r'<a class="btn" href="([^"]+)">([^<]+)</a>', html)
    assert first_btn.groups() == ("#experience", "View experience")


def test_hero_has_no_experience_button_without_experience(full_data, render):
    del full_data["experience"]
    assert "View experience" not in render(full_data)


# ---- earlier roles ----------------------------------------------------------

def test_newest_three_roles_are_expanded_and_older_ones_collapsed(full_data, render):
    html = render(extras(full_data))
    before, after = html.split('<details class="earlier">')
    for i in range(3):
        assert f"Role {i}" in before
    for i in (3, 4):
        assert f"Role {i}" in after and f"Role {i}" not in before
    assert "Earlier roles (2)" in html


def test_no_details_block_when_all_roles_fit(full_data, render):
    assert "<details" not in render(extras(full_data, roles=3))


@pytest.mark.parametrize("visible,expected_earlier", [(0, False), (1, True), (5, False)])
def test_experience_visible_is_configurable(full_data, render, visible, expected_earlier):
    data = extras(full_data)
    data["experience_visible"] = visible
    html = render(data)
    assert ("<details" in html) is expected_earlier
    assert all(f"Role {i}" in html for i in range(5))  # collapsed is still in the page


def test_role_tags_render_only_when_given(full_data, render):
    data = extras(full_data)
    del data["experience"][0]["tech"]
    html = render(data)
    assert "Tech1" in html and "Tech0" not in html


def test_full_cv_link_follows_the_experience_list(full_data, render):
    html = render(extras(full_data))
    assert html.index("View full CV") > html.index("Role 4")
    assert html.index("View full CV") < html.index('id="projects"')


# ---- credentials ------------------------------------------------------------

def test_credentials_are_one_compact_card(full_data, render):
    html = render(extras(full_data))
    assert html.count('class="card credentials"') == 1
    for text in ["BSc", "Uni", "Cert", "Issuer", "Education", "Certifications"]:
        assert text in html


def test_credentials_with_only_certifications(full_data, render):
    data = extras(full_data)
    del data["education"]
    html = render(data)
    assert "<h3>Education</h3>" not in html and "<h3>Certifications</h3>" in html


# ---- validation -------------------------------------------------------------

@pytest.mark.parametrize("value", [-1, "3", 1.5, True])
def test_bad_experience_visible_is_rejected(full_data, value):
    full_data["experience_visible"] = value
    assert any("experience_visible" in e for e in validate(full_data))


def test_bad_role_tags_are_rejected_with_the_index(full_data):
    full_data["experience"][1]["tech"] = "Python"
    assert any(e.startswith("experience[1].tech") for e in validate(full_data))
