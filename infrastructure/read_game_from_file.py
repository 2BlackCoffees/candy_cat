from services.bricks_creator_service import  ReadGame

class ReadGameFromFile(ReadGame):
    DIRECTORY = './'
    SUFFIX = '.txt'
    def read_game(self):
        filename = self.DIRECTORY + self.game_name + self.SUFFIX
        with open(filename) as f:
          return f.readlines()