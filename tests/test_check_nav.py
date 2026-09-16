"""Navigation integrity.

Two failure modes, and the tests keep them apart: a curated page that exists but cannot be
reached from the navigation, and a navigation entry that names a page which is not there.
The second check has a deliberate hole — most of this site is assembled from pinned
revisions, so those targets are not on disk — and the hole is tested too, because a check
whose exclusion is untested is a check that will quietly exclude more than it says.
"""

from __future__ import annotations

import textwrap

MINIMAL_MKDOCS = """\
site_name: Estamora
nav:
  - Home: index.md
  - Guide: guide.md
"""


def nav_repo(make_tree, mkdocs: str, documents: dict[str, str]):
    return make_tree({"mkdocs.yml": mkdocs, **{f"docs/{name}": text for name, text in documents.items()}})


def point_at(check, monkeypatch, root):
    monkeypatch.setattr(check, "MKDOCS", root / "mkdocs.yml")
    monkeypatch.setattr(check, "DOCS_DIR", root / "docs")


def test_this_repository_passes(load_check):
    assert load_check("check-nav").main() == 0


def test_the_baseline_fixture_passes(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-nav")
    root = nav_repo(make_tree, MINIMAL_MKDOCS, {"index.md": "x", "guide.md": "y"})
    point_at(check, monkeypatch, root)

    assert check.main() == 0
    assert "2 curated document(s) reachable" in capsys.readouterr().out


def test_a_curated_page_reachable_from_nowhere_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-nav")
    root = nav_repo(make_tree, MINIMAL_MKDOCS, {"index.md": "x", "guide.md": "y", "orphan.md": "z"})
    point_at(check, monkeypatch, root)

    assert check.main() == 1
    assert "docs/orphan.md is curated but appears in no navigation entry" in capsys.readouterr().out


def test_a_navigation_entry_naming_a_missing_file_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-nav")
    mkdocs = MINIMAL_MKDOCS.replace("  - Guide: guide.md", "  - Guide: missing.md")
    root = nav_repo(make_tree, mkdocs, {"index.md": "x"})
    point_at(check, monkeypatch, root)

    assert check.main() == 1
    assert "the navigation names missing.md, which does not exist" in capsys.readouterr().out


def test_assembled_targets_are_not_required_on_disk(load_check, make_tree, monkeypatch):
    check = load_check("check-nav")
    mkdocs = """\
site_name: Estamora
nav:
  - Home: index.md
  - Command line: runner/cli.md
"""
    root = nav_repo(make_tree, mkdocs, {"index.md": "x"})
    point_at(check, monkeypatch, root)

    assert check.main() == 0


def test_a_document_under_an_assembled_prefix_is_not_curated(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-nav")
    root = nav_repo(make_tree, MINIMAL_MKDOCS, {"index.md": "x", "guide.md": "y", "spec/intro.md": "z"})
    point_at(check, monkeypatch, root)

    assert check.main() == 0
    assert "2 curated document(s) reachable" in capsys.readouterr().out


def test_an_empty_navigation_fails_rather_than_passing_vacuously(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-nav")
    root = nav_repo(make_tree, "site_name: Estamora\nnav: []\n", {"index.md": "x"})
    point_at(check, monkeypatch, root)

    assert check.main() == 1
    assert "asserts nothing" in capsys.readouterr().out


def test_the_loader_tolerates_a_tag_pyyaml_does_not_know(load_check):
    """`mkdocs.yml` uses `!ENV` for values set at build time. A check that raised on it would
    break every time a new tag was introduced for an unrelated reason."""
    check = load_check("check-nav")
    import yaml

    loaded = yaml.load("site_url: !ENV [SITE_URL, 'https://example.test']", Loader=check.TolerantLoader)

    assert loaded == {"site_url": ["SITE_URL", "https://example.test"]}


def test_the_loader_handles_an_unknown_tag_on_a_mapping(load_check):
    check = load_check("check-nav")
    import yaml

    loaded = yaml.load("theme:\n  features: !ENV\n    navigation: 1\n", Loader=check.TolerantLoader)

    assert loaded == {"theme": {"features": {"navigation": 1}}}


def test_nav_targets_flattens_nested_entries(load_check):
    check = load_check("check-nav")

    assert check.nav_targets([{"A": "a.md"}, {"B": [{"C": "c.md"}, "d.md"]}, "e.md"]) == [
        "a.md",
        "c.md",
        "d.md",
        "e.md",
    ]


def test_nav_targets_ignores_non_string_entries(load_check):
    check = load_check("check-nav")

    assert check.nav_targets([{"A": None}, {"B": 3}, {"C": {"D": ["e.md"]}}]) == ["e.md"]


def test_nav_targets_of_a_missing_navigation_is_empty(load_check):
    check = load_check("check-nav")

    assert check.nav_targets({}) == []


def test_the_summary_counts_entries_and_documents_separately(load_check, make_tree, monkeypatch, capsys):
    """An entry count and a document count that are conflated is how a check reports success
    over an empty navigation; the message keeps them apart."""
    check = load_check("check-nav")
    mkdocs = textwrap.dedent(
        """\
        site_name: Estamora
        nav:
          - Home: index.md
          - Guide:
              - One: guide.md
        """
    )
    root = nav_repo(make_tree, mkdocs, {"index.md": "x", "guide.md": "y"})
    point_at(check, monkeypatch, root)

    assert check.main() == 0
    assert "navigation: 2 entries, 2 curated document(s) reachable" in capsys.readouterr().out
