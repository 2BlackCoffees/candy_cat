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
        self.sprites: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]] = {}
        self.dynamic_sprites: Set[StaticSprite] = set()
        self.bricks_must_disappear: Set[Brick] = set()
        self.win_lost_management: WinLostManagement = win_lost_management

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
        self.sprites[sprite] = {self.PERIMETER:           sprite.get_perimeter(),
                                self.PERIMETER_OPTIMIZED: sprite.get_perimeter_optimized()}

    def unsubscribe(self, sprite: StaticSprite) -> None:
        """
        Dynamic sprites
        """
        if sprite in self.sprites:
            del self.sprites[sprite]
        if sprite in self.dynamic_sprites:
            self.dynamic_sprites.remove(sprite)
        if sprite in self.bricks_must_disappear:
            self.bricks_must_disappear.remove(sprite)
            if len(self.bricks_must_disappear) == 0:
                self.win_lost_management.inform_player_won()

    def __get_moved_perimeter_to_position(self,pos_x: int, pos_y: int,
                                          perimeter: List[Dict[str, int]]) -> List[Dict[str, int]]:
        """
        Sprites define their perimeter
        """
        return [{'x': pos_x + position['x'], 'y': pos_y + position['y']} \
                for position in perimeter]

    def __get_perimeter(self, sprite: StaticSprite, optimized: bool, \
        sprites: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]]) -> List[Dict[str, int]]:
        """
        Get the proper perimeter: each sprite knows its perimeter.
        This methods calculate the perimieter taking into account th position of the sprite.
        """
        (pos_x, pos_y) = sprite.get_position_for_collision_analysis()
        key = self.PERIMETER_OPTIMIZED if optimized else self.PERIMETER
        return self.__get_moved_perimeter_to_position(pos_x, pos_y, sprites[sprite][key])

    def __points_collision(self, from_perimeter: List[Dict[str, int]], perimeter: List[Dict[str, int]]) -> Tuple[bool, Dict[str, int]]:
        """
        Analyzes if a collision happened and which side collided
        """
        from_top_left_corner, from_bottom_right_corner = from_perimeter
        top_left_corner,      bottom_right_corner      = perimeter
        has_bumped: bool = False
        from_side_bumped: Dict[str, int] = {}

        if not (from_top_left_corner['x']     > bottom_right_corner['x'] or \
                from_bottom_right_corner['x'] < top_left_corner['x'] or \
                from_top_left_corner['y']     > bottom_right_corner['y'] or \
                from_bottom_right_corner['y'] < top_left_corner['y']):
            has_bumped = True
            from_diff_left   = bottom_right_corner['x']      - from_top_left_corner['x']
            from_diff_right  = from_bottom_right_corner['x'] - top_left_corner['x']
            from_diff_top    = from_bottom_right_corner['y'] - top_left_corner['y']
            from_diff_bottom = bottom_right_corner['y']      - from_top_left_corner['y']
            diff_horizontal  = min(from_diff_left, from_diff_right)
            diff_vertical    = min(from_diff_top, from_diff_bottom)

            if diff_horizontal < diff_vertical:
                if from_diff_top < from_diff_bottom:
                    from_side_bumped[self.HORIZONTAL] = from_diff_top
                else:
                    from_side_bumped[self.HORIZONTAL] = -from_diff_bottom

            elif diff_horizontal > diff_vertical:
                if from_diff_left < from_diff_right:
                    from_side_bumped[self.VERTICAL] = from_diff_left
                else:
                    from_side_bumped[self.VERTICAL] = -from_diff_right

        return has_bumped, from_side_bumped

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
        from_sprite: GameMovingSprite = None
        dynamic_sprites = self.dynamic_sprites.copy()
        sprites = self.sprites.copy()
        for from_sprite in dynamic_sprites:
            from_side_bumped: Dict[str, int] = self.check_for_collision(from_sprite, sprites, optimized_perimeter)
            if from_side_bumped is not None:
                moving_sprites_collided[from_sprite] = from_side_bumped

        for from_sprite, from_side_bumped in moving_sprites_collided.items():
            from_sprite.bumped(from_side_bumped)

    def check_for_collision(self, from_sprite: GameMovingSprite, \
        sprites: Dict[StaticSprite, Dict[str, List[Dict[str, int]]]] = None, \
            optimized_perimeter: bool = True) -> Dict[str, int]:
        """
        When a moving sprite is about to move he should call this method first
        before moving: this will call the method bumped of all moving sprites
        that collided
        """
        
        if sprites is None:
            sprites = self.sprites.copy()
        from_perimeter = self.__get_perimeter(from_sprite, optimized_perimeter, sprites)
        for sprite in sprites:
            if sprite != from_sprite:
                perimeter: List[Dict[str, int]] = self.__get_perimeter(sprite, optimized_perimeter, sprites)
                has_bumped, from_side_bumped = \
                        self.__points_collision(from_perimeter, perimeter)
                if has_bumped:
                    sprite.bumped(from_side_bumped)
                    return from_side_bumped
        return None

    def add_score(self, add_score: int) -> None:
        """
        This method is used by a sprite to inform the scor that points need to be added or removed
        TODO: This method should be moved in a separate class as it is breaking the SRP principle
        """
        self.score.increase_score(add_score)
