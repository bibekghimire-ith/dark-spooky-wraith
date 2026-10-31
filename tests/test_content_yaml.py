"""R2-1: content lives in content.yaml; same rules as the dict."""
import textwrap
from pathlib import Path

import pytest
import yaml

from app import PORTFOLIO_DATA, load_content, validate

ROOT = Path(__file__).resolve().parent.parent


def write(tmp_path, text):
    p = tmp_path / "content.yaml"
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_dict_and_yaml_give_identical_validate_results(full_data, tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(full_data, sort_keys=False), encoding="utf-8")
    assert load_content(p) == full_data
    assert validate(load_content(p)) == validate(full_data) == []


def test_same_errors_for_bad_data_in_both_forms(full_data, tmp_path):
    full_data["owner"]["email"] = ""
    full_data["projects"][1]["tech_stack"] = "Rust"
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(full_data), encoding="utf-8")
    assert validate(load_content(p)) == validate(full_data)
    assert len(validate(full_data)) == 2


def test_bad_yaml_raises_an_error_naming_the_file_and_line(tmp_path):
    p = write(tmp_path, """\
        owner:
          name: ok
          title: [unclosed
        """)
    with pytest.raises(ValueError) as exc:
        load_content(p)
    msg = str(exc.value)
    assert "c" in msg and "content.yaml" in msg
    assert "line" in msg


def test_missing_file_gives_a_clear_error(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        load_content(tmp_path / "nope.yaml")


def test_non_mapping_root_is_rejected(tmp_path):
    p = write(tmp_path, "- just\n- a list\n")
    with pytest.raises(ValueError, match="mapping"):
        load_content(p)


def test_shipped_content_yaml_exists_and_is_the_source_of_portfolio_data():
    assert (ROOT / "content.yaml").exists()
    assert PORTFOLIO_DATA == load_content(ROOT / "content.yaml")
    assert validate(PORTFOLIO_DATA) == []


def test_unquoted_yaml_values_that_become_numbers_are_caught(tmp_path):
    p = write(tmp_path, """\
        owner:
          name: X
          title: Y
          bio: Z
          email: 12345
        """)
    assert any("owner.email" in e for e in validate(load_content(p)))
