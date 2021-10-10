from enum import Enum

class GAME_STATUS(Enum):
    IDLE = 0
    REGISTRATION = 1
    IN_GAME = 2
    ANSWERS_COLLECTION = 3

class GameMaster():
    def __init__(self):
        self.status : GAME_STATUS = GAME_STATUS.IDLE

    def start_registration(self):
        self.status = GAME_STATUS.REGISTRATION
    
    def end_registration(self):
        self.status = GAME_STATUS.IDLE

    def start_game(self):
        self.status = GAME_STATUS.IN_GAME

    def end_game(self):
        self.status = GAME_STATUS.IDLE

    def start_answers_collection(self):
        self.status = GAME_STATUS.ANSWERS_COLLECTION

    def end_answers_collection(self):
        self.status = GAME_STATUS.IN_GAME