'''
Writing captions to the transcript file.

Each line is "[HH:MM:SS] sentence". Lines can later be replaced in place
when a better (more complete) version of the same sentence arrives.
'''
import os
import time
import tkinter as tk
from tkinter import filedialog

import aiofiles

from function import config

saved_captions: list[tuple[float, str]] = []  # (time, caption) of recently saved lines
save_dir = os.path.expandvars(os.path.expanduser(config.SAVE_DIR)) if config.SAVE_DIR else ""


def choose_save_dir() -> str:
    '''
    Return the path of a new timestamped transcript file.
    If no save directory is configured, ask once with a folder picker.
    '''
    global save_dir

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    if not save_dir:
        root = tk.Tk()
        root.withdraw()
        save_dir = filedialog.askdirectory(
            title="choose direction",
            initialdir=os.path.expanduser("~")
        )
        root.destroy()

        if not save_dir:
            save_dir = config.DEFAULT_SAVE_DIR

    os.makedirs(save_dir, exist_ok=True)
    return os.path.join(save_dir, f"{timestamp}_captions.txt")


async def save_replace_txt(filename, old_caption: tuple[float, str], new_caption: tuple[float, str]):
    ''' Replace old caption with new caption '''
    t_old, cap_old = old_caption
    _, cap_new = new_caption
    t_formatted = time.strftime("%H:%M:%S", time.localtime(t_old))

    # read file and replace line
    async with aiofiles.open(filename, "r", encoding="utf-8") as f:
        lines = await f.readlines()

    for idx, line in enumerate(lines):
        if t_formatted in line and cap_old in line:
            lines[idx] = f"[{t_formatted}] {cap_new}\n"
            print(f"[REPLACE] Replaced:\n  OLD: {cap_old}\n  NEW: {cap_new}")
            break

    # write back to file
    async with aiofiles.open(filename, "w", encoding="utf-8") as f:
        await f.writelines(lines)


async def save_txt(filename, new_caption: tuple[float, str]):
    ''' Add new caption '''
    t, cap = new_caption
    t_formatted = time.strftime("%H:%M:%S", time.localtime(t))

    async with aiofiles.open(filename, "a", encoding="utf-8") as f:
        await f.write(f"[{t_formatted}] {cap}\n")
