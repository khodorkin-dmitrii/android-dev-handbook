"""Run prepared Edge TTS part commands sequentially with a fixed pause."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shlex
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PYTHON = (ROOT / "build/tts-venv/Scripts/python.exe").resolve()
EXPECTED_SCRIPT = (ROOT / "tools/tts/synthesize_part.py").resolve()
PATH_OPTIONS = ("--file", "--write-media", "--write-boundaries")


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def normalized_path(value: str) -> Path:
    unquoted = value.strip('"')
    path = Path(unquoted.replace("\\", "/"))
    return (path if path.is_absolute() else ROOT / path).resolve()


def parse_command(line: str) -> tuple[list[str], Path, Path]:
    arguments = [value.strip('"') for value in shlex.split(line, posix=False)]
    if len(arguments) < 2:
        raise ValueError("Command is incomplete")
    executable = normalized_path(arguments[0])
    script = normalized_path(arguments[1])
    if executable != EXPECTED_PYTHON or script != EXPECTED_SCRIPT:
        raise ValueError("Only the prepared synthesize_part.py command is allowed")
    arguments[0] = str(executable)
    arguments[1] = str(script)

    resolved: dict[str, Path] = {}
    for option in PATH_OPTIONS:
        try:
            index = arguments.index(option)
        except ValueError as error:
            raise ValueError(f"Required option is missing: {option}") from error
        if index + 1 >= len(arguments):
            raise ValueError(f"Option has no value: {option}")
        path = normalized_path(arguments[index + 1])
        try:
            path.relative_to(ROOT)
        except ValueError as error:
            raise ValueError(f"Path leaves the repository: {path}") from error
        arguments[index + 1] = str(path)
        resolved[option] = path
    return arguments, resolved["--write-media"], resolved["--write-boundaries"]


def output_is_complete(media: Path, boundaries: Path) -> bool:
    return (
        media.exists()
        and media.stat().st_size > 0
        and boundaries.exists()
        and boundaries.stat().st_size > 0
    )


def emit(message: str, log_file) -> None:
    print(message, flush=True)
    log_file.write(message + "\n")
    log_file.flush()


def has_pending(commands: list[tuple[str, list[str], Path, Path]], start: int, force: bool) -> bool:
    return any(force or not output_is_complete(media, boundaries) for _, _, media, boundaries in commands[start:])


def run(args: argparse.Namespace) -> int:
    commands_path = normalized_path(args.commands)
    if not commands_path.exists():
        raise FileNotFoundError(f"Command file does not exist: {commands_path}")
    raw_lines = [line.strip() for line in commands_path.read_text(encoding="utf-8").splitlines()]
    raw_lines = [line for line in raw_lines if line and not line.startswith("#")]
    if not raw_lines:
        raise ValueError("Command file contains no commands")

    commands = []
    for line_number, line in enumerate(raw_lines, start=1):
        try:
            parsed, media, boundaries = parse_command(line)
        except ValueError as error:
            raise ValueError(f"Line {line_number}: {error}") from error
        commands.append((line, parsed, media, boundaries))

    log_path = normalized_path(args.log) if args.log else commands_path.with_suffix(".log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        print(f"Commands: {len(commands)}")
        print(f"Pause: {args.pause_seconds:.0f} seconds")
        print(f"Log: {log_path}")
        for index, (line, _, media, boundaries) in enumerate(commands, start=1):
            state = "COMPLETE" if output_is_complete(media, boundaries) else "PENDING"
            print(f"[{index:02d}/{len(commands):02d}] {state} {line}")
        return 0

    failures: list[tuple[int, int, str]] = []
    completed = 0
    skipped = 0
    with log_path.open("a", encoding="utf-8") as log_file:
        emit(f"=== Run started {timestamp()} ===", log_file)
        emit(f"Commands: {commands_path}", log_file)
        emit(f"Pause after each executed command: {args.pause_seconds:.0f} seconds", log_file)
        for index, (line, command, media, boundaries) in enumerate(commands, start=1):
            label = f"[{index:02d}/{len(commands):02d}]"
            if not args.force and output_is_complete(media, boundaries):
                skipped += 1
                emit(f"{label} SKIP complete: {media.name}", log_file)
                continue
            emit(f"{label} START {timestamp()}", log_file)
            emit(f"{label} COMMAND {line}", log_file)
            started = time.monotonic()
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            try:
                assert process.stdout is not None
                for output_line in process.stdout:
                    emit(f"{label} | {output_line.rstrip()}", log_file)
                return_code = process.wait()
            except KeyboardInterrupt:
                process.terminate()
                process.wait()
                emit(f"{label} CANCELED {timestamp()}", log_file)
                raise
            elapsed = time.monotonic() - started
            if return_code == 0 and output_is_complete(media, boundaries):
                completed += 1
                emit(f"{label} OK {timestamp()} elapsed={elapsed:.1f}s", log_file)
            else:
                failures.append((index, return_code, media.name))
                emit(
                    f"{label} FAILED {timestamp()} exit={return_code} elapsed={elapsed:.1f}s",
                    log_file,
                )
            if has_pending(commands, index, args.force):
                emit(f"{label} PAUSE {args.pause_seconds:.0f}s", log_file)
                time.sleep(args.pause_seconds)
        emit(
            f"=== Run finished {timestamp()}: completed={completed}, skipped={skipped}, failed={len(failures)} ===",
            log_file,
        )
        for index, return_code, name in failures:
            emit(f"FAILED [{index:02d}] exit={return_code} output={name}", log_file)
    return 1 if failures else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commands", required=True)
    parser.add_argument("--pause-seconds", type=float, default=600.0)
    parser.add_argument("--log")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.pause_seconds < 0:
        parser.error("--pause-seconds must be zero or greater")
    try:
        raise SystemExit(run(args))
    except KeyboardInterrupt:
        parser.exit(130, "Canceled by user.\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
