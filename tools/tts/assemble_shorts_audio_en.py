"""Split prepared English Shorts TTS, assemble role tracks and matched subtitles."""

from __future__ import annotations

from dataclasses import asdict
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

import prepare_shorts_audio_en as preparation
import prepare_shorts_answers_en as answer_preparation
import role_audio


ROOT = preparation.ROOT
OUTPUT_ROOT = preparation.OUTPUT_ROOT
WORK_DIR = preparation.WORK_DIR
MANIFEST_PATH = WORK_DIR / "manifest.json"
GAP_SECONDS = 0.8

# End of each English cue except the last one. These boundaries deliberately
# follow the corresponding Russian cue's meaning, even when punctuation and
# sentence lengths differ between the two languages.
CUE_ENDINGS: dict[tuple[int, int], tuple[str, ...]] = {
    (1, 3): ("DIP.", "maintain.", "change.", "same time.", "modification.",
             "blocks.", "base type", "behavior.", "interface.", "use.", "details."),
    (1, 4): ("dependency injection,", "automated testing."),
    (1, 10): ("locality.",),
    (1, 15): ("internal state.", "one thread,"),
    (2, 6): ("hold data.",),
    (2, 7): ("same type.", "restricted hierarchy"),
    (2, 8): ("singleton.",),
    (2, 16): ("instantiated.",),
    (3, 2): ("a Service", "an IBinder.", "is bound.", "started it"),
    (3, 10): ("none.", "automatically,"),
    (3, 15): ("complexity.",),
    (4, 4): ("stable value.", "is recreated"),
    (5, 1): ("parallel loading.",),
    (5, 11): ("between coroutines.",),
    (5, 23): ("lifecycle state.",),
    (6, 1): ("data orchestration.",),
    (6, 3): ("a snackbar.",),
    (6, 8): ("most screens.",),
    (6, 9): ("No.",),
    (6, 10): ("New State.", "pure function,"),
    (6, 12): ("it.copy(...) }.",),
    (6, 13): ("stable abstractions.",),
    (6, 14): ("dependency direction,", "and reuse.", "shared contracts;"),
    (7, 2): ("or method.", "itself,"),
    (8, 1): ("a server.",),
    (10, 3): ("and error handling.", "write code and tests,"),
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def chapter_dir(item: preparation.Segment) -> Path:
    return OUTPUT_ROOT / f"{item.chapter:02d}-en-{item.chapter_slug}"


def read_manifest() -> tuple[dict[str, Any], list[preparation.Segment]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if (manifest.get("schema"), manifest.get("collection"), manifest.get("language")) != (1, "shorts", "en"):
        raise ValueError("Unexpected English Shorts manifest")
    if manifest["source_sha256"] != preparation.sha256(preparation.SOURCE):
        raise ValueError("Source changed since TTS preparation")
    expected = preparation.build_segments() + answer_preparation.build_answers()
    if manifest["segments"] != [asdict(item) for item in expected]:
        raise ValueError("Prepared segments no longer match the source")
    items = [preparation.Segment(**item) for item in manifest["segments"]]
    if len(items) != 271 or len(manifest["batches"]) != 31:
        raise ValueError("Expected 271 segments in 31 batches")
    return manifest, items


def ordered_items(items: list[preparation.Segment], chapter: int) -> list[preparation.Segment]:
    return sorted(
        (item for item in items if item.chapter == chapter),
        key=lambda item: 0 if item.kind == "title" else item.ordinal * 2 + (item.kind == "answer"),
    )


def cue_parts(item: preparation.Segment) -> list[str]:
    if item.kind != "answer":
        return [item.canonical_text]
    endings = CUE_ENDINGS.get((item.chapter, item.ordinal))
    if endings is None:
        return role_audio.cue_parts(item.canonical_text)
    source = re.sub(r"\s+", " ", item.canonical_text).strip()
    result: list[str] = []
    cursor = 0
    for ending in endings:
        position = source.find(ending, cursor)
        if position < 0:
            raise ValueError(f"Cue marker not found in {item.id}: {ending!r}")
        end = position + len(ending)
        result.append(source[cursor:end].strip())
        cursor = end
    result.append(source[cursor:].strip())
    if any(not part for part in result):
        raise ValueError(f"Empty cue in {item.id}")
    if role_audio.normalized_spoken(" ".join(result)) != role_audio.normalized_spoken(source):
        raise ValueError(f"Cue text mismatch in {item.id}")
    return result


def validate_cue_plan(items: list[preparation.Segment]) -> None:
    ru_items = {
        (item.chapter, item.ordinal): item
        for item in role_audio.build_segments() if item.kind == "answer"
    }
    answer_keys = {(item.chapter, item.ordinal) for item in items if item.kind == "answer"}
    if not set(CUE_ENDINGS).issubset(answer_keys):
        raise ValueError("Cue override refers to an absent answer")
    for item in items:
        if item.kind != "answer":
            continue
        actual = len(cue_parts(item))
        expected = len(role_audio.cue_parts(ru_items[(item.chapter, item.ordinal)].canonical_text))
        if actual != expected:
            raise ValueError(f"Cue count differs from Russian for {item.id}: {actual} != {expected}")
    for chapter, slug in preparation.CHAPTER_CONFIG.values():
        if chapter == preparation.PROTECTED_CHAPTER:
            continue
        expected = sum(len(cue_parts(item)) for item in ordered_items(items, chapter))
        ru_srt = ROOT / f"docs/assets/audio/shorts/ru/{chapter:02d}-ru-shorts-{slug}.srt"
        actual = len(ru_srt.read_text(encoding="utf-8").strip().split("\n\n"))
        if actual != expected:
            raise ValueError(f"Chapter {chapter:02d}: {expected} English cues vs {actual} Russian cues")


def validate_synthesis(manifest: dict[str, Any], items: list[preparation.Segment]) -> None:
    lookup = {item.id: item for item in items}
    assigned: list[str] = []
    for batch in manifest["batches"]:
        stem = batch["id"]
        media = preparation.SYNTHESIS_DIR / f"{stem}.mp3"
        metadata_path = preparation.SYNTHESIS_DIR / f"{stem}.boundaries.json"
        text_path = preparation.BATCHES_DIR / f"{stem}.txt"
        for path in (media, metadata_path, text_path):
            if not path.is_file() or path.stat().st_size == 0:
                raise FileNotFoundError(f"Missing or empty synthesis artifact: {path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        text = text_path.read_text(encoding="utf-8")
        if metadata.get("source_sha256") != sha256_text(text):
            raise ValueError(f"Stale synthesis metadata: {stem}")
        if metadata.get("voice") != batch["voice"] or metadata.get("boundary_type") != "WordBoundary":
            raise ValueError(f"Unexpected TTS voice or boundary type: {stem}")
        if any(metadata.get(key) != manifest["settings"][key] for key in ("rate", "volume", "pitch")):
            raise ValueError(f"Unexpected TTS settings: {stem}")
        boundaries = metadata["boundaries"]
        if role_audio.normalized_spoken("".join(value["text"] for value in boundaries)) != role_audio.normalized_spoken(text):
            raise ValueError(f"Word boundaries do not reconstruct batch text: {stem}")
        batch_items = [lookup[id_] for id_ in batch["segment_ids"]]
        role_audio.align_boundaries([role_audio.Segment(**{**asdict(item), "batch": stem}) for item in batch_items], boundaries)
        assigned.extend(batch["segment_ids"])
    if len(assigned) != len(items) or set(assigned) != set(lookup):
        raise ValueError("Batch segment coverage differs from manifest")


def split_requests(manifest: dict[str, Any], items: list[preparation.Segment]) -> None:
    lookup = {item.id: item for item in items}
    chapter_entries: dict[int, list[dict[str, Any]]] = {}
    for batch in manifest["batches"]:
        stem = batch["id"]
        media = preparation.SYNTHESIS_DIR / f"{stem}.mp3"
        metadata = json.loads((preparation.SYNTHESIS_DIR / f"{stem}.boundaries.json").read_text(encoding="utf-8"))
        boundaries = metadata["boundaries"]
        batch_items = [lookup[id_] for id_ in batch["segment_ids"]]
        align_items = [role_audio.Segment(**{**asdict(item), "batch": stem}) for item in batch_items]
        positions = role_audio.align_boundaries(align_items, boundaries)
        starts = [role_audio.seconds_from_ticks(boundaries[first]["offset"]) for first, _ in positions]
        ends = [role_audio.seconds_from_ticks(boundaries[last]["offset"] + boundaries[last]["duration"]) for _, last in positions]
        cuts = [0.0] + [(end + start) / 2 if start >= end else start for end, start in zip(ends, starts[1:])]
        cut_ends = cuts[1:] + [role_audio.media_duration(media)]
        for item, (first, last), cut_start, cut_end in zip(batch_items, positions, cuts, cut_ends):
            directory = chapter_dir(item)
            directory.mkdir(parents=True, exist_ok=True)
            output = directory / f"{item.output_stem}.mp3"
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{cut_start:.6f}",
                "-t", f"{cut_end - cut_start:.6f}", "-i", str(media), "-c:a", "copy", str(output),
            ], check=True)
            local_boundaries = [{
                **boundary,
                "local_offset": role_audio.seconds_from_ticks(boundary["offset"]) - cut_start,
                "local_duration": role_audio.seconds_from_ticks(boundary["duration"]),
            } for boundary in boundaries[first:last + 1]]
            entry = {
                "id": item.id, "file": output.name, "batch": stem,
                "cut_start": cut_start, "cut_end": cut_end,
                "duration": role_audio.media_duration(output), "boundaries": local_boundaries,
            }
            (directory / f"{item.output_stem}.md").write_text("\n".join([
                f"# {item.id}", "", f"- Source: `{manifest['source']}` - `{item.chapter_title}`",
                f"- Kind: `{item.kind}`", f"- Voice: `{item.voice}`", f"- Batch: `{stem}`",
                f"- Batch cut: `{cut_start:.3f}-{cut_end:.3f}`", "", "## Canonical text", "",
                item.canonical_text, "", "## TTS text", "", item.tts_text, "",
            ]), encoding="utf-8")
            chapter_entries.setdefault(item.chapter, []).append(entry)
        print(f"SPLIT {stem}: {len(batch_items)} segments", flush=True)
    for chapter, entries in chapter_entries.items():
        order = {item.id: index for index, item in enumerate(ordered_items(items, chapter))}
        entries.sort(key=lambda entry: order[entry["id"]])
        directory = chapter_dir(ordered_items(items, chapter)[0])
        (directory / "segments.json").write_text(
            json.dumps({"schema": 1, "segments": entries}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def assemble_chapter(items: list[preparation.Segment]) -> None:
    directory = chapter_dir(items[0])
    inputs = [directory / f"{item.output_stem}.mp3" for item in items]
    if any(not path.is_file() or path.stat().st_size == 0 for path in inputs):
        raise FileNotFoundError(f"Missing split segment in {directory}")
    track = f"{items[0].chapter:02d}-en-shorts-{items[0].chapter_slug}.mp3"
    output = directory / track
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
    command.extend(["-filter_complex", ";".join(filters), "-map", "[out]", "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "48k", str(output)])
    subprocess.run(command, check=True)
    offset = 0.0
    timing_segments = []
    rows = []
    for index, (item, path) in enumerate(zip(items, inputs)):
        duration = role_audio.media_duration(path)
        end = offset + duration
        gap = GAP_SECONDS if index + 1 < len(inputs) else 0.0
        timing_segments.append({"id": item.id, "file": path.name, "duration": duration, "track_start": offset, "track_end": end, "gap_after": gap})
        rows.append(f"| `{item.id}` | `{path.name}` | `{item.voice}` | {duration:.3f} | {offset:.3f}-{end:.3f} | {gap:.3f} |")
        offset = end + gap
    final_duration = role_audio.media_duration(output)
    (directory / "timing.json").write_text(json.dumps({
        "schema": 1, "gap": GAP_SECONDS, "track": track, "segments": timing_segments,
        "duration": final_duration,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (directory / "timing.md").write_text("\n".join([
        f"# Timing: {items[0].chapter:02d}-en-{items[0].chapter_slug}", "",
        f"- Source: `docs/shorts.md` - `{items[0].chapter_title}`",
        f"- Assembled track: `{track}`", f"- Duration: `{role_audio.format_clock(final_duration)}`",
        f"- Gap between segments: `{GAP_SECONDS:.3f} s`", "", "## Segments", "",
        "| ID | File | Voice | Duration | Track start-end | Gap after |",
        "| --- | --- | --- | ---: | --- | ---: |", *rows, "",
    ]), encoding="utf-8")
    print(f"ASSEMBLED {items[0].chapter:02d}: {track} ({final_duration:.3f}s)", flush=True)


def make_subtitles(items: list[preparation.Segment]) -> None:
    directory = chapter_dir(items[0])
    split = json.loads((directory / "segments.json").read_text(encoding="utf-8"))
    timing = json.loads((directory / "timing.json").read_text(encoding="utf-8"))
    split_lookup = {value["id"]: value for value in split["segments"]}
    timing_lookup = {value["id"]: value for value in timing["segments"]}
    cues = []
    for item in items:
        entry = split_lookup[item.id]
        boundaries = entry["boundaries"]
        parts = cue_parts(item)
        align_items = [role_audio.Segment(**{
            **asdict(item), "id": f"{item.id}-cue-{index:02d}",
            "canonical_text": text, "tts_text": text, "batch": entry["batch"],
        }) for index, text in enumerate(parts, start=1)]
        positions = role_audio.align_boundaries(align_items, boundaries)
        track_start = timing_lookup[item.id]["track_start"]
        track_end = min(timing_lookup[item.id]["track_end"], timing["duration"])
        for text, (first, last) in zip(parts, positions):
            start = max(track_start, track_start + boundaries[first]["local_offset"])
            end = min(track_end, track_start + boundaries[last]["local_offset"] + boundaries[last]["local_duration"])
            if end <= start:
                raise ValueError(f"Non-positive cue in {item.id}")
            cues.append((role_audio.styled_subtitle_text(item.kind, text), start, end))
    blocks = [
        f"{index}\n{role_audio.format_srt_time(start)} --> {role_audio.format_srt_time(end)}\n{text}"
        for index, (text, start, end) in enumerate(cues, start=1)
    ]
    output = directory / f"{items[0].chapter:02d}-en-shorts-{items[0].chapter_slug}.srt"
    output.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    output.with_suffix(".srt.json").write_text(
        json.dumps({"schema": 1, "cues": len(cues)}, indent=2) + "\n", encoding="utf-8"
    )
    print(f"SUBTITLES {items[0].chapter:02d}: {len(cues)} cues", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="validate input artifacts and cue plan without writing outputs")
    args = parser.parse_args()
    manifest, items = read_manifest()
    validate_cue_plan(items)
    validate_synthesis(manifest, items)
    print("Validated 31 TTS packages, 271 segments, and Russian-matched cue plan", flush=True)
    if args.check_only:
        return
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        parser.error("ffmpeg and ffprobe are required")
    split_requests(manifest, items)
    for chapter, _ in preparation.CHAPTER_CONFIG.values():
        if chapter == preparation.PROTECTED_CHAPTER:
            continue
        chapter_items = ordered_items(items, chapter)
        assemble_chapter(chapter_items)
        make_subtitles(chapter_items)
    print("Complete: nine new English role tracks and subtitles", flush=True)


if __name__ == "__main__":
    main()
