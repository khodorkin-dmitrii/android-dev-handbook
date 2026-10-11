"""Prepare English role-based Shorts title/question requests without calling TTS."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re

import role_audio


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/shorts.md"
OUTPUT_ROOT = ROOT / "build/audio/shorts-eng"
WORK_DIR = OUTPUT_ROOT / "role-en"
BATCHES_DIR = WORK_DIR / "batches"
SYNTHESIS_DIR = WORK_DIR / "synthesis"
WORD_LIMIT = 200
PROTECTED_CHAPTER = 9

TITLE_VOICE = "en-US-AndrewMultilingualNeural"
QUESTION_VOICE = "en-US-AriaNeural"
RATE = "+25%"
VOLUME = "+0%"
PITCH = "+0Hz"

CHAPTER_CONFIG = {
    "Computer Science": (1, "computer-science"),
    "Kotlin": (2, "kotlin"),
    "Android basics": (3, "android-basics"),
    "Jetpack Compose": (4, "jetpack-compose"),
    "Coroutines and Flow": (5, "coroutines-flow"),
    "Architecture": (6, "architecture"),
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
    output_stem: str


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text, flags=re.UNICODE))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_stem(kind: str, ordinal: int, role: str) -> str:
    if kind == "title":
        return f"01-title-{role}"
    return f"{ordinal * 2:02d}-question-{ordinal:02d}-{role}"


def build_segments() -> list[Segment]:
    markdown = SOURCE.read_text(encoding="utf-8")
    chapters = role_audio.mapped_sections(markdown, 2)
    actual_titles = [title for title, _ in chapters]
    if actual_titles != list(CHAPTER_CONFIG):
        raise ValueError(f"Chapter mapping mismatch: {actual_titles}")

    segments = []
    for title, chapter_markdown in chapters:
        chapter, slug = CHAPTER_CONFIG[title]
        if chapter == PROTECTED_CHAPTER:
            continue
        segments.append(
            Segment(
                id=f"{chapter:02d}-title", chapter=chapter, chapter_title=title,
                chapter_slug=slug, kind="title", ordinal=0, role="andrew",
                voice=TITLE_VOICE, canonical_text=title,
                tts_text=role_audio.ensure_terminal_punctuation(title),
                output_stem=output_stem("title", 0, "andrew"),
            )
        )
        questions = role_audio.mapped_sections(chapter_markdown, 3)
        if not questions:
            raise ValueError(f"Chapter {chapter:02d} has no questions")
        for ordinal, (question, _) in enumerate(questions, start=1):
            segments.append(
                Segment(
                    id=f"{chapter:02d}-question-{ordinal:02d}", chapter=chapter,
                    chapter_title=title, chapter_slug=slug, kind="question",
                    ordinal=ordinal, role="aria", voice=QUESTION_VOICE,
                    canonical_text=question,
                    tts_text=role_audio.ensure_terminal_punctuation(question),
                    output_stem=output_stem("question", ordinal, "aria"),
                )
            )
    if any(item.chapter == PROTECTED_CHAPTER for item in segments):
        raise ValueError("Protected chapter 09 must not be included")
    return segments


def balanced_groups(items: list[Segment]) -> list[list[Segment]]:
    counts = [word_count(item.tts_text) for item in items]
    if any(count > WORD_LIMIT for count in counts):
        position = next(index for index, count in enumerate(counts) if count > WORD_LIMIT)
        raise ValueError(f"{items[position].id} exceeds the {WORD_LIMIT}-word request limit")
    if not items:
        return []

    prefix = [0]
    for count in counts:
        prefix.append(prefix[-1] + count)
    total = prefix[-1]
    for group_count in range(math.ceil(total / WORD_LIMIT), len(items) + 1):
        target = total / group_count

        @lru_cache(maxsize=None)
        def solve(start: int, remaining: int):
            if remaining == 0:
                return (0.0, ()) if start == len(items) else None
            if len(items) - start < remaining:
                return None
            best = None
            last_end = len(items) - remaining + 1
            for end in range(start + 1, last_end + 1):
                words = prefix[end] - prefix[start]
                if words > WORD_LIMIT:
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
        groups = []
        start = 0
        for end in solution[1]:
            groups.append(items[start:end])
            start = end
        return groups
    raise ValueError("Unable to divide questions into complete TTS requests")


def make_batch(batch_id: str, items: list[Segment]) -> dict:
    text = "\n\n".join(item.tts_text for item in items) + "\n"
    return {
        "id": batch_id,
        "voice": items[0].voice,
        "segment_ids": [item.id for item in items],
        "words": word_count(text),
        "characters": len(text.rstrip()),
        "text": text,
    }


def build_batches(segments: list[Segment]) -> list[dict]:
    titles = [item for item in segments if item.kind == "title"]
    questions = [item for item in segments if item.kind == "question"]
    if word_count(" ".join(item.tts_text for item in titles)) > WORD_LIMIT:
        raise ValueError("All titles must fit in their dedicated single request")
    batches = [make_batch("titles-part-01", titles)]
    batches.extend(
        make_batch(f"questions-part-{index:02d}", group)
        for index, group in enumerate(balanced_groups(questions), start=1)
    )
    return batches


def command(batch: dict) -> str:
    stem = batch["id"]
    base = "build\\audio\\shorts-eng\\role-en"
    return (
        "build\\tts-venv\\Scripts\\python.exe tools\\tts\\synthesize_part.py "
        f"--voice {batch['voice']} --rate={RATE} --volume={VOLUME} --pitch={PITCH} "
        f"--file {base}\\batches\\{stem}.txt "
        f"--write-media {base}\\synthesis\\{stem}.mp3 "
        f"--write-boundaries {base}\\synthesis\\{stem}.boundaries.json"
    )


def write_outputs(segments: list[Segment], batches: list[dict]) -> None:
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)
    batch_manifest = []
    for batch in batches:
        stem = batch["id"]
        (BATCHES_DIR / f"{stem}.txt").write_text(batch["text"], encoding="utf-8")
        lines = [
            f"# {stem}", "", f"- Voice: `{batch['voice']}`",
            f"- Words: {batch['words']}", f"- Characters: {batch['characters']}",
            f"- Segments: {len(batch['segment_ids'])}", "", batch["text"].rstrip(), "",
        ]
        (BATCHES_DIR / f"{stem}.md").write_text("\n".join(lines), encoding="utf-8")
        batch_manifest.append({key: value for key, value in batch.items() if key != "text"})

    all_commands = [command(batch) for batch in batches]
    titles_command = [line for line, batch in zip(all_commands, batches) if batch["id"].startswith("titles-")]
    questions_command = [line for line, batch in zip(all_commands, batches) if batch["id"].startswith("questions-")]
    (WORK_DIR / "titles-commands.txt").write_text("\n".join(titles_command) + "\n", encoding="utf-8")
    (WORK_DIR / "questions-commands.txt").write_text("\n".join(questions_command) + "\n", encoding="utf-8")
    (WORK_DIR / "all-commands.txt").write_text("\n".join(all_commands) + "\n", encoding="utf-8")

    manifest = {
        "schema": 1,
        "collection": "shorts",
        "language": "en",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(SOURCE),
        "protected_chapter": PROTECTED_CHAPTER,
        "scope": ["title", "question"],
        "word_limit": WORD_LIMIT,
        "settings": {"rate": RATE, "volume": VOLUME, "pitch": PITCH, "pause": 0.8},
        "segments": [asdict(item) for item in segments],
        "batches": batch_manifest,
    }
    (WORK_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    question_count = sum(item.kind == "question" for item in segments)
    rows = [
        "# English Shorts role audio preparation: titles and questions", "",
        f"- Source: `{manifest['source']}`",
        f"- Chapters included: {len({item.chapter for item in segments})}",
        f"- Protected chapter excluded: {PROTECTED_CHAPTER:02d}",
        f"- Questions: {question_count}", f"- Edge TTS requests: {len(batches)}",
        f"- Maximum words per request: {WORD_LIMIT}",
        "- Scope: titles and question headings only; answers are not included.",
        "", "## Requests", "",
        "| Batch | Voice | Segments | Words | Characters |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for batch in batches:
        rows.append(
            f"| `{batch['id']}` | `{batch['voice']}` | {len(batch['segment_ids'])} | "
            f"{batch['words']} | {batch['characters']} |"
        )
    rows.extend([
        "", "## Runner", "", "```powershell",
        "build\\tts-venv\\Scripts\\python.exe -u tools\\tts\\run_tts_commands.py "
        "--commands build\\audio\\shorts-eng\\role-en\\all-commands.txt "
        "--pause-seconds 960", "```", "",
        "The runner waits 16 minutes after every executed request.",
    ])
    (WORK_DIR / "plan.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    segments = build_segments()
    batches = build_batches(segments)
    write_outputs(segments, batches)
    print(
        f"Prepared {len({item.chapter for item in segments})} chapters, "
        f"{sum(item.kind == 'question' for item in segments)} questions, "
        f"{len(batches)} requests"
    )
    for batch in batches:
        print(
            f"  {batch['id']}: {len(batch['segment_ids'])} segments, "
            f"{batch['words']} words, {batch['characters']} characters"
        )
    print(f"Plan: {WORK_DIR / 'plan.md'}")


if __name__ == "__main__":
    main()
