"""T2: validate() rejects bad data with messages that name the field path."""
import copy

import pytest

from app import PORTFOLIO_DATA, validate


@pytest.fixture
def data():
    """A small valid dataset built in the test, never the real content."""
    return {
        "owner": {
            "name": "Test Owner",
            "title": "Engineer",
            "bio": "Short bio.",
            "email": "test@example.com",
        },
        "social_links": [{"label": "Site", "url": "https://example.com"}],
        "skills": {"Languages": ["Python", "Go"]},
        "projects": [
            {
                "title": "Alpha",
                "description": "First project.",
                "tech_stack": ["Python"],
                "image_url": "img/alpha.png",
                "demo_link": "https://example.com/demo",
                "code_link": "https://example.com/code",
            }
        ],
        "experience": [
            {
                "role": "Dev",
                "company": "Acme",
                "dates": "2020 - 2021",
                "highlights": ["Did a thing."],
            }
        ],
    }


def test_valid_data_has_no_errors(data):
    assert validate(data) == []


def test_shipped_data_is_valid():
    """Guards the real content: a bad edit fails CI, not the live site."""
    assert validate(copy.deepcopy(PORTFOLIO_DATA)) == []


def test_root_must_be_a_dict():
    assert validate([]) == ["PORTFOLIO_DATA must be a dict"]


def test_owner_section_is_required(data):
    del data["owner"]
    assert "owner is required" in validate(data)


@pytest.mark.parametrize("field", ["name", "title", "bio", "email"])
def test_missing_owner_field_names_the_path(data, field):
    del data["owner"][field]
    errors = validate(data)
    assert any(f"owner.{field}" in e for e in errors)


@pytest.mark.parametrize("bad", ["", "   ", None, 42])
def test_owner_fields_must_be_non_empty_strings(data, bad):
    data["owner"]["name"] = bad
    assert any("owner.name" in e for e in validate(data))


def test_tech_stack_must_be_a_list_of_strings(data):
    data["projects"][0]["tech_stack"] = "Python"
    assert "projects[0].tech_stack must be a list of strings" in validate(data)
    data["projects"][0]["tech_stack"] = ["Python", 3]
    assert "projects[0].tech_stack must be a list of strings" in validate(data)


def test_skills_must_map_names_to_lists_of_strings(data):
    data["skills"]["Backend"] = "Flask"
    assert "skills.Backend must be a list of strings" in validate(data)


def test_project_title_is_required(data):
    data["projects"][0]["title"] = ""
    assert "projects[0].title is required" in validate(data)


@pytest.mark.parametrize(
    "path,key",
    [
        (("projects", 0), "demo_link"),
        (("projects", 0), "code_link"),
        (("social_links", 0), "url"),
    ],
)
def test_links_must_use_an_allowed_scheme(data, path, key):
    section, index = path
    data[section][index][key] = "javascript:alert(1)"
    errors = validate(data)
    assert any(f"{section}[{index}].{key}" in e for e in errors)


@pytest.mark.parametrize(
    "link", ["http://example.com", "https://example.com", "mailto:a@example.com"]
)
def test_allowed_link_schemes_pass(data, link):
    data["projects"][0]["demo_link"] = link
    assert validate(data) == []


def test_empty_optional_links_are_allowed(data):
    data["projects"][0]["demo_link"] = ""
    del data["projects"][0]["code_link"]
    assert validate(data) == []


def test_unknown_keys_are_ignored(data):
    data["education"] = [{"degree": "BE"}]
    data["owner"]["nickname"] = "x"
    assert validate(data) == []


def test_all_errors_are_reported_together(data):
    del data["owner"]["email"]
    data["projects"][0]["tech_stack"] = "Python"
    assert len(validate(data)) == 2
