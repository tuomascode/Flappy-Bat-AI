import pytest
from random import seed
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from flappy_bat.game.towers import Towers
from flappy_bat.constants import SCREEN_WIDTH, SCREEN_HEIGHT

SCREEN_X = 1000
SCREEN_Y = 800


class TestTowersInit:
    def test_hole_size_no_reducer(self):
        seed(0)
        t = Towers(SCREEN_X, SCREEN_Y, 0)
        assert t.hole_between_towers == 325

    def test_hole_size_decreases_with_reducer(self):
        seed(0)
        t_small = Towers(SCREEN_X, SCREEN_Y, 500)
        assert t_small.hole_between_towers < 325

    def test_hole_size_clamped_at_minimum(self):
        seed(0)
        t = Towers(SCREEN_X, SCREEN_Y, 100000)
        assert t.hole_between_towers == 135

    def test_hole_size_formula(self):
        from flappy_bat.constants import TOWER_DIFFICULTY_RATE
        seed(0)
        reducer = 200
        t = Towers(SCREEN_X, SCREEN_Y, reducer)
        assert t.hole_between_towers == 325 - reducer // TOWER_DIFFICULTY_RATE

    def test_lower_boundary_within_screen(self):
        for i in range(10):
            seed(i)
            t = Towers(SCREEN_X, SCREEN_Y, 0)
            assert 0 < t.lower_boundary < SCREEN_Y

    def test_color_is_correct(self):
        seed(0)
        t = Towers(SCREEN_X, SCREEN_Y, 0)
        assert t.color == (107, 81, 79)

    def test_position_lower_x_near_right_edge(self):
        seed(0)
        t = Towers(SCREEN_X, SCREEN_Y, 0)
        # position_lower[0] = x - 5 = 995
        assert t.position_lower[0] == SCREEN_X - 5

    def test_position_upper_starts_at_top(self):
        seed(0)
        t = Towers(SCREEN_X, SCREEN_Y, 0)
        # upper tower starts above screen
        assert t.position_upper[1] == -10


class TestTowerGetters:
    def setup_method(self):
        seed(0)
        self.tower = Towers(SCREEN_X, SCREEN_Y, 0)

    def test_get_lower_sizepos_shape(self):
        pos, size = self.tower.get_lower_sizepos()
        assert len(pos) == 2
        assert len(size) == 2

    def test_get_upper_sizepos_shape(self):
        pos, size = self.tower.get_upper_sizepos()
        assert len(pos) == 2
        assert len(size) == 2

    def test_get_lower_boarder_sizepos_shape(self):
        pos, size = self.tower.get_lower_boarder_sizepos()
        assert len(pos) == 2
        assert len(size) == 2

    def test_get_upper_boarder_sizepos_shape(self):
        pos, size = self.tower.get_upper_boarder_sizepos()
        assert len(pos) == 2
        assert len(size) == 2

    def test_get_color(self):
        assert self.tower.get_color() == (107, 81, 79)

    def test_lower_size_positive(self):
        _, size = self.tower.get_lower_sizepos()
        assert size[0] > 0
        assert size[1] > 0

    def test_upper_size_positive(self):
        _, size = self.tower.get_upper_sizepos()
        assert size[0] > 0
        assert size[1] > 0

    def test_boarder_larger_than_tower(self):
        _, lower_size = self.tower.get_lower_sizepos()
        _, lower_boarder_size = self.tower.get_lower_boarder_sizepos()
        assert lower_boarder_size[0] > lower_size[0]
        assert lower_boarder_size[1] > lower_size[1]


class TestTowerMovement:
    def setup_method(self):
        seed(0)
        self.tower = Towers(SCREEN_X, SCREEN_Y, 0)

    def test_move_decreases_x_by_3(self):
        x_before = self.tower.position_lower[0]
        self.tower.move()
        assert self.tower.position_lower[0] == x_before - 3

    def test_move_does_not_change_y(self):
        y_before = self.tower.position_lower[1]
        self.tower.move()
        assert self.tower.position_lower[1] == y_before

    def test_move_updates_upper_tower_x(self):
        x_before = self.tower.position_upper[0]
        self.tower.move()
        assert self.tower.position_upper[0] == x_before - 3

    def test_move_updates_boarders(self):
        lower_x_before = self.tower.lower_boarder_position[0]
        upper_x_before = self.tower.upper_boarder_position[0]
        self.tower.move()
        assert self.tower.lower_boarder_position[0] == lower_x_before - 3
        assert self.tower.upper_boarder_position[0] == upper_x_before - 3

    def test_multiple_moves_accumulate(self):
        x_before = self.tower.position_lower[0]
        for _ in range(5):
            self.tower.move()
        assert self.tower.position_lower[0] == x_before - 15

    def test_move_backwards_increases_x_by_200(self):
        x_before = self.tower.position_lower[0]
        self.tower.move_backwards()
        assert self.tower.position_lower[0] == x_before + 200

    def test_move_backwards_updates_all_positions(self):
        lower_x_before = self.tower.lower_boarder_position[0]
        upper_x_before = self.tower.upper_boarder_position[0]
        self.tower.move_backwards()
        assert self.tower.lower_boarder_position[0] == lower_x_before + 200
        assert self.tower.upper_boarder_position[0] == upper_x_before + 200

    def test_move_half_decreases_x(self):
        x_before = self.tower.position_lower[0]
        self.tower.move_half(SCREEN_X)
        assert self.tower.position_lower[0] < x_before

    def test_move_half_does_not_change_y(self):
        y_before = self.tower.position_lower[1]
        self.tower.move_half(SCREEN_X)
        assert self.tower.position_lower[1] == y_before


class TestTowerPassed:
    def test_not_passed_at_creation(self):
        seed(0)
        t = Towers(SCREEN_X, SCREEN_Y, 0)
        assert t.check_if_tower_passed() is False

    def test_passed_after_enough_moves(self):
        seed(0)
        t = Towers(SCREEN_X, SCREEN_Y, 0)
        # Initial x = 995; needs to drop below -50 — takes ceil((995+50)/3) = 349 moves
        for _ in range(400):
            t.move()
        assert t.check_if_tower_passed() is True

    def test_boundary_condition_consistent(self):
        seed(0)
        t = Towers(SCREEN_X, SCREEN_Y, 0)
        for _ in range(400):
            t.move()
        # check_if_tower_passed should match the actual x position
        assert t.check_if_tower_passed() == (t.position_lower[0] < -50)
