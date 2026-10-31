"""Personal portfolio site.

Edit content.yaml (loaded into PORTFOLIO_DATA below) to change any text, link or image.
Field names are a contract with templates/index.html (see Portfolio-PRD.md).

  owner          name, title, bio, email (all required, non-empty text)
  social_links   list of {label, url}; url starts with http://, https:// or mailto:
  skills         {category: [skill, ...]}
  projects       list of {title, description, tech_stack, image_url,
                 demo_link, code_link}; image_url is a path under static/
                 (for example "img/app.png") or an http(s) URL; the links are optional
  experience     list of {role, company, dates, highlights}; newest first

  analytics      optional {script_src, domain}; both set => one analytics script tag
  posts          blog posts live in posts/*.md (see blog.py)

Unknown keys are ignored, so you can add notes or future sections freely.
"""

import os
from datetime import date
from pathlib import Path

import yaml

from flask import Flask, render_template, url_for

from blog import create_blueprint, load_posts

BASE_DIR = Path(__file__).resolve().parent
CONTENT_PATH = Path(os.environ.get("CONTENT_FILE", BASE_DIR / "content.yaml"))


def load_content(path):
    """Read a content YAML file. Errors name the file and, for bad YAML, the line."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValueError(f"Content file not found: {path}") from None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        problem = getattr(exc, "problem", None) or str(exc)
        raise ValueError(f"Invalid YAML in {path.name}{where}: {problem}") from None
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a mapping of sections at the top level")
    return data


ALLOWED_LINK_PREFIXES = ("http://", "https://", "mailto:")
REQUIRED_OWNER_FIELDS = ("name", "title", "bio", "email")


def _is_text(value):
    return isinstance(value, str) and value.strip() != ""


def _is_text_list(value):
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _check_link(value, path, errors):
    """A link is optional; when set it must use an allowed scheme."""
    if value in (None, ""):
        return
    if not isinstance(value, str) or not value.startswith(ALLOWED_LINK_PREFIXES):
        errors.append(f"{path} must start with http://, https:// or mailto:")


def validate(data):
    """Return human-readable errors for bad data; an empty list means valid."""
    if not isinstance(data, dict):
        return ["PORTFOLIO_DATA must be a dict"]

    errors = []

    owner = data.get("owner")
    if not isinstance(owner, dict):
        errors.append("owner is required")
    else:
        for field in REQUIRED_OWNER_FIELDS:
            if not _is_text(owner.get(field)):
                errors.append(f"owner.{field} is required and must be non-empty text")

    for i, link in enumerate(data.get("social_links") or []):
        _check_link(link.get("url") if isinstance(link, dict) else None,
                    f"social_links[{i}].url", errors)

    skills = data.get("skills") or {}
    if not isinstance(skills, dict):
        errors.append("skills must be a dict of category to list of strings")
    else:
        for category, items in skills.items():
            if not _is_text_list(items):
                errors.append(f"skills.{category} must be a list of strings")

    for i, project in enumerate(data.get("projects") or []):
        if not isinstance(project, dict):
            errors.append(f"projects[{i}] must be a dict")
            continue
        if not _is_text(project.get("title")):
            errors.append(f"projects[{i}].title is required")
        if "tech_stack" in project and not _is_text_list(project["tech_stack"]):
            errors.append(f"projects[{i}].tech_stack must be a list of strings")
        _check_link(project.get("demo_link"), f"projects[{i}].demo_link", errors)
        _check_link(project.get("code_link"), f"projects[{i}].code_link", errors)

    analytics = data.get("analytics")
    if analytics not in (None, ""):
        if not isinstance(analytics, dict):
            errors.append("analytics must be a mapping with script_src and domain")
        else:
            src = analytics.get("script_src")
            if src not in (None, "") and not (isinstance(src, str) and src.startswith("https://")):
                errors.append("analytics.script_src must start with https://")
            domain = analytics.get("domain")
            if domain not in (None, "") and not isinstance(domain, str):
                errors.append("analytics.domain must be text")

    return errors


def image_src(value):
    """Return a safe image URL for a project, or None when there is nothing usable.

    Hosted http(s) URLs pass through. Anything else is treated as a path
    inside static/ and must not climb out of it or use another scheme.
    """
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    if value.lower().startswith(("http://", "https://")):
        return value
    if ":" in value or "\\" in value:
        return None
    parts = [p for p in value.split("/") if p]
    if not parts or ".." in parts:
        return None
    return url_for("static", filename="/".join(parts))


def create_app(data=None, posts=None):
    """Build the Flask app. Bad data stops startup with a message naming the field."""
    data = PORTFOLIO_DATA if data is None else data
    errors = validate(data)
    if errors:
        raise ValueError("Invalid PORTFOLIO_DATA:\n- " + "\n- ".join(errors))

    if posts is None:
        posts = load_posts(BASE_DIR / "posts")

    app = Flask(__name__)
    app.jinja_env.globals["image_src"] = image_src
    app.register_blueprint(create_blueprint(posts, data, date.today().year))

    @app.route("/")
    def index():
        return render_template("index.html", data=data, posts=posts, year=date.today().year)

    @app.route("/cv")
    def cv():
        return render_template("cv.html", data=data, year=date.today().year)

    @app.route("/healthz")
    def healthz():
        return "ok"

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "DENY")
        return response

    return app


PORTFOLIO_DATA = load_content(CONTENT_PATH)
app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", extra_files=[str(CONTENT_PATH)])
