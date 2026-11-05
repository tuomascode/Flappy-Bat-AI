from __future__ import annotations

from random import randint

import pygame

from flappy_bat.constants import ACCEL_SCALE, ASSETS_DIR
from flappy_bat.network.network import Network


class Bat:
    def __init__(self, network: Network) -> None:
        self._images_loaded = False
        self.bat1 = None
        self.bat2 = None
        self.height = 28   # sprite height - 10; overridden by _load_images
        self.width  = 31   # sprite width; overridden by _load_images
        self.speed = 0
        self.y = 500
        self.x = 60
        self.network = network
        self.acceleration = 0

    def _load_images(self) -> None:
        if not self._images_loaded:
            if randint(0, 1) == 1:
                self.bat1 = pygame.image.load(str(ASSETS_DIR / "flap1.png"))
                self.bat2 = pygame.image.load(str(ASSETS_DIR / "flap2.png"))
            else:
                self.bat1 = pygame.image.load(str(ASSETS_DIR / "flap2.png"))
                self.bat2 = pygame.image.load(str(ASSETS_DIR / "flap1.png"))
            self.height = self.bat1.get_height() - 10
            self.width  = self.bat1.get_width()
            self._images_loaded = True

    def move_bat(self, tower: "Towers", size: int) -> None:  # type: ignore[name-defined]
        #The network gets the relative values for positions rather than absolute values. Seems to ease the work of the network

        #Solve relative positions of towers
        lower_relative_tower_position = (tower.lower_boundary - self.height) / size * 2 - 1
        upper_relative_tower_position = (tower.lower_boundary - tower.hole_between_towers) / size * 2 - 1

        #Solve relative position of bat
        relative_bat_location = self.y / size * 2 - 1

        #Give the network some values to solve. Values are tower positions, bat position, speed and acceleration * 10
        network_output = self.network.return_network_solution([relative_bat_location, lower_relative_tower_position, upper_relative_tower_position, self.speed, self.acceleration * 10])

        self.acceleration += network_output[0] * ACCEL_SCALE
        self.speed += self.acceleration
        self.y += self.speed

    def check_impact(self, tower: "Towers", height: int) -> bool:  # type: ignore[name-defined]
        #Check if the bat collides with a tower

        #Check floor and ceiling
        if self.y > height or self.y < 0:
            return True
        #Check contact with towers
        if tower.position_lower[0] < self.x + self.width:
            if tower.position_lower[0] + tower.lower_size[0] > self.x:
                if tower.position_upper[1] + tower.upper_size[1] > self.y:
                    return True
                if tower.position_lower[1] < self.y + self.height:
                    return True
        return False
