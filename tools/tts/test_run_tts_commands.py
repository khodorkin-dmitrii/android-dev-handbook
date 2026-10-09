import unittest

import run_tts_commands


class RunTtsCommandsTest(unittest.TestCase):
    def test_format_remaining(self) -> None:
        self.assertEqual("00:00", run_tts_commands.format_remaining(0))
        self.assertEqual("00:59", run_tts_commands.format_remaining(59))
        self.assertEqual("16:00", run_tts_commands.format_remaining(960))
        self.assertEqual("61:01", run_tts_commands.format_remaining(3661))


if __name__ == "__main__":
    unittest.main()
