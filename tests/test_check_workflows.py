"""The workflow-hardening guard.

The guard is deliberately textual rather than a YAML parse — it asserts two keys and one
trigger, which is a shape a reader can check by eye — so these tests are about the *shapes*
of workflow files it accepts and refuses, not about GitHub's parser. The distinction matters
for what a green run means: this check says a job declared a timeout, not that GitHub will
honour it.
"""

from __future__ import annotations

import pytest

GOOD = """\
name: CI
on:
  push:
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: echo ok
"""


def write_workflows(make_tree, files: dict[str, str]):
    return make_tree({f".github/workflows/{name}": text for name, text in files.items()})


def test_this_repositories_workflows_pass(load_check):
    assert load_check("check-workflows").main() == 0


def test_the_baseline_fixture_passes(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-workflows")
    monkeypatch.setattr(check, "WORKFLOWS", write_workflows(make_tree, {"ci.yml": GOOD}) / ".github" / "workflows")

    assert check.main() == 0
    assert "1 workflow(s) audited" in capsys.readouterr().out


def test_a_job_without_a_timeout_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-workflows")
    source = GOOD.replace("    timeout-minutes: 10\n", "")
    monkeypatch.setattr(check, "WORKFLOWS", write_workflows(make_tree, {"ci.yml": source}) / ".github" / "workflows")

    assert check.main() == 1
    assert "timeout-minutes" in capsys.readouterr().out


def test_one_job_declaring_a_timeout_is_not_enough_for_two(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-workflows")
    source = GOOD + """\
  publish:
    runs-on: ubuntu-latest
    steps:
      - run: echo publish
"""
    monkeypatch.setattr(check, "WORKFLOWS", write_workflows(make_tree, {"ci.yml": source}) / ".github" / "workflows")

    assert check.main() == 1
    assert "2 job(s) but 1 timeout-minutes declaration(s)" in capsys.readouterr().out


def test_permissions_may_be_declared_per_job_instead(load_check, make_tree, monkeypatch):
    check = load_check("check-workflows")
    source = """\
name: CI
on:
  push:
jobs:
  build:
    permissions:
      contents: read
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - run: echo ok
"""
    monkeypatch.setattr(check, "WORKFLOWS", write_workflows(make_tree, {"ci.yml": source}) / ".github" / "workflows")

    assert check.main() == 0


def test_declaring_no_permissions_at_all_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-workflows")
    source = GOOD.replace("permissions:\n  contents: read\n", "")
    monkeypatch.setattr(check, "WORKFLOWS", write_workflows(make_tree, {"ci.yml": source}) / ".github" / "workflows")

    assert check.main() == 1
    assert "inherits the repository default token scope" in capsys.readouterr().out


def test_pull_request_target_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-workflows")
    source = GOOD.replace("on:\n  push:\n", "on:\n  pull_request_target:\n")
    monkeypatch.setattr(check, "WORKFLOWS", write_workflows(make_tree, {"ci.yml": source}) / ".github" / "workflows")

    assert check.main() == 1
    assert "pull_request_target" in capsys.readouterr().out


def test_a_file_declaring_no_jobs_is_refused(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-workflows")
    source = "name: CI\non:\n  push:\npermissions:\n  contents: read\njobs:\n"
    monkeypatch.setattr(check, "WORKFLOWS", write_workflows(make_tree, {"ci.yml": source}) / ".github" / "workflows")

    assert check.main() == 1
    assert "no jobs found" in capsys.readouterr().out


def test_no_workflows_at_all_fails_rather_than_passing_vacuously(load_check, make_tree, monkeypatch, capsys):
    check = load_check("check-workflows")
    empty = make_tree({"placeholder": ""}) / ".github" / "workflows"
    empty.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(check, "WORKFLOWS", empty)

    assert check.main() == 1
    assert "asserts nothing" in capsys.readouterr().out


@pytest.mark.parametrize("name", ["ci.yml", "check.yaml"])
def test_both_yml_spellings_are_audited(load_check, make_tree, monkeypatch, name):
    check = load_check("check-workflows")
    monkeypatch.setattr(check, "WORKFLOWS", write_workflows(make_tree, {name: GOOD}) / ".github" / "workflows")

    assert check.main() == 0
