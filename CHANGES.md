# Changes From Original Repository

This working copy adds a daily-use Windows hotkey workflow on top of the original SaveLiveCaptions controller.

## Added

- `HotkeyLauncher.pyw`: invisible global hotkey service for `Win + Alt + C`.
- `StartSaveLiveCaptions.vbs`: starts the hotkey service without showing a console.
- `HotkeyLauncher.log`: troubleshooting log created by the launcher.
- A Windows Startup-folder shortcut so the launcher starts at login.

## Changed

- `AutoStartLiveCaptions.py` now runs the Live Captions and recording workflow as a worker launched by the hotkey service.
- `src/main.py` registers `Win + Alt + X` as a global stop shortcut.
- Stop handling saves and closes the recording, closes Windows Live Captions, unregisters the hotkey, and exits the controller.
- Repeated `Win + Alt + C` presses are ignored while a recording workflow is already running.
- Recording output is automatically placed in the project's `RecordedCaptions` directory, without opening a folder picker.

## Preserved

- The original floating controller remains available.
- The original record and stop buttons remain available.
- No additional Python package was added.
- The existing caption capture and save logic remains in use.

## Daily Use

After Windows login, use:

- `Win + Alt + C` to start Live Captions and recording.
- `Win + Alt + X` to stop, save, close Live Captions, and exit.

The startup shortcut targets `.venv\\Scripts\\pythonw.exe` and runs `HotkeyLauncher.pyw` from the project directory.
