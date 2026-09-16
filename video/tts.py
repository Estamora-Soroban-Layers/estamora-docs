#!/usr/bin/env python3
"""Synthesize the narration, one file per scene, with the local neural voice.

Runs offline. No API key, no service, no per-character cost -- which is also why the whole
video is reproducible by anyone who checks out this pipeline rather than being a one-off
artefact that only exists in one place.
"""

from __future__ import annotations

import json
import subprocess
import wave
from pathlib import Path

ROOT = Path("/tmp/video")
VOICE = ROOT / "voice" / "en_GB-cori-high.onnx"
AUDIO = ROOT / "audio"
MODEL_FLAG = str(VOICE)


def load_voice():
    from piper.voice import PiperVoice

    return PiperVoice.load(str(VOICE), config_path=str(VOICE) + ".json")


def synthesize_with_api(voice, text: str, out: Path) -> bool:
    try:
        with wave.open(str(out), "wb") as handle:
            voice.synthesize_wav(text, handle)
        return out.stat().st_size > 1000
    except Exception as problem:  # noqa: BLE001
        print(f"    api synthesis failed ({problem}); using the cli")
        return False


def synthesize_with_cli(text: str, out: Path) -> bool:
    textfile = ROOT / "_scene_text.txt"
    textfile.write_text(text, encoding="utf-8")
    result = subprocess.run(
        ["piper", "-m", MODEL_FLAG, "-i", str(textfile), "-f", str(out)],
        capture_output=True,
        text=True,
    )
    textfile.unlink(missing_ok=True)
    return result.returncode == 0 and out.exists() and out.stat().st_size > 1000


def duration_of(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def main() -> None:
    scenes = json.loads((ROOT / "scenes.json").read_text(encoding="utf-8"))
    AUDIO.mkdir(exist_ok=True)

    voice = None
    try:
        voice = load_voice()
    except Exception as problem:  # noqa: BLE001
        print(f"could not load the voice for in-process use ({problem}); using the cli")

    durations: dict[str, float] = {}
    words = 0
    for scene in scenes:
        out = AUDIO / f"{scene['id']}.wav"
        text = scene["narration"]
        words += len(text.split())

        ok = False
        if voice is not None:
            ok = synthesize_with_api(voice, text, out)
        if not ok:
            ok = synthesize_with_cli(text, out)
        if not ok:
            raise SystemExit(f"could not synthesize {scene['id']}")

        # A little silence at the end of each scene, so a cut never lands on the last
        # syllable. It is added here rather than in the edit so that the duration recorded
        # for the scene is the duration the scene actually occupies.
        padded = out.with_name(out.stem + "-padded.wav")
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(out),
                "-af", "apad=pad_dur=0.9,aresample=48000",
                "-ac", "2",
                str(padded),
            ],
            check=True,
        )
        padded.replace(out)
        durations[scene["id"]] = round(duration_of(out), 3)
        print(f"  {scene['id']:14s} {durations[scene['id']]:7.2f}s  {len(text.split()):3d} words")

    (ROOT / "durations.json").write_text(json.dumps(durations, indent=2), encoding="utf-8")
    total = sum(durations.values())
    print(f"\nnarration: {words} words, {total:.1f}s ({total / 60:.2f} min), {words / (total / 60):.0f} wpm")


if __name__ == "__main__":
    main()
