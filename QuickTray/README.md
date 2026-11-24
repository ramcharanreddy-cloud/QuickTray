<div align="center">
  <img src="QuickTray.png" alt="QuickTray logo" width="112" />
  <h1>QuickTray</h1>
  <p><strong>Your files. One gesture away.</strong></p>
  <p>A lightweight floating file tray for Windows. Keep screenshots, downloads and recent files within reach without interrupting your workflow.</p>
  <img alt="Windows" src="https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square" />
  <img alt="PySide6" src="https://img.shields.io/badge/UI-PySide6-41CD52?style=flat-square" />
  <img alt="Portable" src="https://img.shields.io/badge/distribution-portable-805AD5?style=flat-square" />
  <p><a href="../../releases/latest"><strong>Download QuickTray</strong></a> · <a href="#getting-started">Getting started</a> · <a href="docs/BUILD.md">Build from source</a></p>
</div>

## Overview

QuickTray brings recent local files into a compact floating workspace. Drag a screenshot into a compatible application, pin a frequently used document, or switch between two layouts without opening File Explorer.

## Features

| Feature | Description |
| --- | --- |
| Floating Glass Shelf | Compact file grid with quick controls. |
| Floating Island | Collapsible interface with animated transitions. |
| Drag and drop | Drag supported files into compatible applications. |
| Recent files | Background refresh of watched folders, with image thumbnails. |
| Image stack | Filter the tray to images using the three-dot menu. |
| Quick actions | Open with confirmation, copy file or path, pin favourites, reveal in Explorer. |
| Personalisation | Dark, light and system appearance; always-on-top and optional startup. |
| Local-first design | File scanning and preferences are handled locally by the application. |

## Getting started

1. Download `QuickTray.exe` from the [latest release](../../releases/latest).
2. Save it in a folder you control and scan it with your antivirus.
3. Launch it. No separate Python installation is required for the bundled executable.
4. Press **Ctrl + Shift + Space** to show or hide the tray. The notification-area icon provides an alternative.

The initial release is intended for Windows. Compatibility across Windows versions and architectures has not been independently established. Unsigned builds may trigger Windows security warnings; investigate warnings rather than disabling protection.

## Everyday controls

| Action | Control |
| --- | --- |
| Show / hide | Ctrl + Shift + Space or system tray icon |
| Add watched folder | Plus button |
| Refresh | Refresh button |
| Settings / image stack | Three-dot menu |
| Open file | Double-click, then confirm |
| Copy / pin / reveal | Right-click file |
| Exit | System tray menu or Settings |

## Privacy and file handling

QuickTray scans the immediate contents of configured local folders, including Windows Downloads, Desktop, Documents, Pictures and Screenshots where available. It displays favourites and up to 30 additional recent files. It excludes unsupported extensions, hidden/system files, network drives and reparse/offline paths through its path checks. These checks are not a security sandbox or malware scanner.

Preferences, watched folder paths and favourites are stored locally using Qt settings. Optional startup uses the current user's Windows Run registry entry. Dragging or copying a file hands it to the destination application; that application's privacy policy applies. See [security policy](SECURITY.md).

## Development

```powershell
py -m pip install -r requirements.txt
py quicktray.py
```

See [build instructions](docs/BUILD.md), [architecture](docs/ARCHITECTURE.md) and [contributing](CONTRIBUTING.md).

## Project status

Initial portable release preparation. See [changelog](CHANGELOG.md). Licensing terms are pending the repository owner's decision; public visibility alone does not grant reuse rights.
