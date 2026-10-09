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

The default voice is `ru-RU-DmitryNeural` at rate `+25%`, volume `+0%`, pitch
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
build/tts-venv/Scripts/python tools/tts/generate.py --voice ru-RU-SvetlanaNeural --rate=+25% --volume=+0% --pitch=+0Hz --output build/audio/shorts-ru-preview-svetlana.mp3
```

`--output` changes both the MP3 and its matching `.txt` path. Relative paths
resolve from the repository root. Use a signed value such as `--rate=+25%`
with an equals sign. The voice determines pauses and pronunciation beyond the
explicit map. See the [edge-tts documentation](https://github.com/rany2/edge-tts)
for supported controls.

## Produce a role-based track

For a role-based track, keep every intermediate and review artifact together in
one ignored build directory. Use this naming pattern:

```text
build/audio/shorts-ru/09-ru-libraries-and-build/
```

The track number, language and short topic id must be in the directory name.
For English, use `build/audio/shorts-eng/NN-en-<topic-id>/`. Do not mix source
files from different tracks or languages in the same directory.

Split the track into ordered, independently generated segments. The current
Russian track 09 is the reference layout:

```text
01-title-andrew.txt / .mp3
02-question-1-svetlana.txt / .mp3
03-answer-1-dmitry.txt / .mp3
04-question-2-svetlana.txt / .mp3
05-answer-2-dmitry.txt / .mp3
09-ru-shorts-libraries-build.mp3       # assembled review track
09-ru-shorts-libraries-build.srt       # subtitle draft for review
timing.md                               # measured durations, trims and offsets
```

Use `docs/shorts.ru.md` as the canonical source for Russian wording and order,
and `docs/shorts.md` for English. The title is the section title, question
segments are the Markdown question headings, and answer segments contain only
their corresponding answer text. Keep canonical readable wording separate from
TTS text: Russian pronunciation-map spellings belong only in Russian `.txt`
files sent to speech synthesis, never in subtitles. Do not apply that map to
English; synthesize English from its canonical text.

The selected pilot voice sets are:

| Language | Section title | Question headings | Answers |
| --- | --- | --- | --- |
| Russian | `en-US-AndrewMultilingualNeural` (male) | `ru-RU-SvetlanaNeural` (female) | `ru-RU-DmitryNeural` (male) |
| English | `en-US-AndrewMultilingualNeural` (male) | `en-US-AriaNeural` (female) | `en-US-GuyNeural` (male) |

This keeps the male/female/male role pattern in both languages, while giving
the two male roles different voices. Treat these as the current pilot choices;
record the exact voice, rate, volume, pitch and pronunciation-map status for
each segment rather than relying on implicit defaults.

Synthesize each prepared text with an explicit command so all controls are
visible and repeatable. Example for an answer segment:

```powershell
build/tts-venv/Scripts/python -m edge_tts --voice ru-RU-DmitryNeural --rate=+25% --volume=+0% --pitch=+0Hz --file build/audio/shorts-ru/09-ru-libraries-and-build/03-answer-1-dmitry.txt --write-media build/audio/shorts-ru/09-ru-libraries-and-build/03-answer-1-dmitry.mp3
```

Change only the role voice and input/output segment paths for other segments.
Do not omit the explicit rate, volume or pitch.

### Use Edge TTS carefully

Edge TTS is a shared public service. Never submit segment syntheses in parallel
or launch a batch of concurrent requests. Submit one request, wait for it to
finish and verify the MP3, then wait at least 1 second before starting the next
request. If a request fails transiently, pause before retrying; do not repeat
segments that already succeeded. Retry one failed segment at most once, after a
5-second pause; if it fails again, stop and report the failure rather than
continuing to poll the service. Reuse valid segment files and synthesize only
the missing or deliberately changed text.

Generate only missing or intentionally changed segments. A failed synthesis
must not be mistaken for a current segment: verify each output exists, has a
plausible duration and corresponds to its adjacent `.txt`. Do not synthesize
the full track again just to change one role segment. Assemble the numbered
segments in order with FFmpeg. If trimming leading/trailing silence or adding
gaps, record the exact input trim points and gap lengths in `timing.md` before
or while assembling. Do not rely on undocumented manual edits.

## Timing notes and subtitle draft

`timing.md` is the compact timing ledger for the track. Keep measured values,
not estimates based on text length. Include:

- canonical source file and section heading;
- final assembled audio duration;
- for each segment: filename, role/voice, raw duration, trim-in and trim-out,
  assembled start/end, and deliberate pause after it;
- for each subtitle cue: cue number, corresponding question/answer phrase,
  segment-local start/end, and assembled start/end;
- any uncertain boundary that needs listening review.

Use this compact layout to make regeneration and subtitle follow-ups refer to
stable cue and segment ids without duplicating the full chapter text:

```md
# Timing: 09-ru-libraries-and-build

- Source: `docs/shorts.ru.md` - `Libraries and Build`
- Pronunciation map: `build/audio/pronunciation-ru.json` (record SHA-256)
- Assembled track: `09-ru-shorts-libraries-build.mp3`
- Assembled duration: `00:00:32.830`

## Segments

| ID | File | Voice / rate | Raw duration | Trim in-out | Track start-end | Gap after |
| --- | --- | --- | ---: | --- | --- | ---: |

## Cue alignment

| Cue | Segment | Segment-local start-end | Track start-end | Boundary evidence / review note |
| ---: | --- | --- | --- | --- |
```

Keep cue wording only in the SRT; use cue numbers and source order here. Record
times to milliseconds. For each cue boundary, note the audible pause or the
specific speech onset/offset used to place it. Mark uncertain boundaries rather
than filling them with guessed times.

Segment boundaries establish the search range for subtitle alignment. Within a
long answer, use the actual audio and natural pauses to place cue boundaries.
Use the canonical Markdown for subtitle wording and the speech-ready `.txt` only
to locate the spoken equivalent. Do not estimate timestamps from character or
word counts, regenerate wording from speech recognition, or change cue text while
doing a timing-only update.

### Required English/Russian cue parity

When English and Russian transcripts are both provided for a track, they must
have exactly the same number of cues in the same order. Match them one-to-one:
the title maps to the title, each question to its translation, and each answer
cue to the equivalent phrase or clause in the other language. Keep the phrase
boundaries semantically equivalent; matching cue count alone is not sufficient.
Use the canonical source for each language to verify wording. Timestamps are
aligned independently to each language's actual audio and do not need to match.
Before review or promotion, compare both SRTs cue by cue and confirm the 1:1
mapping. If a phrase cannot be matched cleanly, resolve the split or report it
for review instead of silently adding, omitting or combining a cue.

Whenever a segment is regenerated, remeasure its duration. Recalculate the
assembled offsets of all following segments and recheck affected subtitle cues;
do not carry old offsets forward. If only a segment's speech changes but its
position does not, still verify its internal cue boundaries against the new
audio. Before review, validate SRT numbering, syntax, positive durations,
chronological non-overlap and final cue end against the assembled MP3 duration.

Keep the working SRT draft beside the segments in the track directory. The user
reviews the assembled track and draft first. After approval, copy only the
approved MP3 and SRT into `docs/assets/audio/shorts/{ru|en}/` and
`docs/assets/audio/shorts/subtitles/{ru|en}/`, respectively. Update
`docs/assets/audio/shorts/manifest.json` only when a transcript URL/format needs
to be added or a published path changes. Then validate the manifest, build with
`mkdocs build --strict`, and verify that the expected assets were copied to
`site/`. A local copy in `docs/` is prepared for publication; it is not live
until the repository's deployment process runs.

## Keep follow-up tasks small

For a follow-up, specify the track id, language, exact canonical source, track
directory and the intended scope (text, selected role segments, assembly or
timing-only). Point to `timing.md` and the current SRT rather than restating the
whole chapter. Do not reopen or regenerate unrelated tracks. Preserve existing
segment choices unless the request changes them, and report only changed files,
measured duration, validation result and unresolved listening checks.

Generated audio, timing ledgers and subtitle drafts under `build/audio/` are
ignored by Git. The public copies under `docs/assets/audio/` are tracked source
files and should be updated only after user review. Do not commit or push unless
explicitly requested.

## Role-audio pipeline for the remaining Russian chapters

`role_audio.py` implements the staged publication workflow for chapters 01-08
and 10. Chapter 09 is protected and excluded from the default manifest because
its role-based audio and subtitles are already complete. The tool never moves
review artifacts into `docs/assets/`.

The preparation phase is local and makes no speech-service requests:

```powershell
build/tts-venv/Scripts/python tools/tts/role_audio.py prepare --dry-run
build/tts-venv/Scripts/python tools/tts/role_audio.py prepare
build/tts-venv/Scripts/python tools/tts/role_audio.py validate --stage prepared
```

It writes a machine-readable manifest, a human-readable plan, and eleven batch
descriptions under `build/audio/role-ru/`: one title batch, one question batch,
and one answer batch for each of the nine active chapters. Canonical text and
speech-ready text remain distinct. The manifest records source and
pronunciation-map hashes.

Before a live phase, inspect the exact work without contacting `edge-tts`:

```powershell
build/tts-venv/Scripts/python tools/tts/role_audio.py synthesize --group shared --dry-run
build/tts-venv/Scripts/python tools/tts/role_audio.py synthesize --group answers --chapter 01 --dry-run
```

Live synthesis is always sequential. It writes the raw batch MP3 and the
`WordBoundary` response metadata atomically, retries a failed batch once after
five seconds, waits between batches, and reuses a successful result when its
text and voice-setting fingerprint still matches:

```powershell
build/tts-venv/Scripts/python tools/tts/role_audio.py synthesize --group shared
build/tts-venv/Scripts/python tools/tts/role_audio.py validate --stage synthesized --group shared
build/tts-venv/Scripts/python tools/tts/role_audio.py synthesize --group answers
```

The remaining commands do not contact the speech service. Run `split` for the
same group after synthesis. It uses the saved word boundaries to create ordered
MP3 and Markdown artifacts inside each chapter directory. It fails instead of
guessing when the returned boundary text cannot be matched exactly.

```powershell
build/tts-venv/Scripts/python tools/tts/role_audio.py split --group shared
build/tts-venv/Scripts/python tools/tts/role_audio.py split --group answers
build/tts-venv/Scripts/python tools/tts/role_audio.py assemble
build/tts-venv/Scripts/python tools/tts/role_audio.py subtitles
build/tts-venv/Scripts/python tools/tts/role_audio.py validate --stage subtitles
```

Use repeatable `--chapter NN` filters for answer synthesis, splitting, assembly,
or subtitles when work should proceed one chapter at a time. Use `--force` only
when an existing current artifact must deliberately be replaced. The
`--include-protected` preparation option exists only for a future explicitly
approved rebuild of chapter 09 and must not be used in the current iteration.

### Run prepared answer parts sequentially

The manual answer-part plan for chapters 02-08 and 10 is stored in
`build/audio/role-ru/synthesis/answers-remaining-commands.txt`. Preview its
state without making network requests:

```powershell
build/tts-venv/Scripts/python tools/tts/run_tts_commands.py --commands build/audio/role-ru/synthesis/answers-remaining-commands.txt --dry-run
```

Run pending parts sequentially with the default 10-minute pause after every
completed command:

```powershell
build/tts-venv/Scripts/python -u tools/tts/run_tts_commands.py --commands build/audio/role-ru/synthesis/answers-remaining-commands.txt
```

The runner streams each child command's output to the console and appends the
same messages to `answers-remaining-commands.log`. It makes no automatic retry.
A repeated run skips parts that already have non-empty MP3 and boundary JSON
outputs. `Ctrl+C` stops the active command or pause. Use `--force` only to
deliberately regenerate completed parts, and use `--pause-seconds N` only when a
different interval is explicitly required.
