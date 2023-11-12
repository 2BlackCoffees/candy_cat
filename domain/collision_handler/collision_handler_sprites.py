"""
Handle collisions
"""
from typing import Tuple
from typing import List
from typing import Dict
from typing import Set
from math import floor, ceil
from datetime import datetime

from domain.sprites.base_classes.static_sprite import StaticSprite
from domain.collision_handler.collision_handler import CollisionHandler
from domain.sprites.base_classes.static_sprite import Brick
from domain.sprites.sprites import GameMovingSprite
from domain.sprites.sprites import UnbreakableBrick
from domain.sprites.sprites import PoisonedBrick
from domain.sprites.sprites import BreakableBrick
from domain.user_panel_interface.score_banner import Score
from domain.game_task_handler import WinLostManagement
from infrastructure.gui_library import Canvas

from pprint import pprint, pformat

class CollisionHandlerSprites(CollisionHandler):
    """
    This class handles collisions:
    it checks whether 2 objects bumped against each other.
    """
    FROM_SIDE = 'from_side'
    SPRITE = 'sprite'
    PERIMETER='perimeter'
    PERIMETER_OPTIMIZED='perimeter_optimized'
    CACHE_WIDTH_BLOCK_SIZE = 10
    CACHE_HEIGHT_BLOCK_SIZE = 10

    def __init__(self, score: Score, win_lost_management: WinLostManagement, screen: Canvas):
        self.score = score
        self.sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]] = {}
        self.sprite_ids_around_sprite_id: Dict[str, List[str]] = {}
        self.dynamic_sprites: Set[GameMovingSprite] = set()
        self.bricks_must_disappear: Set[Brick] = set()
        self.win_lost_management: WinLostManagement = win_lost_management
        self.game_width, self.game_height = -1, -1
        self.generic_sprite_width, self.generic_sprite_height, self.from_height = -1, -1, -1
        self.screen_width, self.screen_height = screen.get_screen_size()

        self.yx_to_sprite: \
            List[List[Dict[StaticSprite, Dict[str, List[Dict[str, int]]]]]] = []

    def __print_table(self, yx_to_sprite, x_ball, y_ball, x_min = -1, x_max = -1, y_min = -1, y_max = -1, print_detailed: bool = False):
        for y in range(len(yx_to_sprite)):
            line: str = ''
            for x in range(len(yx_to_sprite[y])):
                char: str = ' '
                data = yx_to_sprite[y][x]
                if len(data) > 0:
                    sprite = list(data.keys())[0]
                    if isinstance(sprite, UnbreakableBrick):
                        char = 'U'
                    elif isinstance(sprite, BreakableBrick):
                        char = '1'
                    if isinstance(sprite, PoisonedBrick):
                        char = 'P'
                if x >= x_min and x < x_max and y >= y_min and y < y_max:
                    if char == 'U': char = 'u'
                    elif char == '1': char = 'I'
                    elif char == 'P': char = 'p'
                    elif char == ' ': char = '-'
                    else: char = "*"
                if x == x_ball and y == y_ball:
                    char = "0"
                if print_detailed:
                    char = f'{x},{y}:{char}'
                line += char
            print(line)
        # if not print_detailed:
        #     self.__print_table(x_min, x_max, y_min, y_max, True)
    def __print_cached_block(self, cached_blocks, ball_x, bally) -> None:
        yx_copy = [
                [ {} for _ in range(self.game_width) ] for _ in range(self.game_height)
        ]
        for sprite, _ in cached_blocks.items():
            perimeter = self.__get_perimeter(sprite, True, self.sprites_to_perimeter)
            x, y = self.__get_sprite_indexes_from_xyposition(perimeter[0]['x'], perimeter[0]['y'])
            if x >= 0 and y>= 0 and x < self.game_width and y < self.game_height:
                yx_copy[y][x][sprite] = perimeter
        self.__print_table(yx_copy, ball_x, bally)

    def set_game_size(self, game_size: Tuple[int, int]) -> None:
        self.game_width, self.game_height = game_size
        self.yx_to_sprite = [
                [ {} for _ in range(self.game_width) ] for _ in range(self.game_height)
        ]

    def set_generic_sprite_size(self, generic_sprite_size: Tuple[int, int], from_height: int) -> None:
        generic_sprite_width, generic_sprite_height = generic_sprite_size
        self.generic_sprite_width: int = int(generic_sprite_width)
        self.generic_sprite_height: int = int(generic_sprite_height)
        self.from_height = from_height
        
    @staticmethod
    def __get_sprites_around_sprite_from_sprite_id(sprite_ids: List[str], 
                                                   sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]]) -> List[StaticSprite]:
        return_sprites: List[StaticSprite] = [ 
            sprite for sprite in sprites_to_perimeter.keys() \
                                              if sprite.get_unique_id() in sprite_ids ]
        return return_sprites    

    def __get_coordinates_corners(self, sprite: StaticSprite, optimized: bool):
       perimeter = self.__get_perimeter(sprite, optimized, self.sprites_to_perimeter)
       return (perimeter[0]['x'], perimeter[0]['y'], perimeter[1]['x'], perimeter[1]['y'])
         
    def __get_sprite_indexes_from_xyposition(self, current_sprite_pos_x: int, current_sprite_pos_y: int) -> Tuple[int, int]:
        current_index_x: int = -1
        current_index_y: int = -1
        
        if current_sprite_pos_y < self.screen_height - self.from_height:
            current_index_x = int(current_sprite_pos_x / self.generic_sprite_width)
            current_index_y = int(current_sprite_pos_y / self.generic_sprite_height)

        return current_index_x, current_index_y
    
    def __are_valid_indexes(self, index_x: int, index_y: int) -> bool:
        return index_x >= 0 and index_x < self.game_width and index_y >= 0 and index_y < self.game_height
    
    def __get_all_surrounding_cache_blocks(self, 
                                           perimeter: List[Dict[str, int]], 
                                           dynamic_sprites: Set[GameMovingSprite])\
          -> List[List[Dict[StaticSprite, Dict[str, List[Dict[str, int]]]]]]:
        
        # We need to find all indexes of all sprites for all four corners
        x_min: int = self.game_width - 1
        y_min: int = self.game_height - 1
        x_max = -1
        y_max = -1

        surrounding_cached_blocks: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]] = {}
        for sprite in dynamic_sprites:
            surrounding_cached_blocks[sprite] = self.sprites_to_perimeter[sprite]
        for point in perimeter:
            x, y = self.__get_sprite_indexes_from_xyposition(point['x'], point['y'])
            if x >= 0 and y>= 0:
                if(x < x_min):
                    x_min = max(0, x - 3)
                if(y < y_min):
                    y_min = max(0, y - 3)
                if(x > x_max):
                    x_max = min(self.game_width, x + 3)
                if(y > y_max):
                    y_max = min(self.game_height, y + 3)
                dbg_position = f"x:, {point['x']}, {x_min}, {x}, {x_max}, y:, {point['y']}, {y_min}, {y}, {y_max}"
                dbg_print_table: bool = True
                dbg_yx_copy = [
                    [ {} for _ in range(self.game_width) ] for _ in range(self.game_height)
                ]

                for index_y in range(y_min, y_max):
                    for index_x in range(x_min, x_max):
                        if self.__are_valid_indexes(index_x,index_y) and len(self.yx_to_sprite[index_y][index_x]) > 0:
                            for sprite, perimeter in (self.yx_to_sprite[index_y][index_x]).items():
                                dbg_print_table = True
                                print(f"dbg: Brick at {index_x}, {index_y}: {dbg_position}")
                                surrounding_cached_blocks[sprite] = perimeter
                                dbg_yx_copy[index_y][index_x][sprite] = perimeter
                if dbg_print_table:
                    print(f'x_min: {x_min}, x_max: {x_max}, y_min: {y_min}, y_max: {y_max}')
                    self.__print_table(self.yx_to_sprite, x, y, x_min, x_max, y_min, y_max)
                    #self.__print_table(dbg_yx_copy, x ,y)
                    self.__print_cached_block(surrounding_cached_blocks, x, y)
                                    
        
        return surrounding_cached_blocks

    def subscribe_static(self, sprite: Brick) -> None:
        """
        Subscribe a new static sprite which needs to be analyzed against a collision
        """
        self.__save_sprite_for_collision(sprite)

        if sprite.bring_points():
            self.bricks_must_disappear.add(sprite)

    def subscribe_moving(self, sprite: GameMovingSprite) -> None:
        """
        Subscribe a new sprite which needs to be analyzed against a collision
        """
        self.dynamic_sprites.add(sprite)
        self.__save_sprite_for_collision(sprite)

    def __save_sprite_for_collision(self, sprite: StaticSprite) -> None:
        """
        Dynamic sprites
        """
        perimeter_optimized: List[Dict[str, int]] = sprite.get_perimeter_optimized()
        self.sprites_to_perimeter[sprite] = {self.PERIMETER:           sprite.get_perimeter(),
                                             self.PERIMETER_OPTIMIZED: perimeter_optimized}
        current_sprite_pos_x, current_sprite_pos_y = sprite.get_position_for_collision_analysis()
        index_x, index_y = self.__get_sprite_indexes_from_xyposition(current_sprite_pos_x, current_sprite_pos_y)

        #print(f'__save_sprite_for_collision: (self.generic_sprite_width: {self.generic_sprite_width}, self.generic_sprite_height: {self.generic_sprite_height}); (current_sprite_pos_x: {current_sprite_pos_x}, current_sprite_pos_y: {current_sprite_pos_y}) to (index_x: {index_x}, index_y: {index_y})')
        if self.__are_valid_indexes(index_x, index_y):
            self.yx_to_sprite[index_y][index_x][sprite] = self.sprites_to_perimeter[sprite]

    def unsubscribe(self, sprite: StaticSprite) -> None:
        """
        Dynamic sprites
        """

        if sprite in self.sprites_to_perimeter:
            del self.sprites_to_perimeter[sprite]
        if sprite in self.dynamic_sprites:
            self.dynamic_sprites.remove(sprite)
        if sprite in self.bricks_must_disappear:
            self.bricks_must_disappear.remove(sprite)
            if len(self.bricks_must_disappear) == 0:
                self.win_lost_management.inform_player_won()

        current_sprite_pos_x, current_sprite_pos_y = sprite.get_position_for_collision_analysis()
        index_x, index_y = self.__get_sprite_indexes_from_xyposition(current_sprite_pos_x, current_sprite_pos_y)
        self.yx_to_sprite[index_y][index_x] = {}
        #self.__update_perimeters_around_removed_sprite(sprite)

    def __get_moved_perimeter_to_position(self,pos_x: int, pos_y: int,
                                          perimeter: List[Dict[str, int]]) -> List[Dict[str, int]]:
        """
        Sprites define their perimeter
        """
        return [{'x': pos_x + position['x'], 'y': pos_y + position['y']} \
                for position in perimeter]

    def __get_perimeter(self, sprite: StaticSprite, optimized: bool, \
        sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]]) -> List[Dict[str, int]]:
        """
        Get the proper perimeter: each sprite knows its perimeter.
        This methods calculate the perimieter taking into account th position of the sprite.
        """
        (pos_x, pos_y) = sprite.get_position_for_collision_analysis()
        perimeter_type = self.PERIMETER_OPTIMIZED if optimized else self.PERIMETER
        return self.__get_moved_perimeter_to_position(pos_x, pos_y, sprites_to_perimeter[sprite][perimeter_type])

    def __get_side_bumped_unused(self,
                          moving_sprite_perimeter: List[Dict[str, int]], 
                          moving_sprite: GameMovingSprite, 
                          static_sprite_perimeter: List[Dict[str, int]])  -> Tuple[bool, Dict[str, int]]:
        has_bumped: bool = False
        moving_sprite_side_bumped: Dict[str, int] = {}
        moving_sprite_x_direction: int = moving_sprite.get_x_direction()
        moving_sprite_y_direction: int = moving_sprite.get_y_direction()
        moving_sprite_top_left_corner, moving_sprite_bottom_right_corner = moving_sprite_perimeter
        top_left_corner,               bottom_right_corner               = static_sprite_perimeter

        moving_sprite_top_left_corner_x,     moving_sprite_top_left_corner_y     = moving_sprite_top_left_corner['x'],     moving_sprite_top_left_corner['y']
        moving_sprite_bottom_right_corner_x, moving_sprite_bottom_right_corner_y = moving_sprite_bottom_right_corner['x'], moving_sprite_bottom_right_corner['y']
        top_left_corner_x,                   top_left_corner_y                   = top_left_corner['x'],                   top_left_corner['y']
        bottom_right_corner_x,               bottom_right_corner_y               = bottom_right_corner['x'],               bottom_right_corner['y']

        # Check if collision happened
        if not (moving_sprite_top_left_corner_x     > bottom_right_corner_x or
                moving_sprite_bottom_right_corner_x < top_left_corner_x     or
                moving_sprite_top_left_corner_y     > bottom_right_corner_y or
                moving_sprite_bottom_right_corner_y < top_left_corner_y):

            dbg_index_x, dbg_index_y = self.__get_sprite_indexes_from_xyposition(top_left_corner_x, top_left_corner_y)
            print(f"Bumped sprite: x: {top_left_corner_x}, y: {top_left_corner_y}, dbg_index_x: {dbg_index_x}, dbg_index_y: {dbg_index_y}")

            has_bumped = True

            # Calculate next coordinates if sprite moves 1 step more in current direction
            moving_sprite_top_left_corner_next_x = moving_sprite_top_left_corner_x +  moving_sprite_x_direction
            moving_sprite_bottom_right_corner_next_x = moving_sprite_bottom_right_corner_x +  moving_sprite_x_direction
            moving_sprite_top_left_corner_next_y = moving_sprite_top_left_corner_y +  moving_sprite_y_direction
            moving_sprite_bottom_right_corner_next_y = moving_sprite_bottom_right_corner_y +  moving_sprite_y_direction
    
            # Calculate diff sprite having moved in current direction and position of sprite bumped into (this will help increase the collision effect)
            moving_sprite_diff_left   = bottom_right_corner_x                    - moving_sprite_top_left_corner_next_x 
            moving_sprite_diff_right  = moving_sprite_bottom_right_corner_next_x - top_left_corner_x
            moving_sprite_diff_top    = bottom_right_corner_y                    - moving_sprite_bottom_right_corner_next_y
            moving_sprite_diff_bottom = moving_sprite_bottom_right_corner_y      - top_left_corner_y 

            # Collision leads to the lowest values of diff
            diff_horizontal : int = moving_sprite_diff_left
            if moving_sprite_diff_right < moving_sprite_diff_left:
                print("Bumped from the right!")
                diff_horizontal = moving_sprite_diff_right
            else:
                print("Bumped from the left!")

            diff_vertical : int = moving_sprite_diff_top
            if moving_sprite_diff_bottom < moving_sprite_diff_top:
                print("Bumped from the bottom!")
                diff_vertical = moving_sprite_diff_bottom
            else:
                print("Bumped from the top!")
    
            # Now we look for the direction that will remove the collision
            check_next_move : List[Tuple(int, int)] = \
                              [ (-moving_sprite_x_direction, moving_sprite_y_direction),\
                                (moving_sprite_x_direction, -moving_sprite_y_direction),\
                                (-moving_sprite_x_direction, -moving_sprite_y_direction)]
            # Check if collision is mostly vertically or horizontally
            if diff_vertical < diff_horizontal:
                print("Collision happened mostly vertically")
                check_next_move = [ (moving_sprite_x_direction, -moving_sprite_y_direction),\
                                    (-moving_sprite_x_direction, moving_sprite_y_direction),\
                                    (-moving_sprite_x_direction, -moving_sprite_y_direction)]
            else:
                print("Collision happened mostly horizontally")

            # Look for the best new direction
            selected_moving_sprite_x_direction: int = -moving_sprite_x_direction
            selected_moving_sprite_y_direction: int = -moving_sprite_y_direction
    
            for (tmp_moving_sprite_x_direction, tmp_moving_sprite_y_direction) in check_next_move:
                moving_sprite_top_left_corner_next_x     = moving_sprite_top_left_corner_x     + tmp_moving_sprite_x_direction
                moving_sprite_bottom_right_corner_next_x = moving_sprite_bottom_right_corner_x + tmp_moving_sprite_x_direction
                moving_sprite_top_left_corner_next_y     = moving_sprite_top_left_corner_y     + tmp_moving_sprite_y_direction
                moving_sprite_bottom_right_corner_next_y = moving_sprite_bottom_right_corner_y + tmp_moving_sprite_y_direction

                # If the collision does not exist anymore, save the direction
                if (moving_sprite_top_left_corner_next_x     > bottom_right_corner_x or \
                    moving_sprite_bottom_right_corner_next_x < top_left_corner_x or \
                    moving_sprite_top_left_corner_next_y     > bottom_right_corner_y or \
                    moving_sprite_bottom_right_corner_next_y < top_left_corner_y):
                        selected_moving_sprite_x_direction = tmp_moving_sprite_x_direction
                        selected_moving_sprite_y_direction = tmp_moving_sprite_y_direction
                        break
            
            moving_sprite_diff_left   = bottom_right_corner_x               - moving_sprite_top_left_corner_x 
            moving_sprite_diff_right  = moving_sprite_bottom_right_corner_x - top_left_corner_x
            moving_sprite_diff_top    = moving_sprite_bottom_right_corner_y - top_left_corner_y
            moving_sprite_diff_bottom = bottom_right_corner_y               - moving_sprite_top_left_corner_x 
            diff_horizontal  = min(moving_sprite_diff_left, moving_sprite_diff_right)
            diff_vertical    = min(moving_sprite_diff_top, moving_sprite_diff_bottom)
    
            if selected_moving_sprite_x_direction == -moving_sprite_x_direction:
                if moving_sprite_diff_top < moving_sprite_diff_bottom:
                    moving_sprite_side_bumped[self.HORIZONTAL] = moving_sprite_diff_top
                else:
                    moving_sprite_side_bumped[self.HORIZONTAL] = -moving_sprite_diff_bottom
    
            if selected_moving_sprite_y_direction == -moving_sprite_y_direction:
                if moving_sprite_diff_left < moving_sprite_diff_right:
                    moving_sprite_side_bumped[self.VERTICAL] = moving_sprite_diff_left
                else:
                    moving_sprite_side_bumped[self.VERTICAL] = -moving_sprite_diff_right

        return has_bumped, moving_sprite_side_bumped
    
    def __get_side_bumped(self,
                          moving_sprite_perimeter: List[Dict[str, int]], 
                          moving_sprite: GameMovingSprite, 
                          static_sprite_perimeter: List[Dict[str, int]])  -> Tuple[bool, Dict[str, int]]:
        has_bumped: bool = False
        moving_sprite_side_bumped: Dict[str, int] = {}
        moving_sprite_x_direction: int = moving_sprite.get_x_direction()
        moving_sprite_y_direction: int = moving_sprite.get_y_direction()
        moving_sprite_top_left_corner, moving_sprite_bottom_right_corner = moving_sprite_perimeter
        top_left_corner,               bottom_right_corner               = static_sprite_perimeter

        if not (moving_sprite_top_left_corner['x']     > bottom_right_corner['x'] or \
                moving_sprite_bottom_right_corner['x'] < top_left_corner['x'] or \
                moving_sprite_top_left_corner['y']     > bottom_right_corner['y'] or \
                moving_sprite_bottom_right_corner['y'] < top_left_corner['y']):

            has_bumped = True

            moving_sprite_top_left_corner_next_x = moving_sprite_top_left_corner['x'] +  moving_sprite_x_direction
            moving_sprite_bottom_right_corner_next_x = moving_sprite_bottom_right_corner['x'] +  moving_sprite_x_direction
            moving_sprite_top_left_corner_next_y = moving_sprite_top_left_corner['y'] +  moving_sprite_y_direction
            moving_sprite_bottom_right_corner_next_y = moving_sprite_bottom_right_corner['y'] +  moving_sprite_y_direction
    
            moving_sprite_diff_left   = bottom_right_corner['x']               - moving_sprite_top_left_corner_next_x 
            moving_sprite_diff_right  = moving_sprite_bottom_right_corner_next_x - top_left_corner['x']
            moving_sprite_diff_top    = moving_sprite_bottom_right_corner_next_y - top_left_corner['y']
            moving_sprite_diff_bottom = bottom_right_corner['y']               - moving_sprite_top_left_corner_next_y 
            diff_horizontal  = min(moving_sprite_diff_left, moving_sprite_diff_right)
            diff_vertical    = min(moving_sprite_diff_top, moving_sprite_diff_bottom)
    
            check_next_move = [ (-moving_sprite_x_direction, moving_sprite_y_direction),\
                                (moving_sprite_x_direction, -moving_sprite_y_direction),\
                                (-moving_sprite_x_direction, -moving_sprite_y_direction)]
            if diff_vertical < diff_horizontal:
                check_next_move = [ (moving_sprite_x_direction, -moving_sprite_y_direction),\
                                    (-moving_sprite_x_direction, moving_sprite_y_direction),\
                                    (-moving_sprite_x_direction, -moving_sprite_y_direction)]
    
            selected_moving_sprite_x_direction: int = -moving_sprite_x_direction
            selected_moving_sprite_y_direction: int = -moving_sprite_y_direction
    
            for (tmp_moving_sprite_x_direction, tmp_moving_sprite_y_direction) in check_next_move:
                moving_sprite_top_left_corner_next_x = moving_sprite_top_left_corner['x'] + tmp_moving_sprite_x_direction
                moving_sprite_bottom_right_corner_next_x = moving_sprite_bottom_right_corner['x'] + tmp_moving_sprite_x_direction
                moving_sprite_top_left_corner_next_y = moving_sprite_top_left_corner['y'] + tmp_moving_sprite_y_direction
                moving_sprite_bottom_right_corner_next_y = moving_sprite_bottom_right_corner['y'] + tmp_moving_sprite_y_direction
    
                if (moving_sprite_top_left_corner_next_x     > bottom_right_corner['x'] or \
                    moving_sprite_bottom_right_corner_next_x < top_left_corner['x'] or \
                    moving_sprite_top_left_corner_next_y     > bottom_right_corner['y'] or \
                    moving_sprite_bottom_right_corner_next_y < top_left_corner['y']):
                        selected_moving_sprite_x_direction = tmp_moving_sprite_x_direction
                        selected_moving_sprite_y_direction = tmp_moving_sprite_y_direction
                        break

            moving_sprite_diff_left   = bottom_right_corner['x']               - moving_sprite_top_left_corner['x'] 
            moving_sprite_diff_right  = moving_sprite_bottom_right_corner['x'] - top_left_corner['x']
            moving_sprite_diff_top    = moving_sprite_bottom_right_corner['y'] - top_left_corner['y']
            moving_sprite_diff_bottom = bottom_right_corner['y']               - moving_sprite_top_left_corner['y'] 
            diff_horizontal  = min(moving_sprite_diff_left, moving_sprite_diff_right)
            diff_vertical    = min(moving_sprite_diff_top, moving_sprite_diff_bottom)
    
            if selected_moving_sprite_x_direction == -moving_sprite_x_direction:
                if moving_sprite_diff_top < moving_sprite_diff_bottom:
                    moving_sprite_side_bumped[self.HORIZONTAL] = moving_sprite_diff_top
                else:
                    moving_sprite_side_bumped[self.HORIZONTAL] = -moving_sprite_diff_bottom
    
            if selected_moving_sprite_y_direction == -moving_sprite_y_direction:
                if moving_sprite_diff_left < moving_sprite_diff_right:
                    moving_sprite_side_bumped[self.VERTICAL] = moving_sprite_diff_left
                else:
                    moving_sprite_side_bumped[self.VERTICAL] = -moving_sprite_diff_right

        return has_bumped, moving_sprite_side_bumped
        
    def __points_collision(self, 
                           moving_sprite_perimeter: List[Dict[str, int]], 
                           moving_sprite: GameMovingSprite, 
                           static_sprite: StaticSprite, 
                           surrounding_sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]],
                           optimized_perimeter: bool) -> Tuple[bool, Dict[str, int]]:
        """
        Analyzes if a collision happened and which side collided
        """
        static_sprite_perimeter = self.__get_perimeter(static_sprite, optimized_perimeter, surrounding_sprites_to_perimeter)

        for point in static_sprite_perimeter:
            dbg_index_x, dbg_index_y = self.__get_sprite_indexes_from_xyposition(point['x'], point['y'])
            print(f"static_sprite {static_sprite}: x: {point['x']}, y: {point['y']}, dbg_index_x: {dbg_index_x}, dbg_index_y: {dbg_index_y}")

        final_moving_sprite_side_bumped: Dict[str, int] = {}
        has_bumped, moving_sprite_side_bumped = self.__get_side_bumped(moving_sprite_perimeter, 
                                                                       moving_sprite, 
                                                                       static_sprite_perimeter)
        if has_bumped:

            latest_moving_sprite_side_bumped: Dict[str, int] = moving_sprite_side_bumped
            
            for sprite_around in surrounding_sprites_to_perimeter.keys():
                if sprite_around != moving_sprite:
                    static_sprite_perimeter = self.__get_perimeter(sprite_around, optimized_perimeter, surrounding_sprites_to_perimeter)
                    has_bumped, moving_sprite_side_bumped = self.__get_side_bumped(moving_sprite_perimeter, 
                                                                        moving_sprite, 
                                                                        static_sprite_perimeter)
                    if has_bumped:
                        print(f"Bumped: {moving_sprite} bumped against {sprite_around} = ")
                        print(f"  moving_sprite_side_bumped: {pformat(moving_sprite_side_bumped)}, latest_moving_sprite_side_bumped: {pformat(latest_moving_sprite_side_bumped)}")

                        for key in moving_sprite_side_bumped.keys():

                            if key not in latest_moving_sprite_side_bumped.keys():
                                latest_moving_sprite_side_bumped[key] = moving_sprite_side_bumped[key]
                            else:
                                print(f'Analyzing: latest_moving_sprite_side_bumped[{key}] = {latest_moving_sprite_side_bumped[key]} and  moving_sprite_side_bumped[{key}] = {moving_sprite_side_bumped[key]}')
                                if latest_moving_sprite_side_bumped[key] != moving_sprite_side_bumped[key]:
                                    latest_moving_sprite_side_bumped[key] = 0
                                # if latest_moving_sprite_side_bumped[key] < 0 and moving_sprite_side_bumped[key] < 0:
                                #     latest_moving_sprite_side_bumped[key] = max(latest_moving_sprite_side_bumped[key], moving_sprite_side_bumped[key])
                                # elif latest_moving_sprite_side_bumped[key] > 0 and moving_sprite_side_bumped[key] > 0:
                                #     latest_moving_sprite_side_bumped[key] = min(latest_moving_sprite_side_bumped[key], moving_sprite_side_bumped[key])
                                # else:
                                #     print(f"Cancelling: latest_moving_sprite_side_bumped[{key}] to 0!!!")
                                #     latest_moving_sprite_side_bumped[key] = 0
                            print(f'Set: latest_moving_sprite_side_bumped[{key}] = {latest_moving_sprite_side_bumped[key]}')
                        for key in moving_sprite_side_bumped.keys():
                            print(f'Analyze: latest_moving_sprite_side_bumped[{key}] = {latest_moving_sprite_side_bumped[key]}')

            for key in latest_moving_sprite_side_bumped.keys():
                if latest_moving_sprite_side_bumped[key] != 0:
                    final_moving_sprite_side_bumped[key] = latest_moving_sprite_side_bumped[key]

        for key in final_moving_sprite_side_bumped.keys():
            print(f'Final: final_moving_sprite_side_bumped[{key}] = {final_moving_sprite_side_bumped[key]}')

        if has_bumped and len(final_moving_sprite_side_bumped) == 0:
            print("Bumped hapened but no direction change could be found")
        return has_bumped, final_moving_sprite_side_bumped

    def horizontal_collision_side_bumped(self, from_side_bumped: Dict[str, int]) -> Tuple[bool, int]:
        """
        Says whether a collision happened horizontally
        """
        if self.HORIZONTAL in from_side_bumped:
            return True, from_side_bumped[self.HORIZONTAL]
        return False, 0


    def vertical_collision_side_bumped(self, from_side_bumped: Dict[str, int]) -> Tuple[bool, int]:
        """
        Says whether a collision happened vertically
        """
        if self.VERTICAL in from_side_bumped:
            return True, from_side_bumped[self.VERTICAL]
        return False, 0

    def inform_sprite_about_to_move(self, optimized_perimeter: bool = True) -> None:
        """
        When a moving sprite is about to move he should call this method first
        before moving: this will call the method bumped of all moving sprites
        that collided
        """
        
        moving_sprites_collided: Dict[StaticSprite, Dict[str, int]] = {}
        copied_moving_sprite: GameMovingSprite = None
        copied_dynamic_sprites = self.dynamic_sprites.copy()
        #sprites = self.sprites_to_perimeter.copy()
        for copied_moving_sprite in copied_dynamic_sprites:
            moving_sprite_side_bumped: Dict[str, int] = self.check_for_collision(copied_moving_sprite, copied_dynamic_sprites, optimized_perimeter)
            if moving_sprite_side_bumped is not None:
                moving_sprites_collided[copied_moving_sprite] = moving_sprite_side_bumped

        for copied_moving_sprite, moving_sprite_side_bumped in moving_sprites_collided.items():
            copied_moving_sprite.bumped(moving_sprite_side_bumped)

    def check_for_collision(self, moving_sprite: GameMovingSprite, dynamic_sprites: Set[GameMovingSprite] = None,\
            optimized_perimeter: bool = True) -> Dict[str, int]:
        """
        When a moving sprite is about to move he should call this method first
        before moving: this will call the method bumped of all moving sprites
        that collided
        """
        #pprint(self.sprite_ids_around_sprite_id)
        #dbg_time_start = datetime.now()
        if dynamic_sprites == None: 
            dynamic_sprites = self.dynamic_sprites

        moving_sprite_perimeter = self.__get_perimeter(moving_sprite, optimized_perimeter, self.sprites_to_perimeter)
        surrounding_sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]] = \
            self.__get_all_surrounding_cache_blocks(moving_sprite_perimeter, dynamic_sprites).copy()
        return_value: Dict[str, int] = None

        for point in moving_sprite_perimeter:
            dbg_index_x, dbg_index_y = self.__get_sprite_indexes_from_xyposition(point['x'], point['y'])
            print(f"moving_sprite: x: {point['x']}, y: {point['y']}, dbg_index_x: {dbg_index_x}, dbg_index_y: {dbg_index_y}")
        for static_sprite in surrounding_sprites_to_perimeter:
            if static_sprite != moving_sprite:
                has_bumped, moving_sprite_side_bumped = \
                        self.__points_collision(moving_sprite_perimeter, 
                                                moving_sprite, 
                                                static_sprite,
                                                surrounding_sprites_to_perimeter,
                                                optimized_perimeter
                                                )
                if has_bumped:
                    static_sprite.bumped(moving_sprite_side_bumped)
                    return_value = moving_sprite_side_bumped
                    break
        #print(f"check_for_collision time: {(datetime.now() - dbg_time_start).microseconds / 1000} ms")

        return return_value

    def add_score(self, add_score: int) -> None:
        """
        This method is used by a sprite to inform the scor that points need to be added or removed
        TODO: This method should be moved in a separate class as it is breaking the SRP principle
        """
        self.score.increase_score(add_score)
