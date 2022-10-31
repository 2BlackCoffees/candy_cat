"""
Abstract classes for inversion of control
"""
from abc import ABC, abstractmethod

class WinLostManagement(ABC):
    """
    Inform when game is won / lost
    """
    @abstractmethod
    def inform_player_lost(self) -> None:
        """
        Implement logic when player lost
        """

    @abstractmethod
    def inform_player_won(self) -> None:
        """
        Implement logic when player lost
        """

class GameTaskChanger(ABC): # pylint: disable=too-few-public-methods
    """
    Inform that next task of the game should be processed
    """
    @abstractmethod
    def next_task(self) -> None:
        """
        Implement logic when player lost
        """
