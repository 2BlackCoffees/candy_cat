from typing import List, Tuple
from services.game_state import GameState

class Exercises:

    @staticmethod
    def create_board(character: int) -> Tuple[int, int]:
        """
        Character represents the caharcer we read in a file describing the 
        board we want to display.
        If the character is ' ' then it is blank and you can return: (0, 0)
        If the character is 'U' then it is an unbreakable brick and you can return (1, 0)
        If the character is between '0' and '9' which means it is a digit then it is a breakable $ brick and you should return:
        (2, the ordinal value of characer - ordinal value of '0')
        The ordinal value is computed with the function ord().
        If the character is greater than 'P' then it is a breakable skull and you should return:
        (3, the ordinal value of characer - ordinal value of 'P' + 1)
        """
        return (0, 0) 
        
    @staticmethod
    def init_game_values() -> Tuple[int, int, int]:
        """
        When the user lost or the game starts, we need to define 
        * the number of balls for the new game
        * the initial score
        * which game we want the user starts with
        """
        number_balls: int = 1
        current_score: int = 0
        game_index: int = 0
        return (number_balls, current_score, game_index)

    @staticmethod
    def get_initial_state() -> GameState:
        """
        This is the state the game will start with, you will need that later on
        """
        return GameState.WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY

    @staticmethod
    def get_maximum_sprite_movement(smallest_brick_side_size: int):
        """
        This game will work properly only if the movement defined by the number of sprite 
        is either equal to 
        -> smallest_brick_side_size divided by 15 or 
        -> 1 if  smallest_brick_side_size divided by 15 is less than 1
        Try to play with different values like 
        -> smallest_brick_side_size * 3 to see what happens
        """
        return 0

    @staticmethod
    def get_opposite_horizontal_movement_direction(
        horizontal_movement: int
    ) -> bool:
        """
        horizontal_movement specifies the number of pixels the ball is 
        moving horizontally.
        When this function is called the program expects that the 
        opposite value of horizontal_movement is returned.
        """
        return 0

    @staticmethod
    def is_vertical_collision_or_screen_vertical_boudary_reached(
        vertical_collision: bool, 
        ball_position_vertical: int, 
        ball_height: int, 
        screen_height: int
    ) -> bool:
        """
        We need to check whether a vertical collision happened,
        you can use the boolean variable vertical_collision for this.
        Vertical screen collision means that the vertical position of the ball 
        is either less than 1 or bigger than screen_height - ball_height
        """
        return False

    @staticmethod
    def is_horizontal_collision_or_screen_horizontal_boudary_reached(
        horizontal_collision: bool, 
        ball_position_horizontal: int, 
        ball_width: int, 
        screen_width: int
    ) -> bool:
        """
        We need to check whether a horizontal collision happened,
        you can use the boolean variable horizontal_collision for this.
        Horizontal screen collision means that the horizontal position of the ball 
        is either less than 1 or bigger than screen_width - ball_width
        """
        return False

    @staticmethod
    def get_opposite_vertical_movement_direction(
        vertical_movement: int
    ) -> bool:
        """
        vertical_movement specifies the number of pixels the ball is 
        moving vertically.
        When this function is called the program expects that the 
        opposite value of vertical_movement is returned.
        """
        return 0


    @staticmethod
    def failed_message(remaining_balls):
        """ 
        Here you should return a list of 3 strings:
        First string:
         You beginner, you lost :-)
        Second string:
          You have another ??? ball(s)
        ??? must be replaced with the value of remaining_balls

        A list is created as follows: ['Hello', 'World']
        """
        return [""]

    @staticmethod
    def new_number_balls_after_a_ball_was_missed(
          current_number_balls: int) -> int:
        """
        A ball was missed by the player so 
        we need to tell the game how many remaining balls there are...
        """
        return 0

    @staticmethod
    def restart_from_first_scene_after_last_scene(
            current_scene_number:int, 
            number_of_scenes: int) -> int:
        """
        Return either the current scene number 
        if is is below number_of_scenes
        Otherwise return 0
        """
        return 0
    @staticmethod
    def return_game_name(
            index_of_list:int, 
            list_of_games: List[str]) -> str:
        """
        Return the element of the list pointed
        by the index of the list.
        Bonus: Return the first element 
        if the index is bigger than the size of the list
        """
        return list_of_games[0]
    @staticmethod
    def get_next_state(game_state: GameState) -> GameState:
        """
        We define here a state machine.
        In Software a state machine is an algorithm whose state define what the program should be doing.
        These state can change and the next state is usally strongly coupled with the previous state.

        In other words we expect the following:
        GameState.ASKING_USER_NAME -> GameState.SHOWING_SCORE
        GameState.SHOWING_SCORE -> GameState.PLAYING
        GameState.WAITING_PLAYER_READY_BEFORE_GAME_RESTART -> GameState.PLAYING
        GameState.WAITING_PLAYER_READY_BEFORE_NEXT_LEVEL -> GameState.PLAYING
        """
        return GameState.PLAYING

    @staticmethod
    def get_next_state_when_lost(remaining_balls: int, 
                                 user_is_elected_to_wall_of_fame: bool) -> GameState:
        """
        This is the second part of the state machine

        This time the user just missed a ball, so we have the follwing cases:
        * The use missed a ball but there are more balls to play (meaning remaining_balls is greater than 0)
          -> go to state GameState.WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY
        * There are 0 or less balls
          * the user is elected for the wall of fames (user_is_elected_to_wall_of_fame is True)
            -> go to state GameState.ASKING_USER_NAME to ask the user his name
          * otherwise 
            -> go to state GameState.WAITING_PLAYER_READY_BEFORE_GAME_RESTART
        """
        return GameState.ASKING_USER_NAME


    
    @staticmethod
    def get_sorted_new_score_list(user_name: str, score: int, 
                                  score_list: List[Tuple[str, int]], 
                                  max_scores: int = 10) -> None:
        """
        A list of score is a list composed of a tuple of a string (the name of the player) and an integer (its score)
        The list that we get is ordered with the old scores, a new score is now achieved.
        This new score must be placed at the correct position: position 0 is the best score, position 9 is the worst score

        Here the variable score_list (which is a list) is passed by reference (not very important to understand in detail, 
           but we do not need to return a new list as we are modifyig the variable in place)

        Here we must:
        1. Simply append a new tuple to the list if the list is empty
        2. If the list is not empty:
          a. Iterate over all elements of the list starting from the highest score
          b. If the variable score provided in the variable score is greater than the score in the list
             then the position should be used for the user ans score 
          c. Remember that the other scores must not be lost
          d. We want only 10 scores in the variable score_list
        
        """
        pass # pass means nothing to do ...
