from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Tuple
import pygame
class Constants:
    LEFT_KEY: int = pygame.K_LEFT
    RIGHT_KEY: int = pygame.K_RIGHT
    PREFERRED_FONT: str = 'Comic Sans MS'
    QUIT: int = pygame.QUIT
    ESCAPE: int = pygame.K_ESCAPE
    RETURN: int = pygame.K_RETURN
    KEY_Q: int = pygame.K_q
    SPACE: int = pygame.K_SPACE
    red: Tuple[int, int, int] = (255, 0, 0)
    black: Tuple[int, int, int] = (0, 0, 0)
    green: Tuple[int, int, int] = (0, 255, 0)
    blue: Tuple[int, int, int] = (0, 0, 255)

class BasicCanvas(ABC):

    @abstractmethod
    def blit(self, image: pygame.Surface, pox_x: int, pos_y: int) -> None:
         """
         Display image
         """

@dataclass
class Rect:
    x: int
    y: int
    top: int
    left: int
    bottom: int
    right: int

class SpriteImage:
    def __init__(self, image: pygame.Surface, screen: BasicCanvas, image_path: str):
        self.image: pygame.Surface = image
        self.screen: BasicCanvas = screen
        self.rect: Rect = self.get_rect()
        self.image_path = image_path
        self.unused: pygame.Surface = pygame.Surface((10, 10))

    def set_position(self, pos_x: int, pos_y: int) -> None:
        self.rect.x = pos_x
        self.rect.y = pos_y

    def get_width(self) -> int:
        return self.image.get_width()
        
    def get_height(self) -> int:
        return self.image.get_height()
        
    def get_rect(self) -> Rect:
        image_rect: pygame.Rect = self.image.get_rect()
        return Rect(image_rect.x, image_rect.y, 
                 image_rect.top, image_rect.left,
                 image_rect.bottom, image_rect.right)

    def move_relative(self, inc_x: int, inc_y: int) -> None:
        self.rect.x += inc_x
        self.rect.y += inc_y

    def get_pos_x(self) -> int:
        return self.rect.x

    def get_pos_y(self) -> int:
        return self.rect.y

    def display_on_screen(self) -> None:
        """
        Paint the sprite on the screen
        """
        self.screen.blit(self.image, self.rect.x, self.rect.y)

    def display_on_screen_at_position(self, pos_x: int, pos_y: int) -> None:
        """
        Paint the sprite on the screen
        """
        self.set_position(pos_x, pos_y)
        self.display_on_screen()

    def set_new_image(self, sprite_image: SpriteImage) -> None:
        self.image = sprite_image.image



class SpriteImageOpaque(SpriteImage):
    

    def __init__(self, image_key: SpriteImage, screen: BasicCanvas, number_opacities: int, image_path: str):
        super().__init__(image_key.image, screen, image_path)
        self.opaque_images: Dict[str, List[SpriteImage]] = dict()
        self.image_key: SpriteImage = image_key
        self.screen: BasicCanvas = screen
        self.rect: Rect = self.get_rect()
        self.number_opacities = number_opacities
        self.__create_opacities()

    def __create_opacities(self) -> None:
        """
        Breakable bricks change opacity when they get bumped.
        All the opacities are created upfront to be sure the effect will be smooth
        """
        if self.image_path in self.opaque_images:
            return

        self.opaque_images[self.image_path] = []#[self.image]
        for opacity in range(self.number_opacities):
            new_image = self.image_key.image.copy()
            new_image.fill((255, 255, 255,
                            100 + opacity * 155 // self.number_opacities),
                            None, pygame.BLEND_RGBA_MULT)
            self.opaque_images[self.image_path].append(\
                SpriteImage(new_image, self.screen, self.image_path))
        self.opaque_images[self.image_path].append(self)

    def select_image_index(self, index:int) -> None:
        max_images: int = len(self.opaque_images[self.image_path])
        if index >= 0 and index < max_images:
            self.image_key.set_new_image(self.opaque_images[self.image_path][index])

        else:
            print(f'ERROR: Using index {index} whose value must be between 0 and {max_images}')
    

class SoundPlayer:
    def __init__(self, path_to_sounds: List[str]):
        self.sounds: Dict[str, pygame.mixer.Sound] = dict()
        for path_to_sound in path_to_sounds:
            self.sounds[path_to_sound] =  pygame.mixer.Sound(path_to_sound)
    
    def play(self, path_to_sound = None):
        if path_to_sound in self.sounds:
            pygame.mixer.Sound.play(self.sounds[path_to_sound])
        elif len(self.sounds) == 1:
            sound = list(self.sounds.values())[0]
            pygame.mixer.Sound.play(sound)
        else:
            print(f'ERROR: sound {self.sounds} seems to be empty!')

class Events:
    def __init__(self):
        self.type: int = 0
        self.key: int = 0
        self.event_list: List[pygame.event.Event] = []
        self.current_event: pygame.event.Event = None

    def has_more_events(self) -> bool:
        new_events = pygame.event.get()
        if len(new_events) > 0:
            self.event_list.extend(new_events)
        if len(self.event_list) > 0:
            self.current_event = self.event_list[0]
            self.event_list = self.event_list[1:]
        else:
            self.current_event = None
        return self.current_event != None
    
    def wants_to_quit(self):
        return self.current_event.type == pygame.QUIT

    def any_key_pressed(self) -> bool:
        return self.current_event.type == pygame.KEYDOWN
        
    def any_key_release(self) -> bool:
        return self.current_event.type == pygame.KEYUP
        
    def mouse_moved(self) -> bool:
        return self.current_event.type == pygame.MOUSEMOTION
        
    def get_mouse_position(self) ->  Tuple[int, int]:
        return pygame.mouse.get_pos()
        
    def mouse_button_down(self) -> bool:
        return self.current_event.type == pygame.MOUSEBUTTONDOWN

    def key_down(self, key_list: List[int]) -> bool:
        return self.any_key_pressed() and \
            self.current_event.key in key_list

    def key_pressed(self) -> int:
        return self.current_event.key
    
    def key_pressed_name(self) -> str:
        return pygame.key.name(self.current_event.key)
    
class Canvas(BasicCanvas):
    @staticmethod
    def __init():
      pygame.init()
      pygame.mixer.init()
      pygame.font.init()

    def blit(self, image: pygame.Surface, pos_x: int, pos_y: int) -> None:
        self.screen.blit(image, (pos_x, pos_y))

    def __init__(self,
                 window_title: str, 
                 screen_width: int, screen_height: int,
                 start_music_path: str):
        Canvas.__init()
        self.screen: pygame.Surface = pygame.display.set_mode((screen_width, screen_height),
                                     pygame.HWSURFACE | pygame.DOUBLEBUF) # | pygame.FULLSCREEN)
        pygame.display.set_caption(window_title)
        start_sound = pygame.mixer.Sound(start_music_path)
        pygame.mixer.Sound.play(start_sound)
        self.clock: pygame.time.Clock = pygame.time.Clock()

    def fill_color(self, color: Tuple[int, int, int]) -> None:
        self.screen.fill(color)

    def get_screen_size(self) -> Tuple[int, int]:
        return pygame.display.get_surface().get_size()
    def refresh(self) -> None:
        pygame.display.flip()
        self.clock.tick(80)

    @staticmethod
    def quit():
        pygame.quit()
    
    # Do not use this method in your code!
    def get_surface(self) -> pygame.Surface:
        return self.screen
    def __load_image(self, image_path: str, width: int, height:int) -> pygame.Surface:
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (width, height))

        return image

    def load(self, image_path: str, width: int, height:int) -> SpriteImage:
        return SpriteImage(self.__load_image(image_path, width, height), self, image_path)

    def create_rectangle(self, \
        width: int, height: int, 
        color: Tuple[int, int, int], alpha: int) -> SpriteImage:
        rectangle: pygame.Surface = pygame.Surface(\
                           (width, height), pygame.SRCALPHA)
        red, green, blue = color
        rectangle.fill((red,green,blue,alpha))
        return SpriteImage(rectangle, self, None)
    


class Font:
    def __init__(self, screen: BasicCanvas, font_size: int):
        super().__init__()
        self.screen = screen
        self.font:  pygame.font.Font = \
            pygame.font.SysFont(Constants.PREFERRED_FONT, font_size)
    
    def render_font(self, message: str, color: Tuple[int, int, int]) -> SpriteImage:
        font_image: pygame.Surface =  self.font.render(message, False, color)
        return SpriteImage(font_image, self.screen, None)
