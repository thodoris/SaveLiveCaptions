import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from function.texthook import is_incomplete_sentence, split_into_sentences  # noqa: E402


class SplitIntoSentencesTest(unittest.TestCase):
    def test_splits_on_sentence_punctuation(self):
        text = "We add a new symbol entry to our table. We ensure that the symbols already exist."
        self.assertEqual(
            split_into_sentences(text),
            ["We add a new symbol entry to our table.", "We ensure that the symbols already exist."],
        )

    def test_does_not_split_decimals_or_urls(self):
        text = "The value is 3.14 today. Visit https://example.com/page for details."
        self.assertEqual(
            split_into_sentences(text),
            ["The value is 3.14 today.", "Visit https://example.com/page for details."],
        )

    def test_keeps_trailing_unfinished_text(self):
        sentences = split_into_sentences("This one is finished. And this one is still being spoken")
        self.assertEqual(sentences[-1], "And this one is still being spoken")

    def test_empty_input(self):
        self.assertEqual(split_into_sentences(""), [])


class IncompleteSentenceTest(unittest.TestCase):
    def test_english(self):
        self.assertFalse(is_incomplete_sentence("This is complete."))
        self.assertTrue(is_incomplete_sentence("This is still going"))
        self.assertTrue(is_incomplete_sentence("   "))


if __name__ == "__main__":
    unittest.main()
