
"""
Create scene and handle the state machine of the game
"""
from typing import List
from enum import Enum
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
from infrastructure.read_game_from_file import ReadGameFromFile
from repository.score_save import FileScoreSaver
import pygame

class GameState(Enum):
    """
    Various states belonging to the state machine
    """
    WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY = 1
    WAITING_PLAYER_READY_BEFORE_GAME_RESTART = 2
    WAITING_PLAYER_READY_BEFORE_NEXT_LEVEL = 3
    PLAYING = 4
    ASKING_USER_NAME = 5
    SHOWING_SCORE = 6

class CreateSceneService(WinLostManagement, GameTaskChanger):
    """
    Create the visual part of the game
    """
    def __init__(self,
                 game_list: List[str],
                 screen: pygame.Surface):
        self.game_index:int = 0
        self.game_list: List[str] = game_list
        self.screen: pygame.Surface = screen
        self.message: List[str] =[]
        self.score_height: int = 80
        self.from_height: int = 50
        self.get_name: GetName = GetName(self.screen)
        self.game_state: GameState = GameState.WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY
        self.file_score_saver: FileScoreSaver = FileScoreSaver('scores.txt')
        self.score_handler: ScoreHandler = ScoreHandler(self.file_score_saver)
        self.remaining_balls: int = 3
        self.player: Player = None
        self.ball: Ball = None
        self.score: Score = None
        self.bricks: List[StaticSprite] = None
        self.event_dispatcher: EventDispatcher = None
        self.collision_handler: CollisionHandler = None
        self.current_score: int = 0
        self.lost_game: pygame.mixer.Sound =  pygame.mixer.Sound(Common.YOU_LOST)
        self.next_level: pygame.mixer.Sound =  pygame.mixer.Sound(Common.NEXT_LEVEL)
        self.go_game_board: pygame.mixer.Sound =  pygame.mixer.Sound(Common.GO_GAME_BOARD)

        self.init_game()
        self.create_game()

    def is_done(self) -> bool:
        """
        Decides when the user decides to stop
        """
        return self.event_dispatcher.is_done()

    def __create_main_sprites(self) -> None:
        """
        Handle ball, player and event dispatch
        """
        screen_width, screen_height = self.screen.get_size()

        self.event_dispatcher = EventDispatcher()
        self.event_dispatcher.subscribe_next_task(self)

        self.player = Player(self.screen)\
            .set_image(150, 8, Common.PING_IMAGE_NAME)\
                .set_position(screen_width // 2, screen_height)\
                    .set_collision_handler(self.collision_handler)
        self.collision_handler.subscribe_moving(self.player)
        self.event_dispatcher.subscribe(self.player)

        self.ball = Ball(self.screen)\
            .set_image(10, 10, Common.BALL_IMAGE_NAME)\
                .set_position(screen_width // 2, 4 * screen_height // 5)\
                    .set_collision_handler(self.collision_handler)
        self.ball.subscribe(self)
        self.collision_handler.subscribe_moving(self.ball)

    def create_game(self) -> None:
        """
        Create game as defined by game_index
        """
        if self.game_index >= len(self.game_list):
            self.game_index = 0
        game_name = self.game_list[self.game_index]
        self.score = Score(self.screen, self.score_height, self.current_score, self.remaining_balls)
        self.collision_handler = CollisionHandlerSprites(self.score, self)
        bricks_creator_service = BricksCreatorService(
            self.from_height, self.screen,
                ReadGameFromFile(game_name), self.collision_handler)
        self.bricks = bricks_creator_service.create_bricks()
        for brick in self.bricks:
            self.collision_handler.subscribe_static(brick)
        self.__create_main_sprites()

    def init_game(self) -> None:
        """
        Initialize a new game when the player lost
        """
        self.remaining_balls = 3
        self.current_score = 0
        self.game_index = 0

    def inform_player_lost(self) -> None:
        """
        Behaviour when the player lost
        """
        self.remaining_balls -= 1
        self.score.set_number_balls(self.remaining_balls)
        if self.remaining_balls > 0:
            self.message = ["You beginner, you lost :-)",
                            f'You have another {self.remaining_balls} ball(s)']
            self.game_state = GameState.WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY
        else:
            if self.score_handler.is_wall_of_fames(self.score.get_score()):
                pygame.mixer.Sound.play(self.go_game_board)
                self.get_name.clear_input()
                self.game_state = GameState.ASKING_USER_NAME
            else:
                pygame.mixer.Sound.play(self.lost_game)
                self.message = ["No wall of fame for this time ... ",
                                "your score is far too low!"]
                self.game_state = GameState.WAITING_PLAYER_READY_BEFORE_GAME_RESTART

    def inform_player_won(self) -> None:
        """
        Behaviour when the player won
        """
        self.message = ["Well done :-)",
                        "Next one will be much harder :-)",
                        f'You have another {self.remaining_balls} ball(s)']
        self.game_state = GameState.WAITING_PLAYER_READY_BEFORE_NEXT_LEVEL
        pygame.mixer.Sound.play(self.next_level)

    def next_task(self) -> None:
        """
        Handle the state machine of the game
        """
        if self.game_state == GameState.ASKING_USER_NAME:
            self.score_handler.add_score(
                self.get_name.get_user_string(), self.score.get_score())
            self.game_state = GameState.SHOWING_SCORE
        elif self.game_state in [ GameState.SHOWING_SCORE,
                                  GameState.WAITING_PLAYER_READY_BEFORE_GAME_RESTART ]:
            self.init_game()
            self.create_game()
            self.game_state = GameState.PLAYING
        elif self.game_state == GameState.WAITING_PLAYER_READY_BEFORE_LEVEL_REPLAY:
            self.game_state = GameState.PLAYING
        elif self.game_state == GameState.WAITING_PLAYER_READY_BEFORE_NEXT_LEVEL:
            self.current_score += self.score.get_score()
            self.remaining_balls = 3
            self.game_index += 1
            self.create_game()
            self.game_state = GameState.PLAYING

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

        self.screen.fill(Common.BLACK)
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
