"""R2-3: Markdown blog."""
import datetime

import pytest

from app import create_app
from blog import load_posts, parse_post


def post(title="Hello", date="2026-01-02", body="Body text.", extra=""):
    lines = ["---", f"title: {title}", f"date: {date}"]
    if extra:
        lines.append(extra)
    lines += ["---", body, ""]
    return "\n".join(lines)


# ---- parse_post -------------------------------------------------------------

def test_parse_post_reads_front_matter_and_renders_markdown():
    p = parse_post(post(body="Some **bold** text."), "hello-world.md")
    assert p["title"] == "Hello"
    assert p["date"] == datetime.date(2026, 1, 2)
    assert p["slug"] == "hello-world"
    assert p["draft"] is False
    assert "<strong>bold</strong>" in p["html"]


def test_parse_post_summary_defaults_to_empty_and_can_be_set():
    assert parse_post(post(), "a.md")["summary"] == ""
    assert parse_post(post(extra="summary: Short."), "a.md")["summary"] == "Short."


def test_draft_flag_is_read():
    assert parse_post(post(extra="draft: true"), "a.md")["draft"] is True


@pytest.mark.parametrize("bad_date", ["not-a-date", "2026-13-40", "01/02/2026"])
def test_bad_date_is_rejected_naming_the_file(bad_date):
    with pytest.raises(ValueError) as exc:
        parse_post(post(date=bad_date), "broken-post.md")
    assert "broken-post.md" in str(exc.value) and "date" in str(exc.value)


def test_missing_title_or_front_matter_is_rejected():
    with pytest.raises(ValueError, match="title"):
        parse_post("---\ndate: 2026-01-01\n---\nBody", "x.md")
    with pytest.raises(ValueError, match="front matter"):
        parse_post("Just text, no front matter.", "x.md")


@pytest.mark.parametrize("name", ["Bad Name.md", "../evil.md", "UPPER.md", "a_b.md", "-x.md", ".md"])
def test_slug_must_be_lowercase_words_and_dashes(name):
    with pytest.raises(ValueError, match="slug|file name"):
        parse_post(post(), name)


def test_fenced_code_is_highlighted():
    p = parse_post(post(body="```python\nprint('x')\n```"), "code.md")
    assert 'class="codehilite"' in p["html"]


# ---- sanitising -------------------------------------------------------------

@pytest.mark.parametrize("body", [
    "<script>alert(1)</script>",
    "text <img src=x onerror=alert(1)> text",
    "<iframe src='https://evil.example'></iframe>",
    "<a href=\"javascript:alert(1)\">x</a>",
])
def test_raw_html_never_becomes_live_markup(body):
    html = parse_post(post(body=body), "s.md")["html"]
    for live in ["<script", "<img", "<iframe", "<a href=\"javascript"]:
        assert live not in html.lower(), (live, html)


@pytest.mark.parametrize("link", [
    "javascript:alert(1)", "JaVaScRiPt:alert(1)", "java\tscript:alert(1)",
    "data:text/html;base64,AAAA", "vbscript:x",
])
def test_dangerous_link_schemes_are_removed(link):
    html = parse_post(post(body=f"[click]({link})"), "s.md")["html"]
    assert "javascript" not in html.lower().replace("&", "")
    assert "data:text" not in html and "vbscript" not in html
    assert "click" in html


def test_safe_links_are_kept():
    html = parse_post(post(body="[a](https://example.com) [b](/blog/x) [c](mailto:t@example.com)"), "s.md")["html"]
    for href in ["https://example.com", "/blog/x", "mailto:t@example.com"]:
        assert f'href="{href}"' in html


# ---- load_posts -------------------------------------------------------------

def test_load_posts_sorts_newest_first_and_hides_drafts(tmp_path):
    (tmp_path / "old.md").write_text(post(title="Old", date="2025-01-01"))
    (tmp_path / "new.md").write_text(post(title="New", date="2026-06-01"))
    (tmp_path / "wip.md").write_text(post(title="Wip", date="2026-07-01", extra="draft: true"))
    (tmp_path / "notes.txt").write_text("ignored")
    assert [p["title"] for p in load_posts(tmp_path)] == ["New", "Old"]


def test_load_posts_missing_directory_is_empty(tmp_path):
    assert load_posts(tmp_path / "none") == []


def test_one_bad_post_stops_loading_with_its_file_name(tmp_path):
    (tmp_path / "ok.md").write_text(post())
    (tmp_path / "bad.md").write_text(post(date="nope"))
    with pytest.raises(ValueError, match="bad.md"):
        load_posts(tmp_path)


# ---- routes -----------------------------------------------------------------

@pytest.fixture
def client(full_data, tmp_path):
    (tmp_path / "first-post.md").write_text(post(title="First Post", date="2026-03-01", body="Hello **world**.", extra="summary: A summary."))
    (tmp_path / "hidden.md").write_text(post(title="Hidden Draft", extra="draft: true"))
    (tmp_path / "evil.md").write_text(post(title="Evil", date="2026-02-01", body="<script>alert(1)</script>"))
    return create_app(full_data, posts=load_posts(tmp_path)).test_client()


def test_blog_list_shows_titles_dates_and_summaries(client):
    r = client.get("/blog")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "First Post" in html and "2026-03-01" in html and "A summary." in html
    assert 'href="/blog/first-post"' in html
    assert "Hidden Draft" not in html
    assert html.index("First Post") < html.index("Evil")


def test_blog_post_page(client):
    r = client.get("/blog/first-post")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "<strong>world</strong>" in html and "<title>First Post" in html
    assert 'href="/blog"' in html


def test_unknown_and_draft_slugs_return_404(client):
    assert client.get("/blog/nope").status_code == 404
    assert client.get("/blog/hidden").status_code == 404
    assert client.get("/blog/..%2Fapp").status_code == 404


def test_script_tag_in_a_post_is_not_served_live(client):
    html = client.get("/blog/evil").get_data(as_text=True)
    assert "<script>alert(1)" not in html


def test_empty_blog_list_still_renders(full_data):
    r = create_app(full_data, posts=[]).test_client().get("/blog")
    assert r.status_code == 200 and "No posts yet" in r.get_data(as_text=True)


def test_home_nav_links_to_blog_only_when_posts_exist(full_data, tmp_path):
    (tmp_path / "a.md").write_text(post())
    with_posts = create_app(full_data, posts=load_posts(tmp_path)).test_client().get("/").get_data(as_text=True)
    without = create_app(full_data, posts=[]).test_client().get("/").get_data(as_text=True)
    assert 'href="/blog"' in with_posts
    assert 'href="/blog"' not in without


def test_pygments_stylesheet_exists():
    from pathlib import Path
    css = Path(__file__).resolve().parent.parent / "static/css/pygments.css"
    assert css.exists() and ".codehilite" in css.read_text()
