from PySide6.QtCore import Qt, QTimer, QMimeData, QUrl, QSize, Signal, QRectF, QEvent
from PySide6.QtGui import QDrag, QPainter, QColor, QPen
from PySide6.QtWidgets import QApplication, QListWidget, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QLabel
from core.security import safe_file
from ui.animations import Motion
from ui.effects import glare

class CardDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        return self.parent().gridSize()
    def paint(self,painter,option,index):
        opt=QStyleOptionViewItem(option); self.initStyleOption(opt,index)
        painter.save(); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r=QRectF(opt.rect).adjusted(4,4,-4,-4); selected=bool(opt.state & QStyle.StateFlag.State_Selected); hover=bool(opt.state & QStyle.StateFlag.State_MouseOver)
        view=self.parent(); dark=view.window().dark
        path=index.data(Qt.ItemDataRole.UserRole); strength=view.motion.hover.get(path,0)
        progress=view.motion.progress(path); painter.setOpacity(.45+.55*progress); painter.translate(0,4*(1-progress))
        if selected or hover:
            bg=('#52545b' if selected else '#41434a') if dark else ('#d4dce8' if selected else '#e5e7eb')
            painter.setBrush(QColor(bg)); painter.setPen(Qt.PenStyle.NoPen); painter.drawRoundedRect(r,10,10)
        if strength: glare(painter,r,strength)
        size=QSize(76,56); icon=opt.icon.pixmap(size); actual=icon.deviceIndependentSize()
        target=QRectF(r.center().x()-actual.width()/2,r.top()+5+(56-actual.height())/2,actual.width(),actual.height()); target.adjust(-3*strength,-5*strength,3*strength,1*strength); painter.drawPixmap(target,icon,QRectF(icon.rect()))
        painter.setPen(QColor('#f1f1f7' if dark else '#292932')); painter.setFont(opt.font)
        text=opt.fontMetrics.elidedText(opt.text,Qt.TextElideMode.ElideMiddle,int(r.width()-8)); painter.drawText(QRectF(r.left()+4,r.top()+65,r.width()-8,17),Qt.AlignmentFlag.AlignCenter,text); painter.restore()



class DragHandle(QLabel):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.window().pos()
            event.accept()
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and getattr(self, 'offset', None) is not None:
            self.window().move(event.globalPosition().toPoint() - self.offset)
            event.accept()
    def mouseReleaseEvent(self, event):
        self.offset = None
        event.accept()

class Files(QListWidget):
    dropped = Signal()
    dragging = False
    def __init__(self, parent=None):
        super().__init__(parent)
        self.motion=Motion(self)
        self.layout_timer = QTimer(self)
        self.layout_timer.setSingleShot(True)
        self.layout_timer.timeout.connect(self.fit_grid)
        self.viewport().installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched is self.viewport() and event.type() == QEvent.Type.Resize:
            self.layout_timer.start(0)
        return super().eventFilter(watched, event)

    def fit_grid(self):
        if self.dragging:
            self.layout_timer.start(100)
            return
        w, h = self.viewport().width(), self.viewport().height()
        if w < 1 or h < 1:
            return
        # Fixed tile height, bounded width; switch scrolling direction for one row.
        compact = h < 180
        if self.isWrapping() == compact:
            self.setWrapping(not compact)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded if compact else Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff if compact else Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        columns=max(1,w//96)
        size=QSize(min(110,max(96,w//columns)),90)
        if size != self.gridSize():
            self.setGridSize(size)
        self.doItemsLayout()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.press_pos = event.position().toPoint() if event.button() == Qt.MouseButton.LeftButton and self.itemAt(event.position().toPoint()) else None

    def mouseMoveEvent(self, event):
        item=self.itemAt(event.position().toPoint()); self.motion.point(item.data(Qt.ItemDataRole.UserRole) if item else None)
        pos = getattr(self, 'press_pos', None)
        if pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            if (event.position().toPoint() - pos).manhattanLength() >= QApplication.startDragDistance():
                self.press_pos = None
                self.startDrag(Qt.DropAction.CopyAction)
                self.setState(QListWidget.State.NoState)
                return
        super().mouseMoveEvent(event)

    def leaveEvent(self,event):
        self.motion.point(None); super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        self.press_pos = None
        super().mouseReleaseEvent(event)

    def startDrag(self, actions):
        if self.dragging: return
        paths=[QUrl.fromLocalFile(i.data(Qt.ItemDataRole.UserRole)) for i in self.selectedItems() if safe_file(i.data(Qt.ItemDataRole.UserRole))]
        if paths:
            mime=QMimeData(); mime.setUrls(paths)
            drag=QDrag(self); drag.setMimeData(mime)
            item = self.currentItem()
            if item: drag.setPixmap(item.icon().pixmap(68,54))
            self.dragging = True
            try:
                result = drag.exec(Qt.DropAction.CopyAction, Qt.DropAction.CopyAction)
            finally:
                self.dragging = False
            if result != Qt.DropAction.IgnoreAction: self.dropped.emit()
