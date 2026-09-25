<#
.SYNOPSIS
    Install, update, inspect or remove the SaveLiveCaptions hotkey service
    for the current Windows user. Run it through install.cmd in the repo root.

.DESCRIPTION
    Install (default):
      1. Creates .venv with Python 3.10+ and installs requirements.txt
      2. Stops any running hotkey launcher (from this or any other folder)
      3. Creates/refreshes the Startup-folder shortcut so the launcher starts at login
      4. Starts the launcher now

    The launcher always runs from the folder this script lives in. If you move
    the folder, run install.cmd again from the new location.

.EXAMPLE
    install.cmd                  # install / repair / update
    install.cmd -Status          # is it running, where from, recent log lines
    install.cmd -Restart         # restart after editing src\function\config.py
    install.cmd -Uninstall       # stop it and remove the Startup shortcut
#>
[CmdletBinding()]
param(
    [switch]$Uninstall,
    [switch]$Status,
    [switch]$Restart,
    [switch]$NoAutostart
)

$ErrorActionPreference = 'Stop'

$Root         = Split-Path -Parent $PSScriptRoot
$VenvPython   = Join-Path $Root '.venv\Scripts\python.exe'
$VenvPythonW  = Join-Path $Root '.venv\Scripts\pythonw.exe'
$Launcher     = Join-Path $Root 'HotkeyLauncher.pyw'
$LauncherLog  = Join-Path $Root 'logs\launcher.log'
$ShortcutPath = Join-Path ([Environment]::GetFolderPath('Startup')) 'SaveLiveCaptions Hotkey Launcher.lnk'

function Write-Step($Text) { Write-Host "==> $Text" -ForegroundColor Cyan }

function Get-LauncherProcess {
    Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe' OR Name = 'python.exe'" |
        Where-Object { $_.CommandLine -like '*HotkeyLauncher.pyw*' }
}

function Stop-Launcher {
    $procs = @(Get-LauncherProcess)
    foreach ($p in $procs) {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
    if ($procs.Count) { Write-Host "    stopped $($procs.Count) launcher process(es)" }
}

function Start-Launcher {
    Start-Process -FilePath $VenvPythonW -ArgumentList "`"$Launcher`"" -WorkingDirectory $Root
    Start-Sleep -Seconds 2
    if (@(Get-LauncherProcess).Count) {
        Write-Host "    launcher is running"
    } else {
        Write-Warning "The launcher exited immediately. See $LauncherLog"
    }
}

function Find-Python {
    # Returns the command (as an array) of a Python >= 3.10, or $null
    $candidates = @(@('py', '-3'), @('python'), @('python3'))
    foreach ($cmd in $candidates) {
        if (-not (Get-Command $cmd[0] -ErrorAction SilentlyContinue)) { continue }
        $exe  = $cmd[0]
        $rest = @($cmd | Select-Object -Skip 1)
        try {
            $ok = & $exe @rest -c "import sys; print(sys.version_info >= (3, 10))" 2>$null
            if ($ok -eq 'True') { return $cmd }
        } catch { }
    }
    return $null
}

function Show-Status {
    Write-Step 'SaveLiveCaptions status'
    $procs = @(Get-LauncherProcess)
    if ($procs.Count) {
        Write-Host "    launcher: RUNNING"
        $procs | ForEach-Object { Write-Host "      $($_.CommandLine)" }
    } else {
        Write-Host "    launcher: not running"
    }

    if (Test-Path $ShortcutPath) {
        $lnk = (New-Object -ComObject WScript.Shell).CreateShortcut($ShortcutPath)
        $target = "$($lnk.TargetPath) $($lnk.Arguments)"
        Write-Host "    autostart: $target"
        if (-not (Test-Path $lnk.TargetPath)) {
            Write-Warning "The Startup shortcut points to a file that no longer exists. Run install.cmd to fix it."
        } elseif ($lnk.Arguments -notlike "*$Launcher*") {
            Write-Warning "The Startup shortcut runs a different copy than this folder ($Root)."
        }
    } else {
        Write-Host "    autostart: not installed"
    }

    if (Test-Path $LauncherLog) {
        Write-Host "    last launcher log lines:"
        Get-Content $LauncherLog -Tail 8 | ForEach-Object { Write-Host "      $_" }
    }
}

if ($Status) { Show-Status; return }

if ($Uninstall) {
    Write-Step 'Stopping the hotkey launcher'
    Stop-Launcher
    Write-Step 'Removing the Startup shortcut'
    if (Test-Path $ShortcutPath) { Remove-Item $ShortcutPath; Write-Host "    removed" }
    Write-Host "`nUninstalled. Recordings, logs and .venv were left in $Root" -ForegroundColor Green
    return
}

if ($Restart) {
    Write-Step 'Restarting the hotkey launcher'
    Stop-Launcher
    Start-Launcher
    return
}

# ---------------------------------------------------------------- install

Write-Step "Installing SaveLiveCaptions from $Root"

if (-not (Test-Path (Join-Path $env:SystemRoot 'System32\LiveCaptions.exe'))) {
    Write-Warning 'LiveCaptions.exe was not found. Windows Live Captions requires Windows 11 22H2 or later.'
}

if (-not (Test-Path $VenvPython)) {
    Write-Step 'Creating virtual environment (.venv)'
    $python = Find-Python
    if (-not $python) {
        throw 'Python 3.10 or newer was not found. Install it from https://www.python.org/downloads/ (tick "Add python.exe to PATH") and run install.cmd again.'
    }
    $exe  = $python[0]
    $rest = @($python | Select-Object -Skip 1)
    & $exe @rest -m venv (Join-Path $Root '.venv')
    if ($LASTEXITCODE) { throw 'Creating the virtual environment failed.' }
}

Write-Step 'Installing dependencies'
& $VenvPython -m pip install --disable-pip-version-check --quiet -r (Join-Path $Root 'requirements.txt')
if ($LASTEXITCODE) { throw 'pip install failed.' }

Write-Step 'Stopping any running launcher'
Stop-Launcher

if ($NoAutostart) {
    if (Test-Path $ShortcutPath) { Remove-Item $ShortcutPath }
} else {
    Write-Step 'Creating Startup shortcut (starts the launcher at login)'
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut($ShortcutPath)
    $lnk.TargetPath       = $VenvPythonW
    $lnk.Arguments        = "`"$Launcher`""
    $lnk.WorkingDirectory = $Root
    $lnk.Description      = 'SaveLiveCaptions global hotkeys'
    $icon = Join-Path $Root 'assets\SaveLC.ico'
    if (Test-Path $icon) { $lnk.IconLocation = $icon }
    $lnk.Save()
    Write-Host "    $ShortcutPath"
}

Write-Step 'Starting the launcher'
Start-Launcher

$hotkeys = & $VenvPython -c "import sys; sys.path.insert(0, r'$Root\src'); from function import config; from function.hotkeys import format_hotkey as f; print(f(config.START_HOTKEY) + ';' + f(config.STOP_HOTKEY))"
$start, $stop = $hotkeys -split ';'
Write-Host ''
Write-Host 'Done.' -ForegroundColor Green
Write-Host "  $start  start Live Captions and record"
Write-Host "  $stop  stop, save and close"
$saveDir = & $VenvPython -c "import sys; sys.path.insert(0, r'$Root\src'); from function import save; print(save.save_dir or '(asked each time)')"
Write-Host "  Transcripts: $saveDir"
Write-Host "  Logs:        $(Join-Path $Root 'logs')"
