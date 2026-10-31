"""R2-6: the Lighthouse CI gates are configured as the plan says."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_lighthouserc_gates_three_urls_at_95_on_mobile():
    cfg = json.loads((ROOT / "lighthouserc.json").read_text())["ci"]
    urls = cfg["collect"]["url"]
    for path in ("/", "/cv", "/blog"):
        assert any(u.endswith(path) for u in urls), path
    assert "startServerCommand" in cfg["collect"]
    settings = cfg["collect"].get("settings", {})
    assert settings.get("preset", "mobile") in ("mobile", "perf") or "formFactor" in settings
    assertions = cfg["assert"]["assertions"]
    for category in ("performance", "accessibility", "best-practices", "seo"):
        level, opts = assertions[f"categories:{category}"]
        assert level == "error" and opts["minScore"] >= 0.95, category


def test_gitlab_ci_runs_tests_layout_and_lighthouse():
    ci = (ROOT / ".gitlab-ci.yml").read_text()
    for needle in ("pytest", "playwright install", "lhci autorun"):
        assert needle in ci, needle
