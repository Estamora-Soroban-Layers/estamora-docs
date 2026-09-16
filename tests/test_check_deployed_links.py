"""The post-deployment check.

This one exists because a check in CI cannot see the deployment: it once reported a 404 for
a pitch file that was published correctly seconds later, because the page naming it had gone
live before the file had. So the tests are about two things — that the URL list is derived
from the built pages rather than typed, and that a derivation which produces almost nothing
fails instead of passing vacuously.
"""

from __future__ import annotations

import urllib.error
from email.message import Message

BASE = "https://estamora-docs.vercel.app"

PAGE = """\
<!doctype html>
<html>
  <body>
    <a href="/guide/">Guide</a>
    <a href="#top">Top</a>
    <a href="page.html#section">A page</a>
    <a href="https://other.example/elsewhere">Elsewhere</a>
    <a href="mailto:someone@example.test">Mail</a>
    <img src="a&amp;b.png">
    <video poster="assets/pitch-thumbnail.png">
      <source src="assets/estamora-pitch.mp4" type="video/mp4">
    </video>
  </body>
</html>
"""


class FakeResponse:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def urlopen_playing(*outcomes):
    def fake(request, timeout=None):  # noqa: ANN001, ANN202
        outcome = outcomes[0] if len(outcomes) == 1 else outcomes.pop(0)
        kind, value = outcome
        if kind == "ok":
            return FakeResponse(value)
        if kind == "http":
            raise urllib.error.HTTPError(request.full_url, value, "synthetic", Message(), None)
        raise value

    return fake


def built_site(make_tree, page: str = PAGE, markdown: str = ""):
    root = make_tree({"site/index.html": page, "README.md": markdown})
    return root


def test_references_resolves_relative_references_the_way_a_browser_does(load_check, make_tree):
    check = load_check("check-deployed-links")
    root = built_site(make_tree)

    found = check.references(root / "site", BASE)

    assert found[f"{BASE}/assets/estamora-pitch.mp4"] == "index.html"
    assert found[f"{BASE}/assets/pitch-thumbnail.png"] == "index.html"
    assert found[f"{BASE}/guide/"] == "index.html"


def test_references_drops_a_fragment(load_check, make_tree):
    """`page.html#section` is a request for `page.html`; the fragment never leaves the browser."""
    check = load_check("check-deployed-links")
    root = built_site(make_tree)

    assert f"{BASE}/page.html" in check.references(root / "site", BASE)


def test_references_ignores_other_hosts_and_non_requests(load_check, make_tree):
    check = load_check("check-deployed-links")
    root = built_site(make_tree)

    found = check.references(root / "site", BASE)

    assert not any("other.example" in url for url in found)
    assert not any(url.startswith("mailto:") for url in found)
    assert not any(url.endswith("#top") for url in found)


def test_references_unescapes_html_entities(load_check, make_tree):
    """`&amp;` in a page is an ampersand in a URL. Comparing the escaped form would request a
    path with the entity still in it, and 404 on a file that is served."""
    check = load_check("check-deployed-links")
    root = built_site(make_tree)

    assert f"{BASE}/a&b.png" in check.references(root / "site", BASE)


def test_references_follows_a_poster_because_it_names_a_published_image(load_check, make_tree):
    """The player's poster is a relative reference to an image this repository publishes, and it
    was the one attribute the check did not read: a poster that resolves to nothing renders as an
    empty box, which reads as a styling problem rather than a missing file."""
    check = load_check("check-deployed-links")
    root = built_site(make_tree)

    assert f"{BASE}/assets/pitch-thumbnail.png" in check.references(root / "site", BASE)


def test_references_ignores_a_lazy_loading_attribute(load_check, make_tree):
    """`data-src` is not a request. The guard has to be a lookbehind rather than a `\b` — a hyphen
    is a word boundary, so `\bsrc` still matches inside `data-src`. Asserting a lazy attribute as
    though the page requested it directly is a failure invented by the check, not found by it."""
    check = load_check("check-deployed-links")
    root = built_site(make_tree, page='<img data-src="lazy.png" srcset="a.png 1x">')

    found = check.references(root / "site", BASE)

    assert found == {}


def test_references_records_the_page_a_url_came_from(load_check, make_tree):
    check = load_check("check-deployed-links")
    root = built_site(make_tree)

    assert check.references(root / "site", BASE)[f"{BASE}/page.html"] == "index.html"


def test_references_finds_absolute_self_references_in_the_repositorys_own_markdown(load_check, make_tree):
    """The README is not published, but a URL in it that points at this host is still a URL a
    reader can click, so it is asserted after the deployment alongside the pages."""
    check = load_check("check-deployed-links")
    root = built_site(make_tree, markdown=f"[shot]({BASE}/assets/shot.png)\n[other](https://example.test/x)\n")

    found = check.references(root / "site", BASE)

    assert found[f"{BASE}/assets/shot.png"] == "README.md"
    assert not any("example.test" in url for url in found)


def test_references_keeps_the_first_reference_for_a_url(load_check, make_tree):
    check = load_check("check-deployed-links")
    page = '<img src="same.png"><img src="same.png">'
    root = built_site(make_tree, page=page)

    assert check.references(root / "site", BASE)[f"{BASE}/same.png"] == "index.html"


def test_served_reports_a_200_as_served(load_check, monkeypatch):
    check = load_check("check-deployed-links")
    monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("ok", 200)))

    assert check.served(f"{BASE}/") == (True, "200")


def test_served_reports_an_http_error_as_not_served(load_check, monkeypatch):
    check = load_check("check-deployed-links")
    monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("http", 404)))

    assert check.served(f"{BASE}/gone") == (False, "404")


def test_served_reports_a_transport_failure_as_not_served(load_check, monkeypatch):
    """Unlike the outward link check, a transport failure here *is* a failure: this check runs
    against the deployment, and not being able to reach it is not a passing grade."""
    check = load_check("check-deployed-links")
    monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("raise", RuntimeError("reset"))))

    assert check.served(f"{BASE}/") == (False, "RuntimeError")


def test_main_fails_when_the_site_was_not_built(load_check, monkeypatch, tmp_path, capsys):
    check = load_check("check-deployed-links")
    monkeypatch.setattr(check.sys, "argv", ["check-deployed-links.py", "--site", str(tmp_path / "absent")])

    assert check.main() == 1
    assert "run this after building the site" in capsys.readouterr().out


def test_main_fails_when_the_derivation_produces_almost_nothing(load_check, monkeypatch, capsys):
    """A derived list can be derived wrongly, and an empty one means the check is broken rather
    than the site being perfect."""
    check = load_check("check-deployed-links")
    monkeypatch.setattr(check, "references", lambda site, base: {f"{BASE}/only": "index.html"})
    monkeypatch.setattr(check.sys, "argv", ["check-deployed-links.py", "--site", "."])

    assert check.main() == 1
    assert "the derivation is broken" in capsys.readouterr().out


def test_main_passes_when_everything_is_served(load_check, monkeypatch, capsys):
    check = load_check("check-deployed-links")
    targets = {f"{BASE}/p{index}.png": "index.html" for index in range(6)}
    monkeypatch.setattr(check, "references", lambda site, base: targets)
    monkeypatch.setattr(check, "served", lambda url: (True, "200"))
    monkeypatch.setattr(check.sys, "argv", ["check-deployed-links.py", "--site", "."])

    assert check.main() == 0
    assert "6 URL(s), 0 not served" in capsys.readouterr().out


def test_main_fails_and_names_the_referring_file(load_check, monkeypatch, capsys):
    check = load_check("check-deployed-links")
    targets = {f"{BASE}/p{index}.png": "index.html" for index in range(5)}
    targets[f"{BASE}/gone.png"] = "README.md"
    monkeypatch.setattr(check, "references", lambda site, base: targets)
    monkeypatch.setattr(check, "served", lambda url: (False, "404") if url.endswith("gone.png") else (True, "200"))
    monkeypatch.setattr(check.sys, "argv", ["check-deployed-links.py", "--site", "."])

    assert check.main() == 1
    assert "::error file=README.md::the deployed site returned 404" in capsys.readouterr().out
