import pygame
from random import randint, seed
import NEMT as et


#Welcome to my self-written topologically evolving AI algorithm program!


# In this project, I built a learning algorithm to play the game.
# It's a neural network with a capacity to evolve new hidden nodes and connections.
# The network is represented as a table.
# The network calculates the values recursively. How fun!

# The reasoning behind this project was to learn how to build a neural network from scratch and from first principles.
# The one difference between the Flappy Bird and Flappy Bat games is that the AI controls the acceleration of the bat, rather than making it jump.
# This added an extra challenge for the AI, as jump algorithms are relatively easy to find.

#Features:
#  1. A flappy bat game that only an AI can play.
#  2. An AI to play the game.

#Performance:
#  Depending on your luck you can find a solution to the problem in less than 100 generations
#  However, the performance varies wildly. Sometimes you don't even get a minimum viable candidate for 100 generations.
#  Still fun to look at.

# --- Game constants ---
SCREEN_WIDTH     = 1000
SCREEN_HEIGHT    = 800
TOWER_WIDTH      = 50
TOWER_MOVE_SPEED = 3
TOWER_SPACING    = 200
TOWER_GAP_MAX    = 325
TOWER_GAP_MIN    = 135
TOWER_BOUNDARY   = 30
ACCEL_SCALE      = 0.025
POPULATION_SIZE  = 500
STAGNATION_LIMIT = 10
MIN_VIABLE_SCORE = 8


class Towers:
    def __init__(self, x: int, y: int, reducer: int) -> None:
        #Reducer will grow as the game goes on to make the gaps between towers smaller
        self.hole_between_towers = TOWER_GAP_MAX - reducer // 25
        if self.hole_between_towers < TOWER_GAP_MIN:
            self.hole_between_towers = TOWER_GAP_MIN

        self.lower_boundary = randint(self.hole_between_towers + TOWER_BOUNDARY, y - TOWER_BOUNDARY)
        self.color = 107, 81, 79

        #Position of the floortower
        self.position_lower = x - 5, self.lower_boundary
        self.position_upper = self.position_lower[0], -10

        #Define sizes for draw function
        self.lower_size = TOWER_WIDTH, y - self.lower_boundary + 5
        self.upper_size = TOWER_WIDTH, self.lower_boundary - self.hole_between_towers + 5

        #Define the border sizes and positions. These serve as the black borders of the towers
        self.lower_boarder_position = self.position_lower[0] - 5, self.position_lower[1] - 5
        self.lower_boarder_size = self.lower_size[0] + 10, self.lower_size[1] + 10
        self.upper_boarder_position = self.position_upper[0] - 5, self.position_upper[1] - 5
        self.upper_boarder_size = self.upper_size[0] + 10, self.upper_size[1] + 10

    #Getter functions to get values required by drawing and impact_checking functions
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

    #Move functions to move the towers around.
    def move(self) -> None:
        self.lower_boarder_position = self.lower_boarder_position[0] - TOWER_MOVE_SPEED, self.lower_boarder_position[1]
        self.upper_boarder_position = self.upper_boarder_position[0] - TOWER_MOVE_SPEED, self.upper_boarder_position[1]
        self.position_lower = self.position_lower[0] - TOWER_MOVE_SPEED, self.position_lower[1]
        self.position_upper = self.position_upper[0] - TOWER_MOVE_SPEED, self.position_upper[1]
    def move_backwards(self) -> None:
        self.lower_boarder_position = self.lower_boarder_position[0] + TOWER_SPACING, self.lower_boarder_position[1]
        self.upper_boarder_position = self.upper_boarder_position[0] + TOWER_SPACING, self.upper_boarder_position[1]
        self.position_lower = self.position_lower[0] + TOWER_SPACING, self.position_lower[1]
        self.position_upper = self.position_upper[0] + TOWER_SPACING, self.position_upper[1]
    def move_half(self, move_value: float) -> None:
        move_value = (move_value + 50) / 3
        self.lower_boarder_position = self.lower_boarder_position[0] - move_value, self.lower_boarder_position[1]
        self.upper_boarder_position = self.upper_boarder_position[0] - move_value, self.upper_boarder_position[1]
        self.position_lower = self.position_lower[0] - move_value, self.position_lower[1]
        self.position_upper = self.position_upper[0] - move_value, self.position_upper[1]


class Bat:
    def __init__(self, network: et.Network) -> None:
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
                self.bat1 = pygame.image.load("flap1.png")
                self.bat2 = pygame.image.load("flap2.png")
            else:
                self.bat1 = pygame.image.load("flap2.png")
                self.bat2 = pygame.image.load("flap1.png")
            self.height = self.bat1.get_height() - 10
            self.width  = self.bat1.get_width()
            self._images_loaded = True

    def move_bat(self, tower: Towers, size: int) -> None:
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

    def check_impact(self, tower: Towers, height: int) -> bool:
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


def _show_loading_screen(screen: pygame.Surface, generation: int) -> None:
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("Times New Roman", 24)
    text = font.render(
        f"Finding minimum viable network. Generation: {generation}. This can take up to 40-100 generations",
        True, (255, 255, 255)
    )
    screen.blit(text, (25, 25))
    text = font.render(
        "Each generation has 1000 networks. The min viable network prevents local maximum 'stuckness'",
        True, (255, 255, 255)
    )
    screen.blit(text, (25, 60))
    pygame.display.flip()


def _draw_frame(screen: pygame.Surface, towers: list[Towers], bats: list[Bat], best_score: float, generation: int, score: int) -> None:
    screen.fill((100, 100, 100))
    for tower in towers:
        pygame.draw.rect(screen, (0, 0, 0), tower.get_upper_boarder_sizepos(), border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), tower.get_lower_boarder_sizepos(), border_radius=10)
        pygame.draw.rect(screen, tower.get_color(), tower.get_lower_sizepos(), border_radius=10)
        pygame.draw.rect(screen, tower.get_color(), tower.get_upper_sizepos(), border_radius=10)
    for bat in bats:
        bat._load_images()
        screen.blit(bat.bat1, (bat.x, bat.y))
    font = pygame.font.SysFont("Times New Roman", 24)
    text  = font.render(f"{len(bats)} Bats alive. Current Score: {score} Generation: {generation}", True, (255, 255, 255))
    text2 = font.render(f"Best_score: {'%.2f' % best_score} Hole_between_towers: {towers[0].hole_between_towers}", True, (255, 255, 255))
    screen.blit(text,  (25, 25))
    screen.blit(text2, (25, 50))


def run_simulation(bats_to_run: list[Bat], best_score: float, generation: int, *, display: bool) -> list[tuple[Bat, float]]:
    #Seed is set to 1 because it produces a hard obstacle in the beginning of the course.
    #Better to find one network that can actually react to obstacles than randomly easy ones
    #which you can get through just by staying still.
    seed(1)
    reducer = 0

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    tickrate = 0

    if not display:
        _show_loading_screen(screen, generation)

    #Define towers and adjust the positions for the start
    towers = [Towers(SCREEN_WIDTH, SCREEN_HEIGHT, reducer) for _ in range(3)]
    for i in range(len(towers)):
        for j in range(i):
            towers[i].move_half(SCREEN_WIDTH)
    for tower in towers:
        tower.move_backwards()
    towers = towers[::-1]

    removed_bats = []
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if display and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    tickrate = 60
                if event.key == pygame.K_c:
                    tickrate = 0

        reducer += 1
        bat_remover_helper_list = []
        deletion_value = None

        if len(bats_to_run) == 0:
            return removed_bats

        #Move towers; track which one passed the left edge
        for tower in towers:
            tower.move()
            if tower.check_if_tower_passed():
                deletion_value = tower
                towers.append(Towers(SCREEN_WIDTH, SCREEN_HEIGHT, reducer))

        if deletion_value is not None:
            towers.remove(deletion_value)
            score += 1

        #Move each bat and collect any that hit something
        for bat in bats_to_run:
            bat.move_bat(towers[0], SCREEN_HEIGHT)
            if bat.check_impact(towers[0], SCREEN_HEIGHT):
                if bat not in bat_remover_helper_list:
                    bat_remover_helper_list.append(bat)

        #Score and remove dead bats
        for bat in bat_remover_helper_list:
            bats_to_run.remove(bat)
            mistake_value = abs((towers[0].lower_boundary * 2 - towers[0].hole_between_towers) / 2 - bat.y) / SCREEN_HEIGHT
            removed_bats.append((bat, score - mistake_value))

        if display:
            _draw_frame(screen, towers, bats_to_run, best_score, generation, score)
            pygame.display.flip()
            clock.tick(tickrate)


def main():
    best_score = 0
    best_bat_network = False
    evolution_object = et.Evolution()
    minimum_viable_network_found = False

    bat_list = [Bat(network) for network in evolution_object.create_new_networks(5, 1, number_of_networks=POPULATION_SIZE * 2)]
    counter = 0
    reset_value = STAGNATION_LIMIT

    while True:
        counter += 1
        results_of_simulation = run_simulation(
            bat_list, best_score, counter,
            display=minimum_viable_network_found
        )

        results_of_simulation.sort(reverse=True, key=lambda x: x[1])

        #Reset seed so network evolution works. Seed is set to 1 in the actual game to shape the obstacle course.
        seed()

        #If no bat scored above the threshold, generate a fresh population and try again
        if results_of_simulation[0][1] < MIN_VIABLE_SCORE:
            bat_list = [Bat(network) for network in evolution_object.create_new_networks(5, 1, number_of_networks=POPULATION_SIZE * 2)]
        else:
            minimum_viable_network_found = True

            if not best_bat_network:
                best_bat_network = results_of_simulation[0][0].network
                best_score = results_of_simulation[0][1]
            elif results_of_simulation[0][1] > best_score:
                best_bat_network = results_of_simulation[0][0].network
                best_score = results_of_simulation[0][1]
            else:
                reset_value -= 1

            #Best two bats are either the top two from this round, or the carry-over best and this round's best
            if results_of_simulation[0][0].network == best_bat_network:
                second_best_bat_network = results_of_simulation[1][0].network
            else:
                second_best_bat_network = results_of_simulation[0][0].network

            #Breed next generation from the two best networks
            evolved_bats  = evolution_object.evolve_networks(best_bat_network,        amount_of_networks=POPULATION_SIZE // 4)
            evolved_bats += evolution_object.evolve_networks(best_bat_network,        complexity=0, amount_of_networks=POPULATION_SIZE // 4)
            evolved_bats += evolution_object.evolve_networks(second_best_bat_network, amount_of_networks=POPULATION_SIZE // 4)
            evolved_bats += evolution_object.evolve_networks(second_best_bat_network, complexity=0, amount_of_networks=POPULATION_SIZE // 4)

            bat_list  = [Bat(best_bat_network), Bat(second_best_bat_network)]
            bat_list += [Bat(network) for network in evolved_bats]

            if reset_value == 0:
                print("Stagnated, resetting the search")
                best_bat_network = False
                minimum_viable_network_found = False
                best_score = 0
                reset_value = STAGNATION_LIMIT
                counter = 0
                bat_list = [Bat(et.Network(5, 1, [])) for _ in range(POPULATION_SIZE * 2)]


if __name__ == "__main__":
    main()
