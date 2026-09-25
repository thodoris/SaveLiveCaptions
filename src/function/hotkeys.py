'''
System-wide hotkeys via the Win32 RegisterHotKey API.

RegisterHotKey(NULL, ...) posts WM_HOTKEY to the *thread* that registered
it. That thread must own a message loop that nobody else drains: when the
hotkey was registered on the Tk thread, Tk's own event loop consumed the
WM_HOTKEY messages and the stop shortcut never fired. HotkeyListener
therefore runs its own dedicated thread with its own GetMessage loop.
'''
import ctypes
import logging
import threading
from ctypes import wintypes
from typing import Callable

from function.winapi import WM_HOTKEY, WM_QUIT, kernel32, user32

log = logging.getLogger(__name__)

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000  # holding the keys down does not fire repeatedly

_MODIFIERS = {
    "alt": MOD_ALT,
    "ctrl": MOD_CONTROL,
    "control": MOD_CONTROL,
    "shift": MOD_SHIFT,
    "win": MOD_WIN,
}


def parse_hotkey(combo: str) -> tuple[int, int]:
    '''
    Parse "win+alt+c" into (modifier flags, virtual-key code).
    Raises ValueError for anything unsupported.
    '''
    parts = [p.strip().lower() for p in combo.split("+") if p.strip()]
    if not parts:
        raise ValueError(f"Empty hotkey: {combo!r}")

    *modifier_names, key = parts
    modifiers = 0
    for name in modifier_names:
        if name not in _MODIFIERS:
            raise ValueError(f"Unknown modifier {name!r} in hotkey {combo!r}")
        modifiers |= _MODIFIERS[name]

    if len(key) == 1 and key.isalnum() and key.isascii():
        vk = ord(key.upper())  # VK codes for A-Z / 0-9 equal their ASCII codes
    elif key.startswith("f") and key[1:].isdigit() and 1 <= int(key[1:]) <= 24:
        vk = 0x70 + int(key[1:]) - 1  # VK_F1 = 0x70
    else:
        raise ValueError(f"Unsupported key {key!r} in hotkey {combo!r}")

    return modifiers, vk


def format_hotkey(combo: str) -> str:
    '''"win+alt+c" -> "Win+Alt+C"'''
    return "+".join(p.strip().capitalize() for p in combo.split("+"))


class HotkeyListener(threading.Thread):
    '''
    Registers hotkeys and invokes their callbacks from a background thread.

    Callbacks run on the listener thread, so they must be thread-safe
    (e.g. set a threading.Event that the GUI thread polls).
    '''

    def __init__(self, bindings: dict[str, Callable[[], None]]):
        super().__init__(name="HotkeyListener", daemon=True)
        self._bindings = bindings
        self._thread_id = 0
        self._ready = threading.Event()
        self.failed: list[str] = []  # combos that could not be registered

    def wait_until_ready(self, timeout: float = 5.0) -> bool:
        '''Block until registration finished; afterwards `failed` is populated.'''
        return self._ready.wait(timeout)

    def stop(self) -> None:
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)

    def run(self) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()
        callbacks: dict[int, Callable[[], None]] = {}

        for hotkey_id, (combo, callback) in enumerate(self._bindings.items(), start=1):
            try:
                modifiers, vk = parse_hotkey(combo)
            except ValueError as exc:
                log.error("%s", exc)
                self.failed.append(combo)
                continue

            if user32.RegisterHotKey(None, hotkey_id, modifiers | MOD_NOREPEAT, vk):
                callbacks[hotkey_id] = callback
                log.info("Global hotkey registered: %s", format_hotkey(combo))
            else:
                log.error(
                    "Could not register %s (Windows error %d); another program probably uses it.",
                    format_hotkey(combo), ctypes.get_last_error(),
                )
                self.failed.append(combo)

        self._ready.set()

        msg = wintypes.MSG()
        try:
            # GetMessageW returns 0 on WM_QUIT and -1 on error
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_HOTKEY and msg.wParam in callbacks:
                    try:
                        callbacks[msg.wParam]()
                    except Exception:
                        log.exception("Hotkey callback failed")
        finally:
            for hotkey_id in callbacks:
                user32.UnregisterHotKey(None, hotkey_id)
