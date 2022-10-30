"""
Infrastructure access to read a game
"""
from services.bricks_creator_service import  ReadGame

class ReadGameFromFile(ReadGame): # pylint: disable=too-few-public-methods
    """
    Read from file system
    """
    DIRECTORY = './'
    SUFFIX = '.txt'
    def read_game(self):
        """
        Read the game
        """
        filename = self.DIRECTORY + self.game_name + self.SUFFIX
        with open(filename, encoding="utf-8") as file:
            return file.readlines()
