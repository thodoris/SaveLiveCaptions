import sys
import os
import tkinter as tk
import tkinter.messagebox as msgbox
import ctypes
import ctypes.wintypes
import uiautomation as auto
from function.texthook import hook, lc_detect
from function.save import choose_save_dir, close_file
from function import save
import asyncio


HOTKEY_ID_STOP = 1001
WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_WIN = 0x0008

VK_X = 0x58


def register_stop_hotkey():
    result = ctypes.windll.user32.RegisterHotKey(
        None,
        HOTKEY_ID_STOP,
        MOD_ALT | MOD_WIN,
        VK_X
    )

    if result:
        print("Global hotkey registered: Win+Alt+X")
        return True

    print("WARNING: Could not register Win+Alt+X")
    return False


def unregister_stop_hotkey():
    ctypes.windll.user32.UnregisterHotKey(
        None,
        HOTKEY_ID_STOP
    )


def check_stop_hotkey(window, stop_callback):
    try:
        msg = ctypes.wintypes.MSG()

        while ctypes.windll.user32.PeekMessageW(
            ctypes.byref(msg),
            None,
            WM_HOTKEY,
            WM_HOTKEY,
            1
        ):
            if (
                msg.message == WM_HOTKEY
                and msg.wParam == HOTKEY_ID_STOP
            ):
                stop_callback()

    except Exception as exc:
        print(f"WARNING: Hotkey processing error: {exc}")

    try:
        if window.winfo_exists():
            window.after(
                50,
                check_stop_hotkey,
                window,
                stop_callback
            )
    except tk.TclError:
        pass


# ============================================================
# GLOBAL STATE
# ============================================================

file_handle = None
exit_event = asyncio.Event()
hook_task = None


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_live_captions():
    try:
        auto.SetGlobalSearchTimeout(0.5)

        desktop = auto.GetRootControl()

        captions_window = desktop.Control(
            searchDepth=1,
            ClassName="LiveCaptionsDesktopWindow"
        )

        if not captions_window.Exists(0.5):
            print("Windows Live Captions window not found.")
            return

        hwnd = captions_window.NativeWindowHandle

        if not hwnd:
            print("WARNING: Could not get Live Captions window handle.")
            return

        print("Closing Windows Live Captions...")

        WM_CLOSE = 0x0010

        result = ctypes.windll.user32.PostMessageW(
            hwnd,
            WM_CLOSE,
            0,
            0
        )

        if result:
            print("Windows Live Captions close request sent.")
        else:
            error = ctypes.GetLastError()
            print(
                f"WARNING: Could not send close request "
                f"(Windows error {error})."
            )

    except Exception as exc:
        print(
            f"WARNING: Could not close Windows Live Captions: {exc}"
        )

async def close_all(window):
    global hook_task

    if hook_task is not None:
        await hook_task
        hook_task = None

    await close_file()

    close_live_captions()

    unregister_stop_hotkey()

    window.destroy()


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(loop):

    window = tk.Tk()

    window.title("CatchCaptionsTool")

    # ORIGINAL PROJECT WINDOW
    window.geometry("60x160")
    window.overrideredirect(True)
    window.wm_attributes("-topmost", True)

    # --------------------------------------------------------
    # CHECK LIVE CAPTIONS
    # --------------------------------------------------------

    if not lc_detect():

        msgbox.showerror(
            "Error",
            "Live Captions Not Found"
        )

        window.destroy()

        return

    # --------------------------------------------------------
    # START CAPTURE
    # --------------------------------------------------------

    def start_capture():

        global hook_task

        exit_event.clear()

        start_btn.config(
            state=tk.DISABLED
        )

        stop_btn.config(
            state=tk.NORMAL
        )

        # save.save_dir is preconfigured in main().
        #
        # Therefore choose_save_dir() will NOT open the
        # folder-selection dialog.
        filename = choose_save_dir()

        print()
        print("=" * 60)
        print("Recording captions")
        print("=" * 60)
        print(
            f"Output file:\n{filename}"
        )

        hook_task = loop.create_task(
            hook(
                filename,
                exit_event
            )
        )

    # --------------------------------------------------------
    # STOP CAPTURE
    # --------------------------------------------------------

    def stop_capture():

        exit_event.set()

        start_btn.config(
            state=tk.NORMAL
        )

        stop_btn.config(
            state=tk.DISABLED
        )

        loop.create_task(
            close_all(window)
        )

    register_stop_hotkey()

    # --------------------------------------------------------
    # WINDOW DRAGGING
    # --------------------------------------------------------

    def start_move(event):

        window.x = event.x
        window.y = event.y

    def stop_move(event):

        window.x = None
        window.y = None

    def do_move(event):

        deltax = event.x - window.x
        deltay = event.y - window.y

        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay

        window.geometry(
            f"+{x}+{y}"
        )

    window.bind(
        "<ButtonPress-1>",
        start_move
    )

    window.bind(
        "<ButtonRelease-1>",
        stop_move
    )

    window.bind(
        "<B1-Motion>",
        do_move
    )

    # --------------------------------------------------------
    # ORIGINAL RECORD BUTTON
    # --------------------------------------------------------

    start_btn = tk.Button(
        window,
        text="⚫",
        command=start_capture
    )

    start_btn.pack(
        pady=10
    )

    # --------------------------------------------------------
    # ORIGINAL STOP BUTTON
    # --------------------------------------------------------

    stop_btn = tk.Button(
        window,
        text="◼",
        command=stop_capture
    )

    stop_btn.pack(
        pady=10
    )

    # --------------------------------------------------------
    # ASYNCIO POLLING
    # --------------------------------------------------------

    def poll_loop():
        try:
            if not window.winfo_exists():
                return

            loop.call_soon(
                loop.stop
            )

            loop.run_forever()

            if window.winfo_exists():
                window.after(
                    10,
                    poll_loop
                )

        except tk.TclError:
            # The Tk application has already been destroyed.
            # This can happen during normal shutdown when a
            # previously scheduled poll callback fires.
            return

    window.after(
        10,
        poll_loop
    )

    window.after(
        50,
        check_stop_hotkey,
        window,
        stop_capture
    )

    # --------------------------------------------------------
    # AUTOMATIC RECORDING
    # --------------------------------------------------------
    #
    # This is the only behavioral addition to the original
    # dashboard.
    #
    # The original dashboard remains visible and uses its
    # original Record / Stop buttons.
    #
    # We simply trigger the SAME start_capture() function
    # automatically after the window has been created.
    #
    # The 1-second delay gives Tkinter time to create/display
    # the original controller before recording starts.
    # --------------------------------------------------------

    def automatic_start():

        if not window.winfo_exists():
            return

        print(
            "Automatically starting recording..."
        )

        start_capture()

    window.after(
        1000,
        automatic_start
    )

    # --------------------------------------------------------
    # START ORIGINAL GUI
    # --------------------------------------------------------

    window.mainloop()


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # SAVE DIRECTORY
    # --------------------------------------------------------
    #
    # This is our other minimal modification.
    #
    # The original save.py defines:
    #
    #     save_dir = ""
    #
    # and opens the folder picker only when save_dir is empty.
    #
    # By setting it here, the original Record button continues
    # to work normally but no folder dialog appears.
    # --------------------------------------------------------

    save_dir = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "RecordedCaptions"
    )

    os.makedirs(
        save_dir,
        exist_ok=True
    )

    save.save_dir = save_dir

    print(
        "=" * 60
    )
    print(
        "SaveLiveCaptions"
    )
    print(
        "=" * 60
    )
    print(
        f"Recording directory:\n{save_dir}"
    )

    # --------------------------------------------------------
    # ASYNCIO
    # --------------------------------------------------------

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(
        loop
    )

    # --------------------------------------------------------
    # ORIGINAL DASHBOARD
    # --------------------------------------------------------

    dashboard(loop)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()