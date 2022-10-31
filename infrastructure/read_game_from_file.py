"""
Infrastructure access to read a game
"""
from typing import List
from services.bricks_creator_service import  ReadGame

class ReadGameFromFile(ReadGame): # pylint: disable=too-few-public-methods
    """
    Read from file system
    """
    DIRECTORY: str = './'
    SUFFIX: str = '.txt'
    def read_game(self) -> List[str]:
        """
        Read the game
        """
        filename: str = self.DIRECTORY + self.game_name + self.SUFFIX
        with open(filename, encoding="utf-8") as file:
            return file.readlines()
