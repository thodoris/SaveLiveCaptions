import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from function import config  # noqa: E402
from function.hotkeys import (  # noqa: E402
    MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN, format_hotkey, parse_hotkey,
)


class ParseHotkeyTest(unittest.TestCase):
    def test_letter_with_modifiers(self):
        self.assertEqual(parse_hotkey("win+alt+c"), (MOD_WIN | MOD_ALT, ord("C")))

    def test_case_and_spaces_are_ignored(self):
        self.assertEqual(parse_hotkey(" Ctrl + Shift + x "), (MOD_CONTROL | MOD_SHIFT, ord("X")))

    def test_digit_and_function_keys(self):
        self.assertEqual(parse_hotkey("alt+1"), (MOD_ALT, ord("1")))
        self.assertEqual(parse_hotkey("win+f1"), (MOD_WIN, 0x70))
        self.assertEqual(parse_hotkey("win+f24"), (MOD_WIN, 0x87))

    def test_invalid_hotkeys_raise(self):
        for combo in ["", "win+alt", "hyper+c", "win+f25", "win+é", "win+space"]:
            with self.subTest(combo=combo):
                with self.assertRaises(ValueError):
                    parse_hotkey(combo)

    def test_configured_hotkeys_are_valid(self):
        parse_hotkey(config.START_HOTKEY)
        parse_hotkey(config.STOP_HOTKEY)

    def test_format(self):
        self.assertEqual(format_hotkey("win+alt+c"), "Win+Alt+C")


if __name__ == "__main__":
    unittest.main()
