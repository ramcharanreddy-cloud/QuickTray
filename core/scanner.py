from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, QSize, Qt
from PySide6.QtGui import QImageReader
from core.security import local_path, safe_file

class ScanWorker(QObject):
    finished = Signal(object)
    @staticmethod
    def scan(folders, favourites, previous):
        found={}
        for folder in folders:
            try:
                if not local_path(folder): continue
                for p in folder.iterdir():
                    try:
                        if not safe_file(p):
                            continue
                        info = p.stat()
                        found[str(p)] = max(
                            getattr(info, "st_birthtime", info.st_ctime),
                            info.st_mtime
                        )
                    except OSError: pass
            except OSError: pass
        pinned=[(p,found.get(p,0)) for p in favourites if safe_file(p)]
        recent=pinned+sorted([(p,t) for p,t in found.items() if p not in favourites],key=lambda x:(x[1],x[0]),reverse=True)[:30]
        images={}
        for path,stamp in recent:
            if previous.get(path)==stamp: continue
            if Path(path).suffix.lower() not in ('.png','.jpg','.jpeg','.bmp','.webp','.gif'): continue
            try:
                if safe_file(path) and Path(path).stat().st_size <= 20*1024*1024:
                    reader=QImageReader(path); size=reader.size()
                    if size.isValid() and size.width()*size.height() <= 16000000:
                        reader.setScaledSize(size.scaled(QSize(76,60),Qt.AspectRatioMode.KeepAspectRatio))
                        img=reader.read()
                        if not img.isNull(): images[path]=img
            except OSError: pass
        return recent,images
    @Slot(object)
    def run(self, request):
        folders,favourites,previous=request
        try: result=self.scan(folders,favourites,previous)
        except Exception: result=None
        self.finished.emit((folders,favourites,result))
