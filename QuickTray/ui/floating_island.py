from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel, QPushButton, QSizeGrip
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor
from ui.file_grid import DragHandle
from ui.effects import metallic_logo

class IslandArrow(QPushButton):
    def __init__(self):
        super().__init__(); self.angle=0.0
        self.setAccessibleName('Collapse or expand')
    def set_angle(self, angle):
        self.angle=float(angle); self.update()
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(self.width()/2,self.height()/2); p.rotate(self.angle)
        color=QColor('#eeeeee' if self.window().dark else '#303038')
        pen=QPen(color,1.6); pen.setCapStyle(Qt.PenCapStyle.RoundCap); p.setPen(pen)
        p.drawLine(QPointF(-4,2),QPointF(0,-2)); p.drawLine(QPointF(0,-2),QPointF(4,2)); p.end()

def build(tray, layout):
    pill=QWidget(); pill.setObjectName('pill'); pill.setFixedSize(174,34)
    bar=QHBoxLayout(pill); bar.setContentsMargins(10,3,8,3)
    mark=QLabel(); mark.setPixmap(metallic_logo()); bar.addWidget(mark)
    title=DragHandle('QuickTray'); title.setCursor(Qt.CursorShape.SizeAllCursor); bar.addWidget(title,1)
    tray.collapse_button=IslandArrow(); tray.collapse_button.setFixedSize(25,25); tray.collapse_button.setToolTip('Collapse or expand'); tray.collapse_button.clicked.connect(tray.toggle_collapse); bar.addWidget(tray.collapse_button)
    layout.addWidget(pill,0,Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
    tray.island_header=pill
    body=QWidget(); tray.island_body=body
    from PySide6.QtWidgets import QVBoxLayout
    content=QVBoxLayout(body); content.setContentsMargins(0,0,0,0); content.setSpacing(4)
    content.addWidget(tray.files,1)
    row=QHBoxLayout(); row.addStretch()
    for name in ('add','refresh','settings'): row.addWidget(tray.buttons[name])
    row.addStretch(); grip=QSizeGrip(tray); row.addWidget(grip); content.addLayout(row); layout.addWidget(body,1)
    tray.island_grip=grip
    # A stretchable empty region keeps the header at the top when the body is hidden.
    tray.island_anchor=QWidget(); tray.island_anchor.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    layout.addWidget(tray.island_anchor,1); tray.island_anchor.hide()
