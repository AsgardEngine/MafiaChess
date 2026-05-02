import bge
import bpy
import chess
from LichessNodes import LichessNodes as LN
from ImportManagerEvents import ImportManagerEvents as IME
from BoardEvents import BoardEvents
from MouseEvents import MouseEvents
from collections import OrderedDict

class ChessNodes(bge.types.KX_PythonComponent):
    args = OrderedDict([        
    ])
    
    instance = None
    def start(self, args):
        ChessNodes.instance = self
        self.cursor_node = None
        self.seconds_node = None
        self.mouse_Hold = None
        self.cursor_Position = None
        self.activate = False
        self.empty_moves = ""
        self.mouse_hold_name = ""
        self.mouse_over_name = ""
        self.lastSeconde = 0
        self.last_x = 0.0
        self.last_y = 0.0

        for i in range(64):
            self.empty_moves = self.empty_moves + " "
        
        BoardEvents.instance.register_observer(self)
        IME.instance.register_observer(self)
    
    def newImport(self):
        self.cursor_node = bpy.data.node_groups["Chess_Mouse"].nodes["cursorPosition"]
        self.seconds_node = bpy.data.node_groups["Chess_Time"].nodes["Seconds"]
        self.mouse_Hold = bpy.data.node_groups["Chess_Mouse"].nodes["hold"]
        self.mouse_Over = bpy.data.node_groups["Chess_Mouse"].nodes["over"]
        self.cursor_Position = bpy.data.node_groups["Chess_Mouse"].nodes["cursorPosition"]
        self.activate = True
    
    def chessBoard(self, board, move=None, wCaptures='', bCaptures=''):
        time = int(bge.logic.getRealTime())
        stack = len(board.move_stack)
        if BoardEvents.OFFLINE: time = 0
        LN.instance.setNodesValue('Stockfish', 'nbrAnalysis', stack)

        grp = bpy.data.node_groups["Chess_Board"]
        grp.nodes["from_square"].integer = move.from_square if move else -1
        grp.nodes["to_square"].integer = move.to_square if move else -1
        grp.nodes["kcheck"].boolean = board.is_check()
        grp.nodes["turn"].boolean = board.turn
        grp.nodes["fullmove_number"].integer = stack #board.fullmove_number
        grp.nodes["LastTurnStartAt"].integer = grp.nodes["TurnStartAt"].integer if stack > 2 else time
        grp.nodes["TurnStartAt"].integer = time

        w_score, b_score = 0, 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece: continue
            if piece.color: w_score += self.getPieceValue(piece.piece_type)
            else : b_score += self.getPieceValue(piece.piece_type)

        grp.nodes["wscore"].integer = w_score
        grp.nodes["bscore"].integer = b_score
        grp.nodes["wcaptures"].string = ''.join(sorted(wCaptures))
        grp.nodes["bcaptures"].string = ''.join(sorted(bCaptures))
    
    def getPieceValue(self, type):
        if type == 1: return 1
        if type == 2 or type == 3: return 3
        if type == 4: return 5
        if type == 5: return 9
        return 0
    
    def legalMoves(self, board, moves):        
        all_moves = self.empty_moves
        capture_moves = self.empty_moves
        enPassant_moves = self.empty_moves
        castling_moves = self.empty_moves
        promotion_moves = self.empty_moves
        for move in moves:
            square = move.to_square
            all_moves = all_moves[:square] + 'm' + all_moves[square+1:]
            if board.is_capture(move):
                capture_moves = capture_moves[:square] + 'm' + capture_moves[square+1:]
            if board.is_en_passant(move):
                enPassant_moves = enPassant_moves[:square] + 'm' + enPassant_moves[square+1:]
            if board.is_castling(move):
                castling_moves = castling_moves[:square] + 'm' + castling_moves[square+1:]
            if move.promotion:
                promotion_moves = promotion_moves[:square] + 'm' + promotion_moves[square+1:]

        bpy.data.node_groups["Chess_Board"].nodes["moves"].string = all_moves
        bpy.data.node_groups["Chess_Board"].nodes["captures"].string = capture_moves
        bpy.data.node_groups["Chess_Board"].nodes["castlings"].string = castling_moves
        bpy.data.node_groups["Chess_Board"].nodes["enPassants"].string = enPassant_moves
        bpy.data.node_groups["Chess_Board"].nodes["promotions"].string = promotion_moves        

    def removeLegalMoves(self):
        bpy.data.node_groups["Chess_Board"].nodes["moves"].string = self.empty_moves
        bpy.data.node_groups["Chess_Board"].nodes["captures"].string = self.empty_moves
        bpy.data.node_groups["Chess_Board"].nodes["castlings"].string = self.empty_moves
        bpy.data.node_groups["Chess_Board"].nodes["enPassants"].string = self.empty_moves
        bpy.data.node_groups["Chess_Board"].nodes["promotions"].string = self.empty_moves

    def updatePromotion(self, grade):        
        bpy.data.node_groups["Chess_Board"].nodes["rank"].integer = grade

    def update(self):
        if not self.activate:
            return
        if MouseEvents.Over != self.mouse_over_name:
            self.mouse_over_name = MouseEvents.Over
            self.mouse_Over.string = MouseEvents.Over
        if MouseEvents.Hold != self.mouse_hold_name:
            self.mouse_hold_name = MouseEvents.Hold
            self.mouse_Hold.string = MouseEvents.Hold
        if MouseEvents.Click:
            if self.last_x != MouseEvents.X:
                self.last_x = MouseEvents.X
                self.cursor_Position.vector[0] = MouseEvents.X
            if self.last_y != MouseEvents.Z:
                self.last_y = MouseEvents.Z
                self.cursor_Position.vector[2] = MouseEvents.Z

        currentTime = bge.logic.getRealTime()
        if self.lastSeconde != int(currentTime):
            self.lastSeconde = int(currentTime)
            self.seconds_node.outputs[0].default_value = float(currentTime)
