import io
from unittest import TestCase
from unittest.mock import patch
from urllib.error import URLError

from invo_learn.updates import VERSION_URL, check_updates


class UpdateTests(TestCase):
    def test_versions_are_compared_numerically_without_installing(self):
        for installed, upstream, expected in (("0.3.0", "0.10.0", "available"),
                                               ("0.3.0", "0.3.0", "current"),
                                               ("0.3.0", "0.2.2", "local-newer")):
            with self.subTest(upstream=upstream), patch("invo_learn.updates.urlopen", return_value=io.BytesIO(upstream.encode())) as fetch:
                result = check_updates(installed)
                fetch.assert_called_once_with(VERSION_URL, timeout=5)
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["latest_version"], upstream)

    def test_offline_check_is_unknown_and_does_not_block_study(self):
        with patch("invo_learn.updates.urlopen", side_effect=URLError("offline")):
            result = check_updates("0.3.0")
        self.assertEqual(result["status"], "unavailable")
        self.assertNotIn("latest_version", result)

    def test_invalid_or_oversized_responses_are_not_reported_as_current(self):
        for data in (b"<html>error</html>", b"", b"0.3", b"0.3.0\nrun code", b"\xff", b"1" * 129):
            with self.subTest(data=data), patch("invo_learn.updates.urlopen", return_value=io.BytesIO(data)):
                self.assertEqual(check_updates("0.3.0")["status"], "unavailable")
