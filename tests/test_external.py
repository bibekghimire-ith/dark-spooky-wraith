"""Linked and imported writing (dev.to) and the configurable availability badge. No network is used."""
import json
import re
from datetime import date

import pytest

import external
from app import create_app, validate

POST = {"slug": "local-post", "title": "Local post", "date": date(2026, 5, 1), "summary": "Local.", "html": "", "draft": False}


def link(**kw):
    base = {"title": "Dev post", "url": "https://dev.to/me/dev-post", "date": "2026-06-01", "summary": "On DEV."}
    return {**base, **kw}


def page(full_data, path="/", posts=None, fetch=None):
    app = create_app(full_data, posts=[POST] if posts is None else posts, devto_fetch=fetch or (lambda u: []))
    return app.test_client().get(path).get_data(as_text=True)


# ---- hand-written links -----------------------------------------------------

def test_linked_post_renders_on_home_and_blog_and_opens_safely(full_data):
    full_data["writing"] = {"links": [link()]}
    for path in ("/", "/blog"):
        html = page(full_data, path)
        tag = re.search(r'<a href="https://dev.to/me/dev-post"[^>]*>', html).group(0)
        assert 'target="_blank"' in tag and "noopener" in tag
        assert "Dev post" in html and "On DEV." in html and "dev.to" in html
        assert "opens in a new tab" in html


def test_entries_are_sorted_newest_first_across_local_and_linked(full_data):
    full_data["writing"] = {"links": [link(title="June", date="2026-06-01"), link(title="March", date="2026-03-01",
                                                                                 url="https://dev.to/me/march")]}
    html = page(full_data, "/blog")
    assert html.index("June") < html.index("Local post") < html.index("March")


def test_undated_links_sort_last_and_show_no_date(full_data):
    full_data["writing"] = {"links": [link(title="Undated", date=None)]}
    html = page(full_data, "/blog")
    assert html.index("Local post") < html.index("Undated")


def test_source_label_defaults_to_the_host(full_data):
    full_data["writing"] = {"links": [link(url="https://www.example.org/p", source=None)]}
    assert ">example.org<" in page(full_data)


def test_blog_link_appears_with_only_linked_posts(full_data):
    full_data["writing"] = {"links": [link()]}
    html = page(full_data, posts=[])
    assert 'href="/blog"' in html and 'id="writing"' in html


def test_no_writing_section_without_any_posts(full_data):
    assert 'id="writing"' not in page(full_data, posts=[])


def test_link_text_is_escaped(full_data):
    full_data["writing"] = {"links": [link(title="<script>alert(1)</script>")]}
    assert "<script>alert(1)" not in page(full_data)


# ---- dev.to import ----------------------------------------------------------

def devto_entries():
    return [{"title": "Imported", "summary": "", "date": date(2026, 7, 1), "href": "https://dev.to/me/imported",
             "external": True, "source": "dev.to"}]


def test_username_triggers_an_import(full_data):
    seen = []
    full_data["writing"] = {"devto_username": "me"}
    html = page(full_data, fetch=lambda u: seen.append(u) or devto_entries())
    assert seen == ["me"] and "Imported" in html


def test_a_hand_written_link_wins_over_the_imported_duplicate(full_data):
    full_data["writing"] = {"devto_username": "me", "links": [link(title="Mine", url="https://dev.to/me/imported")]}
    html = page(full_data, fetch=lambda u: devto_entries())
    assert "Mine" in html and "Imported" not in html


def test_a_failed_import_never_stops_the_site(full_data, caplog):
    def boom(username):
        raise OSError("offline")

    full_data["writing"] = {"devto_username": "me", "links": [link()]}
    html = page(full_data, fetch=boom)
    assert "Dev post" in html and "Local post" in html
    assert "dev.to import skipped" in caplog.text


def test_no_username_means_no_network_call(full_data):
    def forbidden(username):
        raise AssertionError("must not fetch")

    full_data["writing"] = {"links": [link()]}
    page(full_data, fetch=forbidden)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_fetch_devto_keeps_only_dev_to_https_articles(monkeypatch):
    payload = [
        {"title": "Good", "url": "https://dev.to/me/good", "description": "d", "published_at": "2026-02-03T10:00:00Z"},
        {"title": "Elsewhere", "url": "https://evil.example/x", "published_at": "2026-02-03T10:00:00Z"},
        {"title": "Plain http", "url": "http://dev.to/me/p"},
        {"url": "https://dev.to/me/untitled"},
    ]
    called = {}

    def fake_urlopen(request, timeout, context=None):
        called["url"], called["timeout"], called["context"] = request.full_url, timeout, context
        return FakeResponse(payload)

    monkeypatch.setattr(external.urllib.request, "urlopen", fake_urlopen)
    entries = external.fetch_devto("me")
    assert [e["title"] for e in entries] == ["Good"]
    assert entries[0]["date"] == date(2026, 2, 3) and entries[0]["source"] == "dev.to"
    assert called["context"] is None or called["context"].verify_mode.name == "CERT_REQUIRED"
    assert called["url"].startswith("https://dev.to/api/articles?username=me") and called["timeout"] <= 10


@pytest.mark.parametrize("name", ["", "a b", "me/../x", "me?x=1", "x" * 41])
def test_fetch_devto_rejects_unsafe_usernames(name):
    with pytest.raises(ValueError):
        external.fetch_devto(name)


# ---- validation -------------------------------------------------------------

def test_valid_writing_config_passes(full_data):
    full_data["writing"] = {"devto_username": "me_1", "links": [link(), link(date=None)]}
    assert validate(full_data) == []


@pytest.mark.parametrize(
    "writing,fragment",
    [
        ("text", "writing must be a mapping"),
        ({"devto_username": "bad name"}, "devto_username"),
        ({"links": [link(url="http://dev.to/x")]}, "links[0].url must start with https://"),
        ({"links": [link(url="javascript:alert(1)")]}, "links[0].url"),
        ({"links": [link(title="")]}, "links[0].title"),
        ({"links": [link(date="31/01/2026")]}, "links[0].date"),
        ({"links": ["nope"]}, "links[0] must be a mapping"),
    ],
)
def test_bad_writing_config_is_rejected_with_the_field_name(full_data, writing, fragment):
    full_data["writing"] = writing
    assert any(fragment in e for e in validate(full_data)), validate(full_data)


# ---- availability badge -----------------------------------------------------

def test_availability_text_shows_as_open(full_data):
    full_data["owner"]["availability"] = "Available from January"
    html = page(full_data)
    assert "Available from January" in html and 'class="status status-open"' in html


@pytest.mark.parametrize("status", ["open", "limited", "closed"])
def test_availability_mapping_sets_the_status_class(full_data, status):
    full_data["owner"]["availability"] = {"text": "Booked until May", "status": status}
    assert f'class="status status-{status}"' in page(full_data)


def test_availability_mapping_defaults_to_open(full_data):
    full_data["owner"]["availability"] = {"text": "Hello"}
    assert 'status-open' in page(full_data)


@pytest.mark.parametrize("value", [None, "", ])
def test_empty_availability_hides_the_badge(full_data, value):
    full_data["owner"]["availability"] = value
    assert 'class="status' not in page(full_data)


def test_availability_text_is_escaped(full_data):
    full_data["owner"]["availability"] = "<b>x</b>"
    assert "<b>x</b>" not in page(full_data)


@pytest.mark.parametrize(
    "value,fragment",
    [({"status": "open"}, "availability.text"), ({"text": "x", "status": "busy"}, "availability.status"),
     (5, "availability must be")],
)
def test_bad_availability_is_rejected(full_data, value, fragment):
    full_data["owner"]["availability"] = value
    assert any(fragment in e for e in validate(full_data)), validate(full_data)
