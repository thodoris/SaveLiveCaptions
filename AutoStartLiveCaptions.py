import os
import sys
import time
import uiautomation as auto


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SRC_DIR = os.path.join(
    BASE_DIR,
    "src"
)

LIVE_CAPTIONS_WINDOW_TIMEOUT = 15


# ============================================================
# IMPORT SAVE LIVE CAPTIONS
# ============================================================

if SRC_DIR not in sys.path:
    sys.path.insert(
        0,
        SRC_DIR
    )

import main


# ============================================================
# FIND WINDOWS LIVE CAPTIONS
# ============================================================

def get_live_captions_window():

    try:

        auto.SetGlobalSearchTimeout(
            0.5
        )

        desktop = auto.GetRootControl()

        window = desktop.Control(
            searchDepth=1,
            ClassName="LiveCaptionsDesktopWindow"
        )

        if window.Exists(0.5):

            return window

    except Exception:

        pass

    return None


# ============================================================
# START WINDOWS LIVE CAPTIONS
# ============================================================

def start_windows_live_captions():

    print(
        "Starting Windows Live Captions..."
    )

    try:

        auto.SendKeys(
            "{Ctrl}{Win}l"
        )

    except Exception as exc:

        print(
            "ERROR sending Live Captions "
            f"shortcut: {exc}"
        )

        return False

    print(
        "Waiting for Windows Live Captions window..."
    )

    start = time.monotonic()

    while (
        time.monotonic() - start
        < LIVE_CAPTIONS_WINDOW_TIMEOUT
    ):

        window = (
            get_live_captions_window()
        )

        if window is not None:

            elapsed = (
                time.monotonic() - start
            )

            print(
                "Live Captions window detected "
                f"after {elapsed:.1f}s"
            )

            return True

        time.sleep(
            0.25
        )

    print(
        "ERROR: Windows Live Captions window "
        "was not detected."
    )

    return False


# ============================================================
# WORKFLOW
# ============================================================

def main_entry():

    print(
        "=" * 60
    )

    print(
        "SaveLiveCaptions - Automatic Mode"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # START / DETECT WINDOWS LIVE CAPTIONS
    # --------------------------------------------------------

    if (
        get_live_captions_window()
        is None
    ):

        if not start_windows_live_captions():

            print(
                "Could not start Windows Live Captions."
            )

            return 1

    else:

        print(
            "Windows Live Captions is already running."
        )

    # --------------------------------------------------------
    # START THE ORIGINAL APPLICATION
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # We deliberately do NOT create our own Tkinter dashboard.
    #
    # main.main() creates the original project's dashboard,
    # including its original 60x160 floating window and its
    # original Record / Stop buttons.
    #
    # The automatic recording behavior is implemented in
    # src/main.py.
    # --------------------------------------------------------

    print(
        "Starting original SaveLiveCaptions dashboard..."
    )

    main.main()

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    sys.exit(main_entry())