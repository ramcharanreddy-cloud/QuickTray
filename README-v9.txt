QuickTray v9.3
Run: py quicktray.py
Install dependencies: py -m pip install -r requirements.txt
Build: py -m PyInstaller --onefile --windowed --icon=QuickTray.ico --add-data "QuickTray.ico;." --add-data "QuickTray.png;." --name QuickTray quicktray.py
Image stack: three-dot menu > Expand image stack; Show all files restores the list. Images remain draggable.
Windows runtime testing required.
