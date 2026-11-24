import sys, ctypes, atexit
from ctypes import wintypes
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImageReader
from PySide6.QtWidgets import QApplication, QMessageBox, QMenu
from ui.window import Tray
from ui.icons import logo

def main():
    app=QApplication(sys.argv)
    # Session-local mutex; held for the lifetime of the application.
    kernel=ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateMutexW.argtypes=[ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    kernel.CloseHandle.restype=wintypes.BOOL
    ctypes.set_last_error(0)
    mutex=kernel.CreateMutexW(None, False, r'Local\QuickTray.Application.v7')
    error=ctypes.get_last_error()
    if not mutex:
        QMessageBox.critical(None,'QuickTray','Unable to acquire application lock.')
        sys.exit(1)
    if error==183:
        kernel.CloseHandle(mutex)
        if '--hidden' not in sys.argv:
            QMessageBox.information(None,'QuickTray','Already running. Press Ctrl+Shift+Space or use the tray icon.')
        sys.exit(0)
    atexit.register(kernel.CloseHandle, mutex)
    app.setQuitOnLastWindowClosed(False)
    QImageReader.setAllocationLimit(64)
    tray=Tray()
    from PySide6.QtWidgets import QSystemTrayIcon
    system=QSystemTrayIcon(logo(), app)
    menu=QMenu(); toggle=menu.addAction('Show / hide QuickTray'); quit_action=menu.addAction('Exit QuickTray')
    def flip():
        if tray.files.dragging: return
        if tray.isVisible() and not tray.hiding: tray.hide_animated()
        else: tray.show_animated()
    toggle.triggered.connect(flip); quit_action.triggered.connect(tray.exit_app)
    system.setContextMenu(menu); system.setToolTip('QuickTray — Ctrl+Shift+Space'); system.show()
    from PySide6.QtCore import QAbstractNativeEventFilter
    class HotkeyFilter(QAbstractNativeEventFilter):
        def nativeEventFilter(self, eventType, message):
            if bytes(eventType) in (b'windows_generic_MSG', b'windows_dispatcher_MSG'):
                msg=wintypes.MSG.from_address(int(message))
                if msg.message==0x0312 and msg.wParam==1:
                    QTimer.singleShot(0, flip)
                    return True, 0
            return False, 0
    user32=ctypes.windll.user32
    hotkey_filter=HotkeyFilter()
    app.installNativeEventFilter(hotkey_filter)
    registered=user32.RegisterHotKey(None, 1, 0x4000 | 0x0002 | 0x0004, 0x20)
    if registered:
        app.aboutToQuit.connect(lambda: user32.UnregisterHotKey(None, 1))
    else:
        QMessageBox.warning(tray, 'QuickTray', 'Ctrl+Shift+Space could not be registered. Close older QuickTray instances or use the system tray menu.')
    system.activated.connect(lambda reason: flip() if reason==QSystemTrayIcon.ActivationReason.Trigger else None)
    def cleanup():
        tray.timer.stop()
        tray.scan_thread.quit()
        tray.scan_thread.wait()
        tray.animation.stop()
        tray.save()
        system.hide()
    app.aboutToQuit.connect(cleanup)
    if "--hidden" not in sys.argv: tray.show_animated()
    sys.exit(app.exec())
