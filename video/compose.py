#!/usr/bin/env python3
"""Compose the pitch video from the captured frames and the synthesised narration.

Every frame comes from `capture.mjs`, which filmed live deployments and real program output.
Nothing here is redrawn: this step only sequences, captions and encodes.

The caption is passed to `drawtext` with `textfile=` rather than `text=`. That is not a
detail -- a colon or an apostrophe in an inline drawtext expression silently truncates or
breaks the filter, and the failure mode is a caption that quietly loses half its words.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path("/tmp/video")
SHOTS = ROOT / "shots"
AUDIO = ROOT / "audio"
CLIPS = ROOT / "clips"
CAPTIONS = ROOT / "captions"
OUT = ROOT / "estamora-pitch.mp4"

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WIDTH, HEIGHT, FPS = 1920, 1080, 30
FADE = 0.30


def run(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-8:])
        raise SystemExit(f"ffmpeg failed for {' '.join(args[:6])}...\n{tail}")


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_name,width,height,sample_rate,channels",
         "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    scenes = json.loads((ROOT / "scenes.json").read_text(encoding="utf-8"))
    durations = json.loads((ROOT / "durations.json").read_text(encoding="utf-8"))
    CLIPS.mkdir(exist_ok=True)
    CAPTIONS.mkdir(exist_ok=True)

    clip_paths: list[Path] = []
    for index, scene in enumerate(scenes):
        shot = SHOTS / f"{scene['shot']}.png"
        if not shot.exists():
            raise SystemExit(f"missing shot for scene {scene['id']}: {shot}")
        audio = AUDIO / f"{scene['id']}.wav"
        if not audio.exists():
            raise SystemExit(f"missing narration for scene {scene['id']}")
        duration = durations[scene["id"]]

        caption = CAPTIONS / f"{scene['id']}.txt"
        caption.write_text(scene["caption"], encoding="utf-8")

        fade_out_start = max(0.0, duration - FADE)
        # The caption holds for the first nine seconds or the scene, whichever is shorter.
        caption_until = min(9.0, duration - 0.4)

        filters = [
            f"scale={WIDTH}:{HEIGHT}",
            "setsar=1",
            f"fps={FPS}",
            f"drawtext=textfile='{caption}':fontfile='{FONT}':fontsize=34:fontcolor=white:"
            f"box=1:boxcolor=0x0b0f16@0.85:boxborderw=20:x=64:y=h-160:"
            f"enable='between(t,0.5,{caption_until:.2f})'",
            f"fade=t=in:st=0:d={FADE}",
            f"fade=t=out:st={fade_out_start:.2f}:d={FADE}",
            "format=yuv420p",
        ]

        clip = CLIPS / f"{index:02d}-{scene['id']}.mp4"
        run([
            "ffmpeg", "-y", "-v", "error",
            "-loop", "1", "-framerate", str(FPS), "-i", str(shot),
            "-i", str(audio),
            "-filter_complex", f"[0:v]{','.join(filters)}[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{duration:.3f}",
            "-movflags", "+faststart",
            str(clip),
        ])
        clip_paths.append(clip)
        print(f"  clip {scene['id']:14s} {duration:7.2f}s")

    listing = ROOT / "clips.txt"
    listing.write_text(
        "\n".join(f"file '{path.resolve()}'" for path in clip_paths) + "\n", encoding="utf-8"
    )

    # The clips are encoded identically, so the concat demuxer can join them without
    # re-encoding. `-c copy` also means the final file is exactly the clips, with no
    # second generation of compression.
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", "-movflags", "+faststart",
        str(OUT),
    ])

    info = probe(OUT)
    duration = float(info["format"]["duration"])
    video = next(s for s in info["streams"] if s.get("width"))
    audio = next(s for s in info["streams"] if s.get("sample_rate"))
    size_mb = OUT.stat().st_size / (1024 * 1024)

    print(f"\n{OUT}")
    print(f"  duration {duration:.1f}s ({duration / 60:.2f} min)")
    print(f"  video    {video['codec_name']} {video['width']}x{video['height']}")
    print(f"  audio    {audio['codec_name']} {audio['sample_rate']} Hz, {audio['channels']} ch")
    print(f"  size     {size_mb:.1f} MB")

    expected = sum(durations.values())
    if abs(duration - expected) > 1.5:
        raise SystemExit(
            f"the finished video is {duration:.1f}s but the scenes total {expected:.1f}s; "
            "a clip is missing from the concatenation"
        )
    if int(video["width"]) != WIDTH or int(video["height"]) != HEIGHT:
        raise SystemExit("the finished video is not 1920x1080")


if __name__ == "__main__":
    main()
