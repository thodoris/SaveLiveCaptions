# Save Live Captions

Save the text of **Windows Live Captions** to timestamped text files, so a
meeting, lecture or video you listened to can be read back later.

> This is a fork of [LiveCaptionsHelper/SaveLiveCaptions](https://github.com/LiveCaptionsHelper/SaveLiveCaptions).
> It adds a background **hotkey workflow** (one key combination starts Live
> Captions and recording, another stops and saves), a one-step installer with
> autostart at login, log files, and several fixes. See [CHANGES.md](CHANGES.md).

```text
[10:02:13] Good morning everyone, let's start with the results from last week.
[10:02:19] Revenue grew by 3.5 percent compared to the previous quarter.
```

## Requirements

- Windows 11 22H2 or later (that is where Live Captions exists; try `Ctrl+Win+L`).
  Open Live Captions once by hand first to finish its setup and language download.
- Python 3.10 or newer from [python.org](https://www.python.org/downloads/)
  (tick *Add python.exe to PATH* during setup).

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
- **Prebuilt .exe**: the upstream [Releases](https://github.com/LiveCaptionsHelper/SaveLiveCaptions/releases)
  page has builds of the original app (without the hotkey workflow).

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

## Development

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests   # unit tests
```

Pulling improvements from the original project:

```powershell
git fetch upstream
git merge upstream/main
```

## License

MIT, see [LICENSE](LICENSE). Original work by LiveCaptionsHelper.
