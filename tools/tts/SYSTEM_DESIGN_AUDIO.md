# System Design audio narration

The source Markdown remains optimized for reading. Audio preparation may add a
separate spoken representation without changing the article.

## Text diagrams

Fenced `text` diagrams must not be read literally. Every diagram used by the
Russian audio pipeline must have an explicit entry in
`system_design_diagrams.ru.json`. Preparation fails when it encounters an
unregistered `text` diagram.

The narration preserves engineering meaning rather than visual layout:

- a linear flow becomes a sequence of actions;
- a conditional branch becomes an `if` or `otherwise` explanation;
- fan-out becomes distribution to independent consumers;
- labels such as `miss`, `retry`, `timeout`, `event`, and `ack` become
  conditions or actions;
- ASCII symbols such as arrows, bars, slashes, and plus signs are never spoken.

The replacement should be concise enough for a Short. It is included in the
audio transcript and subtitles, while the original diagram remains unchanged
in the article.

## Roles

- section titles: `en-US-AndrewMultilingualNeural`;
- questions: `ru-RU-SvetlanaNeural`;
- answers and semantic diagram narration: `ru-RU-DmitryNeural`.

Prepared Edge TTS requests are limited to complete semantic segments and a
maximum of 200 words. A question or answer is never split in the middle.
