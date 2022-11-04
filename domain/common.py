"""
All commons are here
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Common:
    """
    Define constants
    """
    GAME_NAME='wall_breaker/'
    BALL_IMAGE_NAME = GAME_NAME + 'assets/images/ColorfulBall.png'
    PING_IMAGE_NAME = GAME_NAME + 'assets/images/BarPingPong.png'
    BRICK_IMAGE_NAME = GAME_NAME + 'assets/images/PsycheBrick.png'
    UNBREAKABLE_BRICK_IMAGE_NAME = GAME_NAME + 'assets/images/IceBrick.png'
    POISONED_BRICK_IMAGE_NAME = GAME_NAME + 'assets/images/PoisonedBrick.png'

    START_MUSIC = GAME_NAME + 'assets/sounds/guitar_start.wav'
    START_BALL = GAME_NAME + 'assets/sounds/explosion.wav'
    DESTROYED_POISON = GAME_NAME + 'assets/sounds/scream.wav'
    MISSED_BALL = GAME_NAME + 'assets/sounds/missed_ball.wav'
    START_BALL = GAME_NAME + 'assets/sounds/explosion.wav'
    BUMP_POISON = GAME_NAME + 'assets/sounds/bump_poison.wav'
    BUMP_BRICK = GAME_NAME + 'assets/sounds/bump_brick.wav'
    BUMP_UNBREAKABLE_BRICK = GAME_NAME + 'assets/sounds/bump_unbreakable_brick.wav'
    BUMP_PLAYER = GAME_NAME + 'assets/sounds/bump_player.wav'
    DESTROYED_BRICK = GAME_NAME + 'assets/sounds/glass_break.wav'
    NEXT_LEVEL = GAME_NAME + 'assets/sounds/fly_flies.wav'
    YOU_LOST = GAME_NAME + 'assets/sounds/lost.wav'
    KEY_PRESSED = GAME_NAME + 'assets/sounds/key_pressed.wav'
    GO_GAME_BOARD = GAME_NAME + 'assets/sounds/ohyeah.wav'

    red: Tuple[int, int, int] = (255, 0, 0)
    black: Tuple[int, int, int] = (0, 0, 0)
    green: Tuple[int, int, int] = (0, 255, 0)
    blue: Tuple[int, int, int] = (0, 0, 255)
