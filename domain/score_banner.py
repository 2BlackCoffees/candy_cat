"""
Display score and number of remaing balls in the top banner
"""
from typing import Tuple
from domain.static_sprite import Display
from domain.common import Common
import pygame

class Score(pygame.sprite.Sprite):
    """
    Handle the score banner
    """
    def __init__(self, screen: pygame.Surface, height: int, score: int, remaining_balls: int):
        super().__init__()
        pygame.font.init()
        self.font:  pygame.font.Font = pygame.font.SysFont('Comic Sans MS', 30)
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.display: Display = Display(screen, screen_width, screen_height)
        self.height = height
        self.score = score
        self.remaining_balls = remaining_balls

    def increase_score(self, added_score) -> None:
        """
        Increase the score (or decrease if the value is negative)
        """
        self.score += added_score

    def set_number_balls(self, remaining_balls: int) -> None:
        """
        We want to display the number of balls
        """
        self.remaining_balls = remaining_balls

    def get_score(self) -> int:
        """
        Get latest score
        """
        return self.score

    def __get_score_images(self) -> Tuple[pygame.Surface, pygame.Surface, pygame.Surface]:
        """
        Return the images to be displayed on the banner
        """
        color_score: Tuple[int, int, int] = Common.blue
        if self.score < 0:
            color_score = Common.red

        text_surface: pygame.Surface = self.font.render('Your score: ', False, Common.blue)
        score_surface: pygame.Surface =  self.font.render(str(self.score), False, color_score)
        remaining_balls_surface: pygame.Surface =  self.font.render('  -  Remaining balls: ' + \
                                                    str(self.remaining_balls), \
                                                    False, Common.green)
        return text_surface, score_surface, remaining_balls_surface

    def display_on_screen(self) -> None:
        """
        Display images on the banner
        """
        text_surface: pygame.Surface = None
        score_surface: pygame.Surface = None
        remaining_balls_surface: pygame.Surface = None

        text_surface, score_surface, remaining_balls_surface = self.__get_score_images()
        whole_width: int = text_surface.get_width() + score_surface.get_width() + \
                           remaining_balls_surface.get_width()
        left_pos_text: int = (self.display.screen_width - whole_width ) // 2
        left_pos_score = left_pos_text + text_surface.get_width()
        left_pos_remaining_balls = left_pos_score + score_surface.get_width()
        top_pos = (self.height // 2 - max(text_surface.get_height(), \
                                          score_surface.get_height(), \
                                          remaining_balls_surface.get_height()))

        self.display.screen.blit(text_surface, (left_pos_text, top_pos))
        self.display.screen.blit(score_surface, (left_pos_score, top_pos))
        self.display.screen.blit(remaining_balls_surface, (left_pos_remaining_balls, top_pos))
