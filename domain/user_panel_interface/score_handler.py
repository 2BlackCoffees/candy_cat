"""
Handle the score list: who are the top players
"""
from typing import List, Tuple
from abc import ABC, abstractmethod
from students.exercises import Exercises

class ScoreSaver(ABC):
    """
    Abstract class enabling communication with higher level classes
    """
    @abstractmethod
    def save_scores(self, score_list: List[Tuple[str, int]]) -> None:
        """
        Save the scores
        """
    @abstractmethod
    def load_scores(self) -> List[Tuple[str, int]]:
        """
        Load the scores
        """
class ScoreHandler:
    """
    Concrete class displaying score and other stuff in the banner
    """
    max_scores: int = 10
    def __init__(self, score_saver: ScoreSaver):
        self.score_saver: ScoreSaver = score_saver
        self.score_list: List[Tuple[str, int]] = self.score_saver.load_scores()

    def is_wall_of_fames(self, score: int) -> bool:
        """
        Is the user electable to the wall of fame (10 best players?)
        """
        if len(self.score_list) >= self.max_scores:
            _, lowest_score = self.score_list[-1]
            if score < lowest_score:
                return False
        return True

    def add_score(self, user_name: str, score: int) -> None:
        """
        Add score to the wall of fames
        """
        if not self.is_wall_of_fames(score):
            return

        Exercises.get_sorted_new_score_list(user_name, score, self.score_list)
        self.score_saver.save_scores(self.score_list)

    def get_score_list_formated(self) -> List[str]:
        """
        Return the scores in a fromatted way
        """
        return [ user_name + ':' + str(score) for user_name, score in self.score_list]
