from domain.all_scores import ScoreSaver
from typing import List, Tuple
from pprint import pprint
import os.path

class FileScoreSaver(ScoreSaver):
    def __init__(self, file_name: str = 'wall_scores.txt'):
        self.file_name = file_name

    def save_scores(self, score_list: List[Tuple[str, int]]):
        with open(self.file_name, 'w') as f:
            for user_name,score in score_list:
              f.write(user_name + ',' + str(score) + '\n')

    def load_scores(self) -> List[Tuple[str, int]]:
        scores: List[Tuple[str, int]] = []
        if os.path.isfile(self.file_name):
            with open(self.file_name, 'r') as f:
                for user_name_score in f.readlines():
                    user_name, score_str = user_name_score.split(',')
                    scores.append((user_name, int(score_str)))
            pprint(scores)
        return scores