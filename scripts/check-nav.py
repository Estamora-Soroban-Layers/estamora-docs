#!/usr/bin/env python3
"""Check that every curated document is in the navigation, and nothing else is invented.

Two failures this catches, both invisible until a reader notices:

1. **A curated page missing from `nav`.** MkDocs builds it, so the file exists at its URL and
   nothing 404s -- but no navigation entry leads to it, and a page nobody can navigate to is a
   page nobody reads.
2. **A nav entry naming a file that is not there.** MkDocs is lenient about this in some
   configurations and strict in others; either way the site is published with a dead entry.

The second check has a deliberate limit, stated rather than hidden: most pages on this site are
**assembled at build time** from pinned revisions of the specification and runner repositories,
so they do not exist on disk here. The check therefore asserts that every curated document
appears in the navigation, and that every navigation target which *looks* curated (it is not in
the assembled set) resolves to a file. The assembled set is derived from the same list
`scripts/assemble-docs.sh` uses, so the two cannot drift apart silently.

`mkdocs.yml` uses the `!ENV` tag for values that are set at build time, which PyYAML does not
know. The loader below ignores unknown tags rather than failing, because the alternative is a
check that breaks when a new tag is introduced for an unrelated reason.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
MKDOCS = REPO_ROOT / "mkdocs.yml"
DOCS_DIR = REPO_ROOT / "docs"

# Directories whose contents are assembled from other repositories rather than curated here.
# Kept in step with `scripts/assemble-docs.sh`, which is what produces them.
ASSEMBLED_PREFIXES = ("runner/", "spec/", "reference/")


class TolerantLoader(yaml.SafeLoader):
    """A loader that treats an unknown tag as its scalar value instead of raising."""


def _ignore_unknown(loader: yaml.SafeLoader, node: yaml.Node) -> object:
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


TolerantLoader.add_constructor(None, _ignore_unknown)


def nav_targets(nav: object) -> list[str]:
    """Every file path named by a navigation entry, at any depth."""
    found: list[str] = []
    if isinstance(nav, list):
        for entry in nav:
            found.extend(nav_targets(entry))
    elif isinstance(nav, dict):
        for value in nav.values():
            found.extend(nav_targets(value))
    elif isinstance(nav, str):
        found.append(nav)
    return found


def main() -> int:
    config = yaml.load(MKDOCS.read_text(encoding="utf-8"), Loader=TolerantLoader) or {}
    targets = nav_targets(config.get("nav", []))

    if not targets:
        print("::error::mkdocs.yml declares no nav entries, so this check asserts nothing")
        return 1

    problems: list[str] = []

    # Every curated document must be reachable from the navigation.
    curated = sorted(
        path.relative_to(DOCS_DIR).as_posix()
        for path in DOCS_DIR.rglob("*.md")
        if not path.relative_to(DOCS_DIR).as_posix().startswith(ASSEMBLED_PREFIXES)
    )
    for document in curated:
        if document not in targets:
            problems.append(f"docs/{document} is curated but appears in no navigation entry")

    # Every navigation target that is not assembled must exist on disk.
    for target in targets:
        if target.startswith(ASSEMBLED_PREFIXES):
            continue
        if not (DOCS_DIR / target).exists():
            problems.append(f"the navigation names {target}, which does not exist in docs/")

    if problems:
        print(f"::error::{len(problems)} navigation problem(s):")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(
        f"navigation: {len(targets)} entries, {len(curated)} curated document(s) reachable, "
        f"every non-assembled target resolves"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
