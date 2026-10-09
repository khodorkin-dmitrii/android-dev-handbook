"""Prepare balanced manual TTS batches for Russian answer chapters."""

from __future__ import annotations

import argparse
from functools import lru_cache
import json
import math
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "build/audio/shorts-ru/role-ru/manifest.json"
OUTPUT_DIR = ROOT / "build/audio/shorts-ru/role-ru/synthesis"
DEFAULT_CHAPTERS = (2, 3, 4, 5, 6, 7, 8, 10)


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text, flags=re.UNICODE))


def balanced_parts(answers: list[dict[str, object]], word_limit: int) -> list[list[dict[str, object]]]:
    counts = [word_count(str(answer["tts_text"])) for answer in answers]
    if any(count > word_limit for count in counts):
        position = next(index for index, count in enumerate(counts) if count > word_limit)
        raise ValueError(
            f"{answers[position]['id']} has {counts[position]} words and must be split manually"
        )
    part_count = math.ceil(sum(counts) / word_limit)
    target = sum(counts) / part_count
    prefix = [0]
    for count in counts:
        prefix.append(prefix[-1] + count)

    @lru_cache(maxsize=None)
    def solve(start: int, remaining_parts: int) -> tuple[float, tuple[int, ...]] | None:
        if remaining_parts == 0:
            return (0.0, ()) if start == len(answers) else None
        if len(answers) - start < remaining_parts:
            return None
        best: tuple[float, tuple[int, ...]] | None = None
        last_end = len(answers) - remaining_parts + 1
        for end in range(start + 1, last_end + 1):
            words = prefix[end] - prefix[start]
            if words > word_limit:
                break
            tail = solve(end, remaining_parts - 1)
            if tail is None:
                continue
            candidate = ((words - target) ** 2 + tail[0], (end,) + tail[1])
            if best is None or candidate[0] < best[0]:
                best = candidate
        return best

    solution = solve(0, part_count)
    if solution is None:
        raise ValueError(f"Cannot divide answers into parts of at most {word_limit} words")
    result = []
    start = 0
    for end in solution[1]:
        result.append(answers[start:end])
        start = end
    return result


def command(chapter: int, part: int) -> str:
    stem = f"answers-{chapter:02d}-part-{part:02d}"
    base = "build\\audio\\shorts-ru\\role-ru\\synthesis"
    return (
        "build\\tts-venv\\Scripts\\python.exe tools\\tts\\synthesize_part.py "
        "--voice ru-RU-DmitryNeural --rate=+25% --volume=+0% --pitch=+0Hz "
        f"--file {base}\\{stem}.txt "
        f"--write-media {base}\\{stem}.mp3 "
        f"--write-boundaries {base}\\{stem}.boundaries.json"
    )


def prepare(chapters: tuple[int, ...], word_limit: int, dry_run: bool) -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if 9 in chapters:
        raise ValueError("Chapter 09 is protected")
    available = {int(item["chapter"]) for item in data["segments"]}
    missing = sorted(set(chapters) - available)
    if missing:
        raise ValueError(f"Chapters are absent from the manifest: {missing}")
    if not dry_run:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_parts = 0
    all_commands: list[str] = []
    for chapter in chapters:
        answers = [
            item
            for item in data["segments"]
            if int(item["chapter"]) == chapter and item["kind"] == "answer"
        ]
        parts = balanced_parts(answers, word_limit)
        commands = []
        summary = []
        for index, part in enumerate(parts, start=1):
            text = "\n\n".join(str(item["tts_text"]) for item in part) + "\n"
            words = word_count(text)
            summary.append(
                f"part-{index:02d}: answers {part[0]['ordinal']:02d}-{part[-1]['ordinal']:02d}, "
                f"{words} words, {len(text.rstrip())} characters"
            )
            if not dry_run:
                (OUTPUT_DIR / f"answers-{chapter:02d}-part-{index:02d}.txt").write_text(
                    text, encoding="utf-8"
                )
            commands.append(command(chapter, index))
        all_commands.extend(commands)
        if not dry_run:
            (OUTPUT_DIR / f"answers-{chapter:02d}-commands.txt").write_text(
                "\n".join(commands) + "\n", encoding="utf-8"
            )
        total_parts += len(parts)
        print(f"Chapter {chapter:02d}: {len(answers)} answers -> {len(parts)} parts")
        for line in summary:
            print(f"  {line}")
    if not dry_run:
        (OUTPUT_DIR / "answers-remaining-commands.txt").write_text(
            "\n".join(all_commands) + "\n", encoding="utf-8"
        )
    print(f"Total commands: {total_parts}")
    if dry_run:
        print("DRY RUN: no files written")


def combine_existing_commands(chapters: tuple[int, ...], dry_run: bool) -> None:
    commands: list[str] = []
    for chapter in chapters:
        path = OUTPUT_DIR / f"answers-{chapter:02d}-commands.txt"
        if not path.exists():
            raise FileNotFoundError(f"Missing chapter command file: {path}")
        commands.extend(line for line in path.read_text(encoding="utf-8").splitlines() if line)
    output = OUTPUT_DIR / "answers-remaining-commands.txt"
    if not dry_run:
        output.write_text("\n".join(commands) + "\n", encoding="utf-8")
    print(f"Combined commands: {len(commands)}")
    print(f"Output: {output}")
    if dry_run:
        print("DRY RUN: no files written")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapter", type=int, action="append")
    parser.add_argument("--word-limit", type=int, default=200)
    parser.add_argument("--combined-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.word_limit <= 0:
        parser.error("--word-limit must be positive")
    chapters = tuple(args.chapter) if args.chapter else DEFAULT_CHAPTERS
    try:
        if args.combined_only:
            combine_existing_commands(chapters, args.dry_run)
        else:
            prepare(chapters, args.word_limit, args.dry_run)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
