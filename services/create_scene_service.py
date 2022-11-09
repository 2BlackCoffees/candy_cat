
"""
Create scene and handle the state machine of the game
"""
from typing import List
from domain.static_sprite import StaticSprite
from domain.sprites import Ball
from domain.sprites import Player
from domain.game_task_handler import WinLostManagement
from domain.game_task_handler import GameTaskChanger
from domain.event_dispatcher import EventDispatcher
from domain.common import Common
from domain.score_banner import Score
from domain.collision_handler_sprites import CollisionHandlerSprites
from domain.collision_handler import CollisionHandler
from domain.information_screen import AllScores
from domain.information_screen import InformationEndGame
from domain.information_screen import GetName
from domain.score_handler import ScoreHandler
from services.bricks_creator_service import BricksCreatorService
from services.game_state import GameState
from infrastructure.read_game_from_file import ReadGameFromFile
from repository.score_save import FileScoreSaver
from infrastructure.gui_library import SoundPlayer
from infrastructure.gui_library import Canvas
from services.game_state import GameState
from students.exercises import Exercises
class CreateSceneService(WinLostManagement, GameTaskChanger):
    """
    Create the visual part of the game
    """
    def __init__(self,
                 game_list: List[str],
                 screen: Canvas):
        self.game_index:int = 0
        self.game_list: List[str] = game_list
        self.screen: Canvas = screen
        self.message: List[str] =[]
        self.score_height: int = 80
        self.from_height: int = 50
        self.get_name: GetName = GetName(self.screen)
        self.game_state: GameState = GameState.WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY
        file_score_saver: FileScoreSaver = FileScoreSaver('scores.txt')
        self.score_handler: ScoreHandler = ScoreHandler(file_score_saver)
        self.remaining_balls: int = 3
        self.player: Player = None
        self.ball: Ball = None
        self.score: Score = None
        self.bricks: List[StaticSprite] = None
        self.event_dispatcher: EventDispatcher = None
        self.collision_handler: CollisionHandler = None
        self.current_score: int = 0
        self.sound_player: SoundPlayer = SoundPlayer(
            [Common.YOU_LOST,
             Common.NEXT_LEVEL,
             Common.GO_GAME_BOARD])

        self.init_game()
        self.create_game()

    def is_done(self) -> bool:
        """
        Decides when the user decides to stop
        """
        return self.event_dispatcher.is_done()

    def __create_main_sprites(self, highest_ball_increment: int) -> None:
        """
        Handle ball, player and event dispatch
        """
        screen_width, screen_height = self.screen.get_screen_size()

        self.event_dispatcher = EventDispatcher()
        self.event_dispatcher.subscribe_next_task(self)

        self.player = Player(self.screen)\
            .set_image(150, 8, Common.PING_IMAGE_NAME)\
                .set_position(screen_width // 2, screen_height)\
                    .set_collision_handler(self.collision_handler)
        self.collision_handler.subscribe_moving(self.player)
        self.event_dispatcher.subscribe(self.player)

        self.ball = Ball(self.screen)\
            .set_max_increment(highest_ball_increment)\
            .set_image(10, 10, Common.BALL_IMAGE_NAME)\
                .set_position(screen_width // 2, 4 * screen_height // 5)\
                    .set_collision_handler(self.collision_handler)
        self.ball.subscribe(self)
        self.collision_handler.subscribe_moving(self.ball)

    def create_game(self) -> None:
        """
        Create game as defined by game_index
        """
        self.game_index = Exercises.restart_from_first_scene_after_last_scene(self.game_index, len(self.game_list))

        game_name = Exercises.return_game_name(self.game_index, self.game_list)

        self.score = Score(self.screen, self.score_height, self.current_score, self.remaining_balls)
        self.collision_handler = CollisionHandlerSprites(self.score, self)
        bricks_creator_service = BricksCreatorService(
            self.from_height, self.screen,
                ReadGameFromFile(game_name), self.collision_handler)
        self.bricks = bricks_creator_service.create_bricks()
        for brick in self.bricks:
            self.collision_handler.subscribe_static(brick)
        self.__create_main_sprites(\
            max(bricks_creator_service.get_smallest_brick_size() // 15,\
                1))


    def init_game(self) -> None:
        """
        Initialize a new game when the player lost
        """
        self.remaining_balls, self.current_score, self.game_index = \
          Exercises.init_game_values()

    def inform_player_lost(self) -> None:
        """
        Behaviour when the player lost
        """
        self.remaining_balls = Exercises.new_number_balls_after_a_ball_was_missed(self.remaining_balls)
        self.score.set_number_balls(self.remaining_balls)
        user_is_elected_to_wall_of_fame = False
        if self.remaining_balls > 0:
            self.message = ["You beginner, you lost :-)",
                            f'You have another {self.remaining_balls} ball(s)']
        else:
            if self.score_handler.is_wall_of_fames(self.score.get_score()):
                self.sound_player.play(Common.GO_GAME_BOARD)
                self.get_name.clear_input()
                user_is_elected_to_wall_of_fame = True
            else:
                self.sound_player.play(Common.YOU_LOST)
                self.message = ["No wall of fame for this time ... ",
                                "your score is far too low!"]
        self.game_state = Exercises.get_next_state_when_lost(self.remaining_balls, user_is_elected_to_wall_of_fame)

    def inform_player_won(self) -> None:
        """
        Behaviour when the player won
        """
        self.message = ["Well done :-)",
                        "Next one will be much harder :-)",
                        f'You have another {self.remaining_balls} ball(s)']
        self.game_state = GameState.WAITING_PLAYER_READY_BEFORE_NEXT_LEVEL
        self.sound_player.play(Common.NEXT_LEVEL)

    def next_task(self) -> None:
        """
        Handle the state machine of the game
        """
        if self.game_state == GameState.ASKING_USER_NAME:
            self.score_handler.add_score(
                self.get_name.get_user_string(), self.score.get_score())
        elif self.game_state in [ GameState.SHOWING_SCORE,
                                  GameState.WAITING_PLAYER_READY_BEFORE_GAME_RESTART ]:
            self.init_game()
            self.create_game()
        elif self.game_state == GameState.WAITING_PLAYER_READY_BEFORE_NEXT_LEVEL:
            self.current_score += self.score.get_score()
            self.remaining_balls = 3
            self.game_index += 1
            self.create_game()


        self.game_state = Exercises.get_next_state(self.game_state)

    def update_game_scene(self) -> None:
        """
        Visually update the scene of the game
        """
        if self.game_state != GameState.PLAYING:
            self.ball.move_from_bottom(
                self.player.get_best_ball_place_before_start())
        else:
            self.ball.move()

        self.event_dispatcher.process_event()
        self.player.move()

        self.screen.fill_color(Common.black)
        self.player.display_on_screen()
        self.ball.display_on_screen()
        self.score.display_on_screen()
        for brick in self.bricks:
            brick.display_on_screen()
        if self.game_state == GameState.ASKING_USER_NAME:
            self.event_dispatcher.subscribe_input(self.get_name)
            self.get_name.set_input_on_screen_requested(True)
            self.get_name.print_information()
        elif self.game_state in [
            GameState.WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY,
            GameState.WAITING_PLAYER_READY_BEFORE_GAME_RESTART,
            GameState.WAITING_PLAYER_READY_BEFORE_NEXT_LEVEL ]:
            information = InformationEndGame(self.screen, self.message)
            information.print_information()
        elif self.game_state == GameState.SHOWING_SCORE:
            information = AllScores(self.screen, self.score_handler.get_score_list_formated())
            information.print_information()
