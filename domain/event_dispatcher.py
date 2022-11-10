"""
Event dispatcher
"""
from typing import List
from domain.sprites.sprites import UserControlledGameMovingSprite
from domain.game_task_handler import GameTaskChanger
from domain.user_panel_interface.information_screen import InputOnScreen
from domain.common import Common
from infrastructure.gui_library import Canvas
from infrastructure.gui_library import SoundPlayer
from infrastructure.gui_library import Constants
from infrastructure.gui_library import Events

class EventDispatcher():
    """
    Event dispatcher informs registered sprites when specific events occur like
    mouse move or key pressed
    """

    def __init__(self):
        self.is_done_status: bool = False
        self.controlled_moving_sprites: List[UserControlledGameMovingSprite] = []
        self.game_task_changer: GameTaskChanger = None
        self.input_on_screen: InputOnScreen = None
        self.sound_start_ball: SoundPlayer = SoundPlayer([Common.START_BALL])
        self.event_handler: Events = Events()

    def subscribe(self, controlled_moving_sprite: UserControlledGameMovingSprite) -> None:
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

    def unsubscribe(self, controlled_moving_sprite: UserControlledGameMovingSprite) -> None:
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
        while (self.event_handler.has_more_events()):

            if self.event_handler.wants_to_quit():
                self.is_done_status = True

            if self.input_on_screen is not None and \
               self.input_on_screen.is_input_on_screen_requested():
                self.handle_events_for_inputs()
            else:
                self.handle_events_for_game()

    def handle_events_for_inputs(self) -> None:
        """
        We handle here the characters typed when provideing user name
        """
        if self.event_handler.key_down([Constants.ESCAPE, Constants.RETURN]):
            self.input_on_screen.set_input_on_screen_requested(False)
            self.unsubscribe_input()
            self.game_task_changer.next_task()
        elif self.event_handler.any_key_pressed():
            self.input_on_screen.key_pressed(self.event_handler.key_pressed_name())

    def handle_events_for_game(self) -> None:
        """
        Here we handle the control of the game
        """
        if self.event_handler.key_down([Constants.ESCAPE, Constants.KEY_Q]):
            self.is_done_status = True

            for controlled_moving_sprite in self.controlled_moving_sprites:
                controlled_moving_sprite.start_direction(self.event_handler.key_pressed())

        if self.event_handler.any_key_release():
            for controlled_moving_sprite in self.controlled_moving_sprites:
                controlled_moving_sprite.stop_direction(self.event_handler.key_pressed())

        if self.event_handler.mouse_moved():
            for controlled_moving_sprite in self.controlled_moving_sprites:
                controlled_moving_sprite.mouse_position_move(self.event_handler.get_mouse_position())

        if self.event_handler.mouse_button_down() or\
            self.event_handler.key_down([Constants.SPACE]):
            self.sound_start_ball.play()
            self.game_task_changer.next_task()
