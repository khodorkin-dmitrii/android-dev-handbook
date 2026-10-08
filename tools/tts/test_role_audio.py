import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import role_audio


class RoleAudioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = role_audio.build_manifest(False)
        cls.segments = role_audio.manifest_segments(cls.manifest)

    def test_default_scope_excludes_protected_chapter(self):
        chapters = {item.chapter for item in self.segments}
        self.assertEqual(9, len(chapters))
        self.assertNotIn(9, chapters)

    def test_expected_question_answer_counts(self):
        questions = [item for item in self.segments if item.kind == "question"]
        answers = [item for item in self.segments if item.kind == "answer"]
        self.assertEqual(131, len(questions))
        self.assertEqual(len(questions), len(answers))

    def test_batch_plan_has_two_shared_and_nine_answer_calls(self):
        batches = {item["id"] for item in self.manifest["batches"]}
        self.assertEqual(11, len(batches))
        self.assertIn("titles", batches)
        self.assertIn("questions", batches)
        self.assertNotIn("answers-09", batches)

    def test_synthetic_word_boundaries_align_to_segments(self):
        items = [item for item in self.segments if item.batch == "titles"][:2]
        words = []
        offset = 0
        for item in items:
            for word in item.tts_text.rstrip(".").split():
                words.append({"text": word, "offset": offset, "duration": 1_000_000})
                offset += 2_000_000
        positions = role_audio.align_boundaries(items, words)
        self.assertEqual([(0, 1), (2, 2)], positions)

    def test_srt_timestamp_rounding(self):
        self.assertEqual("00:01:02,346", role_audio.format_srt_time(62.3456))

    def test_subtitle_role_styling(self):
        self.assertEqual("<u>Computer Science</u>", role_audio.styled_subtitle_text("title", "Computer Science"))
        self.assertEqual("<i>Что такое SOLID?</i>", role_audio.styled_subtitle_text("question", "Что такое SOLID?"))
        self.assertEqual("Обычный ответ.", role_audio.styled_subtitle_text("answer", "Обычный ответ."))

    def test_preparation_artifacts_can_be_written_offline(self):
        with TemporaryDirectory(dir=role_audio.ROOT / "build") as temporary:
            previous_work_dir = role_audio.WORK_DIR
            previous_manifest = role_audio.MANIFEST
            try:
                role_audio.WORK_DIR = Path(temporary)
                role_audio.MANIFEST = Path(temporary) / "manifest.json"
                role_audio.write_prepared(self.manifest)
                self.assertTrue(role_audio.MANIFEST.exists())
                self.assertTrue((Path(temporary) / "plan.md").exists())
                self.assertEqual(
                    22,
                    len(list((Path(temporary) / "batches").iterdir())),
                )
            finally:
                role_audio.WORK_DIR = previous_work_dir
                role_audio.MANIFEST = previous_manifest


if __name__ == "__main__":
    unittest.main()
