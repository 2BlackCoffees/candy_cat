"""
Handle static sprites
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict
from dataclasses import dataclass
from domain.collision_handler.collision_handler import CollisionHandler
from domain.sprites.base_classes.base_sprite import BaseSprite
from infrastructure.gui_library import Canvas
from infrastructure.gui_library import SpriteImage
from infrastructure.gui_library import SpriteImageOpaque
from infrastructure.gui_library import Rect
from infrastructure.gui_library import SoundPlayer
@dataclass
class Display:
    """
    This data class factors all display related variables
    """
    screen: Canvas = None
    screen_width: int = 0
    screen_height: int = 0

@dataclass
class Image:
    """
    This data class factors all images related variables
    """
    image: SpriteImage = None
    width: int = 0
    height: int = 0
    perimeter: List[Dict[str, int]] = None
    rect: Rect = None
    opaque_images: List[Image] = None

class StaticSprite(BaseSprite):
    """
    Static sprites cannot move, moving sprites are handled by another class
    TODO: A build in the builder patter is needed
    """
    def __init__(self, screen: Canvas):
        self.collision_handler: CollisionHandler = None
        self.image: Image = None
        super().__init__()
        screen_width, screen_height = screen.get_screen_size()
        self.display: Display = Display(screen, screen_width, screen_height)
        self.unique_id: str = str(hex(id(self)))

    def get_width(self) -> int:
        return self.image.width
    
    def get_height(self) -> int:
        return self.image.height
    
    def set_collision_handler(self, collision_handler: CollisionHandler) -> StaticSprite:
        """
        Attach a collision handler
        """
        self.collision_handler = collision_handler
        return self

    def set_position(self, pos_x: int, pos_y: int) -> StaticSprite:
        """
        Define position of the sprite
        """
        if self.image is not None and self.image.image is not None:
            self.image.image.set_position(pos_x - self.image.width // 2,\
                pos_y - self.image.height // 2)
        else:
            print("Error trying to set a position on an image "
                  "that does not exist yet! Set the image first!")
        return self

    def get_unique_id(self) -> str:
        return self.unique_id

    def load_image(self, width: int, height: int, image_path: str) -> StaticSprite:
        return self.display.screen.load(image_path, width, height)

    def set_image(self, width: int, height: int,
                  image_path: str) -> StaticSprite:
        """
        Define the position of the sprite
        """
        if self.image is not None:
            del self.image

        image_sprite: SpriteImage = self.load_image(width, height, image_path)

        perimeter: List[Dict[str, int]] = [{'x': 0, 'y': 0}, {'x': width, 'y': height}]
        self.image = Image(image_sprite, width, height, perimeter,
                           image_sprite.get_rect(), [])
        image_sprite.set_position(self.image.rect.x, self.image.rect.y)


        return self

    def display_on_screen(self) -> None:
        """
        Paint the sprite on the screen
        """
        self.image.image.display_on_screen()

    def get_perimeter(self) -> List[Dict[str, int]]:
        """
        Get the perimeter of the sprite (Currently only as rectanle)
        """
        return self.image.perimeter

    def get_perimeter_optimized(self) -> List[Dict[str, int]]:
        """
        Get the surrounding rectangle for optimization
        """
        return self.image.perimeter

    def get_position(self) -> Tuple[int, int]:
        """
        Get the position of the sprite
        """
        return (self.image.image.get_pos_x(), self.image.image.get_pos_y())

    def get_position_for_collision_analysis(self) -> Tuple[int, int]:
        """
        Position when colliding takes into account movement and direction
        This needs to be extended in other classes if required
        """
        return self.get_position()

    @abstractmethod
    def bumped(self, from_side_bumped: Dict[str, int]) -> None:
        """
        Inform that this sprite bumbed or was bumped
        """

class Brick(StaticSprite):
    """
    Default behaviour for a brick
    """
    def __init__(self, screen: Canvas, bring_point: bool, bump_sound: str):
        self.bring_point = bring_point
        super().__init__(screen)
        self.bump_sound: SoundPlayer = SoundPlayer([bump_sound])

    def play_bump(self) -> None:
        """
        Play bump sound
        """
        self.bump_sound.play()

    def bring_points(self) -> bool:
        """
        Inform whether the brick brink points when bumped
        """
        return self.bring_point


class DestroyableStaticSprite(Brick):
    """
    Handle the behaviour of destroyable bricks
    """
    def __init__(self, screen: Canvas, number_remaining_bumps: int,
                 number_opacities: int,
                 bring_points: bool, bump_sound: str, destroyed_sound: str):
        super().__init__(screen, bring_points, bump_sound)
        screen_width, screen_height = screen.get_screen_size()
        self.display: Display = Display(screen, screen_width, screen_height)
        self.number_remaining_bumps: int = number_remaining_bumps
        self.number_opacities: int = number_opacities
        self.destroyed_sound: SoundPlayer = SoundPlayer([destroyed_sound])

    def set_image(self, width: int, height: int, image_path: str) -> DestroyableStaticSprite:
        super().set_image(width, height, image_path)
        self.sprite_image_opaque: SpriteImageOpaque = SpriteImageOpaque(\
            self.image.image, self.display.screen, self.number_opacities, image_path)
        self.sprite_image_opaque.select_image_index(self.number_remaining_bumps)
        return self


    def set_collision_handler(self, collision_handler: CollisionHandler) -> DestroyableStaticSprite:
        """
        Attach a collision handler
        """
        super().set_collision_handler(collision_handler)
        return self

    def set_number_bumped(self, number_remaining_bumps: int) -> DestroyableStaticSprite:
        """
        Specify how many remaining bumps are allowed before disappearing
        """
        self.number_remaining_bumps = number_remaining_bumps
        return self

    def bumped(self, from_side_bumped: Dict[str, int]) -> None:
        """
        Handle bump
        """
        if self.number_remaining_bumps > 0:
            self.number_remaining_bumps -= 1
            if self.number_remaining_bumps == 0:
                self.collision_handler.add_score(100)
                self.collision_handler.unsubscribe(self)
                self.destroyed_sound.play()
            else:
                self.sprite_image_opaque.select_image_index(self.number_remaining_bumps)
                self.play_bump()


    def set_position(self, pos_x: int, pos_y: int) -> DestroyableStaticSprite:
        super().set_position(pos_x, pos_y)
        return self

    @abstractmethod
    def sprite_destroyed(self) -> None:
        """
        Behaviour when sprite is destroyed
        """

    def display_on_screen(self) -> None:
        """
        Display
        """
        if self.number_remaining_bumps > 0:
            super().display_on_screen()
