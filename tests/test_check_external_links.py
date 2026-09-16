"""The external link check.

Two things about it are worth more than the happy path, and both are tested here. It
*retries a 404 with a GET*, because some servers refuse HEAD and serve GET normally — a
check that failed on that would fail on links that work in a browser. And it reports
403/429/999 as `unknown` rather than broken, because a host that challenges a machine is
not evidence that a link is wrong; a check that is flaky is a check people learn to ignore.
"""

from __future__ import annotations

import json
import urllib.error
from email.message import Message


class FakeResponse:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def http_error(url: str, code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(url, code, "synthetic", Message(), None)  # type: ignore[arg-type]


def urlopen_playing(*outcomes):
    """A stand-in for `urlopen` that plays a scripted sequence of outcomes."""
    calls: list[object] = []

    def fake(request, timeout=None):  # noqa: ANN001, ANN202
        calls.append(request)
        outcome = outcomes[min(len(calls) - 1, len(outcomes) - 1)]
        kind, value = outcome
        if kind == "ok":
            return FakeResponse(value)
        if kind == "http":
            raise http_error(request.full_url, value)
        raise value

    fake.calls = calls  # type: ignore[attr-defined]
    return fake


def test_reachable_reports_a_served_url(load_check, monkeypatch):
    check = load_check("check-external-links")
    monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("ok", 200)))

    assert check.reachable("https://example.test/") == ("ok", 200)


def test_reachable_confirms_with_a_get_when_head_is_refused(load_check, monkeypatch):
    check = load_check("check-external-links")
    fake = urlopen_playing(("http", 404), ("ok", 200))
    monkeypatch.setattr(check.urllib.request, "urlopen", fake)

    assert check.reachable("https://example.test/") == ("ok", 200)
    assert fake.calls[0].get_method() == "HEAD"
    assert fake.calls[1].get_method() == "GET"


def test_reachable_is_broken_when_the_retry_is_also_gone(load_check, monkeypatch):
    check = load_check("check-external-links")
    monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("http", 404), ("http", 410)))

    assert check.reachable("https://example.test/") == ("broken", 410)


def test_reachable_is_unknown_when_the_retry_fails_differently(load_check, monkeypatch):
    check = load_check("check-external-links")
    monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("http", 404), ("http", 500)))

    assert check.reachable("https://example.test/") == ("unknown", 500)


def test_reachable_is_unknown_when_the_retry_fails_in_transit(load_check, monkeypatch):
    check = load_check("check-external-links")
    monkeypatch.setattr(
        check.urllib.request, "urlopen", urlopen_playing(("http", 404), ("raise", RuntimeError("reset")))
    )

    assert check.reachable("https://example.test/") == ("unknown", "transport")


def test_reachable_is_unknown_when_the_head_itself_fails_in_transit(load_check, monkeypatch):
    check = load_check("check-external-links")
    monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("raise", RuntimeError("reset"))))

    assert check.reachable("https://example.test/") == ("unknown", "RuntimeError")


def test_reachable_treats_a_server_error_on_the_head_as_unknown(load_check, monkeypatch):
    """A 5xx is the server's problem and says nothing about whether the link is right."""
    check = load_check("check-external-links")
    monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("http", 500)))

    assert check.reachable("https://example.test/") == ("unknown", 500)


def test_reachable_reports_a_dns_failure_as_unknown(load_check, monkeypatch):
    """A DNS failure is not evidence that a link is wrong — the check runs on a runner, and
    the runner may be the thing that is having a bad day."""
    check = load_check("check-external-links")
    monkeypatch.setattr(
        check.urllib.request,
        "urlopen",
        urlopen_playing(("raise", urllib.error.URLError("temporary failure in name resolution"))),
    )

    state, detail = check.reachable("https://example.test/")
    assert state == "unknown"
    assert "name resolution" in detail


def test_reachable_treats_every_allowed_status_as_unknown(load_check, monkeypatch):
    check = load_check("check-external-links")
    for code in sorted(check.ALLOWED_UNKNOWN):
        monkeypatch.setattr(check.urllib.request, "urlopen", urlopen_playing(("http", code)))
        assert check.reachable("https://example.test/") == ("unknown", code), code


def test_documents_lists_files_and_walks_directories(load_check, make_tree, monkeypatch):
    check = load_check("check-external-links")
    root = make_tree({"README.md": "x", "docs/one.md": "x", "docs/two.md": "x", "docs/skip.txt": "x"})
    monkeypatch.setattr(check, "ROOT", root)
    monkeypatch.setattr(check, "SCAN", ["README.md", "docs", "CHANGELOG.md"])

    names = [path.relative_to(root).as_posix() for path in check.documents()]

    assert names == ["README.md", "docs/one.md", "docs/two.md"]


def test_urls_strips_the_punctuation_a_sentence_adds(load_check, make_tree, monkeypatch):
    check = load_check("check-external-links")
    root = make_tree({"README.md": "See https://example.test/thing, and https://example.test/other."})
    monkeypatch.setattr(check, "ROOT", root)
    monkeypatch.setattr(check, "SCAN", ["README.md"])

    assert set(check.urls()) == {"https://example.test/thing", "https://example.test/other"}


def test_urls_skips_the_skip_hosts(load_check, make_tree, monkeypatch):
    check = load_check("check-external-links")
    root = make_tree({"README.md": "http://localhost:8000/a http://127.0.0.1/b https://example.test/c"})
    monkeypatch.setattr(check, "ROOT", root)
    monkeypatch.setattr(check, "SCAN", ["README.md"])

    assert set(check.urls()) == {"https://example.test/c"}


def test_urls_maps_one_url_to_every_document_that_names_it(load_check, make_tree, monkeypatch):
    check = load_check("check-external-links")
    root = make_tree({"README.md": "https://example.test/shared", "docs/one.md": "https://example.test/shared"})
    monkeypatch.setattr(check, "ROOT", root)
    monkeypatch.setattr(check, "SCAN", ["README.md", "docs"])

    assert check.urls()["https://example.test/shared"] == {"README.md", "docs/one.md"}


def test_main_passes_when_every_link_resolves(load_check, monkeypatch, capsys):
    check = load_check("check-external-links")
    monkeypatch.setattr(check, "urls", lambda: {"https://example.test/a": {"README.md"}})
    monkeypatch.setattr(check, "reachable", lambda url: ("ok", 200))

    assert check.main() == 0
    assert "1 URL(s), 0 broken" in capsys.readouterr().out


def test_main_fails_on_a_broken_link_and_names_the_file(load_check, monkeypatch, capsys):
    check = load_check("check-external-links")
    monkeypatch.setattr(check, "urls", lambda: {"https://example.test/gone": {"CHANGELOG.md"}})
    monkeypatch.setattr(check, "reachable", lambda url: ("broken", 404))

    assert check.main() == 1
    out = capsys.readouterr().out
    assert "::error file=CHANGELOG.md::link returned 404" in out


def test_main_does_not_check_this_sites_own_host(load_check, monkeypatch, capsys):
    """Those URLs name this repository's own output and are asserted after the deployment.
    The check reports them so the decision is legible rather than a silent skip."""
    check = load_check("check-external-links")
    own = f"https://{check.OWN_HOST}/assets/estamora-pitch.mp4"
    checked: list[str] = []

    monkeypatch.setattr(check, "urls", lambda: {own: {"README.md"}})
    monkeypatch.setattr(check, "reachable", lambda url: checked.append(url) or ("ok", 200))

    assert check.main() == 0
    assert checked == []
    out = capsys.readouterr().out
    assert "own        -" in out
    assert "1 on this site's own host" in out


def test_main_reports_unknowns_without_failing(load_check, monkeypatch, capsys):
    check = load_check("check-external-links")
    monkeypatch.setattr(check, "urls", lambda: {"https://example.test/challenged": {"README.md"}})
    monkeypatch.setattr(check, "reachable", lambda url: ("unknown", 403))

    assert check.main() == 0
    assert "1 unknown" in capsys.readouterr().out


def test_main_json_output_is_machine_readable(load_check, monkeypatch, capsys):
    check = load_check("check-external-links")
    monkeypatch.setattr(check, "urls", lambda: {"https://example.test/gone": {"CHANGELOG.md"}})
    monkeypatch.setattr(check, "reachable", lambda url: ("broken", 404))
    monkeypatch.setattr(check.sys, "argv", ["check-external-links.py", "--json"])

    assert check.main() == 1
    payload = json.loads(capsys.readouterr().out.strip().split("\n::error")[0])
    assert payload["checked"] == 1
    assert payload["broken"] == {"https://example.test/gone": {"detail": 404, "in": ["CHANGELOG.md"]}}
