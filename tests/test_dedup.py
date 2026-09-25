"""Unit tests for sentence de-duplication (function.dedup)."""
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from function.dedup import Deduplicator  # noqa: E402


class BetterVersionTest(unittest.TestCase):
    def setUp(self):
        self.d = Deduplicator()

    def test_continuation_is_better(self):
        # Live Captions first showed "... last." and later "... last quarter."
        self.assertTrue(self.d.is_better_version(
            "Revenue grew by three point five percent last quarter.",
            "Revenue grew by three point five percent last."))

    def test_continuation_of_a_long_sentence_is_better(self):
        # one extra word is > 0.95 similar here, which used to count as "the same"
        old = "We discussed the budget for the new building and the timeline for the move in detail."
        new = "We discussed the budget for the new building and the timeline for the move in detail today."
        self.assertGreaterEqual(self.d.similarity_ratio(new, old), 0.95)
        self.assertTrue(self.d.is_better_version(new, old))

    def test_not_a_continuation(self):
        self.assertFalse(self.d.is_continuation("The weather is lasting.", "The weather is last."))
        self.assertFalse(self.d.is_continuation("Revenue grew.", "Revenue grew by five percent."))
        self.assertFalse(self.d.is_better_version("Hello there.", "Hello there."))


class CleanupFileTest(unittest.TestCase):
    def cleanup(self, lines):
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(line + "\n" for line in lines)
            with redirect_stdout(StringIO()):
                Deduplicator().cleanup_file(path)
            with open(path, encoding="utf-8") as f:
                return [line.rstrip("\n") for line in f]
        finally:
            os.remove(path)

    def test_contained_sentence_is_removed_regardless_of_case(self):
        # Transcript from a real test run: Live Captions moved "today" between sentences
        result = self.cleanup([
            "[00:31:45] This is a test of the recording hotkeys.",
            "[00:31:50] The value is three point one four today.",
            "[00:31:54] The value is three point one four.",
            "[00:31:55] Today the meeting was held in twenty twenty six.",
            "[00:31:59] The meeting was held in twenty twenty six.",
            "[00:31:59] Today.",
            "[00:32:00] Revenue grew by three point five percent last quarter.",
        ])
        self.assertEqual(result, [
            "[00:31:45] This is a test of the recording hotkeys.",
            "[00:31:50] The value is three point one four today.",
            "[00:31:55] Today the meeting was held in twenty twenty six.",
            "[00:32:00] Revenue grew by three point five percent last quarter.",
        ])

    def test_distinct_sentences_are_kept(self):
        lines = [
            "[10:00:00] Good morning everyone.",
            "[10:00:05] Let's start with the results from last week.",
            "[10:00:10] Revenue grew by 3.5 percent.",
        ]
        self.assertEqual(self.cleanup(lines), lines)


if __name__ == "__main__":
    unittest.main()
