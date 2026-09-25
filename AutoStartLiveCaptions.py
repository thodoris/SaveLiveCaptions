'''
Recording worker: opens Windows Live Captions if needed, then shows the
dashboard and starts recording immediately.

Normally launched by HotkeyLauncher.pyw on START_HOTKEY, but it can also be
run by hand:  .venv\\Scripts\\python.exe AutoStartLiveCaptions.py
Logs go to logs/recorder.log.
'''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import main as dashboard  # noqa: E402
from function import livecaptions, winapi  # noqa: E402
from function.applog import setup_logging  # noqa: E402


def run() -> int:
    log = setup_logging("recorder")
    log.info("=" * 60)
    log.info("Recorder starting")

    if not livecaptions.start():
        winapi.message_box(
            "SaveLiveCaptions",
            "Windows Live Captions could not be started.\n\n"
            "Live Captions needs Windows 11 22H2 or later. Try opening it "
            "once with Ctrl+Win+L to finish its first-run setup.",
            winapi.MB_ICONERROR,
        )
        return 1

    try:
        dashboard.main(auto_record=True)
    except Exception:
        log.exception("Recorder crashed")
        return 1

    log.info("Recorder finished")
    return 0


if __name__ == "__main__":
    sys.exit(run())
