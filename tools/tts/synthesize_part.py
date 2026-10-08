"""Synthesize one prepared text file and preserve raw WordBoundary metadata."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path


async def synthesize_once(args: argparse.Namespace, text: str, media_part: Path) -> list[dict[str, object]]:
    import edge_tts

    boundaries: list[dict[str, object]] = []
    communicate = edge_tts.Communicate(
        text,
        args.voice,
        rate=args.rate,
        volume=args.volume,
        pitch=args.pitch,
        boundary="WordBoundary",
    )
    with media_part.open("wb") as audio:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                boundaries.append(
                    {
                        "offset": chunk["offset"],
                        "duration": chunk["duration"],
                        "text": chunk["text"],
                    }
                )
    if not media_part.stat().st_size or not boundaries:
        raise RuntimeError("The service returned incomplete audio or no word boundaries")
    return boundaries


async def synthesize(args: argparse.Namespace) -> None:
    source = Path(args.file)
    media = Path(args.write_media)
    boundaries_path = Path(args.write_boundaries)
    text = source.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Input file is empty: {source}")

    media.parent.mkdir(parents=True, exist_ok=True)
    boundaries_path.parent.mkdir(parents=True, exist_ok=True)
    media_part = media.with_suffix(media.suffix + ".part")
    boundaries_part = boundaries_path.with_suffix(boundaries_path.suffix + ".part")
    try:
        boundaries = await synthesize_once(args, text, media_part)
        payload = {
            "schema": 1,
            "source": source.as_posix(),
            "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "voice": args.voice,
            "rate": args.rate,
            "volume": args.volume,
            "pitch": args.pitch,
            "boundary_type": "WordBoundary",
            "boundaries": boundaries,
        }
        boundaries_part.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        media_part.replace(media)
        boundaries_part.replace(boundaries_path)
    finally:
        media_part.unlink(missing_ok=True)
        boundaries_part.unlink(missing_ok=True)

    print(f"Audio: {media} ({media.stat().st_size} bytes)")
    print(f"Boundaries: {boundaries_path} ({len(boundaries)} words)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True)
    parser.add_argument("--write-media", required=True)
    parser.add_argument("--write-boundaries", required=True)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--rate", default="+0%")
    parser.add_argument("--volume", default="+0%")
    parser.add_argument("--pitch", default="+0Hz")
    args = parser.parse_args()
    try:
        asyncio.run(synthesize(args))
    except KeyboardInterrupt:
        parser.exit(130, "Canceled. No final output files were written.\n")
    except Exception as error:
        parser.exit(1, f"Synthesis failed ({type(error).__name__}): {error}\n")


if __name__ == "__main__":
    main()
