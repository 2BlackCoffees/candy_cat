"""
Repository to access scores (save / load)
"""
from typing import List, Tuple
from domain.user_panel_interface.score_handler import ScoreSaver
import os.path

class FileScoreSaver(ScoreSaver):
    """
    Handle scores
    """
    def __init__(self, file_name: str = 'wall_scores.txt'):
        self.file_name: str = file_name

    def save_scores(self, score_list: List[Tuple[str, int]]) -> None:
        """
        Save the scores on file system
        """
        with open(self.file_name, 'w', encoding="utf-8") as file:
            for user_name,score in score_list:
                file.write(user_name + ',' + str(score) + '\n')

    def load_scores(self) -> List[Tuple[str, int]]:
        """
        Load scores from the file system
        """
        scores: List[Tuple[str, int]] = []
        if os.path.isfile(self.file_name):
            with open(self.file_name, 'r', encoding="utf-8") as file:
                for user_name_score in file.readlines():
                    user_name, score_str = user_name_score.split(',')
                    scores.append((user_name, int(score_str)))
        return scores
