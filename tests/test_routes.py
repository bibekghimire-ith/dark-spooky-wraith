"""T1: GET / returns 200 and renders the owner name from the data."""
import pytest

from app import app as default_app
from app import create_app


@pytest.fixture
def small_data():
    return {
        "owner": {
            "name": "Test Owner",
            "title": "Staff Tester",
            "bio": "I test things.",
            "email": "test@example.com",
        },
    }


@pytest.fixture
def client(small_data):
    return create_app(small_data).test_client()


def test_index_returns_200_and_owner_name(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Test Owner" in response.get_data(as_text=True)


def test_index_shows_title_and_bio(client):
    html = client.get("/").get_data(as_text=True)
    assert "Staff Tester" in html
    assert "I test things." in html


def test_title_tag_uses_owner_data(client):
    html = client.get("/").get_data(as_text=True)
    assert "<title>Test Owner - Staff Tester</title>" in html


def test_create_app_refuses_invalid_data(small_data):
    del small_data["owner"]["email"]
    with pytest.raises(ValueError) as excinfo:
        create_app(small_data)
    assert "owner.email" in str(excinfo.value)


def test_module_level_app_serves_the_shipped_data():
    response = default_app.test_client().get("/")
    assert response.status_code == 200
