"""
This module handles the collision
"""
from abc import ABC, abstractmethod
from typing import Tuple
#from pprint import pprint
class CollisionHandler(ABC):
    """
    Abstract class used to avoid circular references from GameMovingSprite
    """
    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'
    NONE = 'none'
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'

    def __init__(self):
        """
        __init__
        """

    @abstractmethod
    def horizontal_collision_side_bumped(self, from_side_bumped: dict) -> Tuple[bool, int]:
        """
        horizontal_collision will return a bool specifying if a
        horizontal collision happened and the int represents its intensity
        """

    @abstractmethod
    def vertical_collision_side_bumped(self, from_side_bumped: dict) -> Tuple[bool, int]:
        """
        vertical_collision will return a bool specifying if a
        vertical_collision collision happened and the int represents its intensity

        """

    @abstractmethod
    def inform_sprite_about_to_move(self) -> None:
        """
        When a sprite is about to move he should inform
        the collision handler with this method
        """

    @abstractmethod
    def add_score(self, score_adde: int) -> None:
        """
        When a sprite is bumped, it can modify the score
        """
    
    @abstractmethod
    def unsubscribe(self, sprite) -> None:
        """
        Unsubscribe the sprite
        """

