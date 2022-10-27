"""
All commons are here
"""
from dataclasses import dataclass


@dataclass
class Common:
    """
    Define constants
    """
    GAME_NAME='wall_breaker/'
    BLACK = (0, 0, 0)
    BALL_IMAGE_NAME = GAME_NAME + 'assets/images/ColorfulBall.png'
    PING_IMAGE_NAME = GAME_NAME + 'assets/images/BarPingPong.png'
    BRICK_IMAGE_NAME = GAME_NAME + 'assets/images/PsycheBrick.png'
    UNBREAKABLE_BRICK_IMAGE_NAME = GAME_NAME + 'assets/images/IceBrick.png'
    POISONED_BRICK_IMAGE_NAME = GAME_NAME + 'assets/images/PoisonedBrick.png'

    MISSED_BALL = GAME_NAME + 'assets/sounds/missed_ball.wav'
    WON = GAME_NAME + 'assets/sounds/won.wav'
    LOST = GAME_NAME + 'assets/sounds/lost.wav'
    BUMP_POISON = GAME_NAME + 'assets/sounds/bump_poison.wav'
    BUMP_BRICK = GAME_NAME + 'assets/sounds/bump_brick.wav'
    BUMP_UNBREAKABLE_BRICK = GAME_NAME + 'assets/sounds/bump_unbreakable_brick.wav'
    BUMP_PLAYER = GAME_NAME + 'assets/sounds/bump_player.wav'
    GLASS_BREAK = GAME_NAME + 'assets/sounds/glass_break.wav'
    FLY_FLIES = GAME_NAME + 'assets/sounds/fly_flies.wav'
