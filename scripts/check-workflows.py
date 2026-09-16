#!/usr/bin/env python3
"""Audit this repository's workflows: least privilege, bounded jobs, no unsafe trigger.

A workflow file is code that runs with a token, and two omissions are both common and both
consequential:

* **No `permissions:`.** A workflow that does not declare them inherits the repository default,
  which on older repositories is read-write on everything. A job that only needs to read a
  checkout should say so, and declaring it is how it says so.
* **No `timeout-minutes:`.** The default is six hours. A hung step occupies a runner for that
  long, and the job reports nothing until it ends.

It also refuses `pull_request_target`, the one trigger that runs with the base repository's token
against a fork's code: a workflow that uses it is a credential theft waiting for a pull request.

The file is parsed textually rather than with PyYAML, deliberately. This is a guard, and a guard
should not agree with whatever a parser happens to accept -- the assertions are about two keys and
one trigger, which is a shape a reader can verify by eye.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

JOB = re.compile(r"^ {2}([A-Za-z0-9_-]+):\s*$", re.MULTILINE)
TIMEOUT = re.compile(r"^\s{4,6}timeout-minutes:\s*\d+", re.MULTILINE)
TOP_PERMISSIONS = re.compile(r"^permissions:\s*$", re.MULTILINE)
JOB_PERMISSIONS = re.compile(r"^\s{4}permissions:\s*$", re.MULTILINE)
UNSAFE_TRIGGER = re.compile(r"^\s*pull_request_target\s*:", re.MULTILINE)


def main() -> int:
    files = sorted(WORKFLOWS.glob("*.y*ml"))
    problems: list[str] = []

    if not files:
        print("::error::no workflows found, so this check asserts nothing")
        return 1

    for path in files:
        source = path.read_text(encoding="utf-8")
        jobs_block = source.split("jobs:", 1)[1] if "jobs:" in source else ""

        if UNSAFE_TRIGGER.search(source):
            problems.append(f"{path.name} triggers on pull_request_target, which runs with the base token")

        job_names = JOB.findall(jobs_block)
        if not job_names:
            problems.append(f"{path.name}: no jobs found, which cannot be right")
            continue

        timeouts = len(TIMEOUT.findall(jobs_block))
        if timeouts < len(job_names):
            problems.append(
                f"{path.name}: {len(job_names)} job(s) but {timeouts} timeout-minutes declaration(s) — "
                f"every job needs one, or a hung step holds a runner for the six-hour default"
            )

        if not TOP_PERMISSIONS.search(source) and len(JOB_PERMISSIONS.findall(jobs_block)) < len(job_names):
            problems.append(
                f"{path.name}: declares neither top-level permissions nor one per job, so it inherits "
                f"the repository default token scope"
            )

    if problems:
        print(f"::error::the workflows do not meet this repository's hardening rules:")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(
        f"{len(files)} workflow(s) audited: every job declares a timeout, permissions are explicit, "
        f"and no workflow uses pull_request_target"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
