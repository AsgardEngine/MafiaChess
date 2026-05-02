import random
import bpy
import bge
from DataManager import DataManager as DM
import webbrowser
import pyperclip as pc
from MouseEvents import MouseEvents
from ImportManagerEvents import ImportManagerEvents
from LichessEvents import LichessEvents
from collections import OrderedDict

class Connexion(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ('CheckToken', True)
    ])
    
    instance = None
    BUTTONS = ['Token_Create_btn', 'Token_Past_btn', 'Token_Login_btn']

    def start(self, args):
        Connexion.instance = self
        self.scene = self.object.scene
        self.objects = self.object.scene.objects
        self.all_Connexion_Objects = {}
        self.check_token = args['CheckToken']
        
        LichessEvents.instance.register_observer(self)
        ImportManagerEvents.instance.register_observer(self)
        MouseEvents.instance.register_observer(self)

        self.token = None

        self.token_ok = False
        self.past_btn_active = True
        self.login_btn_active = self.token_ok

    def newImport(self):
        if self.check_token: LichessEvents.instance.testTokenValidity(DM.getValue('player_token'))
                
    def onReleaseButton(self, btn):
        if btn == "Token_Create_btn": self.openLichess()
        elif btn == "Token_Past_btn": self.onPastToken()
        elif btn == "Token_Login_btn": self.startConnection()
        elif btn == "Settings_Exit_btn": self.onExit()

    def openLichess(self):
        webbrowser.open(DM.getValue('creator_token') + str(random.randint(1, 1000)))
    
    def onExit(self):
        self.saveCustomValue()
        LichessEvents.instance.stopListeningServer()
        bge.logic.endGame()
    
    def saveCustomValue(self):
        inputs = bpy.data.node_groups['Custom_Clickable'].nodes['data'].inputs
        val = ""
        for input in inputs:
            if input.name == "": continue
            if input.default_value: val += "1"
            else: val += "0"
        DM.writeData('custom', val)

    def onPastToken(self):
        if not self.past_btn_active: return
        self.past_btn_active = False

        self.token = pc.paste()
        LichessEvents.instance.testTokenValidity(self.token)
    
    def startConnection(self):
        if not self.login_btn_active or not self.token_ok: return
        self.login_btn_active = False

        LichessEvents.instance.startListeningServer()

    def streamServer(self, event):
        LichessEvents.ONLINE = event['status'] == 200
        self.login_btn_active = self.token_ok
        st = bpy.data.node_groups["Chess_Status"].nodes["sideStatus"].string
        if st == "TOKEN": MouseEvents.instance.onReleaseButton('Token_btn')

    def tokenTest(self, event):
        if event['status'] != 200:
            self.error_grp_node.nodes["tokenTest"].integer = False
            self.error_grp_node.nodes["errorMessage"].string = event['result']
            self.past_btn_active = True
            self.login_btn_active = self.token_ok
            return
        
        tokens_info = event['result']
        token_info = ""

        try:
            first_token = next(iter(tokens_info))
            if tokens_info[first_token] is not None:
                info = tokens_info[first_token]

                required_scopes = {'challenge:read', 'challenge:write', 'board:play'}
                if all(scope in info['scopes'] for scope in required_scopes):
                    DM.writeData("player_token", first_token)                                  
                    self.token_ok = True
                    self.past_btn_active = True
                    self.login_btn_active = self.token_ok
                    bpy.data.node_groups["Lichess_Server"].nodes["tokenTest"].boolean = True
                    LichessEvents.instance.getProfile()
                    return
                else:                    
                    token_info = 'Required scopes: challenge:read, challenge:write, board:play'
            else:
                token_info = 'Token not valid!'
        except (KeyError, AttributeError):
            token_info = 'Undefined ERROR!'

        self.past_btn_active = True
        self.login_btn_active = self.token_ok

        bpy.data.node_groups["Lichess_Server"].nodes["tokenTest"].boolean = False
        bpy.data.node_groups["Lichess_Server"].nodes["errorMessage"].string = token_info
        
                