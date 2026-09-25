'''
Resident background service that owns the global START hotkey.

Started at login by the Startup-folder shortcut that scripts/install.ps1
creates. On START_HOTKEY (default Win+Alt+C) it launches the recording
worker, AutoStartLiveCaptions.py, as a separate process; the worker itself
listens for STOP_HOTKEY. Logs go to logs/launcher.log.
'''
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from function import config, winapi  # noqa: E402
from function.applog import setup_logging  # noqa: E402
from function.hotkeys import HotkeyListener, format_hotkey  # noqa: E402

WORKER = ROOT / "AutoStartLiveCaptions.py"
MUTEX_NAME = "Local\\SaveLiveCaptionsHotkeyLauncher"

log = setup_logging("launcher")


def _pythonw() -> str:
    '''Prefer the windowless interpreter next to the one running us.'''
    candidate = Path(sys.executable).with_name("pythonw.exe")
    return str(candidate) if candidate.exists() else sys.executable


class Launcher:
    def __init__(self) -> None:
        self.worker: subprocess.Popen | None = None

    def on_start_hotkey(self) -> None:
        start = format_hotkey(config.START_HOTKEY)
        if self.worker is not None and self.worker.poll() is None:
            log.info("%s ignored: a recording is already running (stop it with %s).",
                     start, format_hotkey(config.STOP_HOTKEY))
            if config.HOTKEY_FEEDBACK_SOUND:
                winapi.beep(winapi.MB_ICONWARNING)
            return

        log.info("%s pressed; starting recorder.", start)
        if config.HOTKEY_FEEDBACK_SOUND:
            winapi.beep()
        try:
            self.worker = subprocess.Popen(
                [_pythonw(), str(WORKER)],
                cwd=ROOT,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            log.info("Recorder started (pid %d).", self.worker.pid)
        except OSError:
            log.exception("Could not start the recorder")


def main() -> int:
    log.info("=" * 60)
    log.info("SaveLiveCaptions hotkey launcher starting from %s", ROOT)

    if not winapi.acquire_single_instance_mutex(MUTEX_NAME):
        log.info("Another launcher is already running; exiting.")
        return 0

    launcher = Launcher()
    listener = HotkeyListener({config.START_HOTKEY: launcher.on_start_hotkey})
    listener.start()
    listener.wait_until_ready()

    if listener.failed:
        winapi.message_box(
            "SaveLiveCaptions",
            f"Could not register the hotkey {format_hotkey(config.START_HOTKEY)}.\n\n"
            "Another program is probably using it. Change START_HOTKEY in\n"
            f"{ROOT / 'src' / 'function' / 'config.py'}\n"
            "and run install.cmd -Restart.",
            winapi.MB_ICONERROR,
        )
        return 1

    log.info("Ready. Press %s to record, %s to stop.",
             format_hotkey(config.START_HOTKEY), format_hotkey(config.STOP_HOTKEY))
    listener.join()
    return 0


if __name__ == "__main__":
    sys.exit(main())
