"""Static export (build.py): every page, correct links under any base path, safe output folder."""
import re
from datetime import date

import pytest

from app import create_app
from build import build, main, normalise_base_path

POST = {"slug": "hello-post", "title": "Hello post", "date": date(2026, 1, 2), "summary": "S.", "html": "<p>Body</p>",
        "draft": False}


@pytest.fixture
def app(full_data):
    full_data["writing"] = {"links": [{"title": "On DEV", "url": "https://dev.to/me/p", "date": "2026-02-01"}]}
    return create_app(full_data, posts=[POST], check_images=True)


def run(app, out, base=""):
    return build(out, base, app=app, slugs=[POST["slug"]])


def internal_links(html):
    for url in re.findall(r'(?:href|src)="([^"]+)"', html):
        if url.startswith(("http://", "https://", "mailto:", "data:", "#")):
            continue
        yield url


def resolve(out, url, base):
    assert url.startswith(base + "/") or url == base, f"{url} is not under {base or '/'}"
    path = url[len(base):].split("#")[0].lstrip("/")
    for candidate in (path, f"{path}/index.html".lstrip("/")):
        if (out / candidate).is_file():
            return out / candidate
    return None


def test_writes_every_page_as_a_directory_index(app, tmp_path):
    files = run(app, tmp_path / "site")
    for page in ["index.html", "cv/index.html", "blog/index.html", "blog/hello-post/index.html", "404.html",
                 "static/css/site.css", "static/js/site.js", ".nojekyll"]:
        assert (tmp_path / "site" / page).is_file(), page
    assert "index.html" in files


def test_exported_home_page_equals_what_the_app_serves(app, tmp_path):
    run(app, tmp_path / "site")
    assert (tmp_path / "site/index.html").read_bytes() == app.test_client().get("/").get_data()


@pytest.mark.parametrize("base", ["", "/portfolio", "/team/site"])
def test_every_internal_link_resolves_to_an_exported_file(app, tmp_path, base):
    out = tmp_path / "site"
    run(app, out, base)
    pages = [p for p in out.rglob("*.html")]
    assert len(pages) == 5
    for page in pages:
        for url in internal_links(page.read_text(encoding="utf-8")):
            assert resolve(out, url, base) is not None, f"{page.name}: {url} does not exist in the export"


def test_base_path_prefixes_links_and_assets(app, tmp_path):
    run(app, tmp_path / "site", "/portfolio/")
    html = (tmp_path / "site/index.html").read_text()
    assert 'href="/portfolio/cv"' in html and 'src="/portfolio/static/js/site.js"' in html
    assert 'href="/cv"' not in html and 'href="/static' not in html


def test_404_page_is_exported_with_a_working_way_home(app, tmp_path):
    run(app, tmp_path / "site", "/portfolio")
    html = (tmp_path / "site/404.html").read_text()
    assert "Nothing here." in html and 'href="/portfolio/"' in html


def test_linked_external_posts_survive_the_export(app, tmp_path):
    run(app, tmp_path / "site")
    html = (tmp_path / "site/blog/index.html").read_text()
    assert 'href="https://dev.to/me/p"' in html and 'rel="noopener noreferrer"' in html


def test_output_is_replaced_not_merged(app, tmp_path):
    out = tmp_path / "site"
    run(app, out)
    (out / "stale.html").write_text("old")
    run(app, out)
    assert not (out / "stale.html").exists()


def test_junk_files_are_not_copied(app, tmp_path):
    run(app, tmp_path / "site")
    names = {p.name for p in (tmp_path / "site").rglob("*")}
    assert ".DS_Store" not in names and "__pycache__" not in names


@pytest.mark.parametrize("value,expected", [("", ""), ("/", ""), ("/portfolio/", "/portfolio"), ("/a/b", "/a/b")])
def test_normalise_base_path(value, expected):
    assert normalise_base_path(value) == expected


@pytest.mark.parametrize("value", ["portfolio", "/a b", "/a?x=1", "//evil", "/../x"][:3])
def test_bad_base_paths_are_rejected(value):
    with pytest.raises(ValueError):
        normalise_base_path(value)


def test_refuses_to_delete_an_unrelated_non_empty_folder(app, tmp_path):
    precious = tmp_path / "documents"
    precious.mkdir()
    (precious / "thesis.txt").write_text("keep me")
    with pytest.raises(ValueError, match="does not look like a previous build"):
        run(app, precious)
    assert (precious / "thesis.txt").read_text() == "keep me"


def test_builds_into_an_existing_empty_folder(app, tmp_path):
    (tmp_path / "empty").mkdir()
    run(app, tmp_path / "empty")
    assert (tmp_path / "empty/index.html").is_file()


@pytest.mark.parametrize("target", [".", "..", "static", "static/css"])
def test_refuses_the_project_its_parents_and_static(app, monkeypatch, target):
    import build as module
    monkeypatch.chdir(module.BASE_DIR)
    with pytest.raises(ValueError, match="refusing"):
        run(app, target)


def test_refuses_to_publish_when_a_page_fails(app, tmp_path):
    with pytest.raises(RuntimeError, match="refusing to publish"):
        build(tmp_path / "site", app=app, slugs=["no-such-post"])


def test_command_line_reports_bad_arguments_without_a_traceback(capsys):
    assert main(["--base-path", "/a b", "--out", "ignored"]) == 1
    assert "build failed" in capsys.readouterr().err


# ---- single self-contained page ---------------------------------------------

from build import build_single  # noqa: E402


@pytest.fixture
def single_app(full_data):
    full_data["projects"][0]["image_url"] = "img/shot.png"
    full_data["writing"] = {"links": [{"title": "On DEV", "url": "https://dev.to/me/p", "date": "2026-02-01"}]}
    return create_app(full_data, posts=[POST], check_images=True, single_page=True)


def make_single(single_app, tmp_path):
    static = tmp_path / "static"
    (static / "css").mkdir(parents=True)
    (static / "js").mkdir()
    (static / "img").mkdir()
    (static / "css/site.css").write_text("body{background:#fff}")
    (static / "js/site.js").write_text("window.__loaded = true;")
    (static / "img/shot.png").write_bytes(b"png")
    (static / "img/.gitkeep").write_bytes(b"")
    single_app.static_folder = str(static)
    out = tmp_path / "site"
    return out, build_single(out, single_app)


def test_single_page_is_one_html_file_plus_images(single_app, tmp_path):
    out, files = make_single(single_app, tmp_path)
    assert sorted(files) == ["index.html", "static/img/shot.png"]
    assert sorted(p.name for p in out.rglob("*") if p.is_file()) == [".nojekyll", "index.html", "shot.png"]


def test_css_and_js_are_inlined_and_the_script_runs_last(single_app, tmp_path):
    out, _ = make_single(single_app, tmp_path)
    html = (out / "index.html").read_text()
    assert "<style>\nbody{background:#fff}</style>" in html
    assert 'rel="stylesheet"' not in html and "<script defer" not in html
    assert html.index("window.__loaded = true;") > html.index("</main>")
    assert html.rstrip().endswith("</script>\n</body>\n</html>") or html.rstrip().endswith("</body>\n</html>")


def test_no_link_or_asset_depends_on_a_server_path(single_app, tmp_path):
    out, _ = make_single(single_app, tmp_path)
    html = (out / "index.html").read_text()
    assert not re.findall(r'(?:href|src)="/', html)
    assert 'src="static/img/shot.png"' in html
    for url in internal_links(html):
        assert (out / url).is_file(), url


def test_pages_that_are_not_in_the_single_page_are_not_linked(single_app, tmp_path):
    out, _ = make_single(single_app, tmp_path)
    html = (out / "index.html").read_text()
    for gone in ["/cv", "/blog", "View CV", "View full CV", "CV (print view)", "All posts", "Local post"]:
        assert gone not in html, gone


def test_linked_posts_are_kept_in_the_single_page(single_app, tmp_path):
    out, _ = make_single(single_app, tmp_path)
    html = (out / "index.html").read_text()
    assert 'href="https://dev.to/me/p"' in html and 'rel="noopener noreferrer"' in html


def test_the_flask_version_still_links_everything(app):
    html = app.test_client().get("/").get_data(as_text=True)
    assert 'href="/cv"' in html and 'href="/blog"' in html and "<script defer" in html


def test_single_page_without_images_writes_only_the_page(full_data, tmp_path):
    app = create_app(full_data, posts=[], single_page=True)
    out = tmp_path / "site"
    assert build_single(out, app) == ["index.html"]


def test_single_page_refuses_unsafe_or_foreign_folders(single_app, tmp_path):
    foreign = tmp_path / "docs"
    foreign.mkdir()
    (foreign / "notes.txt").write_text("keep")
    with pytest.raises(ValueError, match="does not look like a previous build"):
        build_single(foreign, single_app)
    assert (foreign / "notes.txt").exists()


def test_single_page_fails_loudly_when_the_tags_to_inline_are_missing(single_app, tmp_path, monkeypatch):
    import build as module
    monkeypatch.setattr(module, "STYLE_TAG", re.compile(r"NOPE"))
    with pytest.raises(RuntimeError, match="could not find"):
        make_single(single_app, tmp_path)


def test_cli_builds_the_single_page_by_default(tmp_path, capsys):
    assert main(["--out", str(tmp_path / "site")]) == 0
    assert (tmp_path / "site/index.html").is_file() and not (tmp_path / "site/cv").exists()
    assert "wrote" in capsys.readouterr().out


def test_cli_full_builds_the_multi_page_site(tmp_path):
    assert main(["--full", "--out", str(tmp_path / "site")]) == 0
    assert (tmp_path / "site/cv/index.html").is_file() and (tmp_path / "site/blog/index.html").is_file()


def test_cli_rejects_base_path_without_full(tmp_path, capsys):
    assert main(["--base-path", "/x", "--out", str(tmp_path / "site")]) == 1
    assert "--full" in capsys.readouterr().err
