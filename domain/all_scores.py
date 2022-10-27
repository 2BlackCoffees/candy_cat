from abc import ABC, abstractmethod
from typing import List, Tuple
from pprint import pprint

class ScoreSaver(ABC):
    @abstractmethod
    def save_scores(self, score_list: List[Tuple[str, int]]):
        """
        Save the scores
        """
    @abstractmethod
    def load_scores(self) -> List[Tuple[str, int]]:
        """
        Load the scores
        """

class ScoreHandler: 
    max_scores: int = 10
    def __init__(self, score_saver: ScoreSaver):
        self.score_saver = score_saver
        self.score_list: List[Tuple[str, int]] = self.score_saver.load_scores()

    def is_wall_of_fames(self, score: int) -> bool:
        if len(self.score_list) >= self.max_scores:
            _, lowest_score = self.score_list[-1]
            if score < lowest_score:
                return False
        return True

    def add_score(self, user_name: str, score: int) -> None:
        print("Entering add_score")
        pprint(self.score_list)
        if not self.is_wall_of_fames(score):
            return
        if len(self.score_list) == 0:
            self.score_list.append((user_name, score))
        else:
            # pprint(self.score_list[-1])
            # _, highest_score = self.score_list[-1]
            # print(highest_score)
            # if score > highest_score:
            #     self.score_list.insert(0, (user_name, score))
            # else:
                add_index = len(self.score_list)
                for index in range(0, len(self.score_list)):
                    _, cur_score = self.score_list[index]
                    if score > cur_score:
                        add_index = index
                        break
                print("add_index", add_index)
                pprint(self.score_list)
                if add_index < len(self.score_list):
                    new_score_list: List[Tuple[str, int]] = []
                    if add_index > 0:
                        new_score_list = self.score_list[0:add_index]
                    pprint(new_score_list)
                    new_score_list.append((user_name, score)) 
                    pprint(new_score_list)
                    new_score_list.extend(self.score_list[add_index:])
                    pprint(new_score_list)
                    self.score_list = new_score_list
                    pprint(self.score_list)
                else:
                    self.score_list.append((user_name, score)) 

        if len(self.score_list) > self.max_scores:
            self.score_list = self.score_list[0:10]
        print("Leaving add_score")

        pprint(self.score_list)
        self.score_saver.save_scores(self.score_list)

    def get_score_list_formated(self) -> List[str]:
        """
        Return the scores
        """
        return [ user_name + ':' + str(score) for user_name, score in self.score_list]
