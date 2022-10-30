from enum import Enum

class GameState(Enum):
    """
    Various states belonging to the state machine
    """
    WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY = 1
    WAITING_PLAYER_READY_BEFORE_GAME_RESTART = 2
    WAITING_PLAYER_READY_BEFORE_NEXT_LEVEL = 3
    PLAYING = 4
    ASKING_USER_NAME = 5
    SHOWING_SCORE = 6