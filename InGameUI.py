from pickle import TRUE
import bge
import bpy
from MouseEvents import MouseEvents
from ImportManagerEvents import ImportManagerEvents
from LichessNodes import LichessNodes as LN
from LichessEvents import LichessEvents
from LichessAPI import LichessAPI
from collections import OrderedDict

class InGameUI(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])
    
    instance = None
    BUTTONS = ['Game_Play_btn', 'Game_Stop_btn', 'Game_Abort_btn', 'Game_Draw_btn', 'Game_Resign_btn',
               'Game_Decline_btn', 'Game_Ranked_checkbox']
    def start(self, args):
        InGameUI.instance = self
        self.objects = self.object.scene.objects
        
        LichessEvents.instance.register_observer(self)
        ImportManagerEvents.instance.register_observer(self)
        MouseEvents.instance.register_observer(self)

        self.active = False
        self.player_color = False
    
    def newImport(self):
        self.updatePhysics(suspend=InGameUI.BUTTONS)
        self.updatePhysics(['Game_Play_btn'])
        self.updatePhysics(['Game_Ranked_checkbox'])

    def updatePhysics(self, restore=[], suspend=[]):
        for name in restore:
            self.objects[name].restorePhysics()
        for name in suspend:
            self.objects[name].suspendPhysics()
        
    def streamServer(self, event):
        if event['result'] == 'alive' or event['status'] != 200: return
        self.active = True
        self.updatePhysics(['Game_Play_btn'])

    def update(self):
        pass

#region MouseEvents
    def onReleaseButton(self, btn):
        if btn == "Game_Play_btn": self.onClickPlay()
        elif btn == "Game_Stop_btn": self.onClickStop()
        elif btn == "Game_Abort_btn": self.onClickAbort()
        elif btn == "Game_Draw_btn": self.onClickDraw()
        elif btn == "Game_Decline_btn": self.onClickDrawCancel()
        elif btn == "Game_Resign_btn": self.onClickResign()
        elif btn == "Game_Ranked_checkbox": self.rankedMode()

    def rankedMode(self):
        print("RANKED")
        LichessEvents.RANKED = not LichessEvents.RANKED
        bpy.data.node_groups["Chess_Board"].nodes["ranked"].boolean = LichessEvents.RANKED

    def onClickPlay(self):
        bpy.data.node_groups["Lichess_Server"].nodes["seekCreatedAt"].integer = int(bge.logic.getRealTime())
        if LichessEvents.ONLINE:
            self.active = False
            LichessAPI.instance.play()
        else: MouseEvents.instance.onReleaseButton('Token_btn')
    
    def challengeAIEvent(self, event):
        self.active = event['status'] != 200 or event['status'] != 201

    def onClickStop(self):
        self.active = False
        LichessAPI.instance.stopSeek()

    def onClickDraw(self):
        self.updatePhysics(suspend=['Game_Draw_btn'])
        LichessAPI.instance.draw()
        key = "wdraw" if self.player_color else "bdraw"
        LN.instance.setNodesValue('Lichess_GameStateEvent', key, True)

    def drawEvent(self, event):
        if event['status'] != 200:
            if event['type'] == 'draw': self.updatePhysics(['Game_Draw_btn'])        
            elif event['type'] == 'declineDraw': self.updatePhysics(['Game_Decline_btn'])
        else:
            if event['type'] == 'draw': self.updatePhysics(['Game_Decline_btn'])        
            elif event['type'] == 'declineDraw': self.updatePhysics(['Game_Draw_btn'])

    def onClickDrawCancel(self):
        self.updatePhysics(suspend=['Game_Decline_btn'])
        LichessAPI.instance.declineDraw()
        LN.instance.setNodesValue('Lichess_GameStateEvent', 'wdraw', False)
        LN.instance.setNodesValue('Lichess_GameStateEvent', 'bdraw', False)
    
    def chatLineEvent(self, event):
        if event['text'].endswith('declines draw'):
            self.drawEvent({'status': 200, 'type': 'declineDraw'})
            self.updatePhysics(suspend=['Game_Decline_btn'])
            LN.instance.setNodesValue('Lichess_GameStateEvent', 'bdraw', False)
            LN.instance.setNodesValue('Lichess_GameStateEvent', 'wdraw', False)

    def onClickResign(self):
        self.active = False
        LichessAPI.instance.resign()

    def resignEvent(self, event):
        self.active = event['status'] != 200

    def onClickAbort(self):
        self.active = False
        LichessAPI.instance.abort()

    def abortEvent(self, event):
        self.active = event['status'] != 200
#endregion

#region LichessEvents

    def seekCreated(self, event):
        valide = event['status'] == 200 or event['status'] == 201
        if event['result'] == 'canceled' or not valide :
            self.updatePhysics(['Game_Play_btn'], ['Game_Stop_btn'])
        else: self.updatePhysics(['Game_Stop_btn'], ['Game_Play_btn'])
        
        self.active = True

    def gameStart(self, gameStart):
        self.updatePhysics(['Game_Abort_btn'], ['Game_Play_btn', 'Game_Stop_btn'])
        self.player_color = gameStart['game']['color'] == 'white'

    def gameFull(self, event):        
        self.gameState(event['state'])
        if len(event['state']['moves'].split()) > 2:
            self.updatePhysics(['Game_Draw_btn', 'Game_Resign_btn'], ['Game_Abort_btn'])
        self.active = True

    def gameState(self, event):
        if len(event['moves'].split()) == 2:
            self.updatePhysics(['Game_Draw_btn', 'Game_Resign_btn'], ['Game_Abort_btn'])

        key = "bdraw" if self.player_color else "wdraw"
        if key in event and event[key]: self.updatePhysics(['Game_Decline_btn'])
        key = "wdraw" if self.player_color else "bdraw"
        if key in event and event[key]: self.updatePhysics(suspend=['Game_Draw_btn'])

    def gameFinish(self, event):
        self.updatePhysics(['Game_Play_btn'], ['Game_Abort_btn', 'Game_Draw_btn', 'Game_Resign_btn', 'Game_Decline_btn'])
        LN.instance.setNodesValue('Lichess_GameStateEvent', "wdraw", False)
        LN.instance.setNodesValue('Lichess_GameStateEvent', "bdraw", False)
        self.active = True

    def serverConnected(self, connected):
        bpy.data.node_groups["Lichess_Server"].nodes["Online"].boolean = connected
#endregion