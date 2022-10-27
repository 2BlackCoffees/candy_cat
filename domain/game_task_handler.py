from abc import ABC, abstractmethod

class WinLostManagement(ABC):
    @abstractmethod
    def inform_player_lost():
        """
        Implement logic when player lost
        """

    @abstractmethod
    def inform_player_won():
        """
        Implement logic when player lost
        """

class GameTaskChanger(ABC):
    @abstractmethod
    def next_task():
        """
        Implement logic when player lost
        """