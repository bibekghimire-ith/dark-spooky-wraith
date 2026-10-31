"""Shared fixtures. Content is built in the test, never read from PORTFOLIO_DATA."""
import copy

import pytest

from app import create_app

FULL_DATA = {
    "owner": {
        "name": "Test Owner",
        "title": "Staff Tester",
        "bio": "I test things.",
        "email": "test@example.com",
    },
    "social_links": [
        {"label": "SiteOne", "url": "https://example.com/one"},
        {"label": "MailMe", "url": "mailto:test@example.com"},
    ],
    "skills": {
        "Languages": ["Python", "Go"],
        "Testing": ["Playwright", "Postman"],
    },
    "projects": [
        {
            "title": "Alpha Project",
            "description": "First project description.",
            "tech_stack": ["Flask", "Redis"],
            "image_url": "img/alpha.png",
            "demo_link": "https://example.com/alpha-demo",
            "code_link": "https://example.com/alpha-code",
        },
        {
            "title": "Beta Project",
            "description": "Second project description.",
            "tech_stack": ["Rust"],
            "image_url": "https://cdn.example.com/beta.png",
            "demo_link": "https://example.com/beta-demo",
            "code_link": "https://example.com/beta-code",
        },
    ],
    "experience": [
        {
            "role": "Newest Role",
            "company": "Newest Co",
            "dates": "2024 - Present",
            "highlights": ["Newest highlight one.", "Newest highlight two."],
        },
        {
            "role": "Older Role",
            "company": "Older Co",
            "dates": "2020 - 2024",
            "highlights": ["Older highlight."],
        },
    ],
}


@pytest.fixture
def full_data():
    return copy.deepcopy(FULL_DATA)


@pytest.fixture
def render(full_data):
    """Render the page for a (possibly modified) dataset and return the HTML."""

    def _render(data=None):
        client = create_app(full_data if data is None else data).test_client()
        response = client.get("/")
        assert response.status_code == 200
        return response.get_data(as_text=True)

    return _render
