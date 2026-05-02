from Script.LichessNodes import LichessNodes
import bge
import bpy
import chess
from ImportManagerEvents import ImportManagerEvents as IME
from LichessEvents import LichessEvents
from BoardEvents import BoardEvents
from Audio import Audio
from MouseEvents import MouseEvents
from StockfishManager import StockfishManager as SM
from collections import OrderedDict
'''
SAVE FEN in here
'''
class History(bge.types.KX_PythonComponent):
    args = OrderedDict([])

    instance = None

    def start(self, args):
        History.instance = self
        self.scene = self.object.scene
        self.objects = self.scene.objects

        self.historyFen = []
        self.historyIndex = 0
        self.subEvents()
        
    def subEvents(self):
        LichessEvents.instance.register_observer(self)
        BoardEvents.instance.register_observer(self)
        MouseEvents.instance.register_observer(self)
        
    def update(self):
        pass
    
    def saveFenInHistory(self, board):
        fen = self.getBoardFenNode(self.board)
        data = {'fen_node': fen, 'fen': self.board.fen()}
        self.historyFen.append(data)

        bpy.data.node_groups["Chess_Board"].nodes["fen"].string = fen

        if self.historyIndex == (len(self.historyFen)-2): self.displayHistoryPosition(1000)

    def onLeftArrow(self): self.displayHistoryPosition(-1)
    def onRightArrow(self): self.displayHistoryPosition(+1)
    def onSpace(self): self.displayHistoryPosition(1000)

    def displayHistoryPosition(self, direction):
        history_size = len(self.historyFen) - 1
        self.historyIndex = self.historyIndex + direction
        self.historyIndex = self.historyIndex if self.historyIndex <= history_size else history_size
        self.historyIndex = 0 if self.historyIndex < 0 else self.historyIndex

        grp = bpy.data.node_groups["Chess_Board"]
        grp.nodes["fenNotation"].string = self.historyFen[self.historyIndex]['fen']
        grp.nodes["historyFen"].string = self.historyFen[self.historyIndex]['fen_node']

    def onReleaseButton(self, btn):
        if btn == "Move_back10_btn": self.displayHistoryPosition(-20)
        elif btn == "Move_back_btn": self.displayHistoryPosition(-1)
        elif btn == "Move_forward_btn": self.displayHistoryPosition(1)
        elif btn == "Move_forward10_btn": self.displayHistoryPosition(20)
        elif btn == "Move_current_btn": self.displayHistoryPosition(1000)

    def clearPreMoveAndFocusOnLastFen(self):
        self.playerStack = []
        self.PreBoard = None

        bpy.data.node_groups["Chess_Board"].nodes["preFen"].string = ""
        self.displayHistoryPosition(1000)
    
    def getBoardFenNode(self, board):
        board_fen = ''
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            board_fen += ' ' if piece is None else piece.symbol()
        return board_fen

    def setMove(self):
        board = chess.Board(BoardEvents.CURRENT_BOARD)
        
        data = ""
        for move in board.move_stack:
            data += move.uci()
            data += "        "
        LichessNodes.instance.setNodesValue("Move_Data", "data", data)
    