"""
Handle static sprites
"""
from abc import ABC, abstractmethod
from typing import Tuple


class BaseSprite(ABC):
    @abstractmethod
    def get_position_for_collision_analysis(self) -> Tuple[int, int]:
        """
        Position when colliding takes into account movement and direction
        This needs to be extended in other classes if required
        """
