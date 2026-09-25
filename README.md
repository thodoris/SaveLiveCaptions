# Save Live Captions (personal fork)

> [!NOTE]
> **This is a personal project and a fork.** It is a fork of
> [LiveCaptionsHelper/SaveLiveCaptions](https://github.com/LiveCaptionsHelper/SaveLiveCaptions)
> by M.T.Arden, adapted for my own daily use on Windows 11. It is **not
> affiliated with or endorsed by** the original authors. It is shared as is,
> without support or release guarantees, and may change at any time.
> For the original application, its releases and its issue tracker, go to the
> [original repository](https://github.com/LiveCaptionsHelper/SaveLiveCaptions).

Save the text of **Windows Live Captions** to timestamped text files, so a
meeting, lecture or video you listened to can be read back later.

What this fork adds on top of the original (details in [CHANGES.md](CHANGES.md)):

- a background **hotkey workflow**: one key combination opens Live Captions and
  starts recording, another stops and saves
- a one-step **installer** with autostart at login, plus status, restart and uninstall
- log files, configurable hotkeys and save folder, and several bug fixes
- restructured code with unit tests and [architecture documentation](docs/ARCHITECTURE.md)

```text
[10:02:13] Good morning everyone, let's start with the results from last week.
[10:02:19] Revenue grew by 3.5 percent compared to the previous quarter.
```

## Requirements

- Windows 11 22H2 or later (that is where Live Captions exists; try `Ctrl+Win+L`).
  Open Live Captions once by hand first to finish its setup and language download.
- Python 3.10 or newer from [python.org](https://www.python.org/downloads/)
  (tick *Add python.exe to PATH* during setup).

Developed and tested on Windows 11 (build 26200) with Python 3.12.

## Quick start (hotkey workflow)

```powershell
git clone https://github.com/thodoris/SaveLiveCaptions.git
cd SaveLiveCaptions
.\install.cmd
```

`install.cmd` creates a virtual environment in `.venv`, installs the
dependencies, adds a shortcut to your **Startup folder** so the hotkey service
starts every time you log in, and starts it right away.

| Hotkey | Action |
| --- | --- |
| **Win + Alt + C** | Open Windows Live Captions and start recording |
| **Win + Alt + X** | Stop, save the file, close Live Captions |

You hear a short system sound when a hotkey is received. While recording, the
small dashboard (● / ◼) sits in the top-left corner; its ◼ button stops too.
Transcripts go to `Downloads\SaveLiveCaptions-Recordings\YYYY-MM-DD_HH-MM-SS_captions.txt`
in your user folder. Downloads is used because OneDrive does not sync it, unlike Documents.

Live Captions transcribes whatever your PC plays. To include what *you* say,
enable **Include microphone audio** in the Live Captions settings (gear icon).

### Managing the service

```powershell
.\install.cmd -Status      # running? which folder? autostart OK? last log lines
.\install.cmd -Restart     # after editing src\function\config.py
.\install.cmd              # after moving the folder or `git pull` - repairs everything
.\install.cmd -Uninstall   # stop it and remove autostart (keeps your recordings)
```

The service runs from the folder you installed it from. **If you move the
folder, run `install.cmd` again from the new location**; otherwise the Startup
shortcut points to a folder that no longer exists.

## Configuration

Everything is in [`src/function/config.py`](src/function/config.py):

| Setting | Default | Meaning |
| --- | --- | --- |
| `SAVE_DIR` | `Downloads\SaveLiveCaptions-Recordings` | Where transcripts go. `~` and `%VARIABLES%` are expanded, so paths can be relative to the current user. `""` = ask with a folder picker |
| `START_HOTKEY` / `STOP_HOTKEY` | `win+alt+c` / `win+alt+x` | Modifiers `win alt ctrl shift` + a key `A-Z 0-9 F1-F24` |
| `HOTKEY_FEEDBACK_SOUND` | `True` | Beep when a hotkey is received |
| `CLOSE_LIVE_CAPTIONS_ON_STOP` | `True` | Close the Live Captions window after saving |
| `STABLE_THRESHOLD`, `SIMILARITY`, ... | | Caption de-duplication quality, see comments in the file |

Run `install.cmd -Restart` after changing hotkeys. Other settings apply to the
next recording.

## Other ways to run it

- **Dashboard only** (the original upstream behaviour): open Live Captions,
  then `.venv\Scripts\python.exe src\main.py`. Press ● to record, ◼ to stop and
  exit. Add `--auto` to start recording immediately.
- **Recorder without hotkeys**: `.venv\Scripts\python.exe AutoStartLiveCaptions.py`
  opens Live Captions and starts recording.
- **Prebuilt .exe**: this fork publishes no releases. The original project's
  [Releases](https://github.com/LiveCaptionsHelper/SaveLiveCaptions/releases)
  page has builds of the original app, without this fork's hotkey workflow.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Pressing Win+Alt+C does nothing, no sound | `install.cmd -Status`. If it is not running, run `install.cmd`. Use the **left** Alt key: on keyboard layouts with AltGr, right Alt counts as Ctrl+Alt. |
| A message says the hotkey could not be registered | Another program uses that combination. Change `START_HOTKEY` in `config.py`, then `install.cmd -Restart`. |
| Win+Alt+C beeps differently and nothing happens | A recording is already running. Stop it first with Win+Alt+X. |
| Recording starts but the file stays empty | Live Captions only shows text once it hears speech. Check the Live Captions window shows captions. For your own voice, enable *Include microphone audio*. |
| Worked before, broke after a Windows update | Open Live Captions and run `.venv\Scripts\python.exe scripts\diagnose_live_captions.py`. It shows whether the `CaptionsScrollViewer` control still exists. |
| Anything else | Check `logs\launcher.log` (hotkey service) and `logs\recorder.log` (each recording). |

## How it works

Live Captions exposes its text through Windows UI Automation. The recorder
polls that text four times a second, splits it into sentences, waits until a
sentence is stable, and appends it to the file. Improved versions of a sentence
replace earlier ones, and duplicates are cleaned up when you stop. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the components and data flow.

## Repository layout

| Path | Purpose |
| --- | --- |
| `install.cmd`, `scripts/install.ps1` | Install, repair, status, restart, uninstall (this fork) |
| `HotkeyLauncher.pyw` | Background hotkey service, started at login (this fork) |
| `AutoStartLiveCaptions.py` | Recording worker started by the hotkey (this fork) |
| `src/main.py` | The floating ● / ◼ dashboard (original, restructured) |
| `src/function/config.py` | All settings |
| `src/function/texthook.py`, `dedup.py`, `transformation.py`, `save.py` | Caption capture, de-duplication and saving (original, with fixes) |
| `src/function/livecaptions.py`, `hotkeys.py`, `winapi.py`, `applog.py` | Live Captions control, hotkeys, Win32 calls, logging (this fork) |
| `scripts/diagnose_live_captions.py` | Dumps the Live Captions UI tree for troubleshooting |
| `tests/` | Unit tests (this fork) |
| `docs/ARCHITECTURE.md` | Processes, modules and capture pipeline |
| `SaveLiveCaptionsWithLC.py`, `installer.iss`, `.github/workflows/` | The original project's `.exe` and installer packaging. Kept for reference, not maintained here |

Not in Git (see `.gitignore`): `.venv/` (created by the installer) and `logs/`.

## Development

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # unit tests
```

Git remotes: `origin` is this fork, `upstream` is the original project.
To pull improvements from the original project:

```powershell
git fetch upstream
git merge upstream/main
```

### Contributing back

Fixes that also apply to the original project are offered upstream as
separate, minimal pull requests:

- [LiveCaptionsHelper/SaveLiveCaptions#21](https://github.com/LiveCaptionsHelper/SaveLiveCaptions/pull/21):
  decimals such as `3.14` were split into two sentences.
- [LiveCaptionsHelper/SaveLiveCaptions#22](https://github.com/LiveCaptionsHelper/SaveLiveCaptions/pull/22):
  `word_to_number` mangled numbers and words ("twenty twenty six" became `406`).

## Credits and license

- Original project: [LiveCaptionsHelper/SaveLiveCaptions](https://github.com/LiveCaptionsHelper/SaveLiveCaptions),
  Copyright (c) 2025 M.T.Arden. It provides the caption capture, de-duplication
  and dashboard this fork builds on.
- Fork modifications: Copyright (c) 2026 thodoris.

Both are released under the MIT License, see [LICENSE](LICENSE).
