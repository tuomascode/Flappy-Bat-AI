from random import randint

from flappy_bat.constants import (
    TOWER_WIDTH,
    TOWER_MOVE_SPEED,
    TOWER_SPACING,
    TOWER_GAP_MAX,
    TOWER_GAP_MIN,
    TOWER_BOUNDARY,
)


class Towers:
    def __init__(self, x: int, y: int, reducer: int) -> None:
        # Reducer will grow as the game goes on to make the gaps between towers smaller
        self.hole_between_towers = TOWER_GAP_MAX - reducer // 25
        if self.hole_between_towers < TOWER_GAP_MIN:
            self.hole_between_towers = TOWER_GAP_MIN

        self.lower_boundary = randint(
            self.hole_between_towers + TOWER_BOUNDARY, y - TOWER_BOUNDARY
        )
        self.color = 107, 81, 79

        # Position of the floortower
        self.position_lower = x - 5, self.lower_boundary
        self.position_upper = self.position_lower[0], -10

        # Define sizes for draw function
        self.lower_size = TOWER_WIDTH, y - self.lower_boundary + 5
        self.upper_size = (
            TOWER_WIDTH,
            self.lower_boundary - self.hole_between_towers + 5,
        )

        # Define the border sizes and positions. These serve as the black borders of the towers
        self.lower_boarder_position = (
            self.position_lower[0] - 5,
            self.position_lower[1] - 5,
        )
        self.lower_boarder_size = self.lower_size[0] + 10, self.lower_size[1] + 10
        self.upper_boarder_position = (
            self.position_upper[0] - 5,
            self.position_upper[1] - 5,
        )
        self.upper_boarder_size = self.upper_size[0] + 10, self.upper_size[1] + 10

    # Getter functions to get values required by drawing and impact_checking functions
    def get_upper_sizepos(self) -> tuple:
        return self.position_upper, self.upper_size

    def get_upper_boarder_sizepos(self) -> tuple:
        return self.upper_boarder_position, self.upper_boarder_size

    def get_lower_boarder_sizepos(self) -> tuple:
        return self.lower_boarder_position, self.lower_boarder_size

    def get_lower_sizepos(self) -> tuple:
        return self.position_lower, self.lower_size

    def get_color(self) -> tuple[int, int, int]:
        return self.color

    def check_if_tower_passed(self) -> bool:
        return self.position_lower[0] < -50

    # Move functions to move the towers around.
    def move(self) -> None:
        self.lower_boarder_position = (
            self.lower_boarder_position[0] - TOWER_MOVE_SPEED,
            self.lower_boarder_position[1],
        )
        self.upper_boarder_position = (
            self.upper_boarder_position[0] - TOWER_MOVE_SPEED,
            self.upper_boarder_position[1],
        )
        self.position_lower = (
            self.position_lower[0] - TOWER_MOVE_SPEED,
            self.position_lower[1],
        )
        self.position_upper = (
            self.position_upper[0] - TOWER_MOVE_SPEED,
            self.position_upper[1],
        )

    def move_backwards(self) -> None:
        self.lower_boarder_position = (
            self.lower_boarder_position[0] + TOWER_SPACING,
            self.lower_boarder_position[1],
        )
        self.upper_boarder_position = (
            self.upper_boarder_position[0] + TOWER_SPACING,
            self.upper_boarder_position[1],
        )
        self.position_lower = (
            self.position_lower[0] + TOWER_SPACING,
            self.position_lower[1],
        )
        self.position_upper = (
            self.position_upper[0] + TOWER_SPACING,
            self.position_upper[1],
        )

    def move_half(self, move_value: float) -> None:
        move_value = (move_value + 50) / 3
        self.lower_boarder_position = (
            self.lower_boarder_position[0] - move_value,
            self.lower_boarder_position[1],
        )
        self.upper_boarder_position = (
            self.upper_boarder_position[0] - move_value,
            self.upper_boarder_position[1],
        )
        self.position_lower = (
            self.position_lower[0] - move_value,
            self.position_lower[1],
        )
        self.position_upper = (
            self.position_upper[0] - move_value,
            self.position_upper[1],
        )
