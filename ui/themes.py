from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette
from ui.icons import toolbar_icon

class ThemeMixin:
    def apply_theme(self):
        dark=self.theme=='dark' or (self.theme=='system' and QApplication.palette().color(QPalette.ColorRole.Window).lightness()<128)
        self.dark=dark
        bg,fg,muted,border,card,hover,selected,menu = ('qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #41434b,stop:1 #25262c)','#f5f5fa','#a5a5ad','#64656b','transparent','#41434a','#52545b','#292a2e') if dark else ('qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ffffff,stop:1 #e5e7ec)','#22222b','#686878','#c7c9cf','transparent','#e5e7eb','#d4dce8','#ffffff')
        self.setStyleSheet(f"""
            QWidget#panel {{background:{bg}; border:1px solid {border}; border-radius:22px;}}
            QWidget#panel[island="true"] {{background:{bg}; border-radius:22px;}}
            QWidget#pill {{background:transparent; border:0; border-radius:17px;}}
            QWidget#pill QLabel {{background:transparent; border:0;}}
            QWidget#pill QPushButton {{background:transparent; border:0;}}
            QWidget#pill QPushButton:hover {{background:{hover}; border-radius:12px;}}
            QWidget#panel[collapsed="true"] {{background:{bg}; border-radius:22px;}}
            QLabel#handle, QFrame#separator {{background:{border}; border-radius:2px;}}
            QLabel {{color:{fg}; font-family:'Segoe UI'; font-size:12px;}}
            QLabel#brand {{font-size:16px; font-weight:600;}}
            QLabel#muted {{color:{muted}; font-size:11px;}}
            QPushButton {{background:{card}; color:{fg}; border:0; border-radius:14px; font-size:17px;}}
            QPushButton:hover {{background:{hover};}}
            QPushButton:pressed {{background:{selected};}}
            QPushButton#exitButton:hover {{background:#d85c65; color:white;}}
            QListWidget {{background:transparent; border:0; outline:0; color:{fg}; font-family:'Segoe UI'; font-size:11px;}}
            QListWidget::item {{background:{card}; border:1px solid transparent; border-radius:13px; padding:4px;}}
            QListWidget::item:hover {{background:{hover}; border:1px solid #9381bb;}}
            QListWidget::item:selected {{background:{selected}; border:1px solid #a68cdd; color:{fg};}}
            QScrollBar:vertical {{background:transparent; width:3px;}}
            QScrollBar::handle:vertical {{background:{border}; border-radius:2px; min-height:25px;}}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{height:0;}}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{background:transparent;}}
            QScrollBar:horizontal {{background:transparent; height:3px; margin:0 3px;}}
            QScrollBar::handle:horizontal {{background:{border}; border-radius:3px; min-width:28px;}}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{width:0;}}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{background:transparent;}}
            QMenu {{background:{menu}; color:{fg}; border:1px solid {border}; padding:5px;}}
            QMenu::item {{padding:7px 20px; border-radius:5px;}}
            QMenu::item:selected {{background:{selected};}}
            QToolTip {{background:{menu}; color:{fg}; border:1px solid {border}; padding:5px;}}
        """)

        self.icon_color=fg
        for name,button in self.buttons.items(): button.setIcon(toolbar_icon(name,fg))
        self.files.viewport().update()
