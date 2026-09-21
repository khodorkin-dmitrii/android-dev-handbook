# Experimental Russian Shorts audio

This standalone tool prepares one speech-ready TXT per top-level section of
`docs/shorts.ru.md` or `docs/shorts.md`. It can also use `edge-tts` to narrate
the **first complete Russian Q&A item** as a separate preview. It does not change handbook articles or
publish audio.

No API key, paid subscription or Microsoft Edge installation is required.
An internet connection is required only to synthesize the optional preview:
that text is sent to Microsoft's online speech service. This is AI-generated
speech.

## Setup

Use Python 3.10+ and run from the repository root:

```powershell
python -m venv build/tts-venv
build/tts-venv/Scripts/python -m pip install -r tools/tts/requirements.txt
```

If the environment already exists, only install the requirements. On macOS/Linux,
replace `build/tts-venv/Scripts/python` with `build/tts-venv/bin/python`.
Dependencies and generated files stay separate from the handbook build.

## Generate chapter texts

Each level-2 (`##`) section in `docs/shorts.ru.md` becomes one independent
speech-ready TXT in `build/audio/shorts-ru/`, in source order. This command makes no MP3
and does not contact the speech service:

```powershell
build/tts-venv/Scripts/python tools/tts/generate.py --chapters-text
```

The explicit heading-to-filename mapping in `generate.py` produces these files:

```text
01-ru-shorts-computer-science.txt
02-ru-shorts-kotlin.txt
03-ru-shorts-android-basics.txt
04-ru-shorts-jetpack-compose.txt
05-ru-shorts-coroutines-flow.txt
06-ru-shorts-architecture.txt
07-ru-shorts-dependency-injection.txt
08-ru-shorts-networking.txt
09-ru-shorts-libraries-build.txt
10-ru-shorts-testing.txt
```

Every TXT starts with its spoken chapter title, then contains the questions and
complete answers with paragraph boundaries. The same Markdown cleanup and
`build/audio/pronunciation-ru.json` substitutions used by the preview run independently
for each chapter. Unexpected section headings are reported as unmapped; a
missing expected section stops generation.

## Generate English chapter texts

The English source `docs/shorts.md` uses the same ten chapter boundaries and
Markdown cleanup. This command writes `01-en-shorts-computer-science.txt` through
`10-en-shorts-testing.txt` to `build/audio/shorts-eng/`:

```powershell
build/tts-venv/Scripts/python tools/tts/generate.py --chapters-text-en
```

Only TXT files are generated. The Russian pronunciation map is never applied to
this English source. The chapter title is spoken once before its questions and
answers. Generated files remain ignored by Git under `build/`.

## Generate the preview

```powershell
build/tts-venv/Scripts/python tools/tts/generate.py
```

The default voice is `ru-RU-DmitryNeural` at rate `-5%`, volume `+0%`, pitch
`+0Hz`. This command writes `build/audio/shorts-ru-preview-dmitry.txt` and
`build/audio/shorts-ru-preview-dmitry.mp3`.

To inspect the prepared text without a network request:

```powershell
build/tts-venv/Scripts/python tools/tts/generate.py --text-only
```

The text comes from the first `###` question and its entire answer, ending
before the next heading. Markdown cleanup preserves paragraphs, inline code
text, emphasis text and link labels while skipping raw URLs, images and code
blocks. Then the Russian pronunciation map replaces selected technical terms.
The `.txt` file contains exactly what is passed to `edge-tts`.

## Edit pronunciations

Edit `build/audio/pronunciation-ru.json` as an ordinary JSON object. Each key is
the original English term, and its value is the spoken Russian spelling:

```json
{
  "ViewModel": "Вью Модэл",
  "Repository": "Репозитори"
}
```

The local map was curated from the complete current Russian Shorts file.
It is ignored by Git and is not regenerated at runtime. Keep a private copy: a
fresh checkout needs this file before generating Russian speech text. Replacements match complete terms without regard to case, including phrases,
and longer terms take precedence. Use only one key per term regardless of case.
Unmapped terms remain unchanged.
In particular, short abbreviations such as `API` and `DI` are currently left
as written. Adjust the values after listening tests; the spelling is chosen
for understandable speech, not formal transliteration.

Replacements run only after Markdown extraction from a `.ru.md` source. The
canonical Markdown is never rewritten. The generated `.txt` is overwritten on
each run, so edit the JSON rather than the debug text when improving a term.
A manually edited TXT can still be synthesized directly with `python -m edge_tts
--file ...`, but `generate.py` always starts from Markdown.

## Options

List voices available from the live service:

```powershell
build/tts-venv/Scripts/python -m edge_tts --list-voices | Select-String 'ru-RU'
```

Override the voice or speech controls and choose a separate output:

```powershell
build/tts-venv/Scripts/python tools/tts/generate.py --voice ru-RU-SvetlanaNeural --rate=-10% --volume=+0% --pitch=+0Hz --output build/audio/shorts-ru-preview-svetlana.mp3
```

`--output` changes both the MP3 and its matching `.txt` path. Relative paths
resolve from the repository root. Use `--rate=-10%` with an equals sign for
negative values. The voice determines pauses and pronunciation beyond the
explicit map. See the [edge-tts documentation](https://github.com/rany2/edge-tts)
for supported controls.

Generated audio and debug text are intentionally not committed: `build/audio/`
is ignored by Git. Successful runs replace the selected MP3; failed runs retain
any previous MP3, which may no longer match newly written debug text. This remains
a small TTS experiment, not a publishing pipeline.
