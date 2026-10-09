"""Split prepared Russian System Design TTS requests and assemble tracks/subtitles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

import prepare_system_design_audio as preparation
import role_audio


ROOT = preparation.ROOT
WORK_DIR = preparation.WORK_DIR
OUTPUT_ROOT = preparation.OUTPUT_ROOT
MANIFEST_PATH = WORK_DIR / "manifest.json"
GAP_SECONDS = 0.8
SAMPLE_RATE = 24000
BITRATE = "48k"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_manifest() -> tuple[dict[str, Any], list[preparation.Segment]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema") != 1 or manifest.get("collection") != "system-design-shorts":
        raise ValueError(f"Unsupported System Design manifest: {MANIFEST_PATH}")
    expected_hashes = {
        "source_sha256": preparation.sha256(preparation.SOURCE),
        "pronunciation_sha256": preparation.sha256(preparation.PRONUNCIATION),
        "diagram_narration_sha256": preparation.sha256(preparation.DIAGRAMS),
    }
    for key, expected in expected_hashes.items():
        if manifest.get(key) != expected:
            raise ValueError(f"Prepared manifest is stale: {key} changed; prepare it again")
    segments = [preparation.Segment(**item) for item in manifest["segments"]]
    return manifest, segments


def chapter_dir(segment: preparation.Segment) -> Path:
    return OUTPUT_ROOT / f"{segment.section:02d}-ru-{segment.section_slug}"


def run_ffmpeg(command: list[str]) -> None:
    subprocess.run(command, check=True)


def split_requests(manifest: dict[str, Any], segments: list[preparation.Segment], force: bool) -> None:
    lookup = {segment.id: segment for segment in segments}
    synthesis_dir = WORK_DIR / "synthesis"
    for batch in manifest["batches"]:
        batch_id = batch["id"]
        media = synthesis_dir / f"{batch_id}.mp3"
        metadata_path = synthesis_dir / f"{batch_id}.boundaries.json"
        text_path = preparation.BATCHES_DIR / f"{batch_id}.txt"
        for path in (media, metadata_path, text_path):
            if not path.is_file() or path.stat().st_size == 0:
                raise FileNotFoundError(f"Missing or empty synthesis input: {path}")
        text = text_path.read_text(encoding="utf-8")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("source_sha256") != sha256_text(text):
            raise ValueError(f"Synthesis boundaries do not match batch text: {batch_id}")
        if metadata.get("boundary_type") != "WordBoundary" or metadata.get("voice") != batch["voice"]:
            raise ValueError(f"Unexpected boundary type or voice: {batch_id}")
        if any(metadata.get(key) != manifest["settings"][key] for key in ("rate", "volume", "pitch")):
            raise ValueError(f"TTS settings differ from the prepared manifest: {batch_id}")
        items = [lookup[segment_id] for segment_id in batch["segment_ids"]]
        boundary_text = "".join(str(boundary["text"]) for boundary in metadata["boundaries"])
        if role_audio.normalized_spoken(boundary_text) != role_audio.normalized_spoken(text):
            raise ValueError(f"Word boundaries do not reconstruct the requested text: {batch_id}")
        positions = role_audio.align_boundaries(items, metadata["boundaries"])
        total_duration = role_audio.media_duration(media)
        starts = [role_audio.seconds_from_ticks(metadata["boundaries"][first]["offset"]) for first, _ in positions]
        ends = [
            role_audio.seconds_from_ticks(
                metadata["boundaries"][last]["offset"] + metadata["boundaries"][last]["duration"]
            )
            for _, last in positions
        ]
        cut_points = [0.0]
        for previous_end, next_start in zip(ends, starts[1:]):
            cut_points.append((previous_end + next_start) / 2 if next_start >= previous_end else next_start)
        cut_ends = cut_points[1:] + [total_duration]
        for segment, (first, last), cut_start, cut_end in zip(items, positions, cut_points, cut_ends):
            directory = chapter_dir(segment)
            directory.mkdir(parents=True, exist_ok=True)
            output = directory / f"{segment.output_stem}.mp3"
            if output.exists() and not force:
                raise FileExistsError(f"Segment already exists; use --force to replace it: {output}")
            run_ffmpeg(
                [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{cut_start:.6f}", "-t", f"{cut_end - cut_start:.6f}",
                    "-i", str(media), "-c:a", "copy", str(output),
                ]
            )
            local_boundaries = [
                {
                    **boundary,
                    "local_offset": role_audio.seconds_from_ticks(boundary["offset"]) - cut_start,
                    "local_duration": role_audio.seconds_from_ticks(boundary["duration"]),
                }
                for boundary in metadata["boundaries"][first : last + 1]
            ]
            fingerprint = sha256_text(
                f"{metadata['source_sha256']}|{batch_id}|{cut_start:.6f}|{cut_end:.6f}|copy"
            )
            entry = {
                "id": segment.id,
                "file": output.name,
                "batch": batch_id,
                "fingerprint": fingerprint,
                "cut_start": cut_start,
                "cut_end": cut_end,
                "duration": role_audio.media_duration(output),
                "boundaries": local_boundaries,
            }
            (directory / f"{segment.output_stem}.md").write_text(
                "\n".join(
                    [
                        f"# {segment.id}", "",
                        f"- Source: `{manifest['source']}` - `{segment.section_title}`", 
                        f"- Kind: `{segment.kind}`", f"- Voice: `{segment.voice}`",
                        f"- Batch: `{batch_id}`", 
                        f"- Batch cut: `{cut_start:.3f}-{cut_end:.3f}`", "",
                        "## Canonical text", "", segment.canonical_text, "",
                        "## TTS text", "", segment.tts_text, "",
                    ]
                ),
                encoding="utf-8",
            )
            segment_entries = directory / "segments.json"
            current = {"schema": 1, "segments": []}
            if segment_entries.exists():
                current = json.loads(segment_entries.read_text(encoding="utf-8"))
            values = [value for value in current["segments"] if value["id"] != segment.id]
            values.append(entry)
            order = {item.id: index for index, item in enumerate(segments)}
            current["segments"] = sorted(values, key=lambda value: order[value["id"]])
            segment_entries.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"SPLIT {batch_id}: {len(items)} segments")


def assemble_chapter(items: list[preparation.Segment], force: bool) -> None:
    directory = chapter_dir(items[0])
    inputs = [directory / f"{item.output_stem}.mp3" for item in items]
    split_path = directory / "segments.json"
    split_data = json.loads(split_path.read_text(encoding="utf-8"))
    split_lookup = {value["id"]: value for value in split_data["segments"]}
    if any(not path.is_file() or path.stat().st_size == 0 for path in inputs):
        missing = next(path for path in inputs if not path.is_file() or path.stat().st_size == 0)
        raise FileNotFoundError(f"Missing split segment: {missing}")
    track_name = f"{items[0].section:02d}-ru-system-design-{items[0].section_slug}.mp3"
    output = directory / track_name
    timing_path = directory / "timing.json"
    if output.exists() and timing_path.exists() and not force:
        raise FileExistsError(f"Track already exists; use --force to replace it: {output}")

    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for path in inputs:
        command.extend(["-i", str(path)])
    filters = []
    labels = []
    for index in range(len(inputs)):
        label = f"s{index}"
        filters.append(f"[{index}:a]" + (f"apad=pad_dur={GAP_SECONDS:.3f}" if index + 1 < len(inputs) else "anull") + f"[{label}]")
        labels.append(f"[{label}]")
    filters.append("".join(labels) + f"concat=n={len(inputs)}:v=0:a=1[out]")
    command.extend(["-filter_complex", ";".join(filters), "-map", "[out]", "-ar", str(SAMPLE_RATE), "-ac", "1", "-c:a", "libmp3lame", "-b:a", BITRATE, str(output)])
    run_ffmpeg(command)

    timing_segments = []
    rows = []
    offset = 0.0
    for index, (item, path) in enumerate(zip(items, inputs)):
        duration = role_audio.media_duration(path)
        end = offset + duration
        gap = GAP_SECONDS if index + 1 < len(inputs) else 0.0
        timing_segments.append({"id": item.id, "file": path.name, "duration": duration, "track_start": offset, "track_end": end, "gap_after": gap})
        rows.append(f"| `{item.id}` | `{path.name}` | `{item.voice}` | {duration:.3f} | {offset:.3f}-{end:.3f} | {gap:.3f} |")
        offset = end + gap
    duration = role_audio.media_duration(output)
    fingerprint = sha256_text("|".join(split_lookup[item.id]["fingerprint"] for item in items) + f"|gap={GAP_SECONDS:.3f}")
    timing_path.write_text(json.dumps({"schema": 1, "fingerprint": fingerprint, "gap": GAP_SECONDS, "track": track_name, "segments": timing_segments, "duration": duration}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (directory / "timing.md").write_text(
        "\n".join([
            f"# Timing: {items[0].section:02d}-ru-system-design-{items[0].section_slug}", "",
            f"- Source: `{preparation.SOURCE.relative_to(ROOT).as_posix()}` - `{items[0].section_title}`",
            f"- Assembled track: `{track_name}`", f"- Assembled duration: `{role_audio.format_clock(duration)}`",
            f"- Gap between segments: `{GAP_SECONDS:.3f} s`", "", "## Segments", "",
            "| ID | File | Voice | Duration | Track start-end | Gap after |", "| --- | --- | --- | ---: | --- | ---: |", *rows, "",
        ]), encoding="utf-8"
    )
    print(f"ASSEMBLED {items[0].section:02d}: {track_name} ({duration:.3f}s)")


def align_system_cues(
    item: preparation.Segment,
    split_entry: dict[str, Any],
    mapping: dict[str, str],
) -> list[tuple[str, float, float]]:
    canonical_cues = [item.canonical_text] if item.kind != "answer" else role_audio.cue_parts(item.canonical_text)
    expected = (
        [item.tts_text]
        if item.kind != "answer"
        else [role_audio.apply_pronunciation(value, mapping) for value in canonical_cues]
    )
    alignment_segments = [
        role_audio.Segment(
            id=f"{item.id}-cue-{index:02d}",
            chapter=item.section,
            chapter_title=item.section_title,
            chapter_slug=item.section_slug,
            kind=item.kind,
            ordinal=item.ordinal,
            role=item.role,
            voice=item.voice,
            canonical_text=canonical,
            tts_text=spoken,
            batch=split_entry["batch"],
            output_stem=item.output_stem,
        )
        for index, (canonical, spoken) in enumerate(zip(canonical_cues, expected), start=1)
    ]
    positions = role_audio.align_boundaries(alignment_segments, split_entry["boundaries"])
    result = []
    for text, (first, last) in zip(canonical_cues, positions):
        boundaries = split_entry["boundaries"]
        start = boundaries[first]["local_offset"]
        end = boundaries[last]["local_offset"] + boundaries[last]["local_duration"]
        result.append((text, start, end))
    return result


def make_subtitles(items: list[preparation.Segment], force: bool) -> None:
    directory = chapter_dir(items[0])
    timing = json.loads((directory / "timing.json").read_text(encoding="utf-8"))
    split = json.loads((directory / "segments.json").read_text(encoding="utf-8"))
    timing_lookup = {value["id"]: value for value in timing["segments"]}
    split_lookup = {value["id"]: value for value in split["segments"]}
    output = directory / f"{items[0].section:02d}-ru-system-design-{items[0].section_slug}.srt"
    metadata_path = output.with_suffix(".srt.json")
    if (output.exists() or metadata_path.exists()) and not force:
        raise FileExistsError(f"Subtitles already exist; use --force to replace: {output}")
    mapping = role_audio.read_pronunciation(preparation.PRONUNCIATION)
    cues: list[tuple[str, float, float]] = []
    for item in items:
        timing_entry = timing_lookup[item.id]
        base = float(timing_entry["track_start"])
        segment_end = min(float(timing_entry["track_end"]), float(timing["duration"]))
        for text, start, end in align_system_cues(item, split_lookup[item.id], mapping):
            cue_start = max(base, base + start)
            cue_end = min(segment_end, base + end)
            if cue_end <= cue_start:
                raise ValueError(f"Invalid subtitle timing for {item.id}")
            cues.append((role_audio.styled_subtitle_text(item.kind, text), cue_start, cue_end))
    blocks = [f"{index}\n{role_audio.format_srt_time(start)} --> {role_audio.format_srt_time(end)}\n{text}" for index, (text, start, end) in enumerate(cues, start=1)]
    output.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    fingerprint = sha256_text((output.read_text(encoding="utf-8") + timing["track"]))
    metadata_path.write_text(json.dumps({"schema": 1, "fingerprint": fingerprint, "cues": len(cues)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SUBTITLES {items[0].section:02d}: {len(cues)} cues")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="replace existing segment, track, and subtitle outputs")
    args = parser.parse_args()
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        parser.error("ffmpeg and ffprobe are required")
    manifest, segments = read_manifest()
    # Split outputs are generated from the saved WordBoundary data, with no network calls.
    split_requests(manifest, segments, args.force)
    for section in sorted({item.section for item in segments}):
        items = [item for item in segments if item.section == section]
        assemble_chapter(items, args.force)
        make_subtitles(items, args.force)
    print(f"Complete: {len(segments)} segments across {len(preparation.SECTION_CONFIG)} chapters")


if __name__ == "__main__":
    main()
