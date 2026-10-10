"""Prepare English System Design Shorts batches and Edge TTS commands."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from markdown_it import MarkdownIt

import prepare_system_design_audio as shared
import role_audio

Segment = shared.Segment


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/engineering/system-design/system-design-shorts.md"
DIAGRAMS = ROOT / "tools/tts/system_design_diagrams.en.json"
OUTPUT_ROOT = ROOT / "build/audio/system-design-shorts-en"
WORK_DIR = OUTPUT_ROOT / "role-en"
BATCHES_DIR = WORK_DIR / "batches"
SYNTHESIS_DIR = WORK_DIR / "synthesis"
WORD_LIMIT = 200

TITLE_VOICE = "en-US-AndrewMultilingualNeural"
QUESTION_VOICE = "en-US-AriaNeural"
ANSWER_VOICE = "en-US-GuyNeural"
RATE = "+25%"
VOLUME = "+0%"
PITCH = "+0Hz"

SECTION_CONFIG = {
    "System Design Fundamentals": (1, "fundamentals"),
    "Scalability & Capacity": (2, "scalability-capacity"),
    "Data Storage & Consistency": (3, "data-storage-consistency"),
    "Caching & Data Freshness": (4, "caching-data-freshness"),
    "Async Processing & Messaging": (5, "async-processing-messaging"),
    "Reliability & Failure Handling": (6, "reliability-failure-handling"),
    "System Design Diagrams": (7, "diagrams"),
    "Offline-First Mobile Application": (8, "offline-first-mobile"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_diagrams() -> dict[str, dict[str, str]]:
    payload = json.loads(DIAGRAMS.read_text(encoding="utf-8"))
    if payload.get("schema") != 1 or payload.get("language") != "en":
        raise ValueError(f"Unsupported diagram narration file: {DIAGRAMS}")
    result = {}
    for item in payload.get("diagrams", []):
        source = str(item.get("source", "")).strip()
        narration = str(item.get("narration", "")).strip()
        if not source or not narration or source in result:
            raise ValueError(f"Invalid or duplicate diagram narration: {item.get('id')}")
        result[source] = {"id": str(item.get("id", "")), "narration": narration}
    return result


def build_segments():
    markdown = SOURCE.read_text(encoding="utf-8")
    diagrams = load_diagrams()
    sections = role_audio.mapped_sections(markdown, 2)
    if [title for title, _ in sections] != list(SECTION_CONFIG):
        raise ValueError("English source section mapping does not match expected chapters")

    segments = []
    used_diagrams = []
    for title, section_markdown in sections:
        number, slug = SECTION_CONFIG[title]
        segments.append(
            shared.Segment(
                id=f"{number:02d}-title", section=number, section_title=title,
                section_slug=slug, kind="title", ordinal=0, role="andrew",
                voice=TITLE_VOICE, canonical_text=title,
                tts_text=role_audio.ensure_terminal_punctuation(title),
                output_stem=shared.output_stem("title", 0, "andrew"),
            )
        )
        questions = role_audio.mapped_sections(section_markdown, 3)
        if not questions:
            raise ValueError(f"Section {number:02d} has no questions")
        for ordinal, (question, question_markdown) in enumerate(questions, start=1):
            answer, used = shared.answer_text(question_markdown, diagrams)
            used_diagrams.extend(used)
            for kind, role, voice, canonical in (
                ("question", "aria", QUESTION_VOICE, question),
                ("answer", "guy", ANSWER_VOICE, answer),
            ):
                segments.append(
                    shared.Segment(
                        id=f"{number:02d}-{kind}-{ordinal:02d}", section=number,
                        section_title=title, section_slug=slug, kind=kind,
                        ordinal=ordinal, role=role, voice=voice,
                        canonical_text=canonical, tts_text=canonical,
                        output_stem=shared.output_stem(kind, ordinal, role),
                    )
                )
    expected = sorted(item["id"] for item in diagrams.values())
    if sorted(used_diagrams) != expected:
        raise ValueError(f"Diagram usage mismatch: expected={expected}, used={sorted(used_diagrams)}")
    return segments, used_diagrams


def command(batch: dict) -> str:
    base = "build\\audio\\system-design-shorts-en\\role-en"
    stem = batch["id"]
    return (
        "build\\tts-venv\\Scripts\\python.exe tools\\tts\\synthesize_part.py "
        f"--voice {batch['voice']} --rate={RATE} --volume={VOLUME} --pitch={PITCH} "
        f"--file {base}\\batches\\{stem}.txt "
        f"--write-media {base}\\synthesis\\{stem}.mp3 "
        f"--write-boundaries {base}\\synthesis\\{stem}.boundaries.json"
    )


def write_outputs(segments, batches, diagram_ids):
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)
    for number, slug in SECTION_CONFIG.values():
        (OUTPUT_ROOT / f"{number:02d}-en-{slug}").mkdir(parents=True, exist_ok=True)

    batch_manifest = []
    for batch in batches:
        stem = batch["id"]
        (BATCHES_DIR / f"{stem}.txt").write_text(batch["text"], encoding="utf-8")
        markdown = [
            f"# {stem}", "", f"- Voice: `{batch['voice']}`",
            f"- Words: {batch['words']}", f"- Characters: {batch['characters']}",
            f"- Segments: {len(batch['segment_ids'])}", "", batch["text"].rstrip(), "",
        ]
        (BATCHES_DIR / f"{stem}.md").write_text("\n".join(markdown), encoding="utf-8")
        batch_manifest.append({key: value for key, value in batch.items() if key != "text"})

    groups = {"titles": [], "questions": [], "answers": []}
    sections: dict[int, list[str]] = {}
    all_commands = []
    for batch in batches:
        line = command(batch)
        all_commands.append(line)
        if batch["id"].startswith("titles-"):
            groups["titles"].append(line)
        elif batch["id"].startswith("questions-"):
            groups["questions"].append(line)
        else:
            groups["answers"].append(line)
            section = int(batch["id"].split("-")[1])
            sections.setdefault(section, []).append(line)
    for name, lines in groups.items():
        (WORK_DIR / f"{name}-commands.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for section, lines in sections.items():
        (WORK_DIR / f"answers-{section:02d}-commands.txt").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    (WORK_DIR / "all-commands.txt").write_text("\n".join(all_commands) + "\n", encoding="utf-8")

    manifest = {
        "schema": 1, "collection": "system-design-shorts", "language": "en",
        "source": SOURCE.relative_to(ROOT).as_posix(), "source_sha256": sha256(SOURCE),
        "diagram_narration": DIAGRAMS.relative_to(ROOT).as_posix(),
        "diagram_narration_sha256": sha256(DIAGRAMS), "diagram_ids": diagram_ids,
        "word_limit": WORD_LIMIT,
        "settings": {"rate": RATE, "volume": VOLUME, "pitch": PITCH, "pause": 0.8},
        "segments": [asdict(item) for item in segments], "batches": batch_manifest,
    }
    (WORK_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    questions = sum(item.kind == "question" for item in segments)
    rows = [
        "# English System Design Shorts audio plan", "",
        f"- Source: `{manifest['source']}`", f"- Sections: {len(SECTION_CONFIG)}",
        f"- Questions and answers: {questions}", f"- Edge TTS requests: {len(batches)}",
        f"- Maximum words per request: {WORD_LIMIT}",
        f"- Semantic diagram narrations: {len(diagram_ids)}", "", "## Requests", "",
        "| Batch | Voice | Segments | Words | Characters |", "| --- | --- | ---: | ---: | ---: |",
    ]
    for batch in batches:
        rows.append(
            f"| `{batch['id']}` | `{batch['voice']}` | {len(batch['segment_ids'])} | "
            f"{batch['words']} | {batch['characters']} |"
        )
    rows.extend([
        "", "## Runner", "", "```powershell",
        "build\\tts-venv\\Scripts\\python.exe -u tools\\tts\\run_tts_commands.py "
        "--commands build\\audio\\system-design-shorts-en\\role-en\\all-commands.txt "
        "--pause-seconds 960", "```", "",
        "The runner waits 16 minutes after every executed request.",
    ])
    (WORK_DIR / "plan.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main():
    segments, diagram_ids = build_segments()
    batches = shared.request_batches(segments)
    write_outputs(segments, batches, diagram_ids)
    questions = sum(item.kind == "question" for item in segments)
    print(f"Prepared {len(SECTION_CONFIG)} sections, {questions} questions, {len(batches)} requests")
    for batch in batches:
        print(f"  {batch['id']}: {len(batch['segment_ids'])} segments, {batch['words']} words, {batch['characters']} characters")
    print(f"Plan: {WORK_DIR / 'plan.md'}")


if __name__ == "__main__":
    main()
