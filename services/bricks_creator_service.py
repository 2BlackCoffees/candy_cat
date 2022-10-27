import pygame
from typing import List
from typing import Tuple
from abc import ABC, abstractmethod
from domain.sprites import StaticSprite
from domain.sprites import BreakableBrick
from domain.sprites import PoisonedBrick
from domain.sprites import UnbreakableBrick
from domain.static_sprite import DestroyableStaticSpriteImages
from domain.collision_handler import CollisionHandler
from domain.common import Common

class ReadGame(ABC):
    
    def __init__(self, game_name: str):
        self.game_name: str = game_name
    @abstractmethod
    def read_game() -> List[str]:
      """
      This method needs to be overriden anc ontent needs to be defined in the infrastructure
      """

class BricksCreatorService():

    def __init__(self, from_height: int, screen: pygame.Surface, read_game: ReadGame,
                 collision_handler: CollisionHandler):
        self.screen_width, self.screen_height = screen.get_size()
        self.from_height = from_height
        self.screen = screen
        self.collision_handler = collision_handler
        self.brick_map = read_game.read_game()

    def open_game(self, filename: str):
        with open(filename) as f:
          self.brick_map = f.readlines()

    def __create_unbreakable_brick(self, brick_width: int, brick_height: int, position: dict) -> None:
        return UnbreakableBrick(self.screen)\
            .set_image(brick_width, brick_height, Common.UNBREAKABLE_BRICK_IMAGE_NAME)\
                .set_position(position['x'], position['y'])\
                    .set_collision_handler(self.collision_handler)
                    
    def __create_breakable_brick(self, brick_width: int, brick_height: int, position: dict, 
                                 number_bumper_before_vanishes: int,
                                 destroyable_sprites_images: DestroyableStaticSpriteImages) -> None:
        return BreakableBrick(self.screen, number_bumper_before_vanishes, destroyable_sprites_images)\
            .set_image(brick_width, brick_height, Common.BRICK_IMAGE_NAME)\
                .set_position(position['x'], position['y'])\
                    .set_collision_handler(self.collision_handler)\
                        .set_number_bumped(number_bumper_before_vanishes)
                    
    def __create_poisoned_brick(self, brick_width: int, brick_height: int, position: dict, 
                                number_bumper_before_vanishes: int,
                                destroyable_sprites_images: DestroyableStaticSpriteImages) -> None:
        return PoisonedBrick(self.screen, number_bumper_before_vanishes, destroyable_sprites_images)\
            .set_image(brick_width, brick_height, Common.POISONED_BRICK_IMAGE_NAME)\
                .set_position(position['x'], position['y'])\
                    .set_collision_handler(self.collision_handler)\
                        .set_number_bumped(number_bumper_before_vanishes)
                    
    def create_bricks(self) -> List[StaticSprite]:
        """
        Create the world of bricks
        """
        height: int = self.screen_height - self.from_height
        brick_width: int = self.screen_width / (len(self.brick_map[0]) - 1)
        brick_height: int = 3 * height / (4 * len(self.brick_map))
        index_x: int = 0
        index_y: int = 0
        bricks: List[StaticSprite] = []
        breakable_brick_positions: list = []
        unbreakable_brick_positions: list = []
        poisoned_brick_positions: list = []
        poisoned_number_bumper_before_vanishes: int = 0
        breakable_number_bumper_before_vanishes: int = 0

        for row in self.brick_map:
            for element in row:
                if element != ' ':
                    position = {'x':index_x * brick_width + brick_width // 2,
                                'y':index_y * brick_height + brick_height // 2 + self.from_height}
                    if element == 'U':
                        unbreakable_brick_positions.append(position)

                    elif element[0] > 'P':
                        number_bumper_before_vanishes: int = ord(element[0]) - ord('P')
                        poisoned_brick_positions.append((position, number_bumper_before_vanishes))
                        poisoned_number_bumper_before_vanishes = \
                          max(poisoned_number_bumper_before_vanishes, 
                              number_bumper_before_vanishes)
                    elif element.isdigit():
                        number_bumper_before_vanishes: int = int(element)
                        breakable_brick_positions.append((position, number_bumper_before_vanishes))
                        breakable_number_bumper_before_vanishes = \
                          max(breakable_number_bumper_before_vanishes, 
                              number_bumper_before_vanishes)                        
                index_x += 1
            index_y += 1
            index_x = 0

        bricks = [ self.__create_unbreakable_brick(
                    brick_width, brick_height, position)
                      for position in unbreakable_brick_positions ]

        poisoned_destroyable_sprites_images: DestroyableStaticSpriteImages = \
            DestroyableStaticSpriteImages(Common.POISONED_BRICK_IMAGE_NAME,
                                          poisoned_number_bumper_before_vanishes,
                                          brick_width, brick_height)
        destroyable_sprites_images: DestroyableStaticSpriteImages = \
            DestroyableStaticSpriteImages(Common.BRICK_IMAGE_NAME,
                                          breakable_number_bumper_before_vanishes,
                                          brick_width, brick_height)
        bricks.extend([self.__create_breakable_brick(
                    brick_width, brick_height, position, 
                    number_bumper_before_vanishes, 
                    destroyable_sprites_images)
                      for position, number_bumper_before_vanishes in breakable_brick_positions])


        bricks.extend([self.__create_poisoned_brick(
                    brick_width, brick_height, position, 
                    number_bumper_before_vanishes, 
                    poisoned_destroyable_sprites_images)
                      for position, number_bumper_before_vanishes in poisoned_brick_positions])

        return bricks