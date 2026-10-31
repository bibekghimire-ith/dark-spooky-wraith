"""Featured project card and the inline case study (the page stays a single HTML page)."""
import re

import pytest

from app import create_app, slug, validate

CASE = {"problem": "P text.", "role": "R text.", "approach": "A text.", "result": "Result text."}


def with_case(full_data, index=0, **case):
    full_data["projects"][index]["case_study"] = case or dict(CASE)
    return full_data


def html_of(full_data, check_images=False):
    return create_app(full_data, posts=[], check_images=check_images).test_client().get("/").get_data(as_text=True)


# ---- case study -------------------------------------------------------------

def test_case_study_renders_inside_the_project_card_not_on_another_page(full_data):
    html = html_of(with_case(full_data))
    card = re.search(r'<article class="project card.*?</article>', html, re.S).group(0)
    assert '<details class="case-study" id="case-alpha-project">' in card
    for text in ["Read the case study", "Problem", "P text.", "My role", "R text.", "Approach", "A text.", "Result",
                 "Result text."]:
        assert text in card, text
    assert "/projects/" not in html


def test_only_filled_fields_are_shown(full_data):
    html = html_of(with_case(full_data, problem="Only this."))
    assert "<dt>Problem</dt>" in html
    for label in ["My role", "Approach", "<dt>Result</dt>"]:
        assert label not in html


def test_no_case_study_means_no_details_block(full_data):
    assert "case-study" not in html_of(full_data)


@pytest.mark.parametrize("case", [{}, {"problem": ""}, None, ""])
def test_empty_case_study_renders_nothing(full_data, case):
    full_data["projects"][0]["case_study"] = case
    assert "case-study" not in html_of(full_data)


def test_case_study_text_is_escaped(full_data):
    html = html_of(with_case(full_data, problem="<script>alert(1)</script>"))
    assert "<script>alert(1)" not in html


def test_diagram_renders_with_alt_size_and_lazy_loading(full_data):
    with_case(full_data, problem="P.", diagram="https://cdn.example.com/d.png", diagram_alt="Pipeline diagram")
    html = html_of(full_data)
    tag = re.search(r'<img src="https://cdn.example.com/d.png"[^>]*>', html).group(0)
    assert 'alt="Pipeline diagram"' in tag and 'loading="lazy"' in tag and 'width="640"' in tag


def test_diagram_alt_falls_back_to_the_project_title(full_data):
    with_case(full_data, diagram="https://cdn.example.com/d.png")
    assert 'alt="Alpha Project diagram"' in html_of(full_data)


def test_a_diagram_alone_is_enough_for_a_case_study(full_data):
    with_case(full_data, diagram="https://cdn.example.com/d.png")
    assert "Read the case study" in html_of(full_data)


def test_missing_local_diagram_is_skipped_like_a_missing_image(full_data):
    with_case(full_data, problem="P.", diagram="img/not-there.png")
    html = html_of(full_data, check_images=True)
    assert "not-there.png" not in html and "Read the case study" in html


# ---- featured ---------------------------------------------------------------

def test_featured_project_gets_the_wide_card_and_a_tag(full_data):
    full_data["projects"][0]["featured"] = True
    html = html_of(full_data)
    assert len(re.findall(r'class="project card featured"', html)) == 1
    assert '<p class="tag">featured</p>' in html


def test_nothing_is_featured_by_default(full_data):
    assert "featured" not in html_of(full_data)


def test_last_card_spans_the_row_only_when_the_rest_is_odd(full_data):
    full_data["projects"].append({"title": "Gamma", "description": "g"})
    assert html_of(full_data).count("span-2") == 1  # three plain cards: the last spans
    full_data["projects"][0]["featured"] = True
    assert "span-2" not in html_of(full_data)  # featured + two cards: a clean pair
    full_data["projects"].append({"title": "Delta", "description": "d"})
    assert html_of(full_data).count("span-2") == 1  # featured + three: the last spans


# ---- helpers and validation -------------------------------------------------

@pytest.mark.parametrize("title,expected", [("Log Parser Regression Tool", "log-parser-regression-tool"),
                                            ("  A/B: Test!  ", "a-b-test"), ("***", "project")])
def test_slug(title, expected):
    assert slug(title) == expected


def test_valid_case_study_and_featured_pass_validation(full_data):
    with_case(full_data)["projects"][0]["featured"] = True
    assert validate(full_data) == []


@pytest.mark.parametrize(
    "project_update,fragment",
    [({"featured": "yes"}, "projects[0].featured"), ({"case_study": "text"}, "projects[0].case_study must be"),
     ({"case_study": {"problem": 5}}, "case_study.problem must be text"),
     ({"case_study": {"result": ["x"]}}, "case_study.result must be text")],
)
def test_bad_project_extras_are_rejected(full_data, project_update, fragment):
    full_data["projects"][0].update(project_update)
    assert any(fragment in e for e in validate(full_data)), validate(full_data)


def test_site_script_opens_a_case_study_from_the_url_hash():
    from pathlib import Path
    js = (Path(__file__).resolve().parent.parent / "static/js/site.js").read_text()
    assert "openFromHash" in js and "hashchange" in js and ".open = true" in js
