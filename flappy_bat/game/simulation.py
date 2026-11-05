from random import seed, choice

import pygame

from flappy_bat.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ACCEL_SCALE,
    POPULATION_SIZE,
    STAGNATION_LIMIT,
)
from flappy_bat.network.network import Network
from flappy_bat.network.evolution import Evolution
from flappy_bat.game.towers import Towers
from flappy_bat.game.bat import Bat
from flappy_bat.game.display import _draw_frame
from flappy_bat.game.evaluation import quick_score

_ADAPTIVE_HIGH_BATS = 8    # above this: uncapped speed
_SLOW_TICKRATE = 90


def run_simulation(
    bats_to_run: list[Bat],
    best_score: float,
    generation: int,
    *,
    display: bool,
    featured_network: Network | None = None,
) -> list[tuple[Bat, float]]:
    # Seed is set to 1 because it produces a hard obstacle in the beginning of the course.
    # Better to find one network that can actually react to obstacles than randomly easy ones
    # which you can get through just by staying still.
    seed(1)
    reducer = 0

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    tickrate = 0
    adaptive = True

    # Define towers and adjust the positions for the start
    towers = [Towers(SCREEN_WIDTH, SCREEN_HEIGHT, reducer) for _ in range(3)]
    for i in range(len(towers)):
        for j in range(i):
            towers[i].move_half(SCREEN_WIDTH)
    for tower in towers:
        tower.move_backwards()
    towers = towers[::-1]

    removed_bats = []
    score = 0

    # Pick the bat to track for the output arrow
    if display:
        tracked_bat: Bat | None = next(
            (b for b in bats_to_run if b.network is featured_network), None
        ) if featured_network is not None else None
        if tracked_bat is None and bats_to_run:
            tracked_bat = choice(bats_to_run)
    else:
        tracked_bat = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if display and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    adaptive = False
                    tickrate = _SLOW_TICKRATE
                if event.key == pygame.K_z:
                    adaptive = False
                    tickrate = 0
                if event.key == pygame.K_c:
                    adaptive = True

        reducer += 1
        bat_remover_helper_list = []
        deletion_value = None

        if len(bats_to_run) == 0:
            return removed_bats

        # Move towers; track which one passed the left edge
        for tower in towers:
            tower.move()
            if tower.check_if_tower_passed():
                deletion_value = tower
                towers.append(Towers(SCREEN_WIDTH, SCREEN_HEIGHT, reducer))

        if deletion_value is not None:
            towers.remove(deletion_value)
            score += 1

        # Move each bat and collect any that hit something
        for bat in bats_to_run:
            bat.move_bat(towers[0], SCREEN_HEIGHT)
            if bat.check_impact(towers[0], SCREEN_HEIGHT):
                if bat not in bat_remover_helper_list:
                    bat_remover_helper_list.append(bat)

        # Score and remove dead bats
        for bat in bat_remover_helper_list:
            bats_to_run.remove(bat)
            mistake_value = (
                abs(
                    (towers[0].lower_boundary * 2 - towers[0].hole_between_towers) / 2
                    - bat.y
                )
                / SCREEN_HEIGHT
            )
            removed_bats.append((bat, score - mistake_value))

        if display:
            if adaptive:
                n = len(bats_to_run)
                if n > _ADAPTIVE_HIGH_BATS:
                    tickrate = 0
                else:
                    tickrate = _SLOW_TICKRATE
            if tracked_bat not in bats_to_run:
                tracked_bat = choice(bats_to_run) if bats_to_run else None
            _draw_frame(screen, towers, bats_to_run, best_score, generation, score, tracked_bat, tickrate)
            pygame.display.flip()
            clock.tick(tickrate)


def _initial_bat_list(n: int) -> list[Bat]:
    """Return n Bats whose networks each pass quick_score."""
    bats: list[Bat] = []
    tested = 0
    last_logged = 0
    while len(bats) < n:
        network = Network(5, 1, [])
        tested += 1
        if quick_score(network):
            bats.append(Bat(network))
        if len(bats) - last_logged >= max(1, n // 10):
            print(f"  Initial search: {len(bats)}/{n} viable (tested {tested}, pass rate {len(bats)/tested:.1%})")
            last_logged = len(bats)
    print(f"  Initial search done: {n}/{n} viable found after testing {tested} networks (pass rate {n/tested:.1%})")
    return bats


def _reset_search() -> tuple[None, float, int, int, list[Bat]]:
    print("Stagnated, resetting the search")
    return (None, 0.0, STAGNATION_LIMIT, 0, _initial_bat_list(POPULATION_SIZE))


def main() -> None:
    best_score = 0.0
    best_bat_network = None
    evolution_object = Evolution()

    bat_list = _initial_bat_list(POPULATION_SIZE)
    counter = 0
    reset_value = STAGNATION_LIMIT

    while True:
        counter += 1
        results_of_simulation = run_simulation(
            bat_list, best_score, counter, display=True, featured_network=best_bat_network
        )
        results_of_simulation.sort(reverse=True, key=lambda x: x[1])

        # Reset seed so network evolution works. Seed is set to 1 in the actual game to shape the obstacle course.
        seed()

        if best_bat_network is None or results_of_simulation[0][1] > best_score:
            best_bat_network = results_of_simulation[0][0].network
            best_score = results_of_simulation[0][1]
        else:
            reset_value -= 1

        # Best two bats are either the top two from this round, or the carry-over best and this round's best
        if results_of_simulation[0][0].network == best_bat_network:
            second_best_bat_network = results_of_simulation[1][0].network
        else:
            second_best_bat_network = results_of_simulation[0][0].network

        # Breed next generation from the two best networks
        evolved_bats = evolution_object.evolve_networks(
            best_bat_network, amount_of_networks=POPULATION_SIZE // 4
        )
        evolved_bats += evolution_object.evolve_networks(
            best_bat_network, complexity=0, amount_of_networks=POPULATION_SIZE // 4
        )
        evolved_bats += evolution_object.evolve_networks(
            second_best_bat_network, amount_of_networks=POPULATION_SIZE // 4
        )
        evolved_bats += evolution_object.evolve_networks(
            second_best_bat_network,
            complexity=0,
            amount_of_networks=POPULATION_SIZE // 4,
        )

        bat_list = [Bat(best_bat_network), Bat(second_best_bat_network)]
        bat_list += [Bat(network) for network in evolved_bats]

        if reset_value == 0:
            best_bat_network, best_score, reset_value, counter, bat_list = _reset_search()
