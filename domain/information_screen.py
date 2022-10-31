"""
This package takes care of display of a panel with anything written on it
"""
from abc import ABC, abstractmethod
from typing import Tuple, List
from domain.common import Common
import pygame

class InputOnScreen(ABC):
    """
    Anstract class that even dispatcher uses to communicate with InformationScreen
    """
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

class InformationScreen(): # pylint: disable=too-few-public-methods
    """
    Concrete class to display information on the screen
    """

    def __init__(self, screen: pygame.Surface,
                 list_information_color: List[Tuple[str, Tuple[int, int, int]]] = None):
        super().__init__()
        pygame.font.init()
        self.font: pygame.font.Font = pygame.font.SysFont('Comic Sans MS', 30)
        self.list_information_color: List[Tuple[str, Tuple[int, int, int]]] = \
            list_information_color if list_information_color is not None else []
        self.screen: pygame.Surface = screen
        self.screen_width: int
        self.screen_height: int
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()

    def print_information(self):
        """
        Print the panel with the list of strings
        """
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

class InformationEndGame(InformationScreen): # pylint: disable=too-few-public-methods
    """
    This is a specialised InformationScreen to inform the user
    that the game ended
    """
    def __init__(self, screen: pygame.Surface,
                 list_information: List[str]):
        if list_information is None:
            list_information = []
        list_information_color: List[Tuple[str, Tuple[int, int, int]]] = [
            (information, Common.blue)
              for information in list_information ]

        list_information_color.append(("Press space or left click to start!",
                                       Common.green))
        super().__init__(screen, list_information_color)

class GetName(InformationScreen, InputOnScreen):
    """
    With this class we gather the name of the user
    """
    def __init__(self, screen: pygame.Surface):
        list_information_color: List[Tuple[str, Tuple[int, int, int]]] = [
            ("Enter your name:", Common.blue),
            ("(Press enter when done):", Common.blue),
            ("", Common.green)
        ]
        self.input_requested: bool = True
        super().__init__(screen, list_information_color)
        self.sound_key_pressed: pygame.mixer.Sound =  pygame.mixer.Sound(Common.KEY_PRESSED)

    def key_pressed(self, key:str) -> None:
        """
        Override the behaviour when a key is pressed to write what the
        user is typing. Handle as well backspace
        """
        information, color = self.list_information_color[-1]
        if key == 'backspace':
            if len(information) > 0:
                information = information[:-1]
                pygame.mixer.Sound.play(self.sound_key_pressed)
        elif len(key) == 1:
            information += key
            pygame.mixer.Sound.play(self.sound_key_pressed)
        self.list_information_color[-1] = (information, color)
        self.print_information()

    def is_input_on_screen_requested(self) -> bool:
        """
        This boolean is a helper to help the client know if user input
        is currently activated or not
        """
        return self.input_requested

    def set_input_on_screen_requested(self, input_requested: bool) -> None:
        """
        See above for more info
        """
        self.input_requested = input_requested

    def get_user_string(self) -> str:
        """
        Return what the user typed
        """
        user_name, _ = self.list_information_color[-1]
        return user_name

    def clear_input(self) -> None:
        """
        Clear previously typed input
        """
        _, color = self.list_information_color[-1]
        self.list_information_color[-1] = ("", color)

class AllScores(InformationScreen): # pylint: disable=too-few-public-methods
    """
    Specialised class to display all scores
    """
    def __init__(self, screen: pygame.Surface,
                 list_information: List[str] = None):
        if list_information is None:
            list_information = []
        list_information_color: List[Tuple[str, Tuple[int, int, int]]] = []
        for index in range(min(10, len(list_information))):
            color = Common.red
            if index > len(list_information) // 6:
                color = Common.blue
            if index > len(list_information) // 3:
                color = Common.green
            list_information_color.append((list_information[index], color))

        list_information_color.append(("Press space or left click to continue!",
                                       Common.green))
        super().__init__(screen, list_information_color)
