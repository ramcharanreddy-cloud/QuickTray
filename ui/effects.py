from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QLinearGradient, QColor, QPainter, QPixmap, QImage
from ui.icons import logo

def glare(p, rect, strength):
    g=QLinearGradient(rect.topLeft(),rect.bottomRight())
    g.setColorAt(0,QColor(255,255,255,int(35*strength)))
    g.setColorAt(.48,QColor(255,255,255,0)); g.setColorAt(1,QColor(255,255,255,0))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(g); p.drawRoundedRect(rect,12,12)

def metallic_logo():
    pix=logo().pixmap(64,64)
    if pix.isNull(): return pix
    pix=QPixmap.fromImage(pix.toImage().convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)); p=QPainter(pix)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
    g=QLinearGradient(0,0,64,64)
    for x,a in [(0,65),(.35,0),(.48,100),(.65,0),(1,40)]: g.setColorAt(x,QColor(255,255,255,a))
    p.fillRect(pix.rect(),g); p.end(); return pix.scaled(26,26,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
