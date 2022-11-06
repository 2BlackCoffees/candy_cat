"""
Handle all sprites
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple
from typing import Dict
from domain.common import Common
from domain.game_task_handler import WinLostManagement
from domain.static_sprite import Brick
from domain.static_sprite import StaticSprite
from domain.static_sprite import DestroyableStaticSprite
from infrastructure.gui_library import Canvas
from infrastructure.gui_library import Constants
from infrastructure.gui_library import SoundPlayer
class GameMovingSprite(StaticSprite, ABC):
    """
    Moving sprites should inherit me and provide their own functionality
    """
    def __init__(self, screen: Canvas):
        super().__init__(screen)
        self.change_x: int = 0
        self.change_y: int = 0

    def change_speed(self, horizontal_speed: int, vertical_speed: int) -> None:
        """
        Increase / decrease speed (decrease with negative values)
        """
        self.change_x += horizontal_speed
        self.change_y += vertical_speed

    def set_change_speed_x(self, horizontal_speed: int) -> None:
        """
        Set new horizontal speed
        """
        self.change_x = horizontal_speed

    def set_change_speed_y(self, vertical_speed: int) -> None:
        """
        Set new vertical speed
        """
        self.change_y = vertical_speed

    def get_position_for_collision_analysis(self) -> Tuple[int, int]:
        """
        Analyze collision taking into account next position
        """
        return (self.image.image.get_pos_x() + self.change_x,
                self.image.image.get_pos_y() + self.change_y)

    def change_speed_factor(self, factor_x: int, factor_y: int) -> None:
        """
        Speed factor should not be greater than half of the size of the sprite
        otherwise movement will not be fluid anymore
        """
        if abs(self.change_x) < self.image.width / 2:
            self.change_x *= factor_x
        if abs(self.change_y) < self.image.height / 2:
            self.change_y *= factor_y

    def move(self) -> None:
        """
        Default move
        """
        self.image.image.move_relative(self.change_x, self.change_y)

    def move_from_bottom(self, position) -> None:
        """
        Coordinates are given from bottom
        """
        pos_x, pos_y = position
        self.image.image.set_position(pos_x, pos_y - self.image.height)


class UserControlledGameMovingSprite(GameMovingSprite, ABC):
    """
    This is purely user controlled class
    """

    @abstractmethod
    def start_direction(self, direction: int) -> None:
        """
        Start moving in the specified direction
        """

    @abstractmethod
    def stop_direction(self, direction: int) -> None:
        """
        Stop moving
        """

    @abstractmethod
    def mouse_position_move(self, mouse_position: Tuple[int, int]) -> None:
        """
        Provide mous coordinates
        """

class Ball(GameMovingSprite):
    """
    This is the sprite representing the ball bumping
    """

    def __init__(self, screen: Canvas):
        super().__init__(screen)
        self.horizontal_collision: bool = False
        self.vertical_collision: bool = False
        self.win_lost_management: WinLostManagement = None
        self.change_x: int = 5
        self.change_y: int = 5
        self.sound_missed_ball: SoundPlayer = SoundPlayer([Common.MISSED_BALL])

    def subscribe(self, win_lost_management: WinLostManagement) -> None:
        """
        Inversion of control to inform when game is lost
        """
        self.win_lost_management = win_lost_management

    def bumped(self, from_side_bumped: Dict[str, int]) -> None:
        """
        Inform that ball was bumped
        """
        self.horizontal_collision, _ = \
            self.collision_handler.horizontal_collision_side_bumped(from_side_bumped)

        self.vertical_collision, _ = \
            self.collision_handler.vertical_collision_side_bumped(from_side_bumped)

    def move(self) -> None:
        """
        Move ball
        """
        from_side_bumped: Dict[str, int] = None
        horizontal_collision: bool = False
        vertical_collision: bool = False
        if self.collision_handler is not None:
            from_side_bumped = self.collision_handler.check_for_collision(self)
            if from_side_bumped is not None:
                horizontal_collision, _ = \
                    self.collision_handler.horizontal_collision_side_bumped(from_side_bumped)
                vertical_collision, _ = \
                    self.collision_handler.vertical_collision_side_bumped(from_side_bumped)

        if vertical_collision or \
           (self.image.image.get_pos_y() < 1 or \
            self.image.image.get_pos_y() + self.image.height > self.display.screen_height):
            self.change_y = -self.change_y
            if self.image.image.get_pos_y() + self.image.height > self.display.screen_height:
                self.win_lost_management.inform_player_lost()
                self.sound_missed_ball.play()

        elif horizontal_collision or \
           (self.image.image.get_pos_x() < 1 or \
            self.image.image.get_pos_x() + self.image.width > self.display.screen_width):
            self.change_x = -self.change_x

        self.change_speed_factor(1.05, 1.05)
        super().move()

class BreakableBrick(DestroyableStaticSprite):
    """
    Handles breakable bricks
    """
    def __init__(self, screen: Canvas, number_remaining_bumps: int,
                number_opacities: int):
        super().__init__(screen, number_remaining_bumps, \
                            number_opacities, True, \
                            Common.BUMP_BRICK, Common.DESTROYED_BRICK)
        self.max_bumped_value: int = 0


    def bumped(self, from_side_bumped: Dict[str, int]) -> None:
        """
        Override bumped behaviour
        """
        self.collision_handler.add_score(5)
        super().bumped(from_side_bumped)

    def sprite_destroyed(self) -> None:
        """
        Destroyed? Remove more points
        """
        self.collision_handler.add_score(100)


class UnbreakableBrick(Brick): # pylint: disable=too-few-public-methods
    """
    Handle unbreakable bricks
    """
    def __init__(self, screen: Canvas):
        super().__init__(screen, False, Common.BUMP_UNBREAKABLE_BRICK)

    def bumped(self, from_side_bumped: Dict[str, int]) -> None:
        """
        Override bumped behaviour
        """
        self.play_bump()

class PoisonedBrick(DestroyableStaticSprite):
    """
    Poison bricks remove pints by collisions and even more when they disappear
    """
    def __init__(self, screen: Canvas, number_remaining_bumps: int,
                 number_opacities: int):
        super().__init__(screen, number_remaining_bumps, number_opacities,
                         False, Common.BUMP_POISON, Common.DESTROYED_POISON)
        self.max_bumped_value: int = 0

    def bumped(self, from_side_bumped: Dict[str, int]) -> None:
        """
        Bumped? Remove points
        """
        self.collision_handler.add_score(-10)
        super().bumped(from_side_bumped)

    def sprite_destroyed(self) -> None:
        """
        Destroyed? Remove more points
        """
        self.collision_handler.add_score(-200)

class Player(UserControlledGameMovingSprite):
    """
    This is the concrete user player class
    """
    def __init__(self, screen: Canvas):
        super().__init__(screen)
        self.sound: SoundPlayer = SoundPlayer([Common.BUMP_PLAYER])
        self.next_position_x: int = 0

    def set_position(self, pos_x: int, pos_y: int) -> StaticSprite:
        """
        Set new position of user with coordinates
        """
        super().set_position(pos_x, self.display.screen_height - self.image.height)
        self.next_position_x = pos_x
        return self

    def get_best_ball_place_before_start(self) -> Tuple[int, int]:
        """
        Before we start, the ball should be placed
        right in the middle of the player
        """
        return self.image.image.get_pos_x() + self.image.width // 2, \
               self.image.image.get_pos_y()

    def start_direction(self, direction: int) -> None:
        """
        This starts movement with the keyboard
        """
        if direction == Constants.LEFT_KEY:
            self.change_speed(-5, 0)
        if direction == Constants.RIGHT_KEY:
            self.change_speed(5, 0)

    def stop_direction(self, direction) -> None:
        """
        This stops movement with the keyboard
        """
        if direction in (Constants.LEFT_KEY, Constants.RIGHT_KEY):
            self.set_change_speed_x(0)

    def get_position_for_collision_analysis(self) -> Tuple[int, int]:
        """
        Position when colliding takes into account movement and direction
        This needs to be extended in other classes if required
        """
        return (self.next_position_x, self.image.image.get_pos_y())

    def mouse_position_move(self, mouse_position) -> None:
        """
        This moves with the mouse
        """
        self.change_x = 0
        self.change_y = 0
        mouse_position_x, _ = mouse_position
        if self.image.width // 2 < \
           mouse_position_x < self.display.screen_width - self.image.width // 2:
            self.next_position_x = mouse_position_x -  self.image.width // 2
            if self.collision_handler is not None:
                self.collision_handler.inform_sprite_about_to_move()
            self.image.image.set_position(\
                self.next_position_x, self.image.image.get_pos_y())
        #if(mouse_position_y > self.height // 2 and
        # mouse_position_y < self.screen_height - self.height // 2):
        #    self.rect.y = mouse_position_y -  self.height // 2

    def bumped(self, from_side_bumped: Dict[str, int]) -> None:
        """
        Ball bumped with the player
        """
        self.sound.play()
        horizontal_collision, _ = \
            self.collision_handler.horizontal_collision_side_bumped(from_side_bumped)
        if horizontal_collision:
            self.collision_handler.add_score(10)


    def move(self) -> None:
        """
        Move
        """
        super().change_speed_factor(1.10, 1.10)
        if(self.image.image.get_pos_x() + self.change_x < 1 or \
           self.image.image.get_pos_x() + self.image.width + self.change_x > \
           self.display.screen_width):
            self.change_x = 0
        #if(self.rect.y + self.change_y < 1 or
        # self.rect.y + self.height + self.change_y > self.screen_height):
        #    self.change_y = 0

        super().move()
