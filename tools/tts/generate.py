"""Generate a small Russian Shorts speech preview without changing the source."""

import argparse
import asyncio
import json
from pathlib import Path
import re

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/shorts.ru.md"
OUTPUT = ROOT / "build/audio/shorts-ru-preview-dmitry.mp3"
PRONUNCIATION_RU = ROOT / "build/audio/pronunciation-ru.json"
ITEM_COUNT = 1
DEFAULT_VOICE = "ru-RU-DmitryNeural"
CHAPTER_FILES = {
    "Computer Science": "01-ru-shorts-computer-science.txt",
    "Kotlin": "02-ru-shorts-kotlin.txt",
    "Android basics": "03-ru-shorts-android-basics.txt",
    "Jetpack Compose": "04-ru-shorts-jetpack-compose.txt",
    "Coroutines и Flow": "05-ru-shorts-coroutines-flow.txt",
    "Архитектура": "06-ru-shorts-architecture.txt",
    "Dependency Injection": "07-ru-shorts-dependency-injection.txt",
    "Networking": "08-ru-shorts-networking.txt",
    "Libraries and Build": "09-ru-shorts-libraries-build.txt",
    "Testing": "10-ru-shorts-testing.txt",
}
EN_CHAPTER_FILES = {
    "Computer Science": "01-en-shorts-computer-science.txt",
    "Kotlin": "02-en-shorts-kotlin.txt",
    "Android basics": "03-en-shorts-android-basics.txt",
    "Jetpack Compose": "04-en-shorts-jetpack-compose.txt",
    "Coroutines and Flow": "05-en-shorts-coroutines-flow.txt",
    "Architecture": "06-en-shorts-architecture.txt",
    "Dependency Injection": "07-en-shorts-dependency-injection.txt",
    "Networking": "08-en-shorts-networking.txt",
    "Libraries and Build": "09-en-shorts-libraries-build.txt",
    "Testing": "10-en-shorts-testing.txt",
}


def read_preview() -> str:
    """Read the first complete level-three section, ignoring fenced headings."""
    lines = []
    count = 0
    fence = None
    with SOURCE.open(encoding="utf-8") as source:
        for line in source:
            marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
            if fence:
                if (marker and marker[1][0] == fence[0]
                        and len(marker[1]) >= len(fence)
                        and not marker[2].strip()):
                    fence = None
            elif marker:
                fence = marker[1]
            else:
                heading = re.match(r"^ {0,3}(#{1,3})\s+", line)
                if heading:
                    if count == ITEM_COUNT:
                        break
                    if len(heading[1]) == 3:
                        count += 1
            lines.append(line)
    if count != ITEM_COUNT:
        raise ValueError(f"Expected {ITEM_COUNT} Q&A items in {SOURCE}")
    return "".join(lines)


def clean_inline(token) -> str:
    """Return visible inline text without Markdown syntax, code blocks or URLs."""
    parts = []
    for child in token.children or []:
        if child.type in {"text", "code_inline"}:
            parts.append(child.content)
        elif child.type in {"softbreak", "hardbreak"}:
            parts.append(" ")
    text = re.sub(r"(?:https?://|ftp://|www\.)\S+", "", "".join(parts))
    return re.sub(r"\s+", " ", text).strip()



def speech_text(markdown: str) -> str:
    """Keep inline text and paragraph boundaries; omit code blocks and URLs."""
    items = []
    current = None
    for token in MarkdownIt().parse(markdown):
        if token.type == "heading_open":
            if token.tag == "h3":
                current = []
                items.append(current)
            elif token.tag in {"h1", "h2"}:
                current = None
        elif token.type == "inline" and current is not None:
            text = clean_inline(token)
            if text:
                current.append(text)
    if len(items) != ITEM_COUNT or any(len(item) < 2 for item in items):
        raise ValueError("Each selected question must have a nonempty spoken answer")
    return "\n\n\n".join("\n\n".join(item) for item in items) + "\n"


def apply_russian_pronunciation(text: str, source: Path = SOURCE) -> str:
    """Replace whole Latin terms in extracted Russian speech text only."""
    if not source.name.endswith(".ru.md"):
        return text
    mapping = json.loads(PRONUNCIATION_RU.read_text(encoding="utf-8-sig"))
    if not isinstance(mapping, dict) or not mapping or any(
        not isinstance(term, str) or not term or not isinstance(spoken, str)
        or not spoken for term, spoken in mapping.items()
    ):
        raise ValueError(f"Invalid pronunciation map: {PRONUNCIATION_RU}")
    # A single pass avoids replacements inside replacement values. Case-folded
    # keys must be unique because matching no longer distinguishes case.
    folded = {}
    for term, spoken in mapping.items():
        key = term.casefold()
        if key in folded:
            raise ValueError(f"Duplicate pronunciation term ignoring case: {term}")
        folded[key] = spoken
    alternatives = "|".join(re.escape(term) for term in sorted(mapping, key=len, reverse=True))
    pattern = re.compile(
        r"(?<![A-Za-z0-9_])(?:" + alternatives + r")(?![A-Za-z0-9_])",
        flags=re.IGNORECASE,
    )
    return pattern.sub(lambda match: folded[match.group().casefold()], text)


def split_chapters(markdown: str) -> list[tuple[str, str]]:
    """Find real level-2 headings with the Markdown parser, ignoring code fences."""
    lines = markdown.splitlines(keepends=True)
    headings = []
    tokens = MarkdownIt().parse(markdown)
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2":
            title = clean_inline(tokens[index + 1])
            if not title or token.map is None:
                raise ValueError("A chapter heading has no title or source position")
            headings.append((title, token.map[0]))
    return [
        (title, "".join(lines[start:headings[index + 1][1]
                              if index + 1 < len(headings) else len(lines)]))
        for index, (title, start) in enumerate(headings)
    ]


def chapter_speech_text(markdown: str) -> tuple[str, int]:
    """Speak the chapter title once, then each complete question and answer."""
    title = None
    questions = []
    current = None
    heading = None
    for token in MarkdownIt().parse(markdown):
        if token.type == "heading_open":
            heading = token.tag
            if token.tag == "h3":
                current = []
                questions.append(current)
        elif token.type == "heading_close":
            heading = None
        elif token.type == "inline":
            text = clean_inline(token)
            if not text:
                continue
            if heading == "h2":
                title = text
            elif current is not None:
                current.append(text)
    if not title or not questions or any(len(item) < 2 for item in questions):
        raise ValueError(f"Chapter {title!r} needs a title and complete Q&A items")
    spoken = title + "\n\n" + "\n\n\n".join(
        "\n\n".join(item) for item in questions
    ) + "\n"
    return spoken, len(questions)


def generate_chapter_texts(
    source: Path = SOURCE,
    chapter_files: dict[str, str] = CHAPTER_FILES,
    output_dir: Path = ROOT / "build/audio/shorts-ru",
) -> None:
    chapters = split_chapters(source.read_text(encoding="utf-8"))
    titles = [title for title, _ in chapters]
    if len(titles) != len(set(titles)):
        raise ValueError("Duplicate chapter headings in Russian Shorts")
    missing = set(chapter_files) - set(titles)
    if missing:
        raise ValueError(f"Missing expected chapters: {sorted(missing)}")
    output_dir.mkdir(parents=True, exist_ok=True)
    for title, markdown in chapters:
        filename = chapter_files.get(title)
        if filename is None:
            print(f"Unmapped chapter: {title}")
            continue
        text, count = chapter_speech_text(markdown)
        text = apply_russian_pronunciation(text, source)
        output = output_dir / filename
        output.write_text(text, encoding="utf-8", newline="\n")
        print(f"{output}: {count} Q&A, {len(text)} characters")


async def synthesize(text: str, output: Path, args: argparse.Namespace) -> None:
    import edge_tts

    temporary = output.with_suffix(".mp3.part")
    try:
        await edge_tts.Communicate(
            text, args.voice, rate=args.rate, volume=args.volume, pitch=args.pitch,
        ).save(str(temporary))
        if not temporary.stat().st_size:
            raise RuntimeError("The service returned empty audio")
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-only", action="store_true",
                        help="Write debug text without contacting the speech service")
    chapters = parser.add_mutually_exclusive_group()
    chapters.add_argument("--chapters-text", action="store_true",
                          help="Write one TXT per Russian Shorts chapter; no audio")
    chapters.add_argument("--chapters-text-en", action="store_true",
                          help="Write one TXT per English Shorts chapter; no audio")
    parser.add_argument("--voice", default=DEFAULT_VOICE,
                        help=f"Microsoft voice name (default: {DEFAULT_VOICE})")
    parser.add_argument("--rate", default="-5%", help="Speech rate (default: -5%%)")
    parser.add_argument("--volume", default="+0%", help="Volume (default: +0%%)")
    parser.add_argument("--pitch", default="+0Hz", help="Pitch (default: +0Hz)")
    parser.add_argument("--output", type=Path, default=OUTPUT,
                        help="MP3 path; relative paths resolve from the repository root")
    args = parser.parse_args()
    if args.chapters_text:
        generate_chapter_texts()
        return
    if args.chapters_text_en:
        generate_chapter_texts(
            ROOT / "docs/shorts.md",
            EN_CHAPTER_FILES,
            ROOT / "build/audio/shorts-eng",
        )
        return
    for name, pattern in (("rate", r"[+-]\d+%"), ("volume", r"[+-]\d+%"),
                          ("pitch", r"[+-]\d+Hz")):
        if not re.fullmatch(pattern, getattr(args, name)):
            parser.error(f"Invalid --{name}; use a signed value such as "
                         + ("+0Hz" if name == "pitch" else "-5%"))
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.suffix.lower() != ".mp3":
        parser.error("--output must have an .mp3 extension")
    text = apply_russian_pronunciation(speech_text(read_preview()))
    output.parent.mkdir(parents=True, exist_ok=True)
    debug = output.with_suffix(".txt")
    debug.write_text(text, encoding="utf-8", newline="\n")
    print(f"Text: {debug} ({ITEM_COUNT} Q&A item, {len(text)} characters)")
    if args.text_only:
        return
    try:
        asyncio.run(synthesize(text, output, args))
    except (Exception, KeyboardInterrupt) as error:
        parser.exit(1, f"Speech generation failed ({type(error).__name__}): {error}\n"
                    "Debug text is ready; any previous MP3 is unchanged.\n")
    print(f"Audio: {output} ({output.stat().st_size} bytes; voice: {args.voice})")


if __name__ == "__main__":
    main()
