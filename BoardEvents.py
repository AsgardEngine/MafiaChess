import bge
from collections import OrderedDict

class BoardEvents(bge.types.KX_PythonComponent):
    
    args = OrderedDict([
    ])

    instance = None
    PromotionGrade = 5
    CURRENT_BOARD = None
    CURRENT_SIDE = True
    OFFLINE = True
    def start(self, args):
        BoardEvents.instance = self
        self.observers = []
    
    def register_observer(self, observer):
        self.observers.append(observer)

    def unregister_observer(self, observer):
        self.observers.remove(observer)
    
    def legalMoves(self, board, moves):
        for observer in self.observers:
            try:
                observer.legalMoves(board, moves)
            except AttributeError:
                pass

    def clearLichessNodes(self):
        for observer in self.observers:
            try:
                observer.clearLichessNodes()
            except AttributeError:
                pass

    def removeLegalMoves(self):
        for observer in self.observers:
            try:
                observer.removeLegalMoves()
            except AttributeError:
                pass

    def updatePromotion(self, grade):
        BoardEvents.PromotionGrade = grade
        for observer in self.observers:
            try:
                observer.updatePromotion(grade)
            except AttributeError:
                pass

    def movePerformed(self, move):
        for observer in self.observers:
            try:
                observer.movePerformed(move)
            except AttributeError:
                pass
                     
    def capturePerformed(self, move):
        for observer in self.observers:
            try:
                observer.capturePerformed(move)
            except AttributeError:
                pass
                     
    def castlingPerformed(self):
        for observer in self.observers:
            try:
                observer.castlingPerformed()
            except AttributeError:
                pass
                    
    def kingCheck(self):
        for observer in self.observers:
            try:
                observer.kingCheck()
            except AttributeError:
                pass
              
    def update(self):
        pass