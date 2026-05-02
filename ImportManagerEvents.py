import bge
from collections import OrderedDict

class ImportManagerEvents(bge.types.KX_PythonComponent):
    
    args = OrderedDict([
    ])

    instance = None
    squares = {}
    sounds = []
    customs = []
    settings = []
    stockfishs = []
    tokens = []
    moves = []
    def start(self, args):
        ImportManagerEvents.instance = self
        self.observers = []

    def register_observer(self, observer):
        self.observers.append(observer)
        #print(f'OBSERVER {observer.__class__.__name__}')
        if len(self.observers) == 10:
            self.importBox()

    def unregister_observer(self, observer):
        self.observers.remove(observer)

    def newImport(self):
        for observer in self.observers:
            try:
                #print(f'OBSERVER {observer.__class__.__name__}')
                observer.newImport()
            except AttributeError:
                pass

    def importBox(self):
        for observer in self.observers:
            try:
                observer.importBox()
            except AttributeError:
                pass

    def update(self):
        pass

    def updateSquarePosition(self, color):
        white_board = ImportManagerEvents.squares[0].worldPosition.x < ImportManagerEvents.squares[63].worldPosition.x
        if color == white_board: return
        
        for i in range(32):
            sqrs = ImportManagerEvents.squares
            i_pos = sqrs[i].worldPosition.copy()
            sqrs[i].worldPosition = sqrs[63-i].worldPosition
            sqrs[63-i].worldPosition = i_pos
