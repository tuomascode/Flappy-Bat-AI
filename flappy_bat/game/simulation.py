from random import seed

import pygame

from flappy_bat.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ACCEL_SCALE,
    POPULATION_SIZE,
    STAGNATION_LIMIT,
    MIN_VIABLE_SCORE,
)
from flappy_bat.network.network import Network
from flappy_bat.network.evolution import Evolution
from flappy_bat.game.towers import Towers
from flappy_bat.game.bat import Bat
from flappy_bat.game.display import _draw_frame


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
    evolution_object = Evolution()
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
                bat_list = [Bat(Network(5, 1, [])) for _ in range(POPULATION_SIZE * 2)]
