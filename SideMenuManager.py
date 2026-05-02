import bge
import bpy
from MouseEvents import MouseEvents
from LichessEvents import LichessEvents
from ImportManagerEvents import ImportManagerEvents as IME
from LichessAPI import LichessAPI
from collections import OrderedDict

class SideMenuManager(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        self.objects = self.object.scene.objects
        
        LichessEvents.instance.register_observer(self)
        IME.instance.register_observer(self)
        MouseEvents.instance.register_observer(self)
    
    def newImport(self):
        self.hideUI()

    def updatePhysics(self, restore=[], suspend=[]):
        for obj in restore:
            if 'Clickable' in obj: 
                obj.restorePhysics()
        for obj in suspend:
            if 'Clickable' in obj:
                obj.suspendPhysics()
    
    def update(self):
        pass

    def onReleaseButton(self, btn):
        if btn == "Settings_btn": self.displaySettings()
        elif btn == "Token_btn": self.displayToken()
        elif btn == "Stockfish_btn": self.displayStockfish()
        elif btn == "Custom_btn": self.displayCustom()
    
    def hideUI(self):
        self.updatePhysics(suspend=IME.tokens)
        self.updatePhysics(suspend=IME.settings)
        self.updatePhysics(suspend=IME.customs)
        self.updatePhysics(suspend=IME.stockfishs)
        self.updatePhysics(restore=IME.moves)

        bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string = "MOVES"

    def displayCustom(self):
        st = bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string
        if st == "CUSTOM":
            self.hideUI()
            return
        
        self.updatePhysics(suspend=IME.tokens)
        self.updatePhysics(suspend=IME.settings)
        self.updatePhysics(restore=IME.customs)
        self.updatePhysics(suspend=IME.stockfishs)
        self.updatePhysics(suspend=IME.moves)
        bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string = "CUSTOM"

    def displayToken(self):
        st = bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string
        if st == "TOKEN":
            self.hideUI()
            return
        
        self.updatePhysics(restore=IME.tokens)
        self.updatePhysics(suspend=IME.settings)
        self.updatePhysics(suspend=IME.customs)
        self.updatePhysics(suspend=IME.stockfishs)
        self.updatePhysics(suspend=IME.moves)
        bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string = "TOKEN"

    def displayStockfish(self):
        st = bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string
        if st == "STOCKFISH":
            self.hideUI()
            return
        
        self.updatePhysics(suspend=IME.tokens)
        self.updatePhysics(suspend=IME.settings)
        self.updatePhysics(suspend=IME.customs)
        self.updatePhysics(restore=IME.stockfishs)
        self.updatePhysics(suspend=IME.moves)
        bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string = "STOCKFISH"

    def displaySettings(self):
        st = bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string
        if st == "SETTINGS":
            self.hideUI()
            return
        
        self.updatePhysics(suspend=IME.tokens)
        self.updatePhysics(restore=IME.settings)
        self.updatePhysics(suspend=IME.customs)
        self.updatePhysics(suspend=IME.stockfishs)
        self.updatePhysics(suspend=IME.moves)
        bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string = "SETTINGS"
