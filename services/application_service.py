"""
Main Module
"""
from domain.common import Common
from services.create_scene_service import CreateSceneService
from infrastructure.gui_library import Canvas

def start():
    """
      Main function of the program
    """
    screen_width: int = 1000
    screen_height: int = 800
    screen: Canvas = Canvas('Candy Cat', screen_width, screen_height, Common.START_MUSIC)
    screen: Canvas = Canvas('Candy Cat', screen_width, screen_height, Common.START_MUSIC)

    create_scene_service: CreateSceneService = CreateSceneService(
        [Common.GAME_NAME + 'assets/levels/game2',
        Common.GAME_NAME + 'assets/levels/game4',
        Common.GAME_NAME + 'assets/levels/game1',
        Common.GAME_NAME + 'assets/levels/game3'],screen)


    while not create_scene_service.is_done():
        create_scene_service.update_game_scene()

        screen.refresh()
    Canvas.quit()
