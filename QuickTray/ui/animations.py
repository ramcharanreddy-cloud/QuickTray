from time import monotonic
from PySide6.QtCore import QTimer
class Motion:
    def __init__(self, view):
        self.view=view; self.hover={}; self.arrivals={}; self.target=None
        self.timer=QTimer(view); self.timer.setInterval(16); self.timer.timeout.connect(self.tick)
    def point(self,path):
        if path!=self.target: self.target=path; self.timer.start()
    def arrive(self,path):
        self.arrivals[path]=monotonic(); self.timer.start()
    def tick(self):
        if not self.view.isVisible(): self.hover.clear(); self.arrivals.clear(); self.timer.stop(); return
        active=False
        for path in set(self.hover)|({self.target} if self.target else set()):
            goal=float(path==self.target); v=self.hover.get(path,0); v+=(goal-v)*.28
            if abs(goal-v)<.02: v=goal
            else: active=True
            if v: self.hover[path]=v
            else: self.hover.pop(path,None)
        self.arrivals={p:t for p,t in self.arrivals.items() if monotonic()-t<.22}
        self.view.viewport().update()
        if not active and not self.arrivals: self.timer.stop()
    def progress(self,path): return min(1,(monotonic()-self.arrivals[path])/.22) if path in self.arrivals else 1
