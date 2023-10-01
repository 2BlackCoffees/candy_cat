"""
Handle collisions
"""
from typing import Tuple
from typing import List
from typing import Dict
from typing import Set

from domain.sprites.base_classes.static_sprite import StaticSprite
from domain.collision_handler.collision_handler import CollisionHandler
from domain.sprites.base_classes.static_sprite import Brick
from domain.sprites.sprites import GameMovingSprite
from domain.user_panel_interface.score_banner import Score
from domain.game_task_handler import WinLostManagement

from pprint import pprint

class CollisionHandlerSprites(CollisionHandler):
    """
    This class handles collisions:
    it checks whether 2 objects bumped against each other.
    """
    FROM_SIDE = 'from_side'
    SPRITE = 'sprite'
    PERIMETER='perimeter'
    PERIMETER_OPTIMIZED='perimeter_optimized'

    def __init__(self, score: Score, win_lost_management: WinLostManagement):
        self.score = score
        self.sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]] = {}
        self.sprite_ids_around_sprite_id: Dict[str, List[str]] = {}
        self.dynamic_sprites: Set[StaticSprite] = set()
        self.bricks_must_disappear: Set[Brick] = set()
        self.win_lost_management: WinLostManagement = win_lost_management

    @staticmethod
    def __get_sprites_around_sprite_from_sprite_id(sprite_ids: List[str], 
                                                   sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]]) -> List[StaticSprite]:
        return_sprites: List[StaticSprite] = [ sprite for sprite in sprites_to_perimeter.keys() \
                                              if sprite.get_unique_id() in sprite_ids]
        return return_sprites    

    def __get_coordinates_corners(self, sprite: StaticSprite, optimized: bool = True):
       perimeter = self.__get_perimeter(sprite, optimized, self.sprites_to_perimeter)
       return (perimeter[0]['x'], perimeter[0]['y'], perimeter[1]['x'], perimeter[1]['y'])
         
    def __update_perimeters_around_added_sprite(self, current_sprite: StaticSprite, 
                                                optimized: bool) -> None:
        (current_sprite_pos_x, current_sprite_pos_y, current_sprite_width, current_sprite_height) = \
            self.__get_coordinates_corners(current_sprite)
        
        self.sprite_ids_around_sprite_id[current_sprite.get_unique_id()] = []
        max_diff: int = 2
        sprite_list: List[StaticSprite] = [sprite for sprite in self.sprites_to_perimeter \
                                  if sprite != current_sprite and sprite.get_unique_id() not in self.sprite_ids_around_sprite_id[current_sprite.get_unique_id()]]

        for other_sprite in sprite_list:
            (other_sprite_pos_x, other_sprite_pos_y, other_sprite_width, other_sprite_height) = \
                self.__get_coordinates_corners(other_sprite)
            if (abs(current_sprite_pos_x + current_sprite_width - other_sprite_pos_x)   < max_diff or \
                current_sprite_pos_x == other_sprite_pos_x or \
                abs(other_sprite_pos_x + other_sprite_width - current_sprite_pos_x) < max_diff) \
               and \
               (abs(current_sprite_pos_y + current_sprite_height - other_sprite_pos_y)   < max_diff or \
                current_sprite_pos_y == other_sprite_pos_y or \
                abs(other_sprite_pos_y + other_sprite_height - current_sprite_pos_y) < max_diff):
                
                self.sprite_ids_around_sprite_id[current_sprite.get_unique_id()].append(other_sprite.get_unique_id())

    def __update_perimeters_around_removed_sprite(self, sprite_to_remove: StaticSprite) -> None:

        del self.sprite_ids_around_sprite_id[sprite_to_remove.get_unique_id()]
        for sprite_list in self.sprite_ids_around_sprite_id:
            if sprite_to_remove.get_unique_id() in sprite_list:
                sprite_list.remove(sprite_to_remove.get_unique_id())

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
        self.sprites_to_perimeter[sprite] = {self.PERIMETER:           sprite.get_perimeter(),
                                self.PERIMETER_OPTIMIZED: sprite.get_perimeter_optimized()}
        self.__update_perimeters_around_added_sprite(sprite, True)

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
        self.__update_perimeters_around_removed_sprite(sprite)

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
                           sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]],
                           sprites_around: List[StaticSprite],
                           optimized_perimeter: bool) -> Tuple[bool, Dict[str, int]]:
        """
        Analyzes if a collision happened and which side collided
        """
        static_sprite_perimeter = self.__get_perimeter(static_sprite, optimized_perimeter, sprites_to_perimeter)

        final_moving_sprite_side_bumped: Dict[str, int] = {}
        has_bumped, moving_sprite_side_bumped = self.__get_side_bumped(moving_sprite_perimeter, 
                                                                       moving_sprite, 
                                                                       static_sprite_perimeter)
        if has_bumped:
            latest_moving_sprite_side_bumped: Dict[str, int] = moving_sprite_side_bumped
            
            for sprite_around in sprites_around:
                static_sprite_perimeter = self.__get_perimeter(sprite_around, optimized_perimeter, sprites_to_perimeter)
                has_bumped, moving_sprite_side_bumped = self.__get_side_bumped(moving_sprite_perimeter, 
                                                                       moving_sprite, 
                                                                       static_sprite_perimeter)
                if has_bumped:
                    for key in moving_sprite_side_bumped.keys():
                        if key not in latest_moving_sprite_side_bumped.keys():
                            latest_moving_sprite_side_bumped[key] = moving_sprite_side_bumped[key]
                        else:
                            if latest_moving_sprite_side_bumped[key] != moving_sprite_side_bumped[key]:
                                latest_moving_sprite_side_bumped[key] = 0

            for key in moving_sprite_side_bumped.keys():
                if latest_moving_sprite_side_bumped[key] != 0:
                    final_moving_sprite_side_bumped[key] = latest_moving_sprite_side_bumped[key]

        moving_sprite.set_collision_happened(has_bumped)

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
        moving_sprite: GameMovingSprite = None
        dynamic_sprites = self.dynamic_sprites.copy()
        sprites = self.sprites_to_perimeter.copy()
        for moving_sprite in dynamic_sprites:
            moving_sprite_side_bumped: Dict[str, int] = self.check_for_collision(moving_sprite, sprites, optimized_perimeter)
            if moving_sprite_side_bumped is not None:
                moving_sprites_collided[moving_sprite] = moving_sprite_side_bumped

        for moving_sprite, moving_sprite_side_bumped in moving_sprites_collided.items():
            moving_sprite.bumped(moving_sprite_side_bumped)

    def check_for_collision(self, moving_sprite: GameMovingSprite, \
        sprites_to_perimeter: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]] = None, \
            optimized_perimeter: bool = True) -> Dict[str, int]:
        """
        When a moving sprite is about to move he should call this method first
        before moving: this will call the method bumped of all moving sprites
        that collided
        """

        if sprites_to_perimeter is None:
            sprites_to_perimeter = self.sprites_to_perimeter.copy()
        moving_sprite_perimeter = self.__get_perimeter(moving_sprite, optimized_perimeter, sprites_to_perimeter)
        for sprite in sprites_to_perimeter:
            if sprite != moving_sprite:
                has_bumped, moving_sprite_side_bumped = \
                        self.__points_collision(moving_sprite_perimeter, 
                                                moving_sprite, 
                                                sprite,
                                                sprites_to_perimeter,
                                                CollisionHandlerSprites.__get_sprites_around_sprite_from_sprite_id(\
                                                    self.sprite_ids_around_sprite_id[moving_sprite.get_unique_id()], 
                                                    sprites_to_perimeter),
                                                optimized_perimeter
                                                )
                if has_bumped:
                    sprite.bumped(moving_sprite_side_bumped)
                    return moving_sprite_side_bumped
        return None

    def add_score(self, add_score: int) -> None:
        """
        This method is used by a sprite to inform the scor that points need to be added or removed
        TODO: This method should be moved in a separate class as it is breaking the SRP principle
        """
        self.score.increase_score(add_score)
