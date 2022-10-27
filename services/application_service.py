"""
Main Module
"""
import pygame
from pygame import mixer
from domain.common import Common
# from pprint import pprint
from services.create_scene_service import CreateSceneService

def start():
    """
      Main function of the program
    """
    screen_width: int = 1000
    screen_height: int = 800
    pygame.init()
    mixer.init()
    screen: pygame.Surface = pygame.display.set_mode((screen_width, screen_height),
                                     pygame.HWSURFACE | pygame.DOUBLEBUF)# | pygame.FULLSCREEN)

    pygame.display.set_caption('Wall breaker')
    create_scene_service: CreateSceneService = CreateSceneService([Common.GAME_NAME + 'assets/levels/game3', 
                                                                   Common.GAME_NAME + 'assets/levels/game1', 
                                                                   Common.GAME_NAME + 'assets/levels/game2'],screen)

    clock: pygame.time.Clock = pygame.time.Clock()

    while not create_scene_service.is_done():
        create_scene_service.update_game_scene()

        pygame.display.flip()

        clock.tick(80)

    pygame.quit()
