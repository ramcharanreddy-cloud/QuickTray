from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QSizeGrip, QFrame
from PySide6.QtCore import Qt
from ui.file_grid import DragHandle
from ui.effects import metallic_logo

def build(tray, layout):
    row=QHBoxLayout(); row.setSpacing(8)
    row.addWidget(tray.files,1)
    divider=QFrame(); divider.setObjectName('separator'); divider.setFixedWidth(1); row.addWidget(divider)
    controls=QVBoxLayout(); controls.setSpacing(2); controls.addStretch()
    mark=QLabel(); mark.setPixmap(metallic_logo()); mark.setToolTip("QuickTray"); controls.addWidget(mark,0,Qt.AlignmentFlag.AlignHCenter)
    for name in ('add','refresh','settings'): controls.addWidget(tray.buttons[name])
    controls.addStretch(); row.addLayout(controls); layout.addLayout(row,1)
    footer=QHBoxLayout(); footer.addStretch()
    handle=DragHandle(''); handle.setObjectName('handle'); handle.setFixedSize(34,5); handle.setCursor(Qt.CursorShape.SizeAllCursor); handle.setToolTip('Drag to move QuickTray'); footer.addWidget(handle)
    footer.addStretch(); footer.addWidget(QSizeGrip(tray)); layout.addLayout(footer)
