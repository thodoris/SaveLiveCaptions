# Changes in this fork

This personal fork differs from
[LiveCaptionsHelper/SaveLiveCaptions](https://github.com/LiveCaptionsHelper/SaveLiveCaptions)
as described below. It is based on upstream commit `309ebae`
("[Fix] Fix exit bug with only incomplete sentence"). Fixes marked
*(upstream PR)* have also been offered to the original project.

## Hotkey workflow

- `HotkeyLauncher.pyw`: resident background service started at login. It
  registers **Win+Alt+C**, which starts a recording.
- `AutoStartLiveCaptions.py`: recording worker. It opens Windows Live Captions
  by running `LiveCaptions.exe` directly (no longer by sending the toggling
  `Ctrl+Win+L` shortcut), then starts recording right away.
- **Win+Alt+X** stops, saves, closes Live Captions and exits.
- Both hotkeys can be changed in `src/function/config.py`. A system sound
  confirms each key press. A message box appears if a hotkey is already taken.

## Installation

- `install.cmd` / `scripts/install.ps1`: creates `.venv`, installs
  dependencies, creates or repairs the Startup shortcut, and starts the
  service. Also supports `-Status`, `-Restart` and `-Uninstall`.
- Replaces the manual Startup shortcut and `StartSaveLiveCaptions.vbs`.

## Fixes

- **Stop hotkey never fired**: Tk's event loop consumed the `WM_HOTKEY`
  messages. Hotkeys now run on a dedicated listener thread (`function/hotkeys.py`).
- **Recording gave up after ~20 s of silence**: the recorder now waits for the
  first caption until you stop.
- **Decimals were split into two sentences** (`3.` / `14 today.`) in
  `split_into_sentences`. *(upstream PR:
  [#21](https://github.com/LiveCaptionsHelper/SaveLiveCaptions/pull/21))*
- **Spoken numbers were mangled during duplicate detection**: `word_to_number`
  matched number words inside other words and combined them wrongly
  ("twenty twenty six" became `406`, "nineteen eighty" became `9teen 8y`, and
  every letter "a" became `1`). It was rewritten to follow English number
  grammar, including years spoken in pairs, with unit tests.
- **Pressing stop twice** (button and hotkey) could crash while closing the window.
- **Printing a caption could end a recording** when the console code page cannot
  show it (for example, Chinese on a Greek console).
- **Buttons clipped on high-DPI displays**: the dashboard now sizes itself to
  fit its buttons.
- Background processes wrote nothing visible. Logs now go to `logs/`, and
  uiautomation's `@AutomationLog.txt` goes there too.
- Recordings from the `.exe` build would have been saved inside PyInstaller's
  temporary folder.
- Recordings are saved to `Downloads\SaveLiveCaptions-Recordings` of the
  current user, which OneDrive does not sync. The real folder is used even when
  it has been moved or redirected. `SAVE_DIR` accepts `~` and `%VARIABLES%`.

## Code structure

- New `function/livecaptions.py`, `hotkeys.py`, `winapi.py` and `applog.py`
  replace code that was copied in three places.
- `main.py`: a `Dashboard` class instead of module globals. Plain
  `python src/main.py` behaves like upstream. `--auto` starts recording
  immediately.
- `save.py`: removed an unused file handle that was never closed, plus
  duplicated similarity helpers.
- Unit tests in `tests/` for hotkey parsing and sentence splitting.
- `README.md` and `docs/ARCHITECTURE.md` rewritten and extended.
