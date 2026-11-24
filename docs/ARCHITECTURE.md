# Architecture

- `quicktray.py`: entry point.
- `core/windows.py`: application lifecycle, single-instance mutex, global hotkey and notification-area integration.
- `core/scanner.py`: background folder scan and image thumbnail decoding.
- `core/security.py`: local path and supported-file checks.
- `core/settings.py`: preferences and optional startup registration.
- `ui/window.py`: tray coordination, transitions and file actions.
- `ui/glass_shelf.py`, `ui/floating_island.py`: layout implementations.
- `ui/file_grid.py`: file rendering and drag-and-drop.
- `ui/icons.py`, `ui/effects.py`, `ui/animations.py`, `ui/themes.py`, `ui/menus.py`: visual and interaction helpers.

The scanner runs in a Qt worker thread and returns results to the UI thread. File paths are passed to compatible destinations through Qt drag-and-drop or clipboard MIME data.
