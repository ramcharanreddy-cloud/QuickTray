from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt
from pathlib import Path

def is_image(path):
    return Path(path).suffix.lower() in {".png",".jpg",".jpeg",".webp",".bmp",".gif"}

def show_bubbles(tray):
    menu=QMenu(tray)
    menu.setStyleSheet('QMenu {border-radius:14px; padding:8px;} QMenu::item {padding:9px 18px; border-radius:10px;}')
    settings=menu.addAction('Settings'); stack=menu.addAction('Show all files' if tray.stack_open else 'Expand image stack ('+str(sum(is_image(tray.files.item(i).data(Qt.ItemDataRole.UserRole)) for i in range(tray.files.count())))+')'); hide=menu.addAction('Hide tray')
    action=menu.exec(tray.buttons['settings'].mapToGlobal(tray.buttons['settings'].rect().bottomLeft()))
    if action==settings: tray.options()
    elif action==hide: tray.hide_animated()
    elif action==stack: show_stack(tray)

def show_stack(tray):
    tray.stack_open=not tray.stack_open
    tray.files.clearSelection()
    tray.update_stack()
    tray.files.doItemsLayout()
    tray.files.scrollToTop()
