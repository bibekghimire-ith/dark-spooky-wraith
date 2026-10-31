"""Writing that lives elsewhere (for example dev.to), shown beside the local blog posts.

content.yaml:

    writing:
      devto_username: your-username     # optional: import your dev.to posts at startup
      links:                            # optional: link any post by hand
      - title: My post
        url: https://dev.to/you/my-post
        date: 2026-01-31                # optional
        summary: One line (optional)
        source: dev.to                  # optional label; defaults to the site's host

An import that fails (offline, timeout, dev.to down) is logged and skipped; the site still starts.
"""
import json
import logging
import re
import ssl
import urllib.request
from datetime import date, datetime
from urllib.parse import urlparse

log = logging.getLogger(__name__)

try:  # python.org builds on macOS ship without root certificates; certifi supplies them
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CONTEXT = None  # fall back to the system store; certificates are always verified

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{1,40}$")
DEVTO_API = "https://dev.to/api/articles?username={username}&per_page=10"


def to_date(value):
    """A date, a datetime or a YYYY-MM-DD / ISO string becomes a date; anything else is None."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.strip().replace("Z", "+00:00")).date()
        except ValueError:
            return None
    return None


def _source(url, label=None):
    return (label or "").strip() or (urlparse(url).hostname or "").removeprefix("www.")


def fetch_devto(username, timeout=5):
    """Return the user's published dev.to articles as entries. Raises on network or format errors."""
    if not USERNAME_RE.match(username or ""):
        raise ValueError("devto_username may only use letters, digits and underscores")
    request = urllib.request.Request(
        DEVTO_API.format(username=username), headers={"User-Agent": "portfolio-site", "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout, context=_SSL_CONTEXT) as response:  # fixed https host
        articles = json.loads(response.read().decode("utf-8"))
    entries = []
    for article in articles:
        url = article.get("url") or ""
        if not url.startswith("https://dev.to/") or not article.get("title"):
            continue
        entries.append({"title": article["title"], "summary": article.get("description") or "",
                        "date": to_date(article.get("published_at")), "href": url,
                        "external": True, "source": "dev.to"})
    return entries


def link_entries(links):
    """Hand-written links from content.yaml (already validated) as entries."""
    return [{"title": item["title"].strip(), "summary": (item.get("summary") or "").strip(),
             "date": to_date(item.get("date")), "href": item["url"], "external": True,
             "source": _source(item["url"], item.get("source"))}
            for item in links or []]


def local_entries(posts):
    return [{"title": p["title"], "summary": p["summary"], "date": p["date"],
             "slug": p["slug"], "href": f"/blog/{p['slug']}", "external": False, "source": None} for p in posts]


def build_writing(posts, config, fetch=fetch_devto):
    """Local posts plus linked and imported ones, newest first (undated entries last).

    A hand-written link wins over an imported post with the same address.
    """
    config = config if isinstance(config, dict) else {}
    external = link_entries(config.get("links"))
    username = config.get("devto_username")
    if username:
        try:
            external += [e for e in fetch(username) if e["href"] not in {x["href"] for x in external}]
        except Exception as exc:  # offline or API change must never stop the site
            log.warning("dev.to import skipped: %s", exc)
    entries = local_entries(posts) + external
    return sorted(entries, key=lambda e: (e["date"] is not None, e["date"] or date.min), reverse=True)
