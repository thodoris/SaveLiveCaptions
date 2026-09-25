'''
Floating dashboard that records Windows Live Captions to a text file.

    python src/main.py          # show the dashboard, press ● to record
    python src/main.py --auto   # start recording immediately (used by the hotkey worker)

The dashboard runs Tk and an asyncio loop on the same thread: every 10 ms
Tk hands control to asyncio for one iteration, which drives the caption
hook (function.texthook.hook). The global stop hotkey lives on its own
thread (function.hotkeys) and only sets a flag that the Tk loop polls.
'''
import argparse
import asyncio
import io
import sys
import threading
import tkinter as tk
import tkinter.messagebox as msgbox

from function import config, livecaptions
from function.hotkeys import HotkeyListener, format_hotkey
from function.save import choose_save_dir
from function.texthook import hook


class Dashboard:
    '''The small always-on-top window with the ● record and ◼ stop buttons.'''

    def __init__(self, loop: asyncio.AbstractEventLoop, auto_record: bool = False):
        self.loop = loop
        self.auto_record = auto_record
        self.exit_event = asyncio.Event()
        self.hook_task: asyncio.Task | None = None
        self.stopping = False
        self.destroyed = False
        self.stop_requested = threading.Event()  # set from the hotkey thread

        self.window = tk.Tk()
        self.window.title("CatchCaptionsTool")
        # Size to fit the buttons so they are not clipped on high-DPI displays
        self.window.geometry("+0+0")
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)

        self.window.bind("<ButtonPress-1>", self._start_move)
        self.window.bind("<B1-Motion>", self._do_move)

        stop_hint = f"Stop ({format_hotkey(config.STOP_HOTKEY)})"
        self.start_btn = tk.Button(self.window, text="⚫", command=self.start_capture)
        self.start_btn.pack(padx=10, pady=10)
        self.stop_btn = tk.Button(self.window, text="◼", command=self.stop_capture)
        self.stop_btn.pack(padx=10, pady=10)
        print(f"Dashboard ready. {stop_hint}")

    # --------------------------------------------------------
    # Recording
    # --------------------------------------------------------

    def start_capture(self) -> None:
        if self.hook_task is not None or self.stopping:
            return

        self.exit_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        filename = choose_save_dir()
        print(f"Recording captions to {filename}")
        self.hook_task = self.loop.create_task(hook(filename, self.exit_event))

    def stop_capture(self) -> None:
        '''Stop recording, save, and close the dashboard. Safe to call twice.'''
        if self.stopping:
            return
        self.stopping = True

        self.exit_event.set()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.loop.create_task(self._shutdown())

    async def _shutdown(self) -> None:
        if self.hook_task is not None:
            await self.hook_task  # hook() saves the remaining sentences and cleans the file
            self.hook_task = None

        if config.CLOSE_LIVE_CAPTIONS_ON_STOP:
            livecaptions.close()

        self.destroyed = True
        self.window.destroy()

    # --------------------------------------------------------
    # Window dragging
    # --------------------------------------------------------

    def _start_move(self, event: tk.Event) -> None:
        self._drag_x, self._drag_y = event.x, event.y

    def _do_move(self, event: tk.Event) -> None:
        x = self.window.winfo_x() + event.x - self._drag_x
        y = self.window.winfo_y() + event.y - self._drag_y
        self.window.geometry(f"+{x}+{y}")

    # --------------------------------------------------------
    # Event loop glue
    # --------------------------------------------------------

    def _poll(self) -> None:
        if self.destroyed:
            return

        if self.stop_requested.is_set():
            self.stop_requested.clear()
            print(f"{format_hotkey(config.STOP_HOTKEY)} pressed.")
            self.stop_capture()

        # Run one iteration of the asyncio loop
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()

        if not self.destroyed:
            self.window.after(10, self._poll)

    def run(self) -> None:
        if not livecaptions.is_running():
            msgbox.showerror("Error", "Live Captions Not Found")
            self.window.destroy()
            return

        hotkeys = HotkeyListener({config.STOP_HOTKEY: self.stop_requested.set})
        hotkeys.start()
        try:
            self.window.after(10, self._poll)
            if self.auto_record:
                # Give Tk a moment to show the window first
                self.window.after(1000, self.start_capture)
            self.window.mainloop()
        finally:
            hotkeys.stop()


def main(auto_record: bool = False) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        Dashboard(loop, auto_record=auto_record).run()
    finally:
        loop.close()


if __name__ == "__main__":
    # Captions may contain characters the console code page cannot show
    # (e.g. Chinese on a cp1253 console); never let print() end a recording.
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="replace")

    parser = argparse.ArgumentParser(description="Save Windows Live Captions to a text file.")
    parser.add_argument("--auto", action="store_true", help="start recording immediately")
    main(auto_record=parser.parse_args().auto)
