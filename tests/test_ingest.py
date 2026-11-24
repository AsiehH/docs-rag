import json

import pytest

from app import ingest
from app.ingest import extract_text, html_to_text, load_guide, load_guide_paths


def test_load_guide_paths_skips_comments_and_blank_lines(tmp_path):
    guides_file = tmp_path / "guides.txt"
    guides_file.write_text("# a comment\nvat-rates\n\n  guidance/foo  \n")
    assert load_guide_paths(guides_file) == ["vat-rates", "guidance/foo"]


def test_extract_text_from_body():
    content = {"details": {"body": "<p>Standard rate is 20%</p>"}}
    assert "Standard rate is 20%" in extract_text(content)


def test_extract_text_from_parts_keeps_titles_and_order():
    content = {
        "details": {
            "parts": [
                {"title": "Overview", "body": "<p>First part</p>"},
                {"title": "Rates", "body": "<p>Second part</p>"},
            ]
        }
    }
    text = extract_text(content)
    assert "Overview" in text and "Rates" in text
    assert text.index("First part") < text.index("Second part")


def test_extract_text_raises_when_no_text():
    with pytest.raises(ValueError):
        extract_text({"details": {}})


def test_load_guide_reads_cache_without_fetching(tmp_path, monkeypatch):
    cached_content = {"details": {"body": "cached"}}
    (tmp_path / "guidance__foo.json").write_text(json.dumps(cached_content))

    def fail_if_called(path):
        raise AssertionError("fetch_guide should not be called on a cache hit")

    monkeypatch.setattr(ingest, "fetch_guide", fail_if_called)
    assert load_guide("guidance/foo", raw_dir=tmp_path) == cached_content


def test_load_guide_fetches_and_writes_cache_on_miss(tmp_path, monkeypatch):
    fetched_content = {"details": {"body": "fresh"}}
    monkeypatch.setattr(ingest, "fetch_guide", lambda path: fetched_content)

    assert load_guide("guidance/foo", raw_dir=tmp_path) == fetched_content
    cache_file = tmp_path / "guidance__foo.json"
    assert json.loads(cache_file.read_text()) == fetched_content


def test_html_to_text_strips_tags_and_decodes_entities():
    assert html_to_text("<p>VAT is <em>20%</em> &amp; more</p>") == "VAT is 20% & more"


def test_html_to_text_separates_paragraphs():
    text = html_to_text("<p>First</p><p>Second</p>")
    assert "First" in text and "Second" in text
    assert "FirstSecond" not in text


def test_html_to_text_marks_headings():
    assert "## Overview" in html_to_text("<h2>Overview</h2><p>Body</p>")


def test_html_to_text_has_no_long_blank_runs():
    assert "\n\n\n" not in html_to_text("<p>A</p>\n\n\n\n<p>B</p>")


def test_html_to_text_keeps_spaces_around_inline_tags_in_headings():
    html = "<h2>Your responsibilities as a <abbr>VAT</abbr>-registered business</h2>"
    assert "## Your responsibilities as a VAT-registered business" in html_to_text(html)
