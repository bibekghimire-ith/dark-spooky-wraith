"""Static version of the site: no Flask and no server at run time, so any static host works
(GitHub Pages, GitLab Pages, Netlify, Cloudflare Pages, an S3 bucket, a USB stick).

    python build.py                  # one self-contained build/index.html (CSS and JS inlined)
    python build.py --out public     # choose the folder; it is replaced on every run
    python build.py --full           # also export /cv and the blog as separate pages
    python build.py --full --base-path /portfolio    # full site served under /portfolio/

Every page is rendered by the real app, so the output matches `python app.py`. The single-page
version leaves out the links to /cv and the local blog, which are not part of it; posts you link
or import from dev.to are kept. Imported posts are fetched while building, so rebuild to refresh.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BASE_PATH_RE = re.compile(r"^/[A-Za-z0-9._~/-]*$")
IGNORED = shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc")


def normalise_base_path(value):
    """'' for the domain root, otherwise '/name' with no trailing slash."""
    value = (value or "").strip().rstrip("/")
    if value and not BASE_PATH_RE.match(value):
        raise ValueError(f"--base-path must look like /portfolio (letters, digits, . _ ~ - /), got {value!r}")
    return value


def prepare_output(out_dir):
    """Return a fresh, empty output folder. Refuses places that must never be deleted."""
    out = Path(out_dir).resolve()
    if out == BASE_DIR or out in BASE_DIR.parents or out == Path.home() or BASE_DIR / "static" in (out, *out.parents):
        raise ValueError(f"refusing to write the site into {out}")
    if out.exists():
        # The folder is deleted and recreated, so only touch one that is empty or is a previous build.
        if any(out.iterdir()) and not (out / "index.html").is_file():
            raise ValueError(f"{out} is not empty and does not look like a previous build; choose another --out")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    return out


def build(out_dir, base_path="", app=None, slugs=None):
    """Render the site into out_dir (replaced if it exists). Returns the list of files written."""
    if app is None:
        from app import app as default_app
        app = default_app
    base_path = normalise_base_path(base_path)
    out = prepare_output(out_dir)

    client = app.test_client()
    written = []

    def fetch(url):
        response = client.get(url, environ_overrides={"SCRIPT_NAME": base_path})
        return response.status_code, response.get_data()

    def write(rel, data):
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        written.append(rel)

    urls = ["/", "/cv", "/blog"] + [f"/blog/{slug}" for slug in (slugs or [])]
    for url in urls:
        status, body = fetch(url)
        if status != 200:
            raise RuntimeError(f"{url} returned {status}; refusing to publish a broken site")
        write("index.html" if url == "/" else f"{url.strip('/')}/index.html", body)

    status, body = fetch("/this-page-does-not-exist")
    if status != 404:
        raise RuntimeError("expected the 404 page to return 404")
    write("404.html", body)  # GitHub Pages, GitLab Pages and Netlify serve this for unknown paths

    shutil.copytree(app.static_folder, out / "static", ignore=IGNORED)
    written += [str(p.relative_to(out)) for p in (out / "static").rglob("*") if p.is_file()]
    (out / ".nojekyll").write_bytes(b"")  # GitHub Pages: serve files as they are
    return written


STYLE_TAG = re.compile(r'<link rel="stylesheet" href="/static/css/site\.css"\s*/?>')
SCRIPT_TAG = re.compile(r'\s*<script defer src="/static/js/site\.js"></script>')


def build_single(out_dir, app):
    """One self-contained index.html: CSS and JS inlined, project images copied beside it as static/img."""
    out = prepare_output(out_dir)
    response = app.test_client().get("/")
    if response.status_code != 200:
        raise RuntimeError(f"/ returned {response.status_code}; refusing to publish a broken page")
    html = response.get_data(as_text=True)

    css = (Path(app.static_folder) / "css" / "site.css").read_text(encoding="utf-8")
    js = (Path(app.static_folder) / "js" / "site.js").read_text(encoding="utf-8")
    if "</style" in css.lower() or "</script" in js.lower():
        raise RuntimeError("an asset contains a closing tag and cannot be inlined")
    if not STYLE_TAG.search(html) or not SCRIPT_TAG.search(html):
        raise RuntimeError("could not find the stylesheet and script tags to inline; update build.py")
    html = STYLE_TAG.sub(lambda _m: f"<style>\n{css}</style>", html, count=1)
    html = SCRIPT_TAG.sub("", html, count=1)
    # The script needs the page to exist, so it runs at the end of the body.
    html = html.replace("</body>", f"<script>\n{js}</script>\n</body>", 1)
    html = html.replace('"/static/', '"static/')  # project images: relative, so it works anywhere

    (out / "index.html").write_text(html, encoding="utf-8")
    written = ["index.html"]
    images = Path(app.static_folder) / "img"
    if images.is_dir():
        for source in sorted(images.rglob("*")):
            if source.is_file() and source.name not in {".gitkeep", ".DS_Store"}:
                target = out / "static" / "img" / source.relative_to(images)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                written.append(str(target.relative_to(out)))
    (out / ".nojekyll").write_bytes(b"")
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default="build", help="output folder, replaced on every run (default: build)")
    parser.add_argument("--full", action="store_true", help="export /cv and the blog as separate pages too")
    parser.add_argument("--base-path", default="", help="with --full: path the site is served under, e.g. /portfolio")
    args = parser.parse_args(argv)
    if args.base_path and not args.full:
        print("build failed: --base-path only applies with --full (the single page uses relative links)", file=sys.stderr)
        return 1

    from app import BASE_DIR as app_base, PORTFOLIO_DATA, app, create_app
    from blog import load_posts

    try:
        if args.full:
            slugs = [p["slug"] for p in load_posts(app_base / "posts")]
            files = build(args.out, args.base_path, app=app, slugs=slugs)
        else:
            single = create_app(PORTFOLIO_DATA, posts=[], check_images=True, single_page=True)
            files = build_single(args.out, single)
    except (ValueError, RuntimeError) as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {len(files)} files to {Path(args.out).resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
