"""Markdown blog: posts are files in posts/, loaded once at startup.

A post is posts/<slug>.md with a front matter block:

    ---
    title: My post
    date: 2026-01-31
    summary: One line for the list page (optional)
    draft: true   (optional; drafts are never served)
    ---
    Markdown body...

Raw HTML in a post is never passed through: it is shown as text. Link and image
addresses may only be http, https, mailto or relative.
"""
import re
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml
from flask import Blueprint, abort, render_template
from markdown.treeprocessors import Treeprocessor
from markupsafe import Markup

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", re.DOTALL)
SAFE_SCHEMES = {"http", "https", "mailto"}


class _SafeUrls(Treeprocessor):
    """Drop href/src values that use any scheme other than the safe ones."""

    def run(self, root):
        for el in root.iter():
            for attr in ("href", "src"):
                value = el.get(attr)
                if value is None:
                    continue
                cleaned = re.sub(r"[\x00-\x20]", "", value).lower()
                m = re.match(r"^([a-z][a-z0-9+.\-]*):", cleaned)
                if m and m.group(1) not in SAFE_SCHEMES:
                    del el.attrib[attr]


def _renderer():
    md = markdown.Markdown(
        extensions=["fenced_code", "codehilite", "tables"],
        extension_configs={"codehilite": {"css_class": "codehilite", "guess_lang": False}},
    )
    md.preprocessors.deregister("html_block")  # raw HTML blocks become plain text
    md.inlinePatterns.deregister("html")       # so do inline tags
    md.treeprocessors.register(_SafeUrls(md), "safe_urls", 5)
    return md


def parse_post(text, filename):
    """Turn one file's text into a post dict, or raise ValueError naming the file."""
    if not filename.endswith(".md"):
        raise ValueError(f"{filename}: file name must end in .md")
    slug = filename[: -len(".md")]
    if not SLUG_RE.match(slug):
        raise ValueError(f"{filename}: slug must be lowercase letters, digits and dashes (taken from the file name)")

    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError(f"{filename}: missing front matter block (--- title/date ---) at the top")
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except (yaml.YAMLError, ValueError) as exc:
        raise ValueError(f"{filename}: front matter has a bad value (check the date is YYYY-MM-DD): {exc}") from None
    if not isinstance(meta, dict):
        raise ValueError(f"{filename}: front matter must be key: value lines")

    title = meta.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"{filename}: front matter needs a non-empty title")
    when = meta.get("date")
    if isinstance(when, datetime) or not isinstance(when, date):
        raise ValueError(f"{filename}: front matter date must be written YYYY-MM-DD")
    summary = meta.get("summary") or ""
    if not isinstance(summary, str):
        raise ValueError(f"{filename}: summary must be text")

    return {
        "slug": slug,
        "title": title.strip(),
        "date": when,
        "summary": summary.strip(),
        "draft": meta.get("draft") is True,
        "html": Markup(_renderer().convert(m.group(2))),  # raw HTML was already neutralised
    }


def load_posts(directory):
    """Return published posts, newest first. A missing folder means no posts."""
    directory = Path(directory)
    if not directory.is_dir():
        return []
    posts = []
    for path in sorted(directory.glob("*.md")):
        post = parse_post(path.read_text(encoding="utf-8"), path.name)
        if not post["draft"]:
            posts.append(post)
    return sorted(posts, key=lambda p: p["date"], reverse=True)


def create_blueprint(posts, data, year, writing=None):
    if writing is None:
        from external import local_entries
        writing = local_entries(posts)
    by_slug = {p["slug"]: p for p in posts}
    bp = Blueprint("blog", __name__)

    @bp.route("/blog")
    def blog_list():
        return render_template("blog_list.html", data=data, posts=posts, writing=writing, year=year)

    @bp.route("/blog/<slug>")
    def blog_post(slug):
        post = by_slug.get(slug)
        if post is None:
            abort(404)
        return render_template("blog_post.html", data=data, post=post, posts=posts, year=year)

    return bp
