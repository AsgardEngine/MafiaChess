import bge
import bpy
from DataManager import DataManager
from ImportManagerEvents import ImportManagerEvents as IME
from LichessEvents import LichessEvents
from BoardEvents import BoardEvents
from collections import OrderedDict
from MouseEvents import MouseEvents

class LichessNodes(bge.types.KX_PythonComponent):
    args = OrderedDict([        
    ])
    
    instance = None
    def start(self, args):
        LichessNodes.instance = self
        LichessEvents.instance.register_observer(self)
        IME.instance.register_observer(self)
        BoardEvents.instance.register_observer(self)
        MouseEvents.instance.register_observer(self)
        self.status_node = None
        self.error_grp = None
    
    def newImport(self):
        self.error_grp = bpy.data.node_groups["Lichess_Server"]
        self.status_node = bpy.data.node_groups['Chess_Status'].nodes['status']
        self.status_node.string = 'START'
        self.clearNodesData('Lichess_Account')
        self.setCustomValue()

    def setCustomValue(self):
        inputs = bpy.data.node_groups['Custom_Clickable'].nodes['data'].inputs
        val = DataManager.getValue('custom')
        index = 0
        for v in val:
            try:
                inputs[index].default_value = v == '1'
                index += 1
            except IndexError:
                pass
        

    def onReleaseButton(self, btn):
        if btn.endswith('_custom'):
            val = self.getNodesValue('Custom_Clickable', btn)
            if val == None: return
            self.setNodesValue('Custom_Clickable', btn, not val)

    def clearLichessNodes(self):
        self.clearNodesData('Stockfish')
        self.clearNodesData('Move_data')
        self.clearNodesData('Lichess_GameStartEvent')
        self.clearNodesData('Lichess_GameFullEvent')
        self.clearNodesData('Lichess_GameStateEvent')
        self.clearNodesData('Lichess_GameFinishEvent')
        self.clearNodesData('Lichess_OpponentGone')

    def clearNodesData(self, grp_name):
        inputs = bpy.data.node_groups[grp_name].nodes['data'].inputs
        for input in inputs:
            if input.name == "": continue
            try:
                if input.name == "color": 
                    input.default_value = 'white'
                elif input.name == "fromSquare" or input.name == "toSquare": input.default_value = -1
                else: input.default_value = self.getDefaultValue(input.type)
            except (KeyError, AttributeError) as e: pass #print(f"Error:{grp_name} - {input.name} - {e}")

    def getDefaultValue(self, type):
        if type == 'INT': return 0
        elif type == 'VALUE': return 0.0
        elif type == 'BOOLEAN': return False
        else: return ''

    def getNodesValue(self, grp_name, val_name):
        inputs = bpy.data.node_groups[grp_name].nodes['data'].inputs
        for input in inputs:
            if input.name == val_name:
                return input.default_value
        return None

    def setNodesValue(self, grp_name, val_name, value):
        inputs = bpy.data.node_groups[grp_name].nodes['data'].inputs
        for input in inputs:

            if input.name == val_name:

                try: input.default_value = value
                except (KeyError, AttributeError) as e: print(f"Error: {input.name} - {e}")
                break

    def setNodesData(self, grp_name, data):
        inputs = bpy.data.node_groups[grp_name].nodes['data'].inputs
        for input in inputs:
            name = input.name
            if name == "": continue
            try:
                value = data
                if name == 'turn': value = len(data['moves'].split())%2 == 0
                else:
                    for k in name.split('_'):
                        value = value[k]

                if value == None: continue
                if name == 'ratingDiff' and value != 0:
                    n = bpy.data.node_groups["Lichess_Account"].nodes["data"]
                    r = n.inputs[1].default_value
                    n.inputs[1].default_value = int(r + value)
                
                input.default_value = value
            except (KeyError, AttributeError, TypeError) as e: 
                if name == 'winner':
                    input.default_value = ""
                else: pass #print(f"Error: {name} - {e}")
    
    def getProfileEvent(self, event):
        if event['status'] != 200: return
        self.setNodesData('Lichess_Account', event['result'])

    def streamServer(self, event):
        if event['status'] == 200: self.error_grp.nodes["lastStreamEvent"].integer = int(bge.logic.getRealTime())
        else: self.error_grp.nodes["errorMessage"].string = event['result']

    def tooManyRequests(self, event):
        self.error_grp.nodes["lastErrorTooManyRequests"].integer = int(bge.logic.getRealTime())
        self.error_grp.nodes["errorMessage"].string = event['result']

    def seekCreated(self, event):
        if event['status'] == 200:
            if event['result'] == 'None': self.status_node.string = 'SEARCHING'
            elif event['result'] == 'canceled':
                if str(self.status_node.string) == 'SEARCHING':
                    self.status_node.string = 'START'
        
    def gameStart(self, event):
        self.setNodesData('Lichess_GameStartEvent', event['game'])
    
    def gameFull(self, event):
        self.status_node.string = 'INGAME'
        self.setNodesData('Lichess_GameFullEvent', event)        
        self.gameState(event['state'])

    def gameState(self, event):
        self.setNodesData('Lichess_GameStateEvent', event)

    def gameFinish(self, event):
        self.status_node.string = 'START'
        self.setNodesData('Lichess_GameFinishEvent', event['game'])

    def opponentGone(self, event):
        self.setNodesData('Lichess_OpponentGone', event)
        grp = bpy.data.node_groups["Lichess_OpponentGone"]
        
    def update(self):
        pass
    