"""R2-2: print-friendly CV at /cv."""
import re

import pytest

from app import create_app


@pytest.fixture
def cv(full_data):
    def _cv(data=None):
        r = create_app(full_data if data is None else data).test_client().get("/cv")
        assert r.status_code == 200
        return r.get_data(as_text=True)
    return _cv


def test_cv_returns_200_with_content(cv):
    html = cv()
    for text in ["Test Owner", "Staff Tester", "I test things.", "Newest Role", "Newest Co",
                 "2024 - Present", "Newest highlight one.", "Python", "Alpha Project"]:
        assert text in html, text


def test_cv_omits_the_site_navbar(cv):
    html = cv()
    assert "<nav" not in html
    assert 'href="#projects"' not in html


def test_cv_has_one_h1_and_a_way_back(cv):
    html = cv()
    assert len(re.findall(r"<h1\b", html)) == 1
    assert 'href="/"' in html


def test_cv_has_education_and_certifications_when_given(full_data, cv):
    full_data["education"] = [{"degree": "BSc Test", "school": "Test Uni", "dates": "2010 - 2014"}]
    full_data["certifications"] = [{"name": "Cert One", "issuer": "Issuer X", "date": "2020"}]
    html = cv(full_data)
    for text in ["BSc Test", "Test Uni", "Cert One", "Issuer X"]:
        assert text in html, text


def test_cv_works_with_only_the_required_fields(full_data, cv):
    for key in ("social_links", "skills", "projects", "experience"):
        del full_data[key]
    assert "Test Owner" in cv(full_data)


def test_cv_escapes_content(full_data, cv):
    full_data["owner"]["bio"] = "<script>alert(1)</script>"
    assert "<script>alert(1)" not in cv(full_data)


def test_home_page_links_to_the_cv(render):
    assert 'href="/cv"' in render()


def test_print_rules_exist_in_the_stylesheet():
    from pathlib import Path
    css = (Path(__file__).resolve().parent.parent / "static/css/retro.css").read_text()
    assert "@media print" in css and ".no-print" in css
