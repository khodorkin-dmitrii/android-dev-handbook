import re
import unittest
from importlib.metadata import version

from edge_tts.constants import SEC_MS_GEC_VERSION
from edge_tts.drm import generate_sec_ms_gec_v2

import synthesize_part


class EdgeTtsCompatibilityTest(unittest.TestCase):
    def test_pinned_package_uses_v2_handshake(self):
        self.assertEqual("7.3.0", version("edge-tts"))
        self.assertEqual("2-143.0.3650.75", SEC_MS_GEC_VERSION)
        synthesize_part.validate_edge_tts_protocol()

    def test_upstream_v2_token_vector(self):
        token = generate_sec_ms_gec_v2(1791888000)
        self.assertEqual(
            "492D7694A183A45E-56E821F95D4579C5B7C7E33DC7303FF379EC36D510213555BBBB9EB17EF15876",
            token,
        )
        self.assertRegex(token, re.compile(r"^[0-9A-F]{16}-[0-9A-F]{64}$"))


if __name__ == "__main__":
    unittest.main()
