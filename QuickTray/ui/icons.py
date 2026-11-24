import sys
from pathlib import Path
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor, QPen, QFont, QPainterPath

def logo():
    base = Path(getattr(sys, "_MEIPASS",
                        Path(__file__).resolve().parent.parent))
    icon = QIcon(str(base / "QuickTray.ico"))
    if icon.pixmap(64,64).isNull():
        icon = QIcon(str(base / "QuickTray.png"))
    return icon

def toolbar_icon(name, color, angle=0):
    pix=QPixmap(64,64); pix.fill(Qt.GlobalColor.transparent)
    p=QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.scale(64/24,64/24)
    p.translate(12,12); p.rotate(angle); p.translate(-12,-12)
    pen=QPen(QColor(color),1.7); pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin); p.setPen(pen)
    def line(x,y,a,b): p.drawLine(QPointF(x,y),QPointF(a,b))
    if name=='add':
        p.drawRoundedRect(QRectF(3,7,18,13),2,2); line(4,7,4,4); line(4,4,10,4); line(10,4,13,7); line(12,10,12,17); line(8.5,13.5,15.5,13.5)
    elif name=='refresh':
        p.drawArc(QRectF(4,4,16,16),35*16,290*16); line(20,4,20,10); line(20,10,14,10)
    elif name=='pin':
        path=QPainterPath(QPointF(9,3)); path.lineTo(15,3); path.lineTo(14,10); path.lineTo(18,14); path.lineTo(6,14); path.lineTo(10,10); path.closeSubpath(); p.drawPath(path); line(12,14,12,21)
    elif name=='settings':
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(color))
        for x in (6,12,18): p.drawEllipse(QRectF(x-1.5,10.5,3,3))
    elif name=='gear':
        import math
        p.drawEllipse(QRectF(9,9,6,6)); p.drawEllipse(QRectF(5,5,14,14))
        for i in range(8):
            a=i*math.pi/4; line(12+7*math.cos(a),12+7*math.sin(a),12+10*math.cos(a),12+10*math.sin(a))
    else: line(6,6,18,18); line(18,6,6,18)
    p.end(); return QIcon(pix)


def file_icon(path):
    ext=Path(path).suffix[1:].upper()
    colors={'PY':'#5086ce','PDF':'#d75d69','DOCX':'#487dd2','XLSX':'#31996b','CSV':'#31996b','PPTX':'#d77b49','ZIP':'#b38b42','MP4':'#8d6bd0','MP3':'#c36c9f','JS':'#b39a38','HTML':'#d77b49','CSS':'#547fc8'}
    pix=QPixmap(152,120); pix.fill(Qt.GlobalColor.transparent)
    p=QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.scale(2,2)
    path=QPainterPath(QPointF(20,3)); path.lineTo(46,3); path.lineTo(57,14); path.lineTo(57,54); path.quadTo(57,58,53,58); path.lineTo(20,58); path.quadTo(16,58,16,54); path.lineTo(16,7); path.quadTo(16,3,20,3); path.closeSubpath()
    p.fillPath(path,QColor('#e8e8f0')); p.setPen(QPen(QColor('#a5a5b8'),1)); p.drawLine(46,3,46,14); p.drawLine(46,14,57,14)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(colors.get(ext,'#777b96'))); p.drawRoundedRect(QRectF(12,32,49,19),5,5)
    p.setPen(QColor('white')); f=QFont('Segoe UI',8); f.setBold(True); p.setFont(f); p.drawText(QRectF(12,32,49,19),Qt.AlignmentFlag.AlignCenter,ext[:5]); p.end(); return QIcon(pix)
