import pygame
from pprint import pprint
from typing import Tuple, List
from abc import ABC, abstractmethod

class InputOnScreen(ABC):
    @abstractmethod
    def key_pressed(self, key:str) -> None:
        """
        Key pressed
        """

    @abstractmethod
    def is_input_on_screen_requested(self) -> bool:
        """
        Returns True if we are waiting for some inputs and False if not
        """

    @abstractmethod
    def set_input_on_screen_requested(self, input_requested: bool) -> None:
        """
        Informs that input on screen is done (Return was pressed)
        """

class InformationScreen():
    red: Tuple[int, int, int] = (255, 0, 0)
    black: Tuple[int, int, int] = (0, 0, 0)
    green: Tuple[int, int, int] = (0, 255, 0)
    blue: Tuple[int, int, int] = (0, 0, 255)

    def __init__(self, screen: pygame.Surface, 
                 list_information_color: List[Tuple[str, Tuple[int, int, int]]] = []):
        super().__init__()
        pygame.font.init()
        self.font:  pygame.Font = pygame.font.SysFont('Comic Sans MS', 30)
        self.list_information_color = list_information_color
        self.screen = screen
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()

    def print_information(self):
        list_text_surfaces: List[pygame.Surface] = []
        max_width = -1
        all_heights = 0
        inter_line_space = 10
        for information, color in self.list_information_color:
            text_surface: pygame.Surface = self.font.render(information, False, color)
            list_text_surfaces.append(text_surface)
            if text_surface.get_width() > max_width:
                max_width =  text_surface.get_width() 
            all_heights += text_surface.get_height() + inter_line_space

        left_pos: int = (self.screen_width - max_width) // 2
        top_pos: int = (self.screen_height - all_heights) // 2

        rect_diff_size: int = 40
        rectangle: pygame.Surface = pygame.Surface(
                           (max_width + rect_diff_size,
                            all_heights + rect_diff_size), 
                            pygame.SRCALPHA)   
        rectangle.fill((255,255,255,128))
        self.screen.blit(rectangle, 
                         (left_pos - rect_diff_size // 2,
                         top_pos - rect_diff_size // 2))
        y_pos = top_pos
        for text_surface in list_text_surfaces:
            self.screen.blit(text_surface, 
                                 ((self.screen_width - text_surface.get_width() ) // 2, 
                                 y_pos))
            y_pos +=  text_surface.get_height() + inter_line_space

class InformationEndGame(InformationScreen):
    def __init__(self, screen: pygame.Surface, 
                 list_information: List[str] = []):
        list_information_color: List[Tuple[str, Tuple[int, int, int]]] = [
            (information, InformationScreen.blue) 
              for information in list_information ]
        
        list_information_color.append(("Press space or left click to start!", 
                                       InformationScreen.green))
        super().__init__(screen, list_information_color)

class GetName(InformationScreen, InputOnScreen):
    def __init__(self, screen: pygame.Surface):
        list_information_color: List[Tuple[str, Tuple[int, int, int]]] = [
            ("Enter your name:", InformationScreen.blue),
            ("(Press enter when done):", InformationScreen.blue),
            ("", InformationScreen.green)
        ]
        self.input_requested = True
        super().__init__(screen, list_information_color)

    def key_pressed(self, key:str) -> None:
        information, color = self.list_information_color[-1]
        if key == 'backspace':
            if len(information) > 0:
                information = information[:-1]
        elif len(key) == 1:
            information += key
        self.list_information_color[-1] = (information, color)
        self.print_information()

    def is_input_on_screen_requested(self) -> bool:
        return self.input_requested

    def set_input_on_screen_requested(self, input_requested: bool) -> None:
        self.input_requested = input_requested
    
    def get_user_string(self) -> str:
        user_name, _ = self.list_information_color[-1]
        return user_name

    def clear_input(self):
        _, color = self.list_information_color[-1]
        self.list_information_color[-1] = ("", color)

class AllScores(InformationScreen):
    def __init__(self, screen: pygame.Surface, 
                 list_information: List[str] = []):
        list_information_color: List[Tuple[str, Tuple[int, int, int]]] = []
        for index in range(min(10, len(list_information))):
            color = InformationScreen.red
            if index > len(list_information) // 6: color = InformationScreen.blue
            if index > len(list_information) // 3: color = InformationScreen.green
            list_information_color.append((list_information[index], color))
        
        list_information_color.append(("Press space or left click to continue!", 
                                       InformationScreen.green))
        super().__init__(screen, list_information_color)
