"""Merge manually synthesized answer parts into one pipeline-compatible batch."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import role_audio


ROOT = Path(__file__).resolve().parents[2]
SYNTHESIS_DIR = ROOT / "build/audio/role-ru/synthesis"


def duration(path: Path) -> float:
    completed = subprocess.run(
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
        check=True,
        text=True,
        capture_output=True,
    )
    return float(completed.stdout.strip())


def escaped_concat_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "'\\''")


def merge(chapter: int, force: bool) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("ffmpeg and ffprobe are required")
    if chapter == 9:
        raise ValueError("Chapter 09 is protected")

    manifest = role_audio.load_manifest()
    batch_id = f"answers-{chapter:02d}"
    batch = next((item for item in manifest["batches"] if item["id"] == batch_id), None)
    if batch is None:
        raise ValueError(f"Batch is absent from the manifest: {batch_id}")
    commands_path = SYNTHESIS_DIR / f"{batch_id}-commands.txt"
    if not commands_path.exists():
        raise FileNotFoundError(f"Missing command plan: {commands_path}")
    expected_parts = len(commands_path.read_text(encoding="utf-8").splitlines())
    part_stems = [f"{batch_id}-part-{index:02d}" for index in range(1, expected_parts + 1)]
    text_paths = [SYNTHESIS_DIR / f"{stem}.txt" for stem in part_stems]
    media_paths = [SYNTHESIS_DIR / f"{stem}.mp3" for stem in part_stems]
    boundary_paths = [SYNTHESIS_DIR / f"{stem}.boundaries.json" for stem in part_stems]
    for path in [*text_paths, *media_paths, *boundary_paths]:
        if not path.exists():
            raise FileNotFoundError(f"Missing part artifact: {path}")

    segments = [
        role_audio.Segment(**item)
        for item in manifest["segments"]
        if item["batch"] == batch_id
    ]
    expected_text = "\n\n".join(item.tts_text for item in segments)
    actual_text = "\n\n".join(path.read_text(encoding="utf-8").strip() for path in text_paths)
    if actual_text != expected_text:
        raise ValueError(f"Part texts do not reconstruct {batch_id} exactly")

    combined_boundaries: list[dict[str, object]] = []
    part_ledger = []
    shift_ticks = 0
    total_input_duration = 0.0
    for index, (text_path, media_path, boundary_path) in enumerate(
        zip(text_paths, media_paths, boundary_paths), start=1
    ):
        text = text_path.read_text(encoding="utf-8")
        metadata = json.loads(boundary_path.read_text(encoding="utf-8"))
        if metadata.get("source_sha256") != hashlib.sha256(text.encode("utf-8")).hexdigest():
            raise ValueError(f"Stale boundary metadata: {boundary_path}")
        if metadata.get("boundary_type") != "WordBoundary":
            raise ValueError(f"Expected WordBoundary metadata: {boundary_path}")
        if (
            metadata.get("voice") != batch["voice"]
            or metadata.get("rate") != role_audio.RATE
            or metadata.get("volume") != role_audio.VOLUME
            or metadata.get("pitch") != role_audio.PITCH
        ):
            raise ValueError(f"Voice settings differ in {boundary_path}")
        boundaries = metadata.get("boundaries", [])
        boundary_text = "".join(str(item["text"]) for item in boundaries)
        if role_audio.normalized_spoken(boundary_text) != role_audio.normalized_spoken(text):
            raise ValueError(f"Boundary text does not match {text_path}")
        part_duration = duration(media_path)
        for boundary in boundaries:
            combined_boundaries.append(
                {
                    "offset": int(round(float(boundary["offset"]))) + shift_ticks,
                    "duration": boundary["duration"],
                    "text": boundary["text"],
                }
            )
        part_ledger.append(
            {
                "part": index,
                "media": media_path.name,
                "boundaries": len(boundaries),
                "duration": part_duration,
                "start": total_input_duration,
            }
        )
        total_input_duration += part_duration
        shift_ticks = int(round(total_input_duration * 10_000_000))

    media_output = SYNTHESIS_DIR / f"{batch_id}.mp3"
    boundaries_output = SYNTHESIS_DIR / f"{batch_id}.boundaries.json"
    if (media_output.exists() or boundaries_output.exists()) and not force:
        raise FileExistsError(f"Final batch already exists; use --force: {media_output}")
    concat_path = SYNTHESIS_DIR / f"{batch_id}.concat.txt.part"
    media_part = media_output.with_suffix(".mp3.part")
    boundaries_part = boundaries_output.with_suffix(".json.part")
    try:
        concat_path.write_text(
            "\n".join(f"file '{escaped_concat_path(path)}'" for path in media_paths) + "\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-c:a",
                "copy",
                "-f",
                "mp3",
                str(media_part),
            ],
            check=True,
        )
        output_duration = duration(media_part)
        if abs(output_duration - total_input_duration) > 0.25:
            raise RuntimeError(
                f"Merged duration drift is too large: inputs={total_input_duration:.3f}, "
                f"output={output_duration:.3f}"
            )
        payload = {
            "schema": 1,
            "batch": batch_id,
            "fingerprint": role_audio.synthesis_fingerprint(batch),
            "voice": batch["voice"],
            "rate": role_audio.RATE,
            "volume": role_audio.VOLUME,
            "pitch": role_audio.PITCH,
            "boundary_type": "WordBoundary",
            "boundaries": combined_boundaries,
            "parts": part_ledger,
            "duration": output_duration,
        }
        boundaries_part.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        media_part.replace(media_output)
        boundaries_part.replace(boundaries_output)
    finally:
        concat_path.unlink(missing_ok=True)
        media_part.unlink(missing_ok=True)
        boundaries_part.unlink(missing_ok=True)

    print(
        f"Merged {expected_parts} parts into {media_output.name}: "
        f"{output_duration:.3f} seconds, {len(combined_boundaries)} boundaries"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        merge(args.chapter, args.force)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
