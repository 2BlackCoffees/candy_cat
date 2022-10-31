"""
Handle static sprites
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, List
from dataclasses import dataclass
from domain.collision_handler import CollisionHandler
import pygame

@dataclass
class Display:
    """
    This data class factors all display related variables
    """
    screen: pygame.Surface = None
    screen_width: int = 0
    screen_height: int = 0

@dataclass
class Image:
    """
    This data class factors all images related variables
    """
    image: pygame.Surface = None
    width: int = 0
    height: int = 0
    perimeter: list(dict) = None
    rect: pygame.Rect = None
    opac_images: List[pygame.Surface] = None


class StaticSprite(pygame.sprite.Sprite, ABC):
    """
    Static sprites cannot move, moving sprites are handled by another class
    TODO: A build in the builder patter is needed
    """

    def __init__(self, screen: pygame.Surface):
        self.collision_handler: CollisionHandler = None
        self.image: Image = None
        super().__init__()
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.display: Display = Display(screen, screen_width, screen_height)

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
        if self.image is not None and self.image.rect is not None:
            self.image.rect.x = pos_x - self.image.width // 2
            self.image.rect.y = pos_y - self.image.height // 2
        else:
            print("Error trying to set a position on an image "
                  "that does not exist yet! Set the image first!")
        return self

    def set_image(self, width: int, height: int,
                  image_path: str) -> StaticSprite:
        """
        Define the position of the sprite
        """
        if self.image is not None and self.image.rect is not None:
            self.image.rect.x += self.image.width // 2
            self.image.rect.y += self.image.height // 2

        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (width, height))
        perimeter = [{'x': 0, 'y': 0}, {'x': width, 'y': height}]
        self.image = Image(image, width, height, perimeter,
                           image.get_rect(), [])

        self.set_position(self.image.rect.x, self.image.rect.y)

        return self

    def display_on_screen(self) -> None:
        """
        Paint the sprite on the screen
        """
        self.display.screen.blit(self.image.image, (self.image.rect.x,self.image.rect.y))

    def get_perimeter(self) -> list({}):
        """
        Get the perimeter of the sprite (Currently only as rectanle)
        """
        return self.image.perimeter

    def get_perimeter_optimized(self) -> list({}):
        """
        Get the surrounding rectangle for optimization
        """
        return self.image.perimeter

    def get_position(self) -> Tuple[int, int]:
        """
        Get the position of the sprite
        """
        return (self.image.rect.x, self.image.rect.y)

    def get_position_for_collision_analysis(self) -> Tuple[int, int]:
        """
        Position when colliding takes into account movement and direction
        This needs to be extended in other classes if required
        """
        return self.get_position()

    @abstractmethod
    def bumped(self, from_side_bumped: dict) -> None:
        """
        Inform that this sprite bumbed or was bumped
        """

class Brick(StaticSprite):
    """
    Default behaviour for a brick
    """
    def __init__(self, screen: pygame.Surface, bring_point: bool, bump_sound: str):
        self.bring_point = bring_point
        super().__init__(screen)
        self.bump_sound: pygame.mixer.Sound = pygame.mixer.Sound(bump_sound)

    def play_bump(self) -> None:
        """
        Play bump sound
        """
        pygame.mixer.Sound.play(self.bump_sound)

    def bring_points(self) -> bool:
        """
        Inform whether the brick brink points when bumped
        """
        return self.bring_point

class DestroyableStaticSpriteImages: # pylint: disable=too-few-public-methods
    """
    Destroyable classes automatically disappear when they were several times bumped
    """
    def __init__(self, base_image_path: str, number_opacities: int, width: int, height: int):
        self.number_opacities: int = number_opacities + 2
        self.base_image: pygame.Surface = pygame.image.load(base_image_path).convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (width, height))
        self.opac_images: List[pygame.Surface] = []

        self.__create_all_opacities()

    def __create_all_opacities(self) -> None:
        """
        Breakable bricks change opacity when they get bumped.
        All the opacities are created upfront to be sure the effect will be smooth
        """
        source = self.base_image

        self.opac_images.clear()
        for opacity in range(self.number_opacities):
            new_image = source.copy()
            new_image.fill((255, 255, 255,
                            100 + opacity * 155 // self.number_opacities),
                            None, pygame.BLEND_RGBA_MULT)
            self.opac_images.append(new_image)
        self.opac_images.append(source)

    def get_all_images(self) -> List[pygame.Surface]:
        """
        Return all possible opacities
        """
        return self.opac_images

class DestroyableStaticSprite(Brick):
    """
    Handle the behaviour of destroyable bricks
    """
    def __init__(self, screen: pygame.Surface, number_remaining_bumps: int,
                 destroyable_sprites_images: DestroyableStaticSpriteImages,
                 bring_points: bool, bump_sound: str, destroyed_sound: str = None):
        super().__init__(screen, bring_points, bump_sound)
        self.number_remaining_bumps:int = 1
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.display: Display = Display(screen, screen_width, screen_height)
        self.number_remaining_bumps: int = number_remaining_bumps
        self.destroyable_sprites_images: DestroyableStaticSpriteImages = destroyable_sprites_images
        self.destroyed_sound: pygame.mixer.Sound = None
        if destroyed_sound is not None:
            self.destroyed_sound = pygame.mixer.Sound(destroyed_sound)

    def set_number_bumped(self, number_remaining_bumps: int) -> DestroyableStaticSprite:
        """
        Specify how many remaining bumps are allowed before disappearing
        """
        self.number_remaining_bumps = number_remaining_bumps
        return self

    def bumped(self, from_side_bumped: dict) -> None:
        """
        Handle bump
        """
        if self.number_remaining_bumps > 0:
            self.number_remaining_bumps -= 1
            if self.number_remaining_bumps == 0:
                self.collision_handler.add_score(100)
                self.collision_handler.unsubscribe(self)
                if self.destroyed_sound is not None:
                    pygame.mixer.Sound.play(self.destroyed_sound)
            else:
                self.image.image = self.image.opac_images[self.number_remaining_bumps]
                self.play_bump()

    def set_image(self, width: int, height: int,
                  image_path: str) -> StaticSprite:
        """
        Define the original image
        """
        super().set_image(width, height, image_path)
        self.image.opac_images = \
            self.destroyable_sprites_images.get_all_images()
        self.image.image = self.image.opac_images[self.number_remaining_bumps]
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
