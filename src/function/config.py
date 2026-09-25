'''
User-editable settings for SaveLiveCaptions.

Everything you are likely to want to change lives in this file:
caption-quality thresholds, where transcripts are saved, and the
global hotkeys used by the background launcher.
'''
import os
import sys
from pathlib import Path

from function.winapi import FOLDERID_DOCUMENTS, FOLDERID_DOWNLOADS, known_folder

# ============================================================
# Paths
# ============================================================

# True when running as a PyInstaller-built .exe
FROZEN = getattr(sys, 'frozen', False)

# Folder that contains src/, HotkeyLauncher.pyw, ... (or the .exe when frozen)
PROJECT_ROOT = Path(sys.executable).parent if FROZEN else Path(__file__).resolve().parents[2]

# The current user's folders, wherever they really are (OneDrive, other drive, ...)
DOCUMENTS_DIR = known_folder(FOLDERID_DOCUMENTS, "Documents")
DOWNLOADS_DIR = known_folder(FOLDERID_DOWNLOADS, "Downloads")

# Default transcript folder. Downloads is used because, unlike Documents,
# it is not synced by OneDrive folder backup.
DEFAULT_SAVE_DIR = os.path.join(DOWNLOADS_DIR, "SaveLiveCaptions-Recordings")

# Where caption files are written. Examples:
#   DEFAULT_SAVE_DIR                      Downloads\SaveLiveCaptions-Recordings (default)
#   os.path.join(DOCUMENTS_DIR, "Captions")   Documents (may be synced by OneDrive)
#   "~/Recordings"                        ~ = the current user's profile folder
#   "%USERPROFILE%\\Desktop\\Captions"     environment variables are expanded
#   ""                                    ask with a folder picker each time (upstream behaviour)
SAVE_DIR = DEFAULT_SAVE_DIR

# Launcher / recorder / uiautomation logs
LOG_DIR = PROJECT_ROOT / "logs"

# ============================================================
# Hotkeys (used by HotkeyLauncher.pyw and the dashboard)
# ============================================================
# Format: modifiers and one key joined with "+", case-insensitive.
# Modifiers: win, alt, ctrl, shift.  Keys: A-Z, 0-9, F1-F24.
# After changing these, restart the launcher: install.cmd -Restart

# Start Windows Live Captions and begin recording
START_HOTKEY = "win+alt+c"

# Stop recording, save the file and exit
STOP_HOTKEY = "win+alt+x"

# Play a short system sound when a hotkey is received,
# so you can tell the key press reached the launcher.
HOTKEY_FEEDBACK_SOUND = True

# Close the Windows Live Captions window when recording stops
CLOSE_LIVE_CAPTIONS_ON_STOP = True

# ============================================================
# Caption capture quality (texthook)
# ============================================================

# The threshold for considering sentences as stable
# default is 3, meaning a sentence must be observed 3 times to be considered stable
STABLE_THRESHOLD = 3

# The maximum number of saved sentences to keep in memory
# default is 50
MAX_SAVED_SENTENCES = 50

# The minimum length of a sentence to be considered for saving
# default is 10 characters
MIN_LENGTH = 10

# WHEN TEXTHOOKING the similarity threshold for considering two sentences as similar
# default is 0.85, meaning sentences with similarity above 0.85 will be considered similar
SIMILARITY = 0.85
