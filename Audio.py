import bge
# pyright: reportMissingImports=false
import aud
from LichessEvents import LichessEvents
from BoardEvents import BoardEvents
from collections import OrderedDict
from MouseEvents import MouseEvents

class Audio(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])
    sound_dictionary = {
        "button": "//Assets/Default_BOX/Sounds/button.mp3",
        "capture": "//Assets/Default_BOX/Sounds/capture.mp3",
        "castle": "//Assets/Default_BOX/Sounds/castle.mp3",
        "check": "//Assets/Default_BOX/Sounds/check.mp3",
        "gameOver": "//Assets/Default_BOX/Sounds/gameOver.mp3",
        "move": "//Assets/Default_BOX/Sounds/move.mp3",
        "start": "//Assets/Default_BOX/Sounds/start.mp3"
    }
    instance = None
    def start(self, args):
        Audio.instance = self
        self.device = aud.Device()
        self.device.volume = 0.2
        self.handle = None

        LichessEvents.instance.register_observer(self)
        BoardEvents.instance.register_observer(self)
        MouseEvents.instance.register_observer(self)
        
        self.button = self.getSound('button')
        self.capture = self.getSound('capture')
        self.castle = self.getSound('castle')
        self.check = self.getSound('check')
        self.mate = self.getSound('gameOver')
        self.move = self.getSound('move')
        self.startGame = self.getSound('start')
    
    def playMySound(self, sound):
        self.handle = self.device.play(sound)

    def getSound(self, name):
        return aud.Sound.cache(aud.Sound.file(bge.logic.expandPath(Audio.sound_dictionary[name])))

    def onClickButton(self, btn):
        self.playMySound(self.button)

    def playMoveSound(self, board, move):
        if board.gives_check(move): self.kingCheckSound()
        elif board.is_capture(move): self.capturePerformedSound()
        elif board.is_castling(move): self.castlingPerformedSound()
        else: self.movePerformedSound()

    def movePerformedSound(self):
        self.playMySound(self.move)
    
    def capturePerformedSound(self):
        self.playMySound(self.capture)

    def castlingPerformedSound(self):
        self.playMySound(self.castle)
    
    def kingCheckSound(self):
        self.playMySound(self.check)

    def gameStart(self, event):
        self.playMySound(self.startGame)
    
    def gameFinish(self, event):
        self.playMySound(self.mate)

    def volumeChange(self, vol):
        self.device.volume = vol
    
    def getVolume(self):
        return self.device.volume

    def update(self):
        pass
