import sys, subprocess, winreg
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QMessageBox
from core.security import default_folders

class SettingsMixin:
    def save(self):
        self.settings.setValue('geometry_v9',self.expanded_geometry if self.collapsed else self.saveGeometry()); self.settings.setValue('layout_style',self.layout_style); self.settings.setValue('always_on_top',bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)); self.settings.setValue('favourites',self.favourites); self.settings.setValue('auto_hide',self.auto_hide); self.settings.sync()

    def options(self):
        menu=QMenu(self); auto=menu.addAction('Hide after successful drop'); auto.setCheckable(True); auto.setChecked(self.auto_hide)
        styles=menu.addMenu('Layout style'); layouts={}
        for key,label in [('shelf','Floating Glass Shelf'),('island','Floating Island')]:
            choice=styles.addAction(label); choice.setCheckable(True); choice.setChecked(self.layout_style==key); layouts[choice]=key
        pin=menu.addAction('Always on top'); pin.setCheckable(True); pin.setChecked(bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))
        hide=menu.addAction('Hide QuickTray')
        startup=menu.addAction('Start with Windows'); startup.setCheckable(True)
        keypath=r'Software\Microsoft\Windows\CurrentVersion\Run'
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,keypath) as key: winreg.QueryValueEx(key,'QuickTray'); startup.setChecked(True)
        except OSError: pass
        appearance=menu.addMenu('Appearance'); themes={}
        for key,label in [('dark','Dark'),('light','Light'),('system','System')]:
            choice=appearance.addAction(label); choice.setCheckable(True); choice.setChecked(self.theme==key); themes[choice]=key
        clear=menu.addAction('Clear favourites and custom folders'); menu.addSeparator(); quit_action=menu.addAction('Exit QuickTray'); action=menu.exec(self.mapToGlobal(self.rect().center()))
        if action in layouts:
            if self.collapsed: self.toggle_collapse()
            self.layout_style=layouts[action]; self.build_layout(); self.save(); return
        if action==pin: self.pin(); self.save(); return
        if action==hide: self.hide_animated(); return
        if action==quit_action: self.exit_app(); return
        if action in themes:
            self.theme=themes[action]; self.settings.setValue('appearance',self.theme); self.apply_theme(); return
        if action==clear:
            self.favourites=[]; self.folders=default_folders(); self.settings.remove('folders'); self.save(); self.signature=None; self.refresh(); return
        if action==auto: self.auto_hide=auto.isChecked(); self.save()
        elif action==startup:
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER,keypath) as key:
                    if startup.isChecked():
                        if getattr(sys, 'frozen', False):
                            command=subprocess.list2cmdline([sys.executable, '--hidden'])
                        else:
                            exe=Path(sys.executable).with_name('pythonw.exe')
                            command=subprocess.list2cmdline([str(exe), str(Path(__file__).resolve().parent.parent / "quicktray.py"), '--hidden'])
                        winreg.SetValueEx(key,'QuickTray',0,winreg.REG_SZ,command)
                    else: winreg.DeleteValue(key,'QuickTray')
            except OSError as exc: QMessageBox.warning(self,'QuickTray',str(exc))
