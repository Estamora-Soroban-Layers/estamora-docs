#!/usr/bin/env bash
#
# Put a playable copy of the product pitch beside the pages.
#
#   ./scripts/fetch-pitch-video.sh build/docs/assets
#
# # Why the video is fetched rather than committed
#
# It is 15 MB. A binary that size is re-cloned by every contributor and every CI run for the
# life of the repository, and it would be the largest object in a repository whose point is
# readable documents. The archival copy is the release asset named below: immutable, addressable
# by tag, and with its own retention. This script puts a copy next to the pages at build time.
#
# # Why that copy is not cosmetic
#
# A GitHub release asset is served with `content-type: application/octet-stream` and
# `content-disposition: attachment`. A link to one therefore *downloads* a 15 MB file rather
# than playing it. Somebody who clicks "watch the pitch" and gets a download prompt instead of
# a video is somebody who does not watch the pitch, and the pitch is the fastest way to
# understand this project.
#
# The copy this script fetches is served by the site with `content-type: video/mp4` and
# byte-range support, which is what makes it play inline and seek. The release asset stays the
# archival copy and is linked as a download.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

DEST_DIR="${1:-build/docs/assets}"

# Pinned like the documents, and for the same reason: a video that can change under a published
# URL without a commit here is one nobody can cite. `pitch-v1` is a tag on this repository.
PITCH_TAG="${ESTAMORA_PITCH_TAG:-pitch-v1}"
PITCH_FILE="${ESTAMORA_PITCH_FILE:-estamora-pitch.mp4}"
PITCH_URL="https://github.com/Estamora-Soroban-Layers/estamora-docs/releases/download/${PITCH_TAG}/${PITCH_FILE}"

# A floor rather than an exact size: the check exists to catch an HTML error page or an empty
# file saved under the video's name, not to fail when the edit changes by a few frames.
MIN_BYTES=1000000

say() { printf '%s\n' "$*" >&2; }
die() { say "fetch-pitch-video: $*"; exit 1; }

mkdir -p "$DEST_DIR"
DEST="$DEST_DIR/$PITCH_FILE"

if [ -s "$DEST" ] && [ "$(wc -c <"$DEST")" -ge "$MIN_BYTES" ]; then
    say "fetch-pitch-video: $DEST is already present"
elif [ -n "${ESTAMORA_PITCH_LOCAL:-}" ]; then
    # A contributor re-rendering the video should not have to publish a release to preview the
    # site, and an unreleased local edit is exactly what they want to look at.
    [ -f "$ESTAMORA_PITCH_LOCAL" ] || die "ESTAMORA_PITCH_LOCAL names ${ESTAMORA_PITCH_LOCAL} and it is not a file"
    say "fetch-pitch-video: copying $ESTAMORA_PITCH_LOCAL"
    cp "$ESTAMORA_PITCH_LOCAL" "$DEST"
else
    say "fetch-pitch-video: downloading $PITCH_TAG/$PITCH_FILE"
    # `-L` because the release host answers with a redirect to signed storage, and `--fail` so an
    # HTTP error is a failure rather than a 9-byte file named estamora-pitch.mp4.
    curl --fail --location --silent --show-error --retry 3 --retry-delay 2 \
        --max-time 300 --output "$DEST.part" "$PITCH_URL" \
        || die "could not download $PITCH_URL"
    mv "$DEST.part" "$DEST"
fi

bytes="$(wc -c <"$DEST" | tr -d ' ')"
[ "$bytes" -ge "$MIN_BYTES" ] || die "$DEST is $bytes bytes; expected at least $MIN_BYTES"

# Assert the bytes are an ISO base media file rather than trusting the extension. A redirect
# that landed on an error page, or a truncated download, would otherwise be published as a
# video that does not play.
python3 - "$DEST" <<'PY' || exit 1
import sys
path = sys.argv[1]
with open(path, "rb") as handle:
    header = handle.read(64)
# Every MP4 begins with a big-endian box size followed by the `ftyp` box type.
if len(header) < 12 or header[4:8] != b"ftyp":
    print(f"fetch-pitch-video: {path} is not an MP4 (no ftyp box)", file=sys.stderr)
    sys.exit(1)
PY

say "fetch-pitch-video: $DEST ($bytes bytes, $(python3 -c "print(f'{$bytes/1048576:.1f}')") MiB)"
