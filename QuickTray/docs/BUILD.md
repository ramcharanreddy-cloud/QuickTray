# Build from source

Use Windows with Python and a compatible PySide6 version. Run from the repository root.

```powershell
py -m pip install -r requirements.txt
py -m pip install pyinstaller
py quicktray.py
```

Exit QuickTray before building.

```powershell
py -m PyInstaller --noconfirm --clean --onefile --windowed --icon=QuickTray.ico --add-data "QuickTray.ico;." --add-data "QuickTray.png;." --name QuickTray quicktray.py
```

Output: `dist/QuickTray.exe`. The included `QuickTray.spec` is an alternative build configuration. Dependencies are not pinned; record the actual versions used for each release.

## Release checklist

- Test the EXE on Windows, including a second machine without Python if possible.
- Verify both layouts, drag-and-drop, refresh, shortcuts, startup and exit.
- Scan the executable with antivirus; investigate warnings.
- Record the tested Windows version and architecture.
- Generate a checksum in PowerShell:

```powershell
$hash = (Get-FileHash .\dist\QuickTray.exe -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  QuickTray.exe" | Set-Content -Encoding ascii .\dist\SHA256SUMS.txt
```

Upload the EXE and checksum to a GitHub release tagged `v1.0.0`. Do not commit build output to the source tree. The legacy Inno Setup script is retained for reference, not used for the portable release.
