import bge
from collections import OrderedDict

class MouseEvents(bge.types.KX_PythonComponent):
    
    args = OrderedDict([
    ])

    instance = None
    X = 0
    Z = 0
    Hold = ""
    Over = ""
    Click = False
    Millisecond = False
    ChangeInX = 0
    def start(self, args):
        MouseEvents.instance = self
        self.observers = []

    def register_observer(self, observer):
        self.observers.append(observer)

    def unregister_observer(self, observer):
        self.observers.remove(observer)

    def onClickButton(self, btn):
        for observer in self.observers:
            try:
                observer.onClickButton(btn)
            except AttributeError:
                pass

    def onReleaseButton(self, btn):
        for observer in self.observers:
            try:
                observer.onReleaseButton(btn)
            except AttributeError:
                pass
    
    def onReleasePiece(self, from_square, to_square):
        for observer in self.observers:
            try:
                observer.onReleasePiece(from_square, to_square)
            except AttributeError:
                pass
            
    def onCancelPiece(self, piece):
        for observer in self.observers:
            try:
                observer.onCancelPiece(piece)
            except AttributeError:
                pass

    def onClickPiece(self, piece):
        for observer in self.observers:
            try:
                observer.onClickPiece(piece)
            except AttributeError:
                pass
    
    def onReleaseLeftClick(self):
        for observer in self.observers:
            try:
                observer.onReleaseLeftClick()
            except AttributeError:
                pass

    def onRightClick(self, objHit):
        for observer in self.observers:
            try:
                observer.onRightClick(objHit)
            except AttributeError:
                pass
    
    def onLeftClick(self):
        for observer in self.observers:
            try:
                observer.onLeftClick()
            except AttributeError:
                pass
    
    def onReleaseRightClick(self, objHit):
        for observer in self.observers:
            try:
                observer.onReleaseRightClick(objHit)
            except AttributeError:
                pass
    
    def onLeftArrow(self):
        for observer in self.observers:
            try:
                observer.onLeftArrow()
            except AttributeError:
                pass

    def onRightArrow(self):
        for observer in self.observers:
            try:
                observer.onRightArrow()
            except AttributeError:
                pass

    def onUpArrow(self):
        for observer in self.observers:
            try:
                observer.onUpArrow()
            except AttributeError:
                pass

    def onDownArrow(self):
        for observer in self.observers:
            try:
                observer.onDownArrow()
            except AttributeError:
                pass

    def onSpace(self):
        for observer in self.observers:
            try:
                observer.onSpace()
            except AttributeError:
                pass

    def update(self):
        pass