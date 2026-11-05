import pytest
from random import seed
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from flappy_bat.game.bat import Bat
from flappy_bat.game.towers import Towers
from flappy_bat.constants import SCREEN_WIDTH, SCREEN_HEIGHT, ACCEL_SCALE


class MockNetwork:
    def __init__(self, output=0.0):
        self.output = output

    def return_network_solution(self, inputs):
        return [self.output]


class TestBatInit:
    def test_initial_y_position(self):
        bat = Bat(MockNetwork())
        assert bat.y == 500

    def test_initial_x_position(self):
        bat = Bat(MockNetwork())
        assert bat.x == 60

    def test_initial_physics_zero(self):
        bat = Bat(MockNetwork())
        assert bat.speed == 0
        assert bat.acceleration == 0

    def test_images_not_loaded_at_init(self):
        bat = Bat(MockNetwork())
        assert bat._images_loaded is False
        assert bat.bat1 is None

    def test_default_hitbox_matches_sprite(self):
        bat = Bat(MockNetwork())
        assert bat.width == 31
        assert bat.height == 28

    def test_network_stored(self):
        net = MockNetwork()
        bat = Bat(net)
        assert bat.network is net


class TestBatCheckImpact:
    def setup_method(self):
        seed(0)
        self.tower = Towers(SCREEN_WIDTH, SCREEN_HEIGHT, 0)
        self.bat = Bat(MockNetwork())

    def test_floor_collision(self):
        self.bat.y = SCREEN_HEIGHT + 1
        assert self.bat.check_impact(self.tower, SCREEN_HEIGHT) is True

    def test_at_floor_boundary_no_collision(self):
        # check_impact uses strict y > height, so y == height is NOT a hit
        self.bat.y = SCREEN_HEIGHT
        assert self.bat.check_impact(self.tower, SCREEN_HEIGHT) is False

    def test_ceiling_collision(self):
        self.bat.y = -1
        assert self.bat.check_impact(self.tower, SCREEN_HEIGHT) is True

    def test_no_collision_tower_far_right(self):
        # Move tower far off-screen to the right so there is no x overlap
        for _ in range(50):
            self.tower.move_backwards()
        self.bat.y = SCREEN_HEIGHT // 2
        assert self.bat.check_impact(self.tower, SCREEN_HEIGHT) is False

    def test_lower_tower_collision(self):
        # Bat positioned at the lower tower face with x overlap
        self.bat.x = self.tower.position_lower[0]
        self.bat.y = self.tower.position_lower[1] - 1
        assert self.bat.check_impact(self.tower, SCREEN_HEIGHT) is True

    def test_upper_tower_collision(self):
        # Bat positioned just below the bottom of the upper tower with x overlap
        upper_bottom = self.tower.position_upper[1] + self.tower.upper_size[1]
        self.bat.x = self.tower.position_lower[0]
        self.bat.y = upper_bottom - self.bat.height
        assert self.bat.check_impact(self.tower, SCREEN_HEIGHT) is True

    def test_no_collision_in_gap(self):
        # Bat in the middle of the gap, tower off to the right
        for _ in range(50):
            self.tower.move_backwards()
        gap_mid = self.tower.lower_boundary - self.tower.hole_between_towers // 2
        self.bat.y = gap_mid
        assert self.bat.check_impact(self.tower, SCREEN_HEIGHT) is False


class TestBatMoveBat:
    def setup_method(self):
        seed(0)
        self.tower = Towers(SCREEN_WIDTH, SCREEN_HEIGHT, 0)

    def test_zero_output_no_movement(self):
        bat = Bat(MockNetwork(output=0.0))
        y_before = bat.y
        bat.move_bat(self.tower, SCREEN_HEIGHT)
        assert bat.y == y_before
        assert bat.speed == 0
        assert bat.acceleration == 0

    def test_positive_output_increases_acceleration(self):
        bat = Bat(MockNetwork(output=1.0))
        bat.move_bat(self.tower, SCREEN_HEIGHT)
        assert bat.acceleration == pytest.approx(ACCEL_SCALE)

    def test_negative_output_decreases_acceleration(self):
        bat = Bat(MockNetwork(output=-1.0))
        bat.move_bat(self.tower, SCREEN_HEIGHT)
        assert bat.acceleration == pytest.approx(-ACCEL_SCALE)

    def test_acceleration_accumulates_over_frames(self):
        bat = Bat(MockNetwork(output=1.0))
        bat.move_bat(self.tower, SCREEN_HEIGHT)
        bat.move_bat(self.tower, SCREEN_HEIGHT)
        assert bat.acceleration == pytest.approx(2 * ACCEL_SCALE)

    def test_speed_increases_with_positive_acceleration(self):
        bat = Bat(MockNetwork(output=1.0))
        bat.move_bat(self.tower, SCREEN_HEIGHT)
        assert bat.speed > 0

    def test_bat_moves_down_with_sustained_positive_output(self):
        bat = Bat(MockNetwork(output=1.0))
        y_before = bat.y
        for _ in range(10):
            bat.move_bat(self.tower, SCREEN_HEIGHT)
        assert bat.y > y_before

    def test_bat_moves_up_with_sustained_negative_output(self):
        bat = Bat(MockNetwork(output=-1.0))
        y_before = bat.y
        for _ in range(10):
            bat.move_bat(self.tower, SCREEN_HEIGHT)
        assert bat.y < y_before
