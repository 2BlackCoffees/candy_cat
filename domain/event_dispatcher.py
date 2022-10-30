"""
Event dispatcher
"""
from typing import List
from domain.sprites import GameMovingSprite
from domain.game_task_handler import GameTaskChanger
from domain.information_screen import InputOnScreen
from domain.common import Common
import pygame

class EventDispatcher():
    """
    Event dispatcher informs registered sprites when specific events occur like
    mouse move or key pressed
    """

    def __init__(self):
        self.is_done_status: bool = False
        self.controlled_moving_sprites: List[GameMovingSprite] = []
        self.game_task_changer: GameTaskChanger = None
        self.input_on_screen: InputOnScreen = None
        self.sound_start_ball =  pygame.mixer.Sound(Common.START_BALL)

    def subscribe(self, controlled_moving_sprite: GameMovingSprite) -> None:
        """
        Attach a new sprite
        """
        self.controlled_moving_sprites.append(controlled_moving_sprite)

    def subscribe_input(self, input_on_screen: InputOnScreen) -> None:
        """
        Attach a new input
        """
        self.input_on_screen = input_on_screen

    def subscribe_next_task(self, start_stop_management: GameTaskChanger) -> None:
        """
        Before starting a new game, we wait for user input (click or space).
        Once the user provided the input we inform the subscribed
        class that next task can be started.
        """
        self.game_task_changer = start_stop_management

    def unsubscribe(self, controlled_moving_sprite: GameMovingSprite) -> None:
        """
        Detach a sprite
        """
        self.controlled_moving_sprites.remove(controlled_moving_sprite)
    def unsubscribe_input(self) -> None:
        """
        Detach an input
        """
        self.input_on_screen = None

    def is_done(self) -> bool:
        """
        Inform if is done is required
        """
        return self.is_done_status

    def process_event(self) -> None:
        """
        Handle the events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_done_status = True

            if self.input_on_screen is not None and \
               self.input_on_screen.is_input_on_screen_requested():
                self.handle_events_for_inputs(event)
            else:
                self.handle_events_for_game(event)

    def handle_events_for_inputs(self, event: pygame.event.Event):
        """
        We handle here the characters typed when provideing user name
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.input_on_screen.set_input_on_screen_requested(False)
                self.unsubscribe_input()
                self.game_task_changer.next_task()
            else:
                self.input_on_screen.key_pressed(pygame.key.name(event.key))

    def handle_events_for_game(self, event: pygame.event.Event):
        """
        Here we handle the control of the game
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.is_done_status = True

            for controlled_moving_sprite in self.controlled_moving_sprites:
                controlled_moving_sprite.start_direction(event.key)

        if event.type == pygame.KEYUP:
            for controlled_moving_sprite in self.controlled_moving_sprites:
                controlled_moving_sprite.stop_direction(event.key)

        if event.type == pygame.MOUSEMOTION:
            for controlled_moving_sprite in self.controlled_moving_sprites:
                controlled_moving_sprite.mouse_position_move(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONDOWN or\
            event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            pygame.mixer.Sound.play(self.sound_start_ball)
            self.game_task_changer.next_task()
