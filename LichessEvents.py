import bge
from collections import OrderedDict

class LichessEvents(bge.types.KX_PythonComponent):
    
    args = OrderedDict([
    ])

    instance = None
    ONLINE = False
    gameTime = 10
    gameInc = 0
    gameAI = False
    lastEmptyLine = 0
    delayBetweenLine = 0

    playerColor = False

    RANKED = True
    STATUS = "START"

    def start(self, args):
        LichessEvents.lastEmptyLine = 0
        LichessEvents.instance = self
        self.observers = []
    
    def register_observer(self, observer):
        self.observers.append(observer)

    def unregister_observer(self, observer):
        self.observers.remove(observer)
    
    def notify_observers(self, event):
        print(f"EVENT {event}")
        try:
            if event['status'] == 429:
                self.tooManyRequests(event)
        except (KeyError, AttributeError):
                pass
        event_type = event['type']
        if event_type == 'tokenTest':
            self.tokenTest(event)
        elif event_type == 'streamEvent':  
            self.streamServer(event)
        elif event_type == 'makeMove':
            self.makeMoveEvent(event)
        elif event_type == 'createSeek':
            self.seekCreated(event)
        elif event_type == 'gameStart':
            self.gameStart(event)
        elif event_type == 'gameFull':
            self.gameFull(event)
        elif event_type == 'gameState':
            self.gameState(event)
        elif event_type == 'gameFinish':
            self.gameFinish(event)
        elif event_type == 'opponentGone':
            self.opponentGone(event)
        elif event_type == 'abort':
            self.abortEvent(event)
        elif event_type == 'draw' or event_type == 'declineDraw':
            self.drawEvent(event)
        elif event_type == 'resign':
            self.resignEvent(event)
        elif event_type == 'claimVictory':
            self.claimVictoryEvent(event)
        elif event_type == 'chatLine':
            self.chatLineEvent(event)
        elif event_type == 'getProfile':
            self.getProfileEvent(event)
            
    def tooManyRequests(self, event):
        for observer in self.observers:
            try:
                observer.tooManyRequests(event)
            except AttributeError:
                pass      
    
    def chatLineEvent(self, event):
        for observer in self.observers:
            try:
                observer.chatLineEvent(event)
            except AttributeError:
                pass        
    def abortEvent(self, event):
        for observer in self.observers:
            try:
                observer.abortEvent(event)
            except AttributeError:
                pass        
    def makeMoveEvent(self, event):
        for observer in self.observers:
            try:
                observer.makeMoveEvent(event)
            except AttributeError:
                pass
    def resignEvent(self, event):
        for observer in self.observers:
            try:
                observer.resignEvent(event)
            except AttributeError:
                pass
    def abortEvent(self, event):
        for observer in self.observers:
            try:
                observer.abortEvent(event)
            except AttributeError:
                pass

    def claimVictoryEvent(self, event):
        for observer in self.observers:
            try:
                observer.claimVictoryEvent(event)
            except AttributeError:
                pass

    def testTokenValidity(self, token):
        for observer in self.observers:
            try:
                observer.testTokenValidity(token)
            except AttributeError:
                pass

    def tokenTest(self, event):
        for observer in self.observers:
            try:
                observer.tokenTest(event)
            except AttributeError:
                pass
    
    def getProfileEvent(self, event):
        for observer in self.observers:
            try:
                observer.getProfileEvent(event)
            except AttributeError:
                pass

    def getProfile(self):
        for observer in self.observers:
            try:
                observer.getProfile()
            except AttributeError:
                pass
    
    def streamServer(self, event):
        for observer in self.observers:
            try:
                observer.streamServer(event)
            except AttributeError:
                pass

    def seekCreated(self, event):
        for observer in self.observers:
            try:
                observer.seekCreated(event)
            except AttributeError:
                pass

    def gameStart(self, event):
        LichessEvents.STATUS = "INGAME"
        LichessEvents.playerColor = event['game']['color'] == 'white'
        for observer in self.observers:
            try:                
                observer.gameStart(event)
            except AttributeError:                    
                pass

    def gameFull(self, event):
        for observer in self.observers:
            try:
                observer.gameFull(event)
            except AttributeError:
                pass

    def gameState(self, event):
        for observer in self.observers:
            try:
                observer.gameState(event)
            except AttributeError:
                pass
    
    def gameFinish(self, event):
        LichessEvents.STATUS = "FINISH"
        for observer in self.observers:
            try:
                observer.gameFinish(event)
            except AttributeError:
                pass

    def opponentGone(self, event):
        for observer in self.observers:
            try:
                observer.opponentGone(event)
            except AttributeError:
                pass
    
    def startListeningServer(self):
        for observer in self.observers:
                try:
                    observer.startListeningServer()
                except AttributeError:
                    pass

    def stopListeningServer(self):
        for observer in self.observers:
                try:
                    observer.stopListeningServer()
                except AttributeError:
                    pass
                
    def makeMove(self, uciMove):
        for observer in self.observers:
                try:
                    observer.makeMove(uciMove)
                except AttributeError:
                    pass
    
    def drawEvent(self, event):
        for observer in self.observers:
            try:
                observer.drawEvent(event)
            except AttributeError:
                pass
    def update(self):
        pass
        