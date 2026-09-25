'''
Everything that talks to the Windows Live Captions app itself:
finding, starting and closing its window, and locating the control
that holds the caption text.
'''
import logging
import os
import subprocess
import time

import uiautomation as auto

from function import config
from function.winapi import WM_CLOSE, user32

log = logging.getLogger(__name__)

WINDOW_CLASS = "LiveCaptionsDesktopWindow"
CAPTIONS_AUTOMATION_ID = "CaptionsScrollViewer"
EXE_PATH = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "LiveCaptions.exe")

# uiautomation writes "@AutomationLog.txt" into the current directory by default
config.LOG_DIR.mkdir(parents=True, exist_ok=True)
auto.Logger.SetLogFile(str(config.LOG_DIR / "uiautomation.log"))


def find_window(timeout: float = 0.5) -> auto.Control | None:
    '''Return the Live Captions top-level window, or None if it is not open.'''
    try:
        window = auto.GetRootControl().Control(searchDepth=1, ClassName=WINDOW_CLASS)
        if window.Exists(timeout):
            return window
    except Exception as exc:
        log.debug("Live Captions lookup failed: %s", exc)
    return None


def is_running() -> bool:
    return find_window() is not None


def find_captions_control(window: auto.Control, timeout: float = 0.5) -> auto.Control | None:
    '''
    Return the ScrollViewer whose Name is the full caption text.
    Live Captions only creates it once the first caption appears.
    '''
    try:
        control = window.Control(
            searchDepth=10,
            AutomationId=CAPTIONS_AUTOMATION_ID,
            ClassName="ScrollViewer",
        )
        if control.Exists(timeout):
            return control
    except Exception as exc:
        log.debug("CaptionsScrollViewer lookup failed: %s", exc)
    return None


def _wait_for_modifiers_released(timeout: float = 2.0) -> None:
    '''The user may still be holding Win/Alt from the hotkey; don't mix them into our keys.'''
    modifier_keys = (0x5B, 0x5C, 0x10, 0x11, 0x12)  # LWin, RWin, Shift, Ctrl, Alt
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not any(user32.GetAsyncKeyState(vk) & 0x8000 for vk in modifier_keys):
            return
        time.sleep(0.05)


def start(timeout: float = 15.0) -> bool:
    '''Make sure Live Captions is open. Returns True once its window exists.'''
    if is_running():
        log.info("Windows Live Captions is already running.")
        return True

    log.info("Starting Windows Live Captions...")
    if os.path.exists(EXE_PATH):
        subprocess.Popen([EXE_PATH])
    else:
        # Fallback: the Ctrl+Win+L shortcut toggles Live Captions on/off
        _wait_for_modifiers_released()
        auto.SendKeys("{Ctrl}{Win}l")

    started = time.monotonic()
    while time.monotonic() - started < timeout:
        if find_window(timeout=0.25) is not None:
            log.info("Live Captions window detected after %.1fs", time.monotonic() - started)
            return True
        time.sleep(0.25)

    log.error("Windows Live Captions window did not appear within %.0fs.", timeout)
    return False


def close() -> None:
    '''Ask the Live Captions window to close (same as clicking its X).'''
    window = find_window()
    if window is None:
        log.info("Windows Live Captions window not found; nothing to close.")
        return

    hwnd = window.NativeWindowHandle
    if hwnd and user32.PostMessageW(hwnd, WM_CLOSE, 0, 0):
        log.info("Windows Live Captions close request sent.")
    else:
        log.warning("Could not close Windows Live Captions.")
