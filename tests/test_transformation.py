"""Unit tests for converting spoken numbers to digits (function.transformation)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from function.dedup import Deduplicator  # noqa: E402
from function.transformation import word_to_number  # noqa: E402


class WordToNumberTest(unittest.TestCase):
    def check(self, cases):
        for spoken, expected in cases:
            with self.subTest(spoken=spoken):
                self.assertEqual(word_to_number(spoken), expected)

    def test_cardinals(self):
        self.check([
            ("zero", "0"),
            ("seven", "7"),
            ("nineteen", "19"),
            ("twenty six", "26"),
            ("twenty-six", "26"),
            ("three hundred and five", "305"),
            ("a hundred", "100"),
            ("two thousand", "2000"),
            ("two thousand twenty six", "2026"),
            ("one thousand five hundred", "1500"),
            ("twenty five hundred", "2500"),
            ("two million three hundred thousand", "2300000"),
        ])

    def test_years_spoken_in_pairs(self):
        self.check([
            ("twenty twenty six", "2026"),
            ("twenty twenty", "2020"),
            ("nineteen eighty", "1980"),
            ("nineteen eighty four", "1984"),
            ("twenty oh eight", "2008"),
            ("nineteen hundred", "1900"),
            ("twenty ten", "2010"),
        ])

    def test_ordinals(self):
        self.check([
            ("twenty first", "21st"),
            ("thirty second", "32nd"),
            ("one hundred and first", "101st"),
            ("the first time", "the first time"),
            ("wait one second", "wait 1 second"),
        ])

    def test_only_whole_words_are_converted(self):
        self.check([
            ("the cat sat on a mat", "the cat sat on a mat"),
            ("attention", "attention"),
            ("often someone", "often someone"),
            ("John and Anna", "John and Anna"),
            ("i have seven apples", "i have 7 apples"),
            ("oh no", "oh no"),
            ("tonight", "tonight"),
        ])

    def test_separate_numbers_stay_separate(self):
        self.check([
            ("one two three", "1 2 3"),
            ("five and six", "5 and 6"),
            ("hundred", "hundred"),
        ])

    def test_in_a_sentence(self):
        self.check([
            ("in twenty twenty six we had forty two members.",
             "in 2026 we had 42 members."),
        ])


class SimilarityTest(unittest.TestCase):
    def test_spoken_and_written_numbers_match(self):
        d = Deduplicator()
        self.assertEqual(
            d.similarity_ratio("It happened in twenty twenty six.", "It happened in 2026."), 1.0)
        self.assertEqual(
            d.similarity_ratio("We had forty two members.", "We had 42 members."), 1.0)


if __name__ == "__main__":
    unittest.main()
