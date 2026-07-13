from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
INCLUDES_DIR = DOCS_DIR / "includes"

TECHNICAL_DIRS = {
    "assets",
    "includes",
    "overrides",
    "stylesheets",
}

SERVICE_PAGES = {
    "index.md",
    "index.ru.md",
    "pages-review-tracker.md",
    "shorts.md",
    "shorts.ru.md",
}

BEGIN_MARKER = "<!-- BEGIN GENERATED HANDBOOK STATS -->"
END_MARKER = "<!-- END GENERATED HANDBOOK STATS -->"

SECTION_RE = re.compile(r"^##(?!#)\s+", re.MULTILINE)
TOPIC_RE = re.compile(r"^###(?!#)\s+", re.MULTILINE)
GENERATED_BLOCK_RE = re.compile(
    rf"{re.escape(BEGIN_MARKER)}.*?{re.escape(END_MARKER)}",
    re.DOTALL,
)


@dataclass(frozen=True)
class LanguageStats:
    domains: int
    pages: int
    sections: int
    topics: int
    words: int


def is_content_path(path: Path) -> bool:
    relative_parts = path.relative_to(DOCS_DIR).parts
    relative_path = path.relative_to(DOCS_DIR).as_posix()
    return (
        relative_path not in SERVICE_PAGES
        and not any(part.startswith(".") or part in TECHNICAL_DIRS for part in relative_parts)
    )


def content_markdown_files() -> list[Path]:
    return sorted(
        path
        for path in DOCS_DIR.rglob("*.md")
        if path.is_file() and is_content_path(path)
    )


def english_files(files: list[Path]) -> list[Path]:
    return [path for path in files if not path.name.endswith(".ru.md")]


def russian_files(files: list[Path]) -> list[Path]:
    return [path for path in files if path.name.endswith(".ru.md")]


def count_domains() -> int:
    return sum(
        1
        for path in DOCS_DIR.iterdir()
        if path.is_dir()
        and not path.name.startswith(".")
        and path.name not in TECHNICAL_DIRS
    )


def count_headings(files: list[Path], pattern: re.Pattern[str]) -> int:
    total = 0
    for path in files:
        text = GENERATED_BLOCK_RE.sub("", path.read_text(encoding="utf-8"))
        total += len(pattern.findall(text))
    return total


def count_words(files: list[Path]) -> int:
    word_re = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+(?:[-'][A-Za-zА-Яа-яЁё0-9]+)*")
    total = 0
    for path in files:
        text = GENERATED_BLOCK_RE.sub("", path.read_text(encoding="utf-8"))
        total += len(word_re.findall(text))
    return total


def collect_stats(files: list[Path], domains: int) -> LanguageStats:
    return LanguageStats(
        domains=domains,
        pages=len(files),
        sections=count_headings(files, SECTION_RE),
        topics=count_headings(files, TOPIC_RE),
        words=count_words(files),
    )


def counterpart_for(path: Path) -> Path:
    if path.name.endswith(".ru.md"):
        return path.with_name(path.name.removesuffix(".ru.md") + ".md")
    return path.with_name(path.stem + ".ru.md")


def missing_translation_pairs(files: list[Path]) -> tuple[list[Path], list[Path]]:
    english = english_files(files)
    russian = russian_files(files)

    missing_ru = [path for path in english if not counterpart_for(path).exists()]
    missing_en = [path for path in russian if not counterpart_for(path).exists()]

    return missing_ru, missing_en


def relative_docs_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def warning_block(language: str, has_missing: bool) -> str:
    if not has_missing:
        return ""

    if language == "ru":
        return (
            '\n!!! warning "Синхронизация перевода"\n'
            "    У некоторых страниц нет парной версии на втором языке.\n"
        )

    return (
        '\n!!! warning "Translation sync"\n'
        "    Some pages do not have a matching translation.\n"
    )


def render_stats_block(
    english: LanguageStats,
    russian: LanguageStats,
    *,
    language: str,
    has_missing: bool,
) -> str:
    tracker_link = (
        '<a class="handbook-hidden-link" href="../en/pages-review-tracker/" '
        'aria-label="Pages Review Tracker">▤</a>'
    )
    if language == "ru":
        shorts_label = "Короткие ответы"
        last_updated = "_Последнее обновление: {{LAST_UPDATED}}_"
    else:
        shorts_label = "Short answers"
        last_updated = "_Last updated: {{LAST_UPDATED}}_"
    shorts_link = (
        f'<a class="handbook-hidden-link" href="shorts/" '
        f'aria-label="{shorts_label}">⚡︎</a>'
    )

    return "\n".join(
        [
            f"## Handbook stats  {tracker_link}  {shorts_link}",
            "",
            last_updated,
            "",
            "| Metric | English | Russian |",
            "|---|---:|---:|",
            f"| Domains | {english.domains} | {russian.domains} |",
            f"| Pages | {english.pages} | {russian.pages} |",
            f"| Sections | {english.sections} | {russian.sections} |",
            f"| Topics | {english.topics} | {russian.topics} |",
            f"| Words | {english.words} | {russian.words} |",
            "",
            warning_block(language, has_missing).rstrip(),
        ]
    ).rstrip() + "\n"


def replace_marked_block(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    generated = f"{BEGIN_MARKER}\n{block}{END_MARKER}"

    if BEGIN_MARKER in text and END_MARKER in text:
        start = text.index(BEGIN_MARKER)
        end = text.index(END_MARKER, start) + len(END_MARKER)
        text = text[:start].rstrip() + "\n\n" + text[end:].lstrip()

    updated = text.rstrip() + "\n\n" + generated + "\n"

    path.write_text(updated, encoding="utf-8", newline="\n")


def print_missing_details(missing_ru: list[Path], missing_en: list[Path]) -> None:
    if not missing_ru and not missing_en:
        print("Translation sync: all content pages have matching counterparts.")
        return

    print("Translation sync warning:")
    if missing_ru:
        print("  English pages missing Russian counterpart:")
        for path in missing_ru:
            print(f"    - {relative_docs_path(path)}")
    if missing_en:
        print("  Russian pages missing English counterpart:")
        for path in missing_en:
            print(f"    - {relative_docs_path(path)}")


def main() -> int:
    if not DOCS_DIR.exists():
        print(f"Docs directory not found: {DOCS_DIR}", file=sys.stderr)
        return 1

    files = content_markdown_files()
    domains = count_domains()
    en_files = english_files(files)
    ru_files = russian_files(files)
    missing_ru, missing_en = missing_translation_pairs(files)
    has_missing = bool(missing_ru or missing_en)

    english = collect_stats(en_files, domains)
    russian = collect_stats(ru_files, domains)

    en_block = render_stats_block(english, russian, language="en", has_missing=has_missing)
    ru_block = render_stats_block(english, russian, language="ru", has_missing=has_missing)

    INCLUDES_DIR.mkdir(parents=True, exist_ok=True)
    (INCLUDES_DIR / "handbook-stats.md").write_text(en_block, encoding="utf-8", newline="\n")
    (INCLUDES_DIR / "handbook-stats.ru.md").write_text(ru_block, encoding="utf-8", newline="\n")

    replace_marked_block(DOCS_DIR / "index.md", en_block)
    replace_marked_block(DOCS_DIR / "index.ru.md", ru_block)

    print("Generated handbook stats:")
    print(f"  Domains:  {english.domains} EN / {russian.domains} RU")
    print(f"  Pages:    {english.pages} EN / {russian.pages} RU")
    print(f"  Sections: {english.sections} EN / {russian.sections} RU")
    print(f"  Topics:   {english.topics} EN / {russian.topics} RU")
    print(f"  Words:    {english.words} EN / {russian.words} RU")
    print_missing_details(missing_ru, missing_en)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
