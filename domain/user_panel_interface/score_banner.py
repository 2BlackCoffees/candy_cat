"""
Display score and number of remaing balls in the top banner
"""
from typing import Tuple
from domain.sprites.base_classes.static_sprite import Display
from domain.common import Common
from infrastructure.gui_library import Canvas
from infrastructure.gui_library import Font
from infrastructure.gui_library import SpriteImage
from infrastructure.gui_library import Constants

class Score:
    """
    Handle the score banner
    """
    def __init__(self, screen: Canvas, height: int, score: int, remaining_balls: int):
        super().__init__()
        self.font: Font = Font(screen, 30)
        screen_width, screen_height = screen.get_screen_size()
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

    def __get_score_images(self) -> Tuple[SpriteImage, SpriteImage]:
        """
        Return the images to be displayed on the banner
        """
        color_score: Tuple[int, int, int] = Common.blue
        if self.score < 0:
            color_score = Common.red

        text_surface: SpriteImage = self.font.render_font('Your score: ', Constants.blue)
        score_surface: SpriteImage =  self.font.render_font(str(self.score), color_score)
        remaining_balls_surface: SpriteImage = \
            self.font.render_font('  -  Remaining balls: ' + \
                str(self.remaining_balls), Constants.green)
        return text_surface, score_surface, remaining_balls_surface

    def display_on_screen(self) -> None:
        """
        Display images on the banner
        """
        text_surface: SpriteImage = None
        score_surface: SpriteImage = None
        remaining_balls_surface: SpriteImage = None

        text_surface, score_surface, remaining_balls_surface = self.__get_score_images()
        whole_width: int = text_surface.get_width() + score_surface.get_width() + \
                           remaining_balls_surface.get_width()
        left_pos_text: int = (self.display.screen_width - whole_width ) // 2
        left_pos_score = left_pos_text + text_surface.get_width()
        left_pos_remaining_balls = left_pos_score + score_surface.get_width()
        top_pos = (self.height // 2 - max(text_surface.get_height(), \
                                          score_surface.get_height(), \
                                          remaining_balls_surface.get_height()))

        text_surface.display_on_screen_at_position(left_pos_text, top_pos)
        score_surface.display_on_screen_at_position(left_pos_score, top_pos)
        remaining_balls_surface.display_on_screen_at_position(left_pos_remaining_balls, top_pos)
