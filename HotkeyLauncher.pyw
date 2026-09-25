import ctypes
import ctypes.wintypes
import os
import subprocess
import sys
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = os.path.join(
    BASE_DIR,
    ".venv",
    "Scripts",
    "pythonw.exe"
)

TARGET = os.path.join(
    BASE_DIR,
    "AutoStartLiveCaptions.py"
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "HotkeyLauncher.log"
)

HOTKEY_ID_START = 2001
WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_WIN = 0x0008

VK_C = 0x43
ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Global\\SaveLiveCaptionsHotkeyLauncher"

launcher_mutex = None
recording_process = None


def log(message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp} {message}\n")
    except OSError:
        pass


def acquire_launcher_mutex():
    global launcher_mutex

    launcher_mutex = ctypes.windll.kernel32.CreateMutexW(
        None,
        False,
        MUTEX_NAME
    )

    if not launcher_mutex:
        log("ERROR: Could not create launcher mutex.")
        return False

    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        log("Launcher already running; exiting duplicate instance.")
        return False

    return True


def find_running_process():
    return (
        recording_process is not None
        and recording_process.poll() is None
    )


def start_recording():
    global recording_process

    if find_running_process():
        log("Win+Alt+C ignored: recording is already running.")
        return

    log("Win+Alt+C pressed.")

    try:
        recording_process = subprocess.Popen(
            [PYTHON_EXE, TARGET],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        log("AutoStartLiveCaptions.py launched.")
    except Exception as exc:
        log(f"ERROR launching recording: {exc}")


def main():
    log("")
    log("=" * 60)
    log("SaveLiveCaptions Hotkey Launcher started")
    log("=" * 60)

    if not acquire_launcher_mutex():
        return 0

    result = ctypes.windll.user32.RegisterHotKey(
        None,
        HOTKEY_ID_START,
        MOD_ALT | MOD_WIN,
        VK_C
    )

    if not result:
        log("ERROR: Could not register Win+Alt+C.")
        return 1

    log("Global hotkey registered: Win+Alt+C")
    msg = ctypes.wintypes.MSG()

    try:
        while ctypes.windll.user32.GetMessageW(
            ctypes.byref(msg),
            None,
            0,
            0
        ) > 0:
            if (
                msg.message == WM_HOTKEY
                and msg.wParam == HOTKEY_ID_START
            ):
                start_recording()
    except Exception as exc:
        log(f"ERROR: Hotkey launcher stopped: {exc}")
        return 1
    finally:
        ctypes.windll.user32.UnregisterHotKey(
            None,
            HOTKEY_ID_START
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())