"""Prepare English Shorts answer batches without contacting Edge TTS."""

from __future__ import annotations

from dataclasses import asdict
import json

import prepare_shorts_audio_en as shared
import role_audio


ANSWER_VOICE = "en-US-GuyNeural"


def build_answers() -> list[shared.Segment]:
    chapters = role_audio.mapped_sections(shared.SOURCE.read_text(encoding="utf-8"), 2)
    if [title for title, _ in chapters] != list(shared.CHAPTER_CONFIG):
        raise ValueError("English Shorts chapter mapping changed")

    answers = []
    for title, chapter_markdown in chapters:
        chapter, slug = shared.CHAPTER_CONFIG[title]
        if chapter == shared.PROTECTED_CHAPTER:
            continue
        for ordinal, (_, question_markdown) in enumerate(
            role_audio.mapped_sections(chapter_markdown, 3), start=1
        ):
            answer = role_audio.answer_text(question_markdown)
            answers.append(
                shared.Segment(
                    id=f"{chapter:02d}-answer-{ordinal:02d}",
                    chapter=chapter,
                    chapter_title=title,
                    chapter_slug=slug,
                    kind="answer",
                    ordinal=ordinal,
                    role="guy",
                    voice=ANSWER_VOICE,
                    canonical_text=answer,
                    tts_text=answer,
                    output_stem=f"{ordinal * 2 + 1:02d}-answer-{ordinal:02d}-guy",
                )
            )
    return answers


def build_answer_batches(answers: list[shared.Segment]) -> list[dict]:
    batches = []
    for chapter, _ in shared.CHAPTER_CONFIG.values():
        if chapter == shared.PROTECTED_CHAPTER:
            continue
        chapter_answers = [item for item in answers if item.chapter == chapter]
        if not chapter_answers:
            raise ValueError(f"Chapter {chapter:02d} has no answers")
        for part, group in enumerate(shared.balanced_groups(chapter_answers), start=1):
            batches.append(shared.make_batch(f"answers-{chapter:02d}-part-{part:02d}", group))
    return batches


def prepare() -> None:
    manifest_path = shared.WORK_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["source_sha256"] != shared.sha256(shared.SOURCE):
        raise ValueError("Source changed since title/question preparation; regenerate those first")
    if manifest["scope"] != ["title", "question"]:
        raise ValueError("Expected title/question-only manifest; answers may already be prepared")
    original_segments = shared.build_segments()
    if manifest["segments"] != [asdict(item) for item in original_segments]:
        raise ValueError("Existing title/question manifest differs from current source")

    answers = build_answers()
    question_ids = {item.id for item in original_segments if item.kind == "question"}
    answer_question_ids = {item.id.replace("-answer-", "-question-") for item in answers}
    if answer_question_ids != question_ids:
        raise ValueError("Answer count/order differs from prepared questions")
    batches = build_answer_batches(answers)
    if any(batch["words"] > shared.WORD_LIMIT for batch in batches):
        raise ValueError("An answer batch exceeds the word limit")

    shared.BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    shared.SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)
    by_chapter: dict[int, list[str]] = {}
    commands = []
    for batch in batches:
        stem = batch["id"]
        text = batch["text"]
        (shared.BATCHES_DIR / f"{stem}.txt").write_text(text, encoding="utf-8")
        lines = [
            f"# {stem}", "", f"- Voice: `{ANSWER_VOICE}`",
            f"- Words: {batch['words']}", f"- Characters: {batch['characters']}",
            f"- Segments: {len(batch['segment_ids'])}", "", text.rstrip(), "",
        ]
        (shared.BATCHES_DIR / f"{stem}.md").write_text("\n".join(lines), encoding="utf-8")
        command = shared.command({**batch, "voice": ANSWER_VOICE})
        commands.append(command)
        chapter = int(stem.split("-")[1])
        by_chapter.setdefault(chapter, []).append(command)

    for chapter, lines in by_chapter.items():
        (shared.WORK_DIR / f"answers-{chapter:02d}-commands.txt").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    (shared.WORK_DIR / "answers-commands.txt").write_text(
        "\n".join(commands) + "\n", encoding="utf-8"
    )
    # Titles and questions are already synthesized. This is the pending queue only.
    (shared.WORK_DIR / "all-commands.txt").write_text(
        "\n".join(commands) + "\n", encoding="utf-8"
    )

    manifest["scope"] = ["title", "question", "answer"]
    manifest["segments"].extend(asdict(item) for item in answers)
    manifest["batches"].extend(
        {key: value for key, value in batch.items() if key != "text"} for batch in batches
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    rows = [
        "# English Shorts role audio - answer synthesis queue", "",
        f"- Source: `{manifest['source']}`",
        f"- Chapters: {len(by_chapter)} (09 excluded)",
        f"- Answers: {len(answers)}",
        f"- Pending Edge TTS requests: {len(batches)}",
        f"- Maximum words per request: {shared.WORD_LIMIT}",
        "- Titles and questions are already synthesized and are not in this queue.",
        "", "| Batch | Answers | Words | Characters |",
        "| --- | ---: | ---: | ---: |",
    ]
    for batch in batches:
        rows.append(
            f"| `{batch['id']}` | {len(batch['segment_ids'])} | "
            f"{batch['words']} | {batch['characters']} |"
        )
    rows.extend([
        "", "## Run from repository root", "", "```powershell",
        "build\\tts-venv\\Scripts\\python.exe -u tools\\tts\\run_tts_commands.py "
        "--commands build\\audio\\shorts-eng\\role-en\\all-commands.txt "
        "--pause-seconds 960", "```", "",
        "The runner pauses for 16 minutes after each completed or failed request and "
        "skips already complete MP3/boundaries pairs.", "",
    ])
    (shared.WORK_DIR / "answers-plan.md").write_text(
        "\n".join(rows), encoding="utf-8"
    )
    print(f"Prepared {len(answers)} answers in {len(batches)} requests")
    for chapter, lines in by_chapter.items():
        print(f"  Chapter {chapter:02d}: {len(lines)} requests")


if __name__ == "__main__":
    prepare()
