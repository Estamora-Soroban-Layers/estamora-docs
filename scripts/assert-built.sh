#!/usr/bin/env bash
set -euo pipefail

if [ ! -f "site/index.html" ]; then
  echo "error: site/index.html is absent" >&2
  exit 1
fi

echo "assert-built: site directory is verified."
