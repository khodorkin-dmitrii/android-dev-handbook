"""Prepare Russian System Design Shorts for role-based Edge TTS synthesis."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

from markdown_it import MarkdownIt

import role_audio


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/engineering/system-design/system-design-shorts.ru.md"
PRONUNCIATION = ROOT / "build/audio/pronunciation-ru.json"
DIAGRAMS = ROOT / "tools/tts/system_design_diagrams.ru.json"
OUTPUT_ROOT = ROOT / "build/audio/system-design-shorts-ru"
WORK_DIR = OUTPUT_ROOT / "role-ru"
BATCHES_DIR = WORK_DIR / "batches"
SYNTHESIS_DIR = WORK_DIR / "synthesis"
WORD_LIMIT = 200

TITLE_VOICE = "en-US-AndrewMultilingualNeural"
QUESTION_VOICE = "ru-RU-SvetlanaNeural"
ANSWER_VOICE = "ru-RU-DmitryNeural"
RATE = "+25%"
VOLUME = "+0%"
PITCH = "+0Hz"

SECTION_CONFIG = {
    "Основы System Design": (1, "fundamentals"),
    "Scalability & Capacity": (2, "scalability-capacity"),
    "Data Storage & Consistency": (3, "data-storage-consistency"),
    "Caching & Data Freshness": (4, "caching-data-freshness"),
    "Async Processing & Messaging": (5, "async-processing-messaging"),
    "Reliability & Failure Handling": (6, "reliability-failure-handling"),
    "System Design Diagrams": (7, "diagrams"),
    "Offline-First Mobile Application": (8, "offline-first-mobile"),
}


@dataclass(frozen=True)
class Segment:
    id: str
    section: int
    section_title: str
    section_slug: str
    kind: str
    ordinal: int
    role: str
    voice: str
    canonical_text: str
    tts_text: str
    output_stem: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text, flags=re.UNICODE))


def load_diagrams() -> dict[str, dict[str, str]]:
    payload = json.loads(DIAGRAMS.read_text(encoding="utf-8"))
    if payload.get("schema") != 1 or payload.get("language") != "ru":
        raise ValueError(f"Unsupported diagram narration file: {DIAGRAMS}")
    result: dict[str, dict[str, str]] = {}
    for item in payload.get("diagrams", []):
        source = str(item.get("source", "")).strip()
        narration = str(item.get("narration", "")).strip()
        if not source or not narration:
            raise ValueError(f"Incomplete diagram narration: {item.get('id', '<unknown>')}")
        if source in result:
            raise ValueError(f"Duplicate diagram source: {item.get('id', '<unknown>')}")
        result[source] = {
            "id": str(item.get("id", "")),
            "narration": narration,
        }
    return result


def answer_text(question_markdown: str, diagrams: dict[str, dict[str, str]]) -> tuple[str, list[str]]:
    values: list[str] = []
    used_diagrams: list[str] = []
    heading: str | None = None
    for token in MarkdownIt().parse(question_markdown):
        if token.type == "heading_open":
            heading = token.tag
        elif token.type == "heading_close":
            heading = None
        elif token.type == "inline" and heading != "h3":
            value = role_audio.clean_inline(token)
            if value:
                values.append(value)
        elif token.type == "fence" and token.info.strip() == "text":
            source = token.content.strip()
            replacement = diagrams.get(source)
            if replacement is None:
                preview = source.splitlines()[0] if source else "<empty>"
                raise ValueError(f"Unregistered text diagram: {preview}")
            values.append(replacement["narration"])
            used_diagrams.append(replacement["id"])
    if not values:
        raise ValueError("Question has no visible answer")
    return "\n\n".join(values), used_diagrams


def output_stem(kind: str, ordinal: int, role: str) -> str:
    if kind == "title":
        return f"01-title-{role}"
    position = ordinal * 2 if kind == "question" else ordinal * 2 + 1
    return f"{position:02d}-{kind}-{ordinal:02d}-{role}"


def build_segments() -> tuple[list[Segment], list[str]]:
    markdown = SOURCE.read_text(encoding="utf-8")
    pronunciation = role_audio.read_pronunciation(PRONUNCIATION)
    diagrams = load_diagrams()
    sections = role_audio.mapped_sections(markdown, 2)
    titles = [title for title, _ in sections]
    if titles != list(SECTION_CONFIG):
        raise ValueError(f"Section mapping mismatch: {titles}")

    segments: list[Segment] = []
    used_diagrams: list[str] = []
    for title, section_markdown in sections:
        number, slug = SECTION_CONFIG[title]
        segments.append(
            Segment(
                id=f"{number:02d}-title",
                section=number,
                section_title=title,
                section_slug=slug,
                kind="title",
                ordinal=0,
                role="andrew",
                voice=TITLE_VOICE,
                canonical_text=title,
                tts_text=role_audio.ensure_terminal_punctuation(title),
                output_stem=output_stem("title", 0, "andrew"),
            )
        )
        questions = role_audio.mapped_sections(section_markdown, 3)
        if not questions:
            raise ValueError(f"Section {number:02d} has no questions")
        for ordinal, (question, question_markdown) in enumerate(questions, start=1):
            answer, answer_diagrams = answer_text(question_markdown, diagrams)
            used_diagrams.extend(answer_diagrams)
            for kind, role, voice, canonical in (
                ("question", "svetlana", QUESTION_VOICE, question),
                ("answer", "dmitry", ANSWER_VOICE, answer),
            ):
                segments.append(
                    Segment(
                        id=f"{number:02d}-{kind}-{ordinal:02d}",
                        section=number,
                        section_title=title,
                        section_slug=slug,
                        kind=kind,
                        ordinal=ordinal,
                        role=role,
                        voice=voice,
                        canonical_text=canonical,
                        tts_text=role_audio.apply_pronunciation(canonical, pronunciation),
                        output_stem=output_stem(kind, ordinal, role),
                    )
                )
    expected_diagrams = sorted(item["id"] for item in diagrams.values())
    if sorted(used_diagrams) != expected_diagrams:
        raise ValueError(
            f"Diagram usage mismatch; expected={expected_diagrams}, used={sorted(used_diagrams)}"
        )
    return segments, used_diagrams


def balanced_groups(items: list[Segment], limit: int) -> list[list[Segment]]:
    if not items:
        return []
    counts = [word_count(item.tts_text) for item in items]
    too_large = [(item.id, count) for item, count in zip(items, counts) if count > limit]
    if too_large:
        raise ValueError(f"A semantic segment exceeds the {limit}-word limit: {too_large}")
    prefix = [0]
    for count in counts:
        prefix.append(prefix[-1] + count)

    for group_count in range(math.ceil(sum(counts) / limit), len(items) + 1):
        target = sum(counts) / group_count

        @lru_cache(maxsize=None)
        def solve(start: int, remaining: int) -> tuple[float, tuple[int, ...]] | None:
            if remaining == 0:
                return (0.0, ()) if start == len(items) else None
            if len(items) - start < remaining:
                return None
            best: tuple[float, tuple[int, ...]] | None = None
            last_end = len(items) - remaining + 1
            for end in range(start + 1, last_end + 1):
                words = prefix[end] - prefix[start]
                if words > limit:
                    break
                tail = solve(end, remaining - 1)
                if tail is None:
                    continue
                candidate = ((words - target) ** 2 + tail[0], (end,) + tail[1])
                if best is None or candidate[0] < best[0]:
                    best = candidate
            return best

        solution = solve(0, group_count)
        if solution is None:
            continue
        groups: list[list[Segment]] = []
        start = 0
        for end in solution[1]:
            groups.append(items[start:end])
            start = end
        return groups
    raise ValueError("Unable to divide segments into complete TTS requests")


def request_batches(segments: list[Segment]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    def add(batch_id: str, items: list[Segment]) -> None:
        text = "\n\n".join(role_audio.ensure_terminal_punctuation(item.tts_text) for item in items) + "\n"
        result.append(
            {
                "id": batch_id,
                "voice": items[0].voice,
                "segment_ids": [item.id for item in items],
                "words": word_count(text),
                "characters": len(text),
                "text": text,
            }
        )

    titles = [item for item in segments if item.kind == "title"]
    add("titles-part-01", titles)
    questions = [item for item in segments if item.kind == "question"]
    for index, items in enumerate(balanced_groups(questions, WORD_LIMIT), start=1):
        add(f"questions-part-{index:02d}", items)
    for section in sorted({item.section for item in segments}):
        answers = [
            item for item in segments if item.section == section and item.kind == "answer"
        ]
        for index, items in enumerate(balanced_groups(answers, WORD_LIMIT), start=1):
            add(f"answers-{section:02d}-part-{index:02d}", items)
    if any(batch["words"] > WORD_LIMIT for batch in result):
        raise ValueError("Prepared request exceeds the word limit")
    return result


def command(batch: dict[str, Any]) -> str:
    base = "build\\audio\\system-design-shorts-ru\\role-ru"
    stem = batch["id"]
    return (
        "build\\tts-venv\\Scripts\\python.exe tools\\tts\\synthesize_part.py "
        f"--voice {batch['voice']} --rate={RATE} --volume={VOLUME} --pitch={PITCH} "
        f"--file {base}\\batches\\{stem}.txt "
        f"--write-media {base}\\synthesis\\{stem}.mp3 "
        f"--write-boundaries {base}\\synthesis\\{stem}.boundaries.json"
    )


def write_outputs(segments: list[Segment], batches: list[dict[str, Any]], diagrams: list[str]) -> None:
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)
    for number, slug in SECTION_CONFIG.values():
        (OUTPUT_ROOT / f"{number:02d}-ru-{slug}").mkdir(parents=True, exist_ok=True)

    manifest_batches = []
    for batch in batches:
        text_path = BATCHES_DIR / f"{batch['id']}.txt"
        text_path.write_text(batch["text"], encoding="utf-8")
        details = [
            f"# {batch['id']}",
            "",
            f"- Voice: `{batch['voice']}`",
            f"- Words: {batch['words']}",
            f"- Characters: {batch['characters']}",
            f"- Segments: {len(batch['segment_ids'])}",
            "",
            batch["text"].rstrip(),
            "",
        ]
        (BATCHES_DIR / f"{batch['id']}.md").write_text("\n".join(details), encoding="utf-8")
        manifest_batches.append({key: value for key, value in batch.items() if key != "text"})

    commands_by_group: dict[str, list[str]] = {"titles": [], "questions": [], "answers": []}
    commands_by_section: dict[int, list[str]] = {}
    all_commands: list[str] = []
    for batch in batches:
        line = command(batch)
        all_commands.append(line)
        if batch["id"].startswith("titles-"):
            commands_by_group["titles"].append(line)
        elif batch["id"].startswith("questions-"):
            commands_by_group["questions"].append(line)
        else:
            commands_by_group["answers"].append(line)
            section = int(batch["id"].split("-")[1])
            commands_by_section.setdefault(section, []).append(line)
    for name, lines in commands_by_group.items():
        (WORK_DIR / f"{name}-commands.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for section, lines in commands_by_section.items():
        (WORK_DIR / f"answers-{section:02d}-commands.txt").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    (WORK_DIR / "all-commands.txt").write_text("\n".join(all_commands) + "\n", encoding="utf-8")

    manifest = {
        "schema": 1,
        "collection": "system-design-shorts",
        "language": "ru",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(SOURCE),
        "pronunciation": PRONUNCIATION.relative_to(ROOT).as_posix(),
        "pronunciation_sha256": sha256(PRONUNCIATION),
        "diagram_narration": DIAGRAMS.relative_to(ROOT).as_posix(),
        "diagram_narration_sha256": sha256(DIAGRAMS),
        "diagram_ids": diagrams,
        "word_limit": WORD_LIMIT,
        "settings": {"rate": RATE, "volume": VOLUME, "pitch": PITCH, "pause": 0.8},
        "segments": [asdict(item) for item in segments],
        "batches": manifest_batches,
    }
    (WORK_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    questions = sum(item.kind == "question" for item in segments)
    lines = [
        "# Russian System Design Shorts audio plan",
        "",
        f"- Source: `{manifest['source']}`",
        f"- Sections: {len(SECTION_CONFIG)}",
        f"- Questions and answers: {questions}",
        f"- Edge TTS requests: {len(batches)}",
        f"- Maximum words per request: {WORD_LIMIT}",
        f"- Semantic diagram narrations: {len(diagrams)}",
        "",
        "## Requests",
        "",
        "| Batch | Voice | Segments | Words | Characters |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for batch in batches:
        lines.append(
            f"| `{batch['id']}` | `{batch['voice']}` | {len(batch['segment_ids'])} | "
            f"{batch['words']} | {batch['characters']} |"
        )
    lines.extend(
        [
            "",
            "## Runner",
            "",
            "```powershell",
            "build\\tts-venv\\Scripts\\python.exe -u tools\\tts\\run_tts_commands.py "
            "--commands build\\audio\\system-design-shorts-ru\\role-ru\\all-commands.txt",
            "```",
            "",
            "The runner currently waits 10 minutes after every executed request.",
        ]
    )
    (WORK_DIR / "plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    segments, diagrams = build_segments()
    batches = request_batches(segments)
    write_outputs(segments, batches, diagrams)
    questions = sum(item.kind == "question" for item in segments)
    print(f"Prepared {len(SECTION_CONFIG)} sections, {questions} questions, {len(batches)} requests")
    for batch in batches:
        print(
            f"  {batch['id']}: {len(batch['segment_ids'])} segments, "
            f"{batch['words']} words, {batch['characters']} characters"
        )
    print(f"Plan: {WORK_DIR / 'plan.md'}")


if __name__ == "__main__":
    main()
