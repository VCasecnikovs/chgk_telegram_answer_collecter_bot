from enum import Enum

class GameStatus(Enum):
    IDLE = 0
    REGISTRATION = 1
    IN_GAME = 2

class GameMaster():
    def __init__(self):
        self.status : GameStatus = GameStatus.IDLE

    def start_registration(self):
        self.status = GameStatus.REGISTRATION
    
    def end_registration(self):
        self.status = GameStatus.IDLE

    def start_game(self):
        self.status = GameStatus.IN_GAME

    def end_game(self):
        self.status = GameStatus.IDLE