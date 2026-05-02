import bge
import bpy
import threading
import chess
import chess.engine
import queue
from ImportManagerEvents import ImportManagerEvents
from BoardEvents import BoardEvents
from MouseEvents import MouseEvents
from LichessEvents import LichessEvents
from collections import OrderedDict
'''
calculate the curent board postion and the best move
process the info with the one of the next move
move score > bm score = magnificante
move score == bm = best move
move score > average but < bm = good
move score do not improve position = passif
move score worth position = bad move
move score < +1 it's blunder
move score < discover mate = impardonable 
 

'''
class InfiniteAnalyseThread(threading.Thread):
    def __init__(self, game_event_queue, stopEvent, fen):
        super().__init__()
        self.fen = fen
        self.board = chess.Board(fen)
        self.game_event_queue = game_event_queue
        self.stopEvent = stopEvent
        self.file_path = bge.logic.expandPath("//Assets/stockfish/stockfish.exe")

    def run(self):
        self.game_event_queue.put("Start")
        engine = chess.engine.SimpleEngine.popen_uci(self.file_path)
        count = 0
        with engine.analysis(self.board) as analysis:
            for info in analysis:
                if not info.get("score"):
                    continue
                info_result = {
                    "fen": self.fen,
                    "info": info
                }
                if self.stopEvent.is_set():
                    break
                self.game_event_queue.put(info_result)

        engine.quit()
        self.game_event_queue.put("End")

class AnalyseGameThread(threading.Thread):
    def __init__(self, game_event_queue, stopEvent, board=chess.Board()):
        super().__init__()
        self.board = board.copy(stack=True)
        self.game_event_queue = game_event_queue
        self.stopEvent = stopEvent
        self.file_path = bge.logic.expandPath("//Assets/stockfish/stockfish.exe")

    def run(self):
        self.game_event_queue.put("Start")
        engine = chess.engine.SimpleEngine.popen_uci(self.file_path)
        size = len(self.board.move_stack)
        bBoard = chess.Board()
        index = 0
        last_info = {'pv': [chess.Move.from_uci("e2e4")]}
        for move in range(size):
            if self.stopEvent.is_set() or index >= size: break
            
            '''bBoard.push(last_info['pv'][0])
            info_bm = engine.analyse(bBoard, chess.engine.Limit(depth=20))

            bBoard.pop()'''

            bBoard.push(self.board.move_stack[index])
            '''if last_info['pv'][0] == self.board.move_stack[index]: info = info_bm
            else: info = engine.analyse(bBoard, chess.engine.Limit(depth=20))'''
            
            info = engine.analyse(bBoard, chess.engine.Limit(depth=20))

            index += 1
            info_result = {
                "fen": bBoard.fen(),
                "info": info,                
                "last_info": last_info,
                "count": size - index
            }
            #"info_bm": info_bm,

            last_info = info

            self.game_event_queue.put(info_result)


        engine.quit()
        self.game_event_queue.put("End")

class StockfishManager(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])
    
    def start(self, args):
        self.scene_name = self.object.scene.name
        self.scene = self.object.scene
        self.objects = self.scene.objects
        
        self.analysis_thread = None
        self.analysis_dictionary = {}
        self.game_event_queue = queue.Queue()
        self.stopAnalyseEvent = threading.Event()

        self.stockfish_enable = True
        self.stockfish_infinite = False
        self.stockfish_searching = False
        self.stockfish_nbr_analysis = 0

        MouseEvents.instance.register_observer(self)
        ImportManagerEvents.instance.register_observer(self)
        LichessEvents.instance.register_observer(self)

    def newImport(self):
        self.updateGroupNode()
        
    def onClickButton(self, btn):
        '''if LichessEvents.STATUS == 'INGAME': return        
        elif btn == 'Stockfish_btn': self.stopStockfish()
        el'''
        if btn == 'Stockfish_Stop_btn': self.stopStockfish()
        elif btn == 'Stockfish_Game_btn': self.startAnalyseGame()
        elif btn == 'Stockfish_Position_btn': self.startAnalyse()
    
    def gameStart(self, event):
        self.stopStockfish()

    def stopStockfish(self):
        if self.analysis_thread and self.analysis_thread.is_alive():            
            if not self.stopAnalyseEvent.is_set(): self.stopAnalyseEvent.set()
            else : print("The analyse will stop at the end of move searching")
        else: print("No thread currently running")

    def startAnalyseGame(self):
        if LichessEvents.STATUS == 'INGAME': return
        if self.analysis_thread and self.analysis_thread.is_alive():
            print("Thread running")
            return
        if not BoardEvents.CURRENT_BOARD: return
        
        self.stopAnalyseEvent.clear()
        self.analysis_thread = AnalyseGameThread(self.game_event_queue, self.stopAnalyseEvent, BoardEvents.CURRENT_BOARD)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()

        self.stockfish_nbr_analysis = len(BoardEvents.CURRENT_BOARD.move_stack)
        self.updateBaseData()
                
    def startAnalyse(self):
        if LichessEvents.STATUS == 'INGAME': return
        if self.analysis_thread and self.analysis_thread.is_alive():
            print("Thread running")
            return
        
        self.stopAnalyseEvent.clear()

        fen = bpy.data.node_groups["Chess_Board"].nodes["fenNotation"].string
        if fen == "": return

        self.analysis_thread = InfiniteAnalyseThread(self.game_event_queue, self.stopAnalyseEvent, fen)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def update(self):
        try:
            info = self.game_event_queue.get_nowait()
            self.handle_board_state(info)
        except queue.Empty:
            pass
    
    def handle_board_state(self, data_info):
        if data_info == "Start":
            self.stockfish_searching = True
            self.updateBaseData()
            return
        elif data_info == "End":
            self.stockfish_searching = False
            self.stockfish_nbr_analysis = 0
            self.updateBaseData()
            return
        elif 'count' in data_info:
            self.stockfish_nbr_analysis = data_info['count']
            self.updateBaseData()
        
        fen = data_info['fen']
        info = data_info['info']
        history = self.getHistory(fen, info['pv'])
        score = info['score'].white() if BoardEvents.CURRENT_SIDE else info['score'].black()
        if fen in self.analysis_dictionary: 
            player_score = self.analysis_dictionary[fen]['player_score']
            best_move_score = self.analysis_dictionary[fen]['best_move_score']
        else: 
            player_score, best_move_score = self.evaluate_move_type(data_info)
        analysis_data = {
            "fen": fen,
            "depth": info['seldepth'],
            "time": int(info['time']),
            "is_mate": score.is_mate(),
            "mate_in": score.mate(),
            "centipawn": score.score(),
            "expectation": score.wdl().expectation(),
            "player_score": int(player_score),
            "best_move_score": int(best_move_score),
            "pv": info['pv'],
            "history": history,
            "history_size": len(history) - 1,
            "history_index": 0
        }
        self.analysis_dictionary[fen] = analysis_data
        self.displayResult(fen)
    
    def evaluate_move_type(self, data):
        if not 'info_bm' in data: return 0,0
        
        player_move_info = chess.engine.InfoDict(data['info'])
        best_move_info = chess.engine.InfoDict(data['info_bm'])
        current_info = chess.engine.InfoDict(data['last_info'])

        if not 'score' in current_info: board_score = 0
        else: board_score = current_info['score'].relative.score()
        if player_move_info['score'].is_mate():
            return "Deadly"
        player_score = -player_move_info['score'].relative.score() - board_score
        best_move_score = -best_move_info['score'].relative.score() - board_score
        # Determine move types based on evaluation difference
        #Just return dif lol
        v='9'
        code = bpy.data.node_groups["Move_data"].nodes["data"].inputs[2].default_value
        #return player_score, best_move_score
        if player_score > best_move_score + 50: v = "0"
        elif player_score > best_move_score + 20: v = "1"
        elif player_score >= best_move_score: v = "2"
        elif player_score > 10: v = "3"
        elif player_score > 0: v = "4"
        elif player_score > -10: v = "5"
        elif player_score > -100: v = "6"
        elif player_score > -1000: v = "7"
        else: v = "8"

        bpy.data.node_groups["Move_data"].nodes["data"].inputs[2].default_value = code + v

        return player_score, best_move_score
        
    def getHistory(self, fen, moves):
        board = chess.Board(fen)

        history = []
        history.append(self.getBoardFenNode(board))

        for move in moves:
            board.push(move)
            history.append(self.getBoardFenNode(board))

        return history
    
    def getBoardFenNode(self, board):
        board_fen = ''

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            board_fen += ' ' if piece is None else piece.symbol()
        
        return board_fen
    
    def displayResult(self, fen, reset=False, pv_direction=0):
        if not fen: fen = bpy.data.node_groups["Chess_Board"].nodes["fenNotation"].string
        elif bpy.data.node_groups["Chess_Board"].nodes["fenNotation"].string != fen: return
        
        if not fen in self.analysis_dictionary:
            self.updateGroupNode()
            return

        if reset: self.analysis_dictionary[fen]['history_index'] = 0
        
        result = self.analysis_dictionary[fen]

        history = result['history']
        history_size = result['history_size']

        history_index = result['history_index'] + pv_direction
        history_index = history_index if history_index <= history_size + 1 else history_size
        history_index = 0 if history_index < 0 else history_index
        self.analysis_dictionary[fen]['history_index'] = history_index

        pv_index = history_index if len(result['pv']) > history_index else - 1
        data = {
            'searching': self.stockfish_searching,
            'nbrAnalysis': int(self.stockfish_nbr_analysis),
            'fen': result['fen'],
            'currentFen': history[history_index],
            'depth': result['depth'],
            'historyIndex': history_index,
            'time': result['time'],
            'mateIn': result['mate_in'],
            'isMate': result['is_mate'],
            'expectation': float(result['expectation']),
            'playerScore': result['player_score'],
            'bestMoveScore': result['best_move_score'],
            'fromSquare': result['pv'][pv_index].from_square,
            'toSquare': result['pv'][pv_index].to_square,
            'centipawn': 0 if not result['centipawn'] else result['centipawn'],
            'pvnbr': history_size
        }
        self.setNodesData('Stockfish', data)

    def updateBaseData(self):
        data = {
            'searching': self.stockfish_searching,
            'nbrAnalysis': int(self.stockfish_nbr_analysis) 
        }
        self.setNodesValue('Stockfish', 'searching', self.stockfish_searching)
        self.setNodesValue('Stockfish', 'nbrAnalysis', int(self.stockfish_nbr_analysis))

    def setNodesValue(self, grp_name, val_name, value):
        inputs = bpy.data.node_groups[grp_name].nodes['data'].inputs
        for input in inputs:
            if input.name == val_name:
                try: input.default_value = value
                except (KeyError, AttributeError) as e: print(f"Error: {input.name} - {e}")
                break
    def updateGroupNode(self):        
        data = {
            'searching': self.stockfish_searching,
            'nbrAnalysis': int(self.stockfish_nbr_analysis),
            'fen': "",
            'currentFen': "",
            'depth': 0,
            'historyIndex': 0,
            'time': 0,
            'isMate': False,
            'mateIn': 0,
            'expectation': 0.0,
            'fromSquare': -1,
            'toSquare': -1,
            'centipawn': 0,
            'pvnbr': 0
        }
        self.setNodesData('Stockfish', data)
        
    def setNodesData(self, grp_name, data):
        inputs = bpy.data.node_groups[grp_name].nodes['data'].inputs
        for input in inputs:
            name = input.name
            if not name in data: continue
            try:
                value = data[name]
                if value == None: 
                    continue      
                input.default_value = value
            except (KeyError, AttributeError, TypeError) as e: 
                print(f"Error: {name} - {e}")

    def onUpArrow(self):
        self.displayResult(None, False, 1)

    def onDownArrow(self):
        self.displayResult(None, False, -1)
    
    def onLeftArrow(self):        
        self.displayResult(None, True)

    def onRightArrow(self):        
        self.displayResult(None, True)

    def onSpace(self):
        self.analysis_dictionary = {}
        self.updateGroupNode()

