import unittest

import prepare_system_design_audio as system_design_audio


class SystemDesignAudioPreparationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.segments, cls.diagram_ids = system_design_audio.build_segments()
        cls.batches = system_design_audio.request_batches(cls.segments)

    def test_expected_structure(self) -> None:
        self.assertEqual(8, sum(item.kind == "title" for item in self.segments))
        self.assertEqual(104, sum(item.kind == "question" for item in self.segments))
        self.assertEqual(104, sum(item.kind == "answer" for item in self.segments))
        self.assertEqual(
            ["application-architecture-vs-system-design", "cache-aside-flow"],
            self.diagram_ids,
        )

    def test_diagrams_use_semantic_narration(self) -> None:
        answers = {item.id: item for item in self.segments if item.kind == "answer"}
        architecture = answers["01-answer-02"].canonical_text
        cache_aside = answers["04-answer-03"].canonical_text
        self.assertIn("поток обычно идёт", architecture)
        self.assertIn("При cache miss", cache_aside)
        self.assertNotIn("->", architecture)
        self.assertNotIn("+->", cache_aside)

    def test_requests_preserve_segments_and_word_limit(self) -> None:
        self.assertEqual(20, len(self.batches))
        self.assertTrue(all(batch["words"] <= system_design_audio.WORD_LIMIT for batch in self.batches))
        prepared_ids = [segment_id for batch in self.batches for segment_id in batch["segment_ids"]]
        expected_ids = [item.id for item in self.segments]
        self.assertCountEqual(expected_ids, prepared_ids)

    def test_commands_use_isolated_collection_directory(self) -> None:
        line = system_design_audio.command(self.batches[0])
        self.assertIn("build\\audio\\system-design-shorts-ru\\role-ru", line)
        self.assertNotIn("build\\audio\\shorts-ru\\role-ru", line)


if __name__ == "__main__":
    unittest.main()
