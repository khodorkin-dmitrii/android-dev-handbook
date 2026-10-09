"""Prepare and build role-based Russian Shorts audio in explicit phases.

The default scope intentionally excludes chapter 09. Network access happens only
for the ``synthesize`` command without ``--dry-run``.
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict, dataclass
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Iterable

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/shorts.ru.md"
PRONUNCIATION = ROOT / "build/audio/pronunciation-ru.json"
WORK_DIR = ROOT / "build/audio/shorts-ru/role-ru"
CHAPTERS_DIR = ROOT / "build/audio/shorts-ru"
MANIFEST = WORK_DIR / "manifest.json"
PROTECTED_CHAPTER = 9
EXPECTED_ACTIVE_CHAPTERS = 9
EXPECTED_ACTIVE_QUESTIONS = 131

TITLE_VOICE = "en-US-AndrewMultilingualNeural"
QUESTION_VOICE = "ru-RU-SvetlanaNeural"
ANSWER_VOICE = "ru-RU-DmitryNeural"
RATE = "+25%"
VOLUME = "+0%"
PITCH = "+0Hz"
GAP_SECONDS = 0.8

CHAPTER_CONFIG = {
    "Computer Science": (1, "computer-science"),
    "Kotlin": (2, "kotlin"),
    "Android basics": (3, "android-basics"),
    "Jetpack Compose": (4, "jetpack-compose"),
    "Coroutines и Flow": (5, "coroutines-flow"),
    "Архитектура": (6, "architecture"),
    "Dependency Injection": (7, "dependency-injection"),
    "Networking": (8, "networking"),
    "Libraries and Build": (9, "libraries-and-build"),
    "Testing": (10, "testing"),
}


@dataclass(frozen=True)
class Segment:
    id: str
    chapter: int
    chapter_title: str
    chapter_slug: str
    kind: str
    ordinal: int
    role: str
    voice: str
    canonical_text: str
    tts_text: str
    batch: str
    output_stem: str


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_files(paths: Iterable[Path], extra: str = "") -> str:
    digest = hashlib.sha256(extra.encode("utf-8"))
    for path in paths:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def clean_inline(token: Any) -> str:
    parts: list[str] = []
    for child in token.children or []:
        if child.type in {"text", "code_inline"}:
            parts.append(child.content)
        elif child.type in {"softbreak", "hardbreak"}:
            parts.append(" ")
    text = re.sub(r"(?:https?://|ftp://|www\.)\S+", "", "".join(parts))
    return re.sub(r"\s+", " ", text).strip()


def mapped_sections(markdown: str, level: int) -> list[tuple[str, str]]:
    """Split Markdown at parser-confirmed headings of one level."""
    lines = markdown.splitlines(keepends=True)
    tokens = MarkdownIt().parse(markdown)
    tag = f"h{level}"
    headings: list[tuple[str, int]] = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == tag:
            if token.map is None:
                raise ValueError(f"{tag} heading has no source position")
            title = clean_inline(tokens[index + 1])
            if not title:
                raise ValueError(f"{tag} heading has no visible title")
            headings.append((title, token.map[0]))
    return [
        (
            title,
            "".join(
                lines[
                    start : headings[index + 1][1]
                    if index + 1 < len(headings)
                    else len(lines)
                ]
            ),
        )
        for index, (title, start) in enumerate(headings)
    ]


def answer_text(question_markdown: str) -> str:
    values: list[str] = []
    heading: str | None = None
    for token in MarkdownIt().parse(question_markdown):
        if token.type == "heading_open":
            heading = token.tag
        elif token.type == "heading_close":
            heading = None
        elif token.type == "inline" and heading != "h3":
            value = clean_inline(token)
            if value:
                values.append(value)
    if not values:
        raise ValueError("Question has no visible answer")
    return "\n\n".join(values)


def read_pronunciation(path: Path = PRONUNCIATION) -> dict[str, str]:
    mapping = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError(f"Invalid pronunciation map: {path}")
    folded: dict[str, str] = {}
    for term, spoken in mapping.items():
        if not isinstance(term, str) or not term or not isinstance(spoken, str) or not spoken:
            raise ValueError(f"Invalid pronunciation entry in {path}")
        key = term.casefold()
        if key in folded:
            raise ValueError(f"Duplicate pronunciation term ignoring case: {term}")
        folded[key] = spoken
    return mapping


def apply_pronunciation(text: str, mapping: dict[str, str]) -> str:
    folded = {key.casefold(): value for key, value in mapping.items()}
    alternatives = "|".join(
        re.escape(term) for term in sorted(mapping, key=len, reverse=True)
    )
    pattern = re.compile(
        r"(?<![A-Za-z0-9_])(?:" + alternatives + r")(?![A-Za-z0-9_])",
        flags=re.IGNORECASE,
    )
    return pattern.sub(lambda match: folded[match.group().casefold()], text)


def ensure_terminal_punctuation(text: str) -> str:
    value = text.rstrip()
    return value if value.endswith((".", "!", "?", ":", ";")) else value + "."


def output_stem(kind: str, ordinal: int, role: str) -> str:
    if kind == "title":
        return f"01-title-{role}"
    position = ordinal * 2 if kind == "question" else ordinal * 2 + 1
    return f"{position:02d}-{kind}-{ordinal:02d}-{role}"


def build_segments(include_protected: bool = False) -> list[Segment]:
    markdown = SOURCE.read_text(encoding="utf-8")
    mapping = read_pronunciation()
    chapters = mapped_sections(markdown, 2)
    actual_titles = [title for title, _ in chapters]
    if set(actual_titles) != set(CHAPTER_CONFIG):
        missing = sorted(set(CHAPTER_CONFIG) - set(actual_titles))
        extra = sorted(set(actual_titles) - set(CHAPTER_CONFIG))
        raise ValueError(f"Chapter mapping mismatch; missing={missing}, extra={extra}")

    segments: list[Segment] = []
    for title, chapter_markdown in chapters:
        number, slug = CHAPTER_CONFIG[title]
        if number == PROTECTED_CHAPTER and not include_protected:
            continue
        title_id = f"{number:02d}-title"
        title_text = ensure_terminal_punctuation(title)
        segments.append(
            Segment(
                id=title_id,
                chapter=number,
                chapter_title=title,
                chapter_slug=slug,
                kind="title",
                ordinal=0,
                role="andrew",
                voice=TITLE_VOICE,
                canonical_text=title,
                tts_text=title_text,
                batch="titles",
                output_stem=output_stem("title", 0, "andrew"),
            )
        )
        questions = mapped_sections(chapter_markdown, 3)
        if not questions:
            raise ValueError(f"Chapter {number:02d} has no questions")
        for ordinal, (question, question_markdown) in enumerate(questions, start=1):
            answer = answer_text(question_markdown)
            question_tts = apply_pronunciation(question, mapping)
            answer_tts = apply_pronunciation(answer, mapping)
            for kind, role, voice, canonical, tts, batch in (
                (
                    "question",
                    "svetlana",
                    QUESTION_VOICE,
                    question,
                    question_tts,
                    "questions",
                ),
                (
                    "answer",
                    "dmitry",
                    ANSWER_VOICE,
                    answer,
                    answer_tts,
                    f"answers-{number:02d}",
                ),
            ):
                segments.append(
                    Segment(
                        id=f"{number:02d}-{kind}-{ordinal:02d}",
                        chapter=number,
                        chapter_title=title,
                        chapter_slug=slug,
                        kind=kind,
                        ordinal=ordinal,
                        role=role,
                        voice=voice,
                        canonical_text=canonical,
                        tts_text=tts,
                        batch=batch,
                        output_stem=output_stem(kind, ordinal, role),
                    )
                )
    return segments


def grouped_batches(segments: Iterable[Segment]) -> dict[str, list[Segment]]:
    batches: dict[str, list[Segment]] = {}
    for segment in segments:
        batches.setdefault(segment.batch, []).append(segment)
    order = {"titles": 0, "questions": 1}
    return dict(sorted(batches.items(), key=lambda item: (order.get(item[0], 2), item[0])))


def batch_text(segments: list[Segment]) -> str:
    return "\n\n".join(ensure_terminal_punctuation(item.tts_text) for item in segments) + "\n"


def build_manifest(include_protected: bool = False) -> dict[str, Any]:
    segments = build_segments(include_protected)
    batches = grouped_batches(segments)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    pronunciation_hash = hashlib.sha256(PRONUNCIATION.read_bytes()).hexdigest()
    return {
        "schema": 1,
        "language": "ru",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": source_hash,
        "pronunciation": PRONUNCIATION.relative_to(ROOT).as_posix(),
        "pronunciation_sha256": pronunciation_hash,
        "protected_chapter_included": include_protected,
        "settings": {"rate": RATE, "volume": VOLUME, "pitch": PITCH, "gap": GAP_SECONDS},
        "segments": [asdict(segment) for segment in segments],
        "batches": [
            {
                "id": batch_id,
                "voice": items[0].voice,
                "segment_ids": [item.id for item in items],
                "text_sha256": sha256_text(batch_text(items)),
                "characters": len(batch_text(items)),
            }
            for batch_id, items in batches.items()
        ],
    }


def manifest_segments(data: dict[str, Any]) -> list[Segment]:
    return [Segment(**value) for value in data["segments"]]


def manifest_markdown(data: dict[str, Any]) -> str:
    segments = manifest_segments(data)
    batches = grouped_batches(segments)
    chapter_numbers = sorted({item.chapter for item in segments})
    question_count = sum(item.kind == "question" for item in segments)
    lines = [
        "# Russian role-audio plan",
        "",
        f"- Source: `{data['source']}`",
        f"- Source SHA-256: `{data['source_sha256']}`",
        f"- Pronunciation SHA-256: `{data['pronunciation_sha256']}`",
        f"- Chapters: {', '.join(f'{value:02d}' for value in chapter_numbers)}",
        f"- Questions and answers: {question_count}",
        f"- Protected chapter 09 included: `{str(data['protected_chapter_included']).lower()}`",
        "",
        "## Batches",
        "",
        "| Batch | Voice | Segments | Characters |",
        "| --- | --- | ---: | ---: |",
    ]
    batch_lookup = {item["id"]: item for item in data["batches"]}
    for batch_id, items in batches.items():
        batch = batch_lookup[batch_id]
        lines.append(
            f"| `{batch_id}` | `{items[0].voice}` | {len(items)} | {batch['characters']} |"
        )
    lines.extend(["", "## Chapters", ""])
    for chapter in chapter_numbers:
        items = [item for item in segments if item.chapter == chapter]
        lines.extend(
            [
                f"### {chapter:02d}. {items[0].chapter_title}",
                "",
                f"- Directory: `build/audio/shorts-ru/{chapter:02d}-ru-{items[0].chapter_slug}/`",
                f"- Questions: {sum(item.kind == 'question' for item in items)}",
                "",
            ]
        )
    return "\n".join(lines)


def batch_markdown(batch_id: str, items: list[Segment]) -> str:
    lines = [
        f"# Batch: {batch_id}",
        "",
        f"- Voice: `{items[0].voice}`",
        f"- Rate / volume / pitch: `{RATE}` / `{VOLUME}` / `{PITCH}`",
        f"- Segments: {len(items)}",
        "",
    ]
    for item in items:
        lines.extend(
            [
                f"## {item.id}",
                "",
                f"- Chapter: `{item.chapter:02d}`",
                f"- Kind: `{item.kind}`",
                "",
                item.tts_text,
                "",
            ]
        )
    return "\n".join(lines)


def write_prepared(data: dict[str, Any]) -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    batches_dir = WORK_DIR / "batches"
    batches_dir.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (WORK_DIR / "plan.md").write_text(manifest_markdown(data) + "\n", encoding="utf-8")
    for batch_id, items in grouped_batches(manifest_segments(data)).items():
        (batches_dir / f"{batch_id}.txt").write_text(batch_text(items), encoding="utf-8")
        (batches_dir / f"{batch_id}.md").write_text(
            batch_markdown(batch_id, items) + "\n", encoding="utf-8"
        )


def load_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"Run prepare first: {MANIFEST}")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema") != 1 or data.get("language") != "ru":
        raise ValueError(f"Unsupported manifest: {MANIFEST}")
    return data


def selected_batches(data: dict[str, Any], group: str, chapters: set[int] | None) -> list[dict[str, Any]]:
    result = []
    for batch in data["batches"]:
        batch_id = batch["id"]
        if group == "shared" and batch_id not in {"titles", "questions"}:
            continue
        if group == "answers" and not batch_id.startswith("answers-"):
            continue
        if chapters and batch_id.startswith("answers-") and int(batch_id[-2:]) not in chapters:
            continue
        result.append(batch)
    return result


def synthesis_fingerprint(batch: dict[str, Any]) -> str:
    value = "\n".join(
        [batch["text_sha256"], batch["voice"], RATE, VOLUME, PITCH, "WordBoundary"]
    )
    return sha256_text(value)


async def synthesize_once(batch: dict[str, Any]) -> tuple[bytes, list[dict[str, Any]]]:
    import edge_tts

    text_path = WORK_DIR / "batches" / f"{batch['id']}.txt"
    communicate = edge_tts.Communicate(
        text_path.read_text(encoding="utf-8"),
        batch["voice"],
        rate=RATE,
        volume=VOLUME,
        pitch=PITCH,
        boundary="WordBoundary",
    )
    audio = bytearray()
    boundaries: list[dict[str, Any]] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            boundaries.append(
                {
                    "offset": chunk["offset"],
                    "duration": chunk["duration"],
                    "text": chunk["text"],
                }
            )
    if not audio or not boundaries:
        raise RuntimeError("The service returned incomplete audio or no word boundaries")
    return bytes(audio), boundaries


async def synthesize_job(batch: dict[str, Any], force: bool) -> bool:
    output_dir = WORK_DIR / "synthesis"
    output_dir.mkdir(parents=True, exist_ok=True)
    media = output_dir / f"{batch['id']}.mp3"
    metadata = output_dir / f"{batch['id']}.boundaries.json"
    fingerprint = synthesis_fingerprint(batch)
    if not force and media.exists() and metadata.exists():
        previous = json.loads(metadata.read_text(encoding="utf-8"))
        if previous.get("fingerprint") == fingerprint and previous.get("boundaries"):
            print(f"SKIP {batch['id']}: cached")
            return False

    last_error: Exception | None = None
    for attempt in range(2):
        if attempt:
            await asyncio.sleep(5)
        try:
            audio, boundaries = await synthesize_once(batch)
            media_part = media.with_suffix(".mp3.part")
            metadata_part = metadata.with_suffix(".json.part")
            media_part.write_bytes(audio)
            payload = {
                "schema": 1,
                "batch": batch["id"],
                "fingerprint": fingerprint,
                "voice": batch["voice"],
                "rate": RATE,
                "volume": VOLUME,
                "pitch": PITCH,
                "boundary_type": "WordBoundary",
                "boundaries": boundaries,
            }
            metadata_part.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            media_part.replace(media)
            metadata_part.replace(metadata)
            print(f"OK   {batch['id']}: {len(audio)} bytes, {len(boundaries)} boundaries")
            return True
        except (Exception, KeyboardInterrupt) as error:
            last_error = error
            if isinstance(error, KeyboardInterrupt):
                raise
    raise RuntimeError(f"Synthesis failed twice for {batch['id']}: {last_error}")


async def run_synthesis(jobs: list[dict[str, Any]], force: bool, delay_seconds: float) -> None:
    generated = False
    for batch in jobs:
        if generated:
            print(f"WAIT {delay_seconds:.0f} seconds before the next batch", flush=True)
            await asyncio.sleep(delay_seconds)
        generated = await synthesize_job(batch, force) or generated


def normalized_spoken(value: str) -> str:
    return "".join(character.casefold() for character in value if character.isalnum())


def align_boundaries(items: list[Segment], boundaries: list[dict[str, Any]]) -> list[tuple[int, int]]:
    useful = [(index, normalized_spoken(item["text"])) for index, item in enumerate(boundaries)]
    useful = [(index, text) for index, text in useful if text]
    positions: list[tuple[int, int]] = []
    cursor = 0
    for segment in items:
        expected = normalized_spoken(ensure_terminal_punctuation(segment.tts_text))
        assembled = ""
        first: int | None = None
        last: int | None = None
        while cursor < len(useful) and len(assembled) < len(expected):
            boundary_index, text = useful[cursor]
            if first is None:
                first = boundary_index
            assembled += text
            last = boundary_index
            cursor += 1
        if assembled != expected or first is None or last is None:
            raise ValueError(
                f"Cannot align WordBoundary data for {segment.id}: "
                f"expected {len(expected)} normalized characters, got {len(assembled)}"
            )
        positions.append((first, last))
    if cursor != len(useful):
        raise ValueError(f"Unassigned WordBoundary entries: {len(useful) - cursor}")
    return positions


def seconds_from_ticks(value: float) -> float:
    return value / 10_000_000


def command_output(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def media_duration(path: Path) -> float:
    return float(
        command_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ]
        )
    )


def chapter_directory(segment: Segment) -> Path:
    return CHAPTERS_DIR / f"{segment.chapter:02d}-ru-{segment.chapter_slug}"


def segment_markdown(segment: Segment, split_data: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {segment.id}",
            "",
            f"- Source: `docs/shorts.ru.md` - `{segment.chapter_title}`",
            f"- Kind: `{segment.kind}`",
            f"- Voice: `{segment.voice}`",
            f"- Rate / volume / pitch: `{RATE}` / `{VOLUME}` / `{PITCH}`",
            f"- Batch: `{segment.batch}`",
            f"- Batch cut: `{split_data['cut_start']:.3f}-{split_data['cut_end']:.3f}`",
            "",
            "## Canonical text",
            "",
            segment.canonical_text,
            "",
            "## TTS text",
            "",
            segment.tts_text,
            "",
        ]
    )


def split_batch(batch: dict[str, Any], items: list[Segment], force: bool) -> None:
    synthesis_dir = WORK_DIR / "synthesis"
    media = synthesis_dir / f"{batch['id']}.mp3"
    metadata_path = synthesis_dir / f"{batch['id']}.boundaries.json"
    if not media.exists() or not metadata_path.exists():
        raise FileNotFoundError(f"Missing synthesis artifacts for {batch['id']}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("fingerprint") != synthesis_fingerprint(batch):
        raise ValueError(f"Stale synthesis metadata for {batch['id']}")
    boundaries = metadata["boundaries"]
    positions = align_boundaries(items, boundaries)
    total_duration = media_duration(media)

    starts = [seconds_from_ticks(boundaries[first]["offset"]) for first, _ in positions]
    ends = [
        seconds_from_ticks(boundaries[last]["offset"] + boundaries[last]["duration"])
        for _, last in positions
    ]
    cut_points = [0.0]
    for previous_end, next_start in zip(ends, starts[1:]):
        cut_points.append((previous_end + next_start) / 2 if next_start >= previous_end else next_start)
    cut_ends = cut_points[1:] + [total_duration]

    by_chapter: dict[int, list[dict[str, Any]]] = {}
    for item, (first, last), cut_start, cut_end in zip(items, positions, cut_points, cut_ends):
        directory = chapter_directory(item)
        directory.mkdir(parents=True, exist_ok=True)
        output = directory / f"{item.output_stem}.mp3"
        chapter_metadata_path = directory / "segments.json"
        existing_lookup: dict[str, dict[str, Any]] = {}
        if chapter_metadata_path.exists():
            existing_payload = json.loads(chapter_metadata_path.read_text(encoding="utf-8"))
            existing_lookup = {value["id"]: value for value in existing_payload["segments"]}
        previous = existing_lookup.get(item.id)
        split_fingerprint = sha256_text(
            "\n".join(
                [
                    synthesis_fingerprint(batch),
                    f"{cut_start:.6f}",
                    f"{cut_end:.6f}",
                    "copy",
                ]
            )
        )
        if force or not output.exists() or not previous or previous.get("fingerprint") != split_fingerprint:
            subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-ss",
                    f"{cut_start:.6f}",
                    "-t",
                    f"{cut_end - cut_start:.6f}",
                    "-i",
                    str(media),
                    "-c:a",
                    "copy",
                    str(output),
                ],
                check=True,
            )
        local_boundaries = []
        for boundary in boundaries[first : last + 1]:
            local_boundaries.append(
                {
                    **boundary,
                    "local_offset": seconds_from_ticks(boundary["offset"]) - cut_start,
                    "local_duration": seconds_from_ticks(boundary["duration"]),
                }
            )
        split_data = {
            "id": item.id,
            "file": output.name,
            "batch": item.batch,
            "fingerprint": split_fingerprint,
            "cut_start": cut_start,
            "cut_end": cut_end,
            "duration": media_duration(output),
            "boundaries": local_boundaries,
        }
        (directory / f"{item.output_stem}.md").write_text(
            segment_markdown(item, split_data), encoding="utf-8"
        )
        by_chapter.setdefault(item.chapter, []).append(split_data)

    for chapter, new_values in by_chapter.items():
        directory = chapter_directory(next(item for item in items if item.chapter == chapter))
        path = directory / "segments.json"
        existing: dict[str, Any] = {"schema": 1, "segments": []}
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
        replacement_ids = {value["id"] for value in new_values}
        merged = [value for value in existing["segments"] if value["id"] not in replacement_ids]
        merged.extend(new_values)
        merged.sort(key=lambda value: next(
            index for index, item in enumerate(manifest_segments(load_manifest())) if item.id == value["id"]
        ))
        existing["segments"] = merged
        path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK   {batch['id']}: split into {len(items)} segments")


def ordered_chapter_segments(segments: list[Segment], chapter: int) -> list[Segment]:
    return sorted(
        (item for item in segments if item.chapter == chapter),
        key=lambda item: (0 if item.kind == "title" else item.ordinal * 2 + (0 if item.kind == "question" else 1)),
    )


def assemble_chapter(items: list[Segment], force: bool) -> None:
    directory = chapter_directory(items[0])
    inputs = [directory / f"{item.output_stem}.mp3" for item in items]
    missing = [path for path in inputs if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing split segment: {missing[0]}")
    output = directory / f"{items[0].chapter:02d}-ru-shorts-{items[0].chapter_slug}.mp3"
    timing_json_path = directory / "timing.json"
    assembly_fingerprint = sha256_files(inputs, extra=f"gap={GAP_SECONDS:.3f};codec=mp3-48k")
    if output.exists() and timing_json_path.exists() and not force and json.loads(
        timing_json_path.read_text(encoding="utf-8")
    ).get("fingerprint") == assembly_fingerprint:
        print(f"SKIP {items[0].chapter:02d}: assembled track exists")
        return
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for path in inputs:
        command.extend(["-i", str(path)])
    labels: list[str] = []
    filters: list[str] = []
    for index in range(len(inputs)):
        label = f"s{index}"
        if index + 1 < len(inputs):
            filters.append(f"[{index}:a]apad=pad_dur={GAP_SECONDS:.3f}[{label}]")
        else:
            filters.append(f"[{index}:a]anull[{label}]")
        labels.append(f"[{label}]")
    filters.append("".join(labels) + f"concat=n={len(inputs)}:v=0:a=1[out]")
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-ar",
            "24000",
            "-ac",
            "1",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "48k",
            str(output),
        ]
    )
    subprocess.run(command, check=True)

    offset = 0.0
    rows = []
    timing_json = {
        "schema": 1,
        "fingerprint": assembly_fingerprint,
        "gap": GAP_SECONDS,
        "track": output.name,
        "segments": [],
    }
    for index, (item, path) in enumerate(zip(items, inputs)):
        duration = media_duration(path)
        end = offset + duration
        gap = GAP_SECONDS if index + 1 < len(items) else 0.0
        rows.append(
            f"| `{item.id}` | `{path.name}` | `{item.voice}` | {duration:.3f} | "
            f"{offset:.3f}-{end:.3f} | {gap:.3f} |"
        )
        timing_json["segments"].append(
            {"id": item.id, "file": path.name, "duration": duration, "track_start": offset, "track_end": end, "gap_after": gap}
        )
        offset = end + gap
    final_duration = media_duration(output)
    timing_json["duration"] = final_duration
    timing_json_path.write_text(
        json.dumps(timing_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    timing_md = [
        f"# Timing: {items[0].chapter:02d}-ru-{items[0].chapter_slug}",
        "",
        f"- Source: `docs/shorts.ru.md` - `{items[0].chapter_title}`",
        f"- Assembled track: `{output.name}`",
        f"- Assembled duration: `{format_clock(final_duration)}`",
        f"- Gap between segments: `{GAP_SECONDS:.3f} s`",
        "",
        "## Segments",
        "",
        "| ID | File | Voice | Duration | Track start-end | Gap after |",
        "| --- | --- | --- | ---: | --- | ---: |",
        *rows,
        "",
    ]
    (directory / "timing.md").write_text("\n".join(timing_md), encoding="utf-8")
    print(f"OK   {items[0].chapter:02d}: {output.name}, {final_duration:.3f} s")


def cue_parts(text: str, limit: int = 120) -> list[str]:
    paragraphs = [value.strip() for value in text.split("\n\n") if value.strip()]
    result: list[str] = []
    for paragraph in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        for sentence in sentences:
            if len(sentence) <= limit:
                result.append(sentence)
                continue
            clauses = re.split(r"(?<=[,;:])\s+", sentence)
            current = ""
            for clause in clauses:
                candidate = f"{current} {clause}".strip()
                if current and len(candidate) > limit:
                    result.append(current)
                    current = clause
                else:
                    current = candidate
            if current:
                result.append(current)
    return result


def align_cues(segment: Segment, split_entry: dict[str, Any], mapping: dict[str, str]) -> list[tuple[str, float, float]]:
    canonical_cues = [segment.canonical_text] if segment.kind != "answer" else cue_parts(segment.canonical_text)
    expected = (
        [segment.tts_text]
        if segment.kind != "answer"
        else [apply_pronunciation(value, mapping) for value in canonical_cues]
    )
    boundaries = split_entry["boundaries"]
    positions = align_boundaries(
        [
            Segment(
                **{
                    **asdict(segment),
                    "id": f"{segment.id}-cue-{index:02d}",
                    "canonical_text": canonical,
                    "tts_text": spoken,
                }
            )
            for index, (canonical, spoken) in enumerate(zip(canonical_cues, expected), start=1)
        ],
        boundaries,
    )
    result = []
    for canonical, (first, last) in zip(canonical_cues, positions):
        start = boundaries[first]["local_offset"]
        end = boundaries[last]["local_offset"] + boundaries[last]["local_duration"]
        result.append((canonical, start, end))
    return result


def format_srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_clock(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    value = timedelta(milliseconds=milliseconds)
    total_seconds = int(value.total_seconds())
    millis = milliseconds % 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def styled_subtitle_text(kind: str, text: str) -> str:
    if kind == "title":
        return f"<u>{text}</u>"
    if kind == "question":
        return f"<i>{text}</i>"
    return text


def build_subtitles(items: list[Segment], force: bool) -> None:
    directory = chapter_directory(items[0])
    output = directory / f"{items[0].chapter:02d}-ru-shorts-{items[0].chapter_slug}.srt"
    metadata_output = output.with_suffix(".srt.json")
    subtitle_fingerprint = sha256_files(
        [directory / "segments.json", directory / "timing.json", MANIFEST],
        extra="subtitle-schema=2",
    )
    if output.exists() and metadata_output.exists() and not force and json.loads(
        metadata_output.read_text(encoding="utf-8")
    ).get("fingerprint") == subtitle_fingerprint:
        print(f"SKIP {items[0].chapter:02d}: subtitle file exists")
        return
    split_payload = json.loads((directory / "segments.json").read_text(encoding="utf-8"))
    timing_payload = json.loads((directory / "timing.json").read_text(encoding="utf-8"))
    split_lookup = {value["id"]: value for value in split_payload["segments"]}
    timing_lookup = {value["id"]: value for value in timing_payload["segments"]}
    mapping = read_pronunciation()
    cues: list[tuple[str, float, float]] = []
    for item in items:
        timing_entry = timing_lookup[item.id]
        base = timing_entry["track_start"]
        segment_end = min(timing_entry["track_end"], timing_payload["duration"])
        for text, start, end in align_cues(item, split_lookup[item.id], mapping):
            cue_start = max(base, base + start)
            cue_end = min(segment_end, base + end)
            if cue_end <= cue_start:
                raise ValueError(f"Non-positive subtitle cue after clamping: {item.id}")
            cues.append((styled_subtitle_text(item.kind, text), cue_start, cue_end))
    blocks = []
    for index, (text, start, end) in enumerate(cues, start=1):
        blocks.append(f"{index}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}")
    output.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    metadata_output.write_text(
        json.dumps(
            {"schema": 1, "fingerprint": subtitle_fingerprint, "cues": len(cues)},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"OK   {items[0].chapter:02d}: {len(cues)} subtitle cues")


def validate_prepared(data: dict[str, Any]) -> None:
    segments = manifest_segments(data)
    chapters = {item.chapter for item in segments}
    questions = [item for item in segments if item.kind == "question"]
    answers = [item for item in segments if item.kind == "answer"]
    if not data["protected_chapter_included"]:
        if PROTECTED_CHAPTER in chapters:
            raise ValueError("Protected chapter 09 unexpectedly appears in the manifest")
        if len(chapters) != EXPECTED_ACTIVE_CHAPTERS or len(questions) != EXPECTED_ACTIVE_QUESTIONS:
            raise ValueError(
                f"Expected {EXPECTED_ACTIVE_CHAPTERS} chapters and {EXPECTED_ACTIVE_QUESTIONS} questions; "
                f"got {len(chapters)} and {len(questions)}"
            )
    if len(questions) != len(answers):
        raise ValueError("Question and answer counts differ")
    if len({item.id for item in segments}) != len(segments):
        raise ValueError("Duplicate segment ids")
    expected_batches = 2 + len(chapters)
    if len(data["batches"]) != expected_batches:
        raise ValueError(f"Expected {expected_batches} batches, got {len(data['batches'])}")


def parse_chapters_arg(values: list[str] | None) -> set[int] | None:
    if not values:
        return None
    result = {int(value) for value in values}
    if PROTECTED_CHAPTER in result:
        raise ValueError("Chapter 09 is protected and is not present in the default manifest")
    return result


def require_programs(*names: str) -> None:
    missing = [name for name in names if shutil.which(name) is None]
    if missing:
        raise RuntimeError(f"Required program is not available: {', '.join(missing)}")


def command_prepare(args: argparse.Namespace) -> None:
    data = build_manifest(args.include_protected)
    validate_prepared(data)
    segments = manifest_segments(data)
    chapters = {item.chapter for item in segments}
    questions = sum(item.kind == "question" for item in segments)
    print(f"Prepared model: {len(chapters)} chapters, {questions} questions, {len(data['batches'])} batches")
    for batch in data["batches"]:
        print(f"  {batch['id']}: {len(batch['segment_ids'])} segments, {batch['characters']} characters")
    if args.dry_run:
        print("DRY RUN: no files written")
        return
    write_prepared(data)
    print(f"Manifest: {MANIFEST}")


def command_synthesize(args: argparse.Namespace) -> None:
    if args.delay_seconds < 0:
        raise ValueError("--delay-seconds must be zero or greater")
    data = load_manifest()
    validate_prepared(data)
    chapters = parse_chapters_arg(args.chapter)
    jobs = selected_batches(data, args.group, chapters)
    if not jobs:
        raise ValueError("No synthesis jobs selected")
    for batch in jobs:
        cached = False
        metadata = WORK_DIR / "synthesis" / f"{batch['id']}.boundaries.json"
        media = WORK_DIR / "synthesis" / f"{batch['id']}.mp3"
        if metadata.exists() and media.exists() and not args.force:
            cached = json.loads(metadata.read_text(encoding="utf-8")).get("fingerprint") == synthesis_fingerprint(batch)
        print(f"{'CACHE' if cached else 'CALL '} {batch['id']}: {batch['characters']} characters")
    if args.dry_run:
        print("DRY RUN: edge-tts was not contacted")
        return
    asyncio.run(run_synthesis(jobs, args.force, args.delay_seconds))


def command_split(args: argparse.Namespace) -> None:
    require_programs("ffmpeg", "ffprobe")
    data = load_manifest()
    segments = manifest_segments(data)
    lookup = {item.id: item for item in segments}
    chapters = parse_chapters_arg(args.chapter)
    for batch in selected_batches(data, args.group, chapters):
        items = [lookup[value] for value in batch["segment_ids"]]
        if args.dry_run:
            print(f"SPLIT {batch['id']}: {len(items)} segments")
        else:
            split_batch(batch, items, args.force)
    if args.dry_run:
        print("DRY RUN: no media files written")


def command_assemble(args: argparse.Namespace) -> None:
    require_programs("ffmpeg", "ffprobe")
    data = load_manifest()
    segments = manifest_segments(data)
    selected = parse_chapters_arg(args.chapter) or {item.chapter for item in segments}
    for chapter in sorted(selected):
        items = ordered_chapter_segments(segments, chapter)
        if not items:
            raise ValueError(f"Chapter {chapter:02d} is not in the manifest")
        if args.dry_run:
            print(f"ASSEMBLE {chapter:02d}: {len(items)} segments")
        else:
            assemble_chapter(items, args.force)
    if args.dry_run:
        print("DRY RUN: no tracks written")


def command_subtitles(args: argparse.Namespace) -> None:
    data = load_manifest()
    segments = manifest_segments(data)
    selected = parse_chapters_arg(args.chapter) or {item.chapter for item in segments}
    for chapter in sorted(selected):
        items = ordered_chapter_segments(segments, chapter)
        if args.dry_run:
            print(f"SUBTITLES {chapter:02d}: {len(items)} source segments")
        else:
            build_subtitles(items, args.force)
    if args.dry_run:
        print("DRY RUN: no subtitle files written")


def command_validate(args: argparse.Namespace) -> None:
    data = load_manifest() if MANIFEST.exists() else build_manifest(False)
    validate_prepared(data)
    segments = manifest_segments(data)
    chapters = parse_chapters_arg(args.chapter)
    batches = selected_batches(data, args.group, chapters)
    selected_ids = {segment_id for batch in batches for segment_id in batch["segment_ids"]}
    selected_segments = [item for item in segments if item.id in selected_ids]
    selected_chapters = chapters or {item.chapter for item in segments}
    if args.stage in {"synthesized", "split", "assembled", "subtitles"}:
        for batch in batches:
            media = WORK_DIR / "synthesis" / f"{batch['id']}.mp3"
            metadata = WORK_DIR / "synthesis" / f"{batch['id']}.boundaries.json"
            if not media.exists() or not metadata.exists():
                raise FileNotFoundError(f"Missing synthesis output for {batch['id']}")
    if args.stage in {"split", "assembled", "subtitles"}:
        require_programs("ffprobe")
        for item in selected_segments:
            media = chapter_directory(item) / f"{item.output_stem}.mp3"
            if not media.exists() or media_duration(media) <= 0:
                raise FileNotFoundError(f"Missing or empty split segment: {media}")
    if args.stage in {"assembled", "subtitles"}:
        for chapter in sorted(selected_chapters):
            items = ordered_chapter_segments(segments, chapter)
            directory = chapter_directory(items[0])
            track = directory / f"{chapter:02d}-ru-shorts-{items[0].chapter_slug}.mp3"
            if not track.exists() or media_duration(track) <= 0:
                raise FileNotFoundError(f"Missing assembled track: {track}")
    if args.stage == "subtitles":
        for chapter in sorted(selected_chapters):
            item = ordered_chapter_segments(segments, chapter)[0]
            subtitle = chapter_directory(item) / f"{chapter:02d}-ru-shorts-{item.chapter_slug}.srt"
            if not subtitle.exists() or " --> " not in subtitle.read_text(encoding="utf-8"):
                raise FileNotFoundError(f"Missing or invalid subtitles: {subtitle}")
    print(f"Validation passed: {args.stage}")


def add_common_phase_arguments(parser: argparse.ArgumentParser, group: bool = False) -> None:
    if group:
        parser.add_argument("--group", choices=("shared", "answers", "all"), required=True)
    parser.add_argument("--chapter", action="append", metavar="NN", help="limit work to a chapter; repeatable")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    prepare = commands.add_parser("prepare", help="extract source text and write the manifest and batch files")
    prepare.add_argument("--dry-run", action="store_true")
    prepare.add_argument(
        "--include-protected",
        action="store_true",
        help="include protected chapter 09; never use for the current publication iteration",
    )
    prepare.set_defaults(func=command_prepare)

    synthesize = commands.add_parser("synthesize", help="run selected edge-tts batches sequentially")
    add_common_phase_arguments(synthesize, group=True)
    synthesize.add_argument(
        "--delay-seconds",
        type=float,
        default=1.0,
        help="delay between live batch requests (default: 1 second)",
    )
    synthesize.set_defaults(func=command_synthesize)

    split = commands.add_parser("split", help="split synthesized batches using WordBoundary metadata")
    add_common_phase_arguments(split, group=True)
    split.set_defaults(func=command_split)

    assemble = commands.add_parser("assemble", help="assemble chapter tracks with fixed pauses")
    add_common_phase_arguments(assemble)
    assemble.set_defaults(func=command_assemble)

    subtitles = commands.add_parser("subtitles", help="build SRT files from canonical text and timing metadata")
    add_common_phase_arguments(subtitles)
    subtitles.set_defaults(func=command_subtitles)

    validate = commands.add_parser("validate", help="validate one completed pipeline stage")
    validate.add_argument(
        "--stage",
        choices=("prepared", "synthesized", "split", "assembled", "subtitles"),
        default="prepared",
    )
    validate.add_argument("--group", choices=("shared", "answers", "all"), default="all")
    validate.add_argument("--chapter", action="append", metavar="NN")
    validate.set_defaults(func=command_validate)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
