from ChessNodes import ChessNodes
import bge
import bpy
import chess
from ImportManagerEvents import ImportManagerEvents as IME
from LichessEvents import LichessEvents
from LichessNodes import LichessNodes
from BoardEvents import BoardEvents
from Audio import Audio
from MouseEvents import MouseEvents
from StockfishManager import StockfishManager as SM
from collections import OrderedDict

class Board(bge.types.KX_PythonComponent):
    args = OrderedDict([])

    instance = None

    def start(self, args):
        Board.instance = self
        self.scene = self.object.scene
        self.objects = self.scene.objects

        self.playerIsWhite, self.stopSendingMove = True, False
        self.board, self.PreBoard = None, None
        self.playerStack, self.historyFen = [], []
        self.historyIndex = 0
        self.wCaptures, self.bCaptures = "", ""
        self.subEvents()
        
    def subEvents(self):
        LichessEvents.instance.register_observer(self)
        BoardEvents.instance.register_observer(self)
        MouseEvents.instance.register_observer(self)
        IME.instance.register_observer(self)

    def setPreBoard(self):
        self.PreBoard = self.board.copy()
        self.PreBoard.turn = self.playerIsWhite

    def newImport(self): self.clearBoard(BoardEvents.OFFLINE, self.playerIsWhite)

    def update(self): self.checkPlayerStack()

    def onRightClick(self, objHit): self.clearPreMoveAndFocusOnLastFen()
    def onClickPiece(self, square): self.displayLegalMoves(square['Square'])
    def onCancelPiece(self, square): BoardEvents.instance.removeLegalMoves()
    def onReleasePiece(self, from_square, to_square):
        BoardEvents.instance.removeLegalMoves()
        if from_square == to_square: return
        
        board = self.PreBoard if self.PreBoard else self.board
        piece_at = board.piece_at(from_square)

        if not piece_at or piece_at.color != self.playerIsWhite: return
        
        uci = chess.SQUARE_NAMES[from_square] + chess.SQUARE_NAMES[to_square]
        move = chess.Move.from_uci(uci)

        if piece_at.piece_type == chess.PAWN and (to_square >= 56 or to_square <= 7):
            move.promotion = BoardEvents.PromotionGrade

        self.playerStack.append(move)
        self.updatePremove()
    
    def updatePremove(self):
        self.setPreBoard()
        for premove in self.playerStack:
            piece = self.PreBoard.piece_at(premove.from_square)
            if premove.promotion: piece.piece_type = premove.promotion
            self.PreBoard.set_piece_at(premove.to_square, piece)
            self.PreBoard.remove_piece_at(premove.from_square)

        bpy.data.node_groups["Chess_Board"].nodes["preFen"].string = self.getBoardFenNode(self.PreBoard)
    
    def checkPlayerStack(self):
        if not BoardEvents.OFFLINE and (self.stopSendingMove or (self.board.turn != self.playerIsWhite) or len(self.playerStack) <= 0): return

        move = self.playerStack.pop(0)

        if not self.board.is_legal(move):                
            self.clearPreMoveAndFocusOnLastFen()
            return
        
        self.performMove(move)
        if not BoardEvents.OFFLINE: LichessEvents.instance.makeMove(move.uci())

    def makeMoveEvent(self, event):
        if event['status'] == 200: return
        self.board.pop()
        self.clearPreMoveAndFocusOnLastFen()
    
    def performMove(self, move):
        Audio.instance.playMoveSound(self.board, move)
        self.getCaptureType(move)                
        self.board.push(move)
        BoardEvents.CURRENT_BOARD = self.board

        if BoardEvents.OFFLINE: self.playerIsWhite = self.board.turn
        self.updatePremove()

        self.updateChessBoardNodes(move)
        self.saveFenInHistory()
        self.setMoveList()
    
    def getCaptureType(self, move):
        if self.board.is_capture(move):
            if self.board.turn: self.wCaptures += str(self.board.piece_type_at(move.to_square))
            else : self.bCaptures += str(self.board.piece_type_at(move.to_square))

    def updateChessBoardNodes(self, move=None):
        ChessNodes.instance.chessBoard(self.board, move, self.wCaptures, self.bCaptures)

    def displayLegalMoves(self, square):
        from_mask = chess.BB_SQUARES[square]

        if self.board.turn != self.playerIsWhite:
            if not self.PreBoard: self.setPreBoard()
            legalMoves = self.PreBoard.generate_pseudo_legal_moves(from_mask=from_mask)        
            BoardEvents.instance.legalMoves(self.PreBoard, list(legalMoves))
            return
        
        legalMoves = self.board.generate_legal_moves(from_mask=from_mask)        
        BoardEvents.instance.legalMoves(self.board, list(legalMoves))

    def clearBoard(self, OFFLINE, color):
        BoardEvents.instance.clearLichessNodes()
        BoardEvents.OFFLINE, self.stopSendingMove = OFFLINE, False
        self.playerIsWhite = color
        BoardEvents.CURRENT_SIDE = color
        self.wCaptures, self.bCaptures = "", ""
        self.historyFen = []
        self.historyIndex = 0
        self.board = chess.Board()
        self.saveFenInHistory()
        self.clearPreMoveAndFocusOnLastFen()
        self.updateChessBoardNodes()
        BoardEvents.instance.removeLegalMoves()
        IME.instance.updateSquarePosition(self.playerIsWhite)
        
    def gameStart(self, event):
        color = event['game']['color'].startswith('w')
        self.clearBoard(False, color)
                
    def gameFull(self, event):
        self.gameState(event["state"])

    def gameState(self, state):
        serverMoves = state['moves'].split()
        localLen, serverLen = len(self.board.move_stack), len(serverMoves)

        for i in range(localLen, serverLen):
            move = chess.Move.from_uci(serverMoves[i])
            self.performMove(move)
            
        if len(self.playerStack) <= 0: self.clearPreMoveAndFocusOnLastFen()
    
    def gameFinish(self, event):
        BoardEvents.OFFLINE = True
        self.playerIsWhite = self.board.turn
        self.stopSendingMove = True
        self.clearPreMoveAndFocusOnLastFen()
        BoardEvents.CURRENT_BOARD = self.board

    def saveFenInHistory(self):
        fen = self.getBoardFenNode(self.board)
        data = {'fen_node': fen, 'fen': self.board.fen()}
        self.historyFen.append(data)
        bpy.data.node_groups["Chess_Board"].nodes["boardPositions"].string = self.concatainFen()

        if self.historyIndex == (len(self.historyFen)-2): self.displayHistoryPosition(1000)

    def onLeftArrow(self): self.displayHistoryPosition(-1)
    def onRightArrow(self): self.displayHistoryPosition(+1)
    def onSpace(self):
        self.displayHistoryPosition(1000)

    def displayHistoryPosition(self, direction):
        history_size = len(self.historyFen) - 1
        self.historyIndex = self.historyIndex + direction
        self.historyIndex = self.historyIndex if self.historyIndex <= history_size else history_size
        self.historyIndex = 0 if self.historyIndex < 0 else self.historyIndex

        grp = bpy.data.node_groups["Chess_Board"]
        grp.nodes["historyIndex"].integer = self.historyIndex
        grp.nodes["fenNotation"].string = self.historyFen[self.historyIndex]['fen']

    def setHistoryToPosition(self, index):
        history_size = len(self.historyFen) - 1

        if self.historyIndex <= 19: self.historyIndex = index
        else:
            v = 20 if self.historyIndex % 2 == 0 else 19
            self.historyIndex = self.historyIndex - v + index

        self.historyIndex = self.historyIndex if self.historyIndex <= history_size else history_size
        self.historyIndex = 0 if self.historyIndex < 0 else self.historyIndex
        grp = bpy.data.node_groups["Chess_Board"]
        grp.nodes["historyIndex"].integer = self.historyIndex
        grp.nodes["fenNotation"].string = self.historyFen[self.historyIndex]['fen']

    def concatainFen(self):
        position = ""
        for data in self.historyFen:
            position += data['fen_node']
        return position

    def onReleaseButton(self, btn):
        if btn == "Q_btn": BoardEvents.instance.updatePromotion(5)
        elif btn == "N_btn": BoardEvents.instance.updatePromotion(2)
        elif btn == "B_btn": BoardEvents.instance.updatePromotion(3)
        elif btn == "R_btn": BoardEvents.instance.updatePromotion(4)
        elif btn == "C_key_btn" and BoardEvents.OFFLINE: self.clearBoard(True, True)
        elif btn.startswith('Move_') and btn.endswith('_btn'): self.getHistoryIndex(btn)
    
    def getHistoryIndex(self, btn):
        modified_string = btn.replace("Move_", "").replace("_btn", "")
        try:
            integer_value = int(modified_string)
            self.setHistoryToPosition(integer_value)
        except ValueError:
            print("The remaining string is not a valid integer.")

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
    
    def setMoveList(self):
        data = ''
        for move in self.board.move_stack:
            data += move.uci()
            if len(move.uci()) == 4: data += ' '
        #bpy.data.node_groups["Move_Data"].nodes["data"].inputs[1].default_value = data
        LichessNodes.instance.setNodesValue("Move_data", "data", data)