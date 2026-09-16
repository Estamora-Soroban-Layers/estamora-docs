"""Every reference to the pitch must keep it playable.

The defect this guards against shipped once: every "watch the pitch" link pointed at the
GitHub release asset, which GitHub serves as `content-disposition: attachment`, so clicking
one downloaded 15 MB instead of playing anything — and every header check that existed
passed. So the tests are mostly about the *rejections*: an unlabelled release link, a
`latest` archive, a player with no declared type, a poster that is not there.
"""

from __future__ import annotations

GOOD_LANDING_PAGE = """\
# Estamora documentation

<video controls poster="assets/pitch-thumbnail.png">
  <source src="assets/estamora-pitch.mp4" type="video/mp4">
</video>
"""

ARCHIVE = "https://github.com/Estamora-Soroban-Layers/estamora-docs/releases/download/pitch-v1/estamora-pitch.mp4"


def pitch_repo(make_tree, readme: str, landing: str = GOOD_LANDING_PAGE, poster: str = "PNG"):
    root = make_tree(
        {
            "README.md": readme,
            "docs/index.md": landing,
            "docs/assets/pitch-thumbnail.png": poster,
        }
    )
    return root


def point_at(check, monkeypatch, root):
    """`main()` reads the module-level `MARKDOWN` list and `REPO_ROOT`, both derived from the
    script's own location, so a fixture has to replace both."""
    monkeypatch.setattr(check, "REPO_ROOT", root)
    monkeypatch.setattr(check, "MARKDOWN", sorted(root.rglob("*.md")))


def test_this_repository_passes(load_check):
    assert load_check("check-pitch-references").main() == 0


def test_a_labelled_archive_link_passes(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    point_at(check, monkeypatch, pitch_repo(make_tree, f"[archived copy]({ARCHIVE})\n"))

    assert check.main() == 0
    assert "pitch references" in capsys.readouterr().out


def test_an_unlabelled_release_asset_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    point_at(check, monkeypatch, pitch_repo(make_tree, f"[watch the pitch]({ARCHIVE})\n"))

    assert check.main() == 1
    assert "a reader clicking this gets a file, not a video" in capsys.readouterr().out


def test_a_latest_archive_link_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    latest = ARCHIVE.replace("/pitch-v1/", "/latest/")
    point_at(check, monkeypatch, pitch_repo(make_tree, f"[archived download]({latest})\n"))

    assert check.main() == 1
    out = capsys.readouterr().out
    assert "uses `latest`" in out
    assert "unexpected archive URL shape" not in out


def test_an_archive_url_of_the_wrong_shape_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    elsewhere = ARCHIVE.replace("Estamora-Soroban-Layers/estamora-docs", "someone-else/other-repo")
    point_at(check, monkeypatch, pitch_repo(make_tree, f"[archived copy]({elsewhere})\n"))

    assert check.main() == 1
    assert "unexpected archive URL shape" in capsys.readouterr().out


def test_a_landing_page_without_a_player_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    point_at(check, monkeypatch, pitch_repo(make_tree, "[archived copy](%s)\n" % ARCHIVE, landing="# No player\n"))

    assert check.main() == 1
    assert "not embedded as a player" in capsys.readouterr().out


def test_a_player_without_a_declared_mime_type_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    landing = GOOD_LANDING_PAGE.replace(' type="video/mp4"', "")
    point_at(check, monkeypatch, pitch_repo(make_tree, "", landing=landing))

    assert check.main() == 1
    assert "declares no MIME type" in capsys.readouterr().out


def test_a_player_without_a_poster_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    landing = GOOD_LANDING_PAGE.replace(' poster="assets/pitch-thumbnail.png"', "")
    point_at(check, monkeypatch, pitch_repo(make_tree, "", landing=landing))

    assert check.main() == 1
    assert "renders as a blank box" in capsys.readouterr().out


def test_a_missing_landing_page_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    root = make_tree({"README.md": ""})
    point_at(check, monkeypatch, root)

    assert check.main() == 1
    assert "no landing page" in capsys.readouterr().out


def test_a_missing_poster_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-pitch-references")
    root = make_tree({"README.md": "", "docs/index.md": GOOD_LANDING_PAGE})
    point_at(check, monkeypatch, root)

    assert check.main() == 1
    assert "is referenced but does not exist" in capsys.readouterr().out


def test_an_empty_poster_is_refused(load_check, make_tree, monkeypatch, capsys):
    """A zero-byte PNG is a file that exists, which is why it is checked separately: the
    player would render nothing and it would look like a styling problem."""
    check = load_check("check-pitch-references")
    point_at(check, monkeypatch, pitch_repo(make_tree, "", poster=""))

    assert check.main() == 1
    assert "is empty" in capsys.readouterr().out


def test_a_playback_link_on_this_site_is_not_a_release_asset(load_check, make_tree, monkeypatch):
    """The fix, asserted directly: the site's own URL is what a playback link must use."""
    check = load_check("check-pitch-references")
    point_at(check, monkeypatch, pitch_repo(make_tree, f"[watch]({check.PLAYABLE})\n"))

    assert check.main() == 0
    assert not check.RELEASE_MEDIA.search(f"[watch]({check.PLAYABLE})\n")
