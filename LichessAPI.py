import bge
# pyright: reportMissingModuleSource=false
import requests
import json
import time
from collections import OrderedDict
from DataManager import DataManager as DM
import threading
import queue
from LichessEvents import LichessEvents

class StreamThread(threading.Thread):
    def __init__(self, game_event_queue, stop_event, url, type_name):
        super().__init__()
        self.res_map = {
            'type': type_name,
            'status': 0,
            'result': 'None'
        }
        self.game_event_queue = game_event_queue
        self.stop_event = stop_event

        #self.stream_url = "https://lichess.org/api/stream/event" 'streamEvent'
        self.stream_url = url
        self.api_token = DM.getValue('player_token')
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "text/event-stream"
        }

    def run(self):
        try:
            with requests.get(self.stream_url, headers=self.headers, stream=True) as response:
                self.res_map['status'] = response.status_code

                if response.status_code == 200:
                    self.game_event_queue.put(self.res_map)

                    for line in response.iter_lines(decode_unicode=True):
                        if self.stop_event.is_set():
                            break
                        if line.strip():
                            event = json.loads(line)
                            self.game_event_queue.put(event)
                        else:
                            self.res_map['result'] = 'alive'
                            self.game_event_queue.put(self.res_map)
                else:
                    self.res_map['result'] = response.text
                    self.game_event_queue.put(self.res_map)

        except Exception as e:
            self.res_map['status'] = 666
            self.res_map['result'] = str(e)
            self.game_event_queue.put(self.res_map)

class PostThread(threading.Thread):
    def __init__(self, game_event_queue, url, type_name, data=None, headers=None, isGet=False):
        super().__init__()
        self.url = url
        self.data = data
        self.isGet = isGet
        self.res_map = {
            'type': type_name,
            'status': 0,
            'result': 'None'
        }
        self.game_event_queue = game_event_queue
        self.api_token  = DM.getValue("player_token")
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
        }
        if headers:
            self.headers = headers

    def run(self):
        try:
            if self.isGet:
                response = requests.get(self.url, data=self.data, headers=self.headers)
            else:
                response = requests.post(self.url, data=self.data, headers=self.headers)

            self.res_map['status'] = response.status_code
            event = json.loads(response.text)
            self.res_map['result'] = event                

        except Exception as e:
            self.res_map['status'] = 666
            self.res_map['result'] = str(e)

        self.game_event_queue.put(self.res_map)
                                    
class CreateSeekThread(threading.Thread):
    def __init__(self, time, inc, game_event_queue, stop_event):
        super().__init__()
        self.time = time
        self.inc = inc
        self.game_event_queue = game_event_queue
        self.stop_event = stop_event
        self.url = 'https://lichess.org/api/board/seek'
        self.headers = {
            'Authorization': f'Bearer {DM.getValue("player_token")}',
        }
        self.data = {
            'variant': 'standard',  
            'rated': 'true' if LichessEvents.RANKED else 'false',
            'timeControl': self.time,
            'increment': self.inc,
        }

    def run(self):
        res_map = {
            'type': 'createSeek',
            'status': 0,
            'result': 'None'
        }
        try:
            with requests.post(self.url, headers=self.headers, data=self.data, stream=True) as response:
                res_map['status'] = response.status_code

                if response.status_code == 200:
                    self.game_event_queue.put(res_map)

                    for line in response.iter_lines():

                        if self.stop_event.is_set():
                            res_map['result'] = 'canceled'
                            self.game_event_queue.put(res_map)
                            break
                else:
                    res_map['result'] = response.text
                    self.game_event_queue.put(res_map)

        except Exception as e:
            res_map['status'] = 666
            res_map['result'] = str(e)
            self.game_event_queue.put(res_map)

class LichessAPI(bge.types.KX_PythonComponent):
    args = OrderedDict([])
    
    instance = None

    def start(self, args):
        LichessAPI.instance = self
        LichessEvents.instance.register_observer(self)
        
        self.game_event_queue = queue.Queue()

        self.stopGameEvent = threading.Event()
        self.gameEvent = None
        
        self.stopGameState = threading.Event()        
        self.gameStateEvent = None

        self.stopSeekEvent = threading.Event()
        self.seekThread = None

        self.game_id = "0000"
        self.claimed = False

        # GAME DATA
        self.player_color = False
    
    def testTokenValidity(self, token):
        headers = {
            'Content-Type': 'text/plain',
        }
        url = 'https://lichess.org/api/token/test'
        PostThread(self.game_event_queue, url, 'tokenTest', data=token, headers=headers).start()
    
    def getProfile(self):
        url = 'https://lichess.org/api/account'
        PostThread(self.game_event_queue, url, 'getProfile', isGet=True).start()

    def startListeningServer(self):
        if self.gameEvent and self.gameEvent.is_alive():
            return
        
        self.game_id = "0000"
        self.stopGameEvent.clear()
        self.stopGameState.clear()

        self.startStreamLichessEvent()

    def startStreamLichessEvent(self):
        url = "https://lichess.org/api/stream/event"
        
        self.gameEvent = StreamThread(self.game_event_queue, self.stopGameEvent, url, 'streamEvent')
        self.gameEvent.daemon = True
        self.gameEvent.start()

    def stopListeningServer(self):
        self.stopSeek()
        if self.gameStateEvent and self.gameStateEvent.is_alive():
            self.stopGameState.set()
        if self.gameEvent and self.gameEvent.is_alive():
            self.stopGameEvent.set()
    
    def update(self):
        try:
            event = self.game_event_queue.get_nowait()
            self.handle_game_state(event)
        except queue.Empty:
            pass
    
    def play(self): 
        self.stopSeek()
        if LichessEvents.gameAI:
            self.challengeTheAI()
        else:
            self.createSeek()

    def challengeTheAI(self):
        url = 'https://lichess.org/api/challenge/ai'        
        data = {
            'level': 1,
            'clock.limit': 600,
            'clock.increment': 0,
            'days': 1,
            'color': 'random',
            'variant': 'standard',
        }
        PostThread(self.game_event_queue, url, 'challengeAI', data).start()
            
    def stopSeek(self):
        if self.seekThread and self.seekThread.is_alive():            
            self.stopSeekEvent.set()            

    def createSeek(self):
        self.stopSeekEvent.clear()       
        self.seekThread = CreateSeekThread(LichessEvents.gameTime, LichessEvents.gameInc, self.game_event_queue, self.stopSeekEvent)
        self.seekThread.daemon = True
        self.seekThread.start()

    def makeMove(self, uci):
        url = f'https://lichess.org/api/board/game/{self.game_id}/move/{uci}'
        PostThread(self.game_event_queue, url, 'makeMove').start()

    def abort(self):
        url = f'https://lichess.org/api/board/game/{self.game_id}/abort'
        PostThread(self.game_event_queue, url, 'abort').start()

    def draw(self):
        url = f'https://lichess.org/api/board/game/{self.game_id}/draw/true'
        PostThread(self.game_event_queue, url, 'draw').start()

    def declineDraw(self):
        url = f'https://lichess.org/api/board/game/{self.game_id}/draw/false'
        PostThread(self.game_event_queue, url, 'declineDraw').start()

    def resign(self):
        url = f'https://lichess.org/api/board/game/{self.game_id}/resign'        
        PostThread(self.game_event_queue, url, 'resign').start()
    
    def claimVictory(self):
        url = f'https://lichess.org/api/board/game/{self.game_id}/claim-victory'
        PostThread(self.game_event_queue, url, 'claimVictory').start()

    def opponentGone(self, event):
        if event['gone'] and event['claimWinInSeconds'] <= 0 and not self.claimed:
            self.claimed = True
            self.claimVictory()

    #   START
    #   INTERFACE GameStateInterface FUNCTIONS
    #   --------------------------------------------------------------------------------
        
    def gameStart(self, gameStart):
        self.claimed = False
        self.player_color = gameStart['game']['color'] == 'white'
        self.game_id = gameStart['game']['fullId']

        url = f"https://lichess.org/api/board/game/stream/{self.game_id}"
    
        self.gameStateEvent = StreamThread(self.game_event_queue, self.stopGameState, url, 'streamGame')
        self.gameStateEvent.daemon = True
        self.gameStateEvent.start()

    def gameFinish(self, event): 
        self.stopSeek()
        self.game_id = "0000"
        self.stopGameState.set()
        self.gameStateEvent.join()
        self.stopGameState.clear()
           
    #   --------------------------------------------------------------------------------
    #   INTERFACE GameStateInterface FUNCTIONS
    #   END
    
    def handle_game_state(self, event):
        event_type = event['type']

        if event_type == 'gameStart' and self.game_id != "0000":
            #A game is already being streamed
            return
        
        if event_type == 'gameFinish' and self.game_id != event['game']['fullId']:
            #The event don't belong the current game being streamed
            return
      
        LichessEvents.instance.notify_observers(event)
