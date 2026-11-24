import os, sys, subprocess, ctypes, winreg, stat, atexit, uuid
from ctypes import wintypes
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QMimeData, QUrl, QSize, QSettings, QPropertyAnimation, QEasingCurve, Signal, QRectF, QPointF, QEvent, QItemSelectionModel, QObject, QThread, Slot
from PySide6.QtGui import QDrag, QPixmap, QIcon, QPainter, QColor, QPen, QImageReader, QPalette, QFont, QPainterPath
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QFileIconProvider, QMenu, QPushButton, QFileDialog, QSizeGrip, QMessageBox, QStyle, QGraphicsDropShadowEffect, QStyledItemDelegate, QStyleOptionViewItem
from PySide6.QtCore import QFileInfo, QRect, QParallelAnimationGroup, QVariantAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect

from core.security import local_path, safe_file, default_folders
from core.scanner import ScanWorker
from core.settings import SettingsMixin
from ui.icons import logo, toolbar_icon, file_icon
from ui.file_grid import Files, CardDelegate, DragHandle
from ui.themes import ThemeMixin

class Tray(QWidget, ThemeMixin, SettingsMixin):
    scan_request = Signal(object)
    def __init__(self):
        super().__init__(); self.setWindowTitle('QuickTray'); self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.settings=QSettings("QuickTray", "SecureEdition"); self.favourites=self.settings.value("favourites", [], type=list); self.auto_hide=self.settings.value("auto_hide", True, type=bool)
        self.setMinimumSize(330,125); self.resize(640,160); self.setWindowIcon(logo()); self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,self.settings.value('always_on_top',True,type=bool))
        self.folders=default_folders()
        self.folders += [Path(x) for x in self.settings.value("folders", [], type=list) if local_path(x)]
        self.favourites = [x for x in self.favourites if safe_file(x)]
        self.signature=None; self.offset=None; self.icons=QFileIconProvider()
        self.outer=QVBoxLayout(self); self.outer.setContentsMargins(1,1,1,1)
        self.buttons={}
        for name,tip,fn in [('add','Add watched folder',self.add_folder),('refresh','Refresh files',self.manual_refresh),('settings','Settings',self.bubble_menu)]:
            b=QPushButton(); b.setFixedSize(26,26); b.setIconSize(QSize(17,17)); b.setToolTip(tip); b.setAccessibleName(tip); b.setCursor(Qt.CursorShape.PointingHandCursor); b.clicked.connect(fn); self.buttons[name]=b
        self.spin_angle=0; self.spin_timer=QTimer(self); self.spin_timer.setInterval(25); self.spin_timer.timeout.connect(self.spin_step)
        self.files=Files(); self.files.setViewMode(QListWidget.ViewMode.IconMode); self.files.setFlow(QListWidget.Flow.LeftToRight); self.files.setWrapping(True); self.files.setIconSize(QSize(76,60)); self.files.setGridSize(QSize(110,100)); self.files.setResizeMode(QListWidget.ResizeMode.Adjust); self.files.setDragDropMode(QListWidget.DragDropMode.DragOnly); self.files.setDefaultDropAction(Qt.DropAction.CopyAction); self.files.setDragEnabled(True); self.files.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection); self.files.setHorizontalScrollMode(QListWidget.ScrollMode.ScrollPerPixel); self.files.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded); self.files.itemDoubleClicked.connect(self.open_file); self.files.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); self.files.customContextMenuRequested.connect(self.menu)
        self.files.setSpacing(0); self.files.setUniformItemSizes(True); self.files.setMovement(QListWidget.Movement.Snap); self.files.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); self.files.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerItem); self.files.setDragEnabled(True); self.files.setAcceptDrops(False); self.files.viewport().setAcceptDrops(False); self.files.setItemDelegate(CardDelegate(self.files)); self.files.layout_timer.start(0); self.files.setMouseTracking(True); self.files.setWordWrap(False); self.files.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.files.dropped.connect(lambda: self.hide_animated() if self.auto_hide else None)
        self.count=QLabel(self); self.count.hide()
        self.layout_style=self.settings.value('layout_style','shelf',type=str)
        if self.layout_style not in ('shelf','island'): self.layout_style='shelf'
        self.collapsed=False; self.panel=None; self.stack_open=False
        self.theme=self.settings.value('appearance','dark',type=str)
        self.build_layout()
        self.animation=QPropertyAnimation(self,b'windowOpacity',self); self.animation.setDuration(100); self.animation.setEasingCurve(QEasingCurve.Type.OutCubic); self.animation.finished.connect(self.animation_done); self.hiding=False
        self.theme=self.settings.value('appearance','dark',type=str)
        self.apply_theme()
        self.scanning=False; self.type_icons={}
        self.scan_thread=QThread(self); self.scan_worker=ScanWorker(); self.scan_worker.moveToThread(self.scan_thread)
        self.scan_request.connect(self.scan_worker.run,Qt.ConnectionType.QueuedConnection)
        self.scan_worker.finished.connect(self.apply_scan,Qt.ConnectionType.QueuedConnection)
        self.scan_thread.finished.connect(self.scan_worker.deleteLater); self.scan_thread.start()
        self.timer=QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(4000); self.refresh()
        screen=QApplication.primaryScreen().availableGeometry(); self.move(screen.center().x()-self.width()//2,screen.top()+35)
        geometry=self.settings.value('geometry_v9')
        if geometry is not None: self.restoreGeometry(geometry)
        self.resize(max(self.width(),330),max(self.height(),self.minimumHeight()))
        if not any(screen.availableGeometry().intersects(self.frameGeometry()) for screen in QApplication.screens()): self.move(30,30)

    def build_layout(self):
        from ui import glass_shelf, floating_island
        if getattr(self, "island_transition", None) is not None:
            self.island_transition.stop(); self.finish_island_transition()
        if self.collapsed:
            self.collapsed=False; self.resize(self.expanded_size)
        if self.panel is not None:
            self.files.setParent(self)
            for button in self.buttons.values(): button.setParent(self)
            self.outer.removeWidget(self.panel); self.panel.hide(); self.panel.deleteLater()
        self.panel=QWidget(); self.panel.setObjectName('panel'); self.panel.setProperty("island", self.layout_style=="island"); self.outer.addWidget(self.panel)
        layout=QVBoxLayout(self.panel); layout.setContentsMargins(10,8,10,6); layout.setSpacing(4)
        if self.layout_style=="island": layout.setContentsMargins(6,4,6,4)
        self.setMinimumSize(330, 174 if self.layout_style=='island' else 150)
        (floating_island if self.layout_style=='island' else glass_shelf).build(self,layout)
        self.files.show()
        for button in self.buttons.values(): button.show()
        self.apply_theme(); self.files.layout_timer.start(0)

    def toggle_collapse(self):
        if self.layout_style!='island' or self.files.dragging or getattr(self,'island_transition',None) is not None: return
        start=self.geometry(); closing=not self.collapsed
        if closing:
            self.expanded_size=self.size(); self.expanded_geometry=self.saveGeometry()
        size=QSize(190,46) if closing else self.expanded_size.expandedTo(QSize(330,174))
        target=QRect(start.x()+(start.width()-size.width())//2,start.y(),size.width(),size.height())
        # Prepare the snapshot without temporarily expanding the native window.
        self.setMinimumSize(190,46)
        body=self.island_body
        layout=self.panel.layout()
        if not closing:
            # The hidden body can be laid out and rendered at its final size.
            margins=layout.contentsMargins()
            outer=self.outer.contentsMargins()
            body.resize(max(1,target.width()-outer.left()-outer.right()-margins.left()-margins.right()),
                        max(1,target.height()-outer.top()-outer.bottom()-margins.top()-margins.bottom()-self.island_header.height()-4))
            body.layout().activate()
            self.files.fit_grid()
        snapshot=body.grab()
        origin_y=self.island_header.mapTo(self,self.island_header.rect().topLeft()).y()+self.island_header.height()+4
        self.island_overlay=QLabel(self); self.island_overlay.setPixmap(snapshot)
        self.island_overlay.setFixedSize(snapshot.deviceIndependentSize().toSize())
        self.island_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.island_overlay.setStyleSheet('background:transparent;border:0;')
        effect=QGraphicsOpacityEffect(self.island_overlay); self.island_overlay.setGraphicsEffect(effect)
        effect.setOpacity(1.0 if closing else 0.0)
        body.hide(); layout.setSpacing(0); self.island_anchor.show()
        layout.invalidate(); self.outer.invalidate(); self.outer.activate(); layout.activate()
        self.island_overlay.move((start.width()-self.island_overlay.width())//2,origin_y)
        self.island_overlay.show(); self.island_overlay.raise_()
        self.collapsed=closing; self.island_target=target
        group=QParallelAnimationGroup(self); self.island_transition=group
        geom=QPropertyAnimation(self,b'geometry',group); geom.setDuration(320); geom.setStartValue(start); geom.setEndValue(target); geom.setEasingCurve(QEasingCurve.Type.OutCubic)
        geom.valueChanged.connect(lambda r: self.island_overlay.move((r.width()-self.island_overlay.width())//2,origin_y))
        group.addAnimation(geom)
        fade=QPropertyAnimation(effect,b'opacity',group); fade.setDuration(320); fade.setStartValue(1.0 if closing else 0.0); fade.setEndValue(0.0 if closing else 1.0); fade.setEasingCurve(QEasingCurve.Type.OutCubic if closing else QEasingCurve.Type.InCubic); group.addAnimation(fade)
        arrow=QVariantAnimation(group); arrow.setDuration(320); arrow.setStartValue(0.0 if closing else 180.0); arrow.setEndValue(180.0 if closing else 0.0); arrow.setEasingCurve(QEasingCurve.Type.OutCubic); arrow.valueChanged.connect(self.collapse_button.set_angle); group.addAnimation(arrow)
        group.finished.connect(self.finish_island_transition); group.start()

    def finish_island_transition(self):
        group=getattr(self,'island_transition',None)
        if group is None: return
        self.island_transition=None; group.stop(); group.deleteLater()
        self.island_overlay.hide(); self.island_overlay.deleteLater()
        self.panel.setProperty('collapsed',self.collapsed)
        self.panel.layout().setContentsMargins(6,4,6,4)
        self.island_anchor.setVisible(self.collapsed)
        self.panel.layout().setSpacing(0 if self.collapsed else 4)
        self.island_body.setVisible(not self.collapsed)
        self.setMinimumSize(190,46) if self.collapsed else self.setMinimumSize(330,174)
        self.setGeometry(self.island_target); self.collapse_button.set_angle(180.0 if self.collapsed else 0.0)
        self.outer.activate(); self.panel.layout().activate()
        self.apply_theme(); self.files.layout_timer.start(0)
        QTimer.singleShot(0,self.refresh)

    def bubble_menu(self):
        from ui.menus import show_bubbles
        show_bubbles(self)

    def manual_refresh(self):
        self.spin_angle=0; self.spin_timer.start(); QTimer.singleShot(0,self.refresh)
    def spin_step(self):
        self.spin_angle+=30
        self.buttons['refresh'].setIcon(toolbar_icon('refresh',self.icon_color,self.spin_angle))
        if self.spin_angle>=360: self.spin_timer.stop()

    def exit_app(self):
        if not self.files.dragging: QApplication.instance().quit()

    def animation_done(self):
        if self.hiding: self.hide(); self.setWindowOpacity(1)
    def hide_animated(self):
        if not self.isVisible(): return
        self.animation.stop(); self.hiding=True; self.animation.setStartValue(self.windowOpacity()); self.animation.setEndValue(0.0); self.animation.start(); self.save()
    def show_animated(self):
        self.animation.stop(); self.hiding=False; self.refresh(); self.setWindowOpacity(0.0); self.show(); self.raise_(); self.activateWindow(); self.animation.setStartValue(0.0); self.animation.setEndValue(1.0); self.animation.start()

    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton: self.offset=e.globalPosition().toPoint()-self.pos()
    def mouseMoveEvent(self,e):
        if self.offset is not None and e.buttons() & Qt.MouseButton.LeftButton: self.move(e.globalPosition().toPoint()-self.offset)
    def mouseReleaseEvent(self,e): self.offset=None
    def pin(self):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,not bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)); self.show()
    def add_folder(self):
        p=QFileDialog.getExistingDirectory(self,'Watch a folder');
        if p and local_path(p): self.folders.append(Path(p)); self.settings.setValue("folders", [str(x) for x in self.folders]); self.refresh()
    def refresh(self):
        if getattr(self,"island_transition",None) is not None or self.files.dragging or QApplication.mouseButtons() & Qt.MouseButton.LeftButton: return
        if self.scanning: return
        self.scanning=True
        self.scan_request.emit((tuple(self.folders),tuple(self.favourites),dict(self.signature or [])))
    @Slot(object)
    def apply_scan(self, payload):
        self.scanning=False
        folders,favourites,result=payload
        if result is None: return
        if folders!=tuple(self.folders) or favourites!=tuple(self.favourites):
            QTimer.singleShot(0,self.refresh); return
        recent,images=result
        if recent==self.signature: return
        if getattr(self,"island_transition",None) is not None or self.files.dragging or QApplication.mouseButtons() & Qt.MouseButton.LeftButton: return
        selected={i.data(Qt.ItemDataRole.UserRole) for i in self.files.selectedItems()}
        scroll=self.files.verticalScrollBar().value(); hscroll=self.files.horizontalScrollBar().value()
        current=self.files.currentItem(); current_path=current.data(Qt.ItemDataRole.UserRole) if current else None
        wanted={path for path,_ in recent}
        self.files.setUpdatesEnabled(False)
        try:
            for row in range(self.files.count()-1,-1,-1):
                if self.files.item(row).data(Qt.ItemDataRole.UserRole) not in wanted: self.files.takeItem(row)
            for row,(path,stamp) in enumerate(recent):
                existing=next((i for i in range(row,self.files.count()) if self.files.item(i).data(Qt.ItemDataRole.UserRole)==path),None)
                if existing is None:
                    item=QListWidgetItem(); item.setData(Qt.ItemDataRole.UserRole,path); self.files.insertItem(row,item); self.files.motion.arrive(path)
                elif existing!=row:
                    item=self.files.takeItem(existing); self.files.insertItem(row,item)
                else: item=self.files.item(row)
                if item.data(int(Qt.ItemDataRole.UserRole)+1)!=stamp:
                    item.setIcon(QIcon(QPixmap.fromImage(images[path])) if path in images else self.thumbnail(path)); item.setData(int(Qt.ItemDataRole.UserRole)+1,stamp)
                item.setText(("★ " if path in self.favourites else "")+Path(path).name); item.setToolTip(Path(path).name)
                if path==current_path: self.files.setCurrentItem(item, QItemSelectionModel.SelectionFlag.NoUpdate)
                item.setSelected(path in selected)
            self.update_stack(); self.signature=recent; self.count.setText(f"{len(recent)} files" if recent else "No recent files")
            self.files.doItemsLayout(); self.files.verticalScrollBar().setValue(scroll); self.files.horizontalScrollBar().setValue(hscroll)
        finally:
            self.files.setUpdatesEnabled(True)
    def update_stack(self):
        from ui.menus import is_image
        for i in range(self.files.count()):
            item=self.files.item(i)
            item.setHidden(self.stack_open and not is_image(item.data(Qt.ItemDataRole.UserRole)))

    def thumbnail(self,path):
        ext=Path(path).suffix.lower()
        if ext not in self.type_icons: self.type_icons[ext]=file_icon(path)
        return self.type_icons[ext]
    def open_file(self,item):
        path=item.data(Qt.ItemDataRole.UserRole)
        if not safe_file(path): return
        if QMessageBox.question(self,'Open file','Open this file in its associated application?\n'+Path(path).name) != QMessageBox.StandardButton.Yes: return
        try: os.startfile(path)
        except OSError: pass
    def menu(self,pos):
        item=self.files.itemAt(pos)
        if not item: return
        path=item.data(Qt.ItemDataRole.UserRole); menu=QMenu(self); op=menu.addAction('Open'); folder=menu.addAction('Show in File Explorer'); copy=menu.addAction('Copy file'); cp=menu.addAction('Copy path'); fav=menu.addAction('Unpin favourite' if path in self.favourites else 'Pin favourite'); action=menu.exec(self.files.mapToGlobal(pos))
        if not safe_file(path): return
        if action==fav:
            if path in self.favourites: self.favourites.remove(path)
            else: self.favourites.append(path)
            self.save(); self.signature=None; self.refresh()
        elif action==op: self.open_file(item)
        elif action==folder: subprocess.Popen([str(Path(os.environ['SystemRoot'])/'explorer.exe'),'/select,',path])
        elif action==copy:
            mime=QMimeData(); mime.setUrls([QUrl.fromLocalFile(path)]); QApplication.clipboard().setMimeData(mime)
        elif action==cp: QApplication.clipboard().setText(path)
