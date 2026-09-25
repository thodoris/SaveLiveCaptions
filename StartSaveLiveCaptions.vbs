Option Explicit

Dim fileSystem, shell, baseDir, pythonw, launcher

Set fileSystem = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

baseDir = fileSystem.GetParentFolderName(WScript.ScriptFullName)
pythonw = fileSystem.BuildPath(baseDir, ".venv\Scripts\pythonw.exe")

If Not fileSystem.FileExists(pythonw) Then
    pythonw = "pythonw.exe"
End If

launcher = fileSystem.BuildPath(baseDir, "HotkeyLauncher.pyw")
shell.Run Chr(34) & pythonw & Chr(34) & " " & Chr(34) & launcher & Chr(34), 0, False
