from random import seed
import datetime
import os
import subprocess

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
_RECORD_FPS = 60
_WIN_SCORE = 100
_GAUNTLET_START = 81      # first pillar with forced gap position


def _gauntlet_gap(label: int) -> str:
    if label < _GAUNTLET_START:
        return "random"
    return "top" if label % 2 == 1 else "bottom"


def _start_recorder(screen: pygame.Surface) -> subprocess.Popen | None:
    w, h = screen.get_size()
    filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    try:
        proc = subprocess.Popen(
            [
                "ffmpeg", "-y",
                "-f", "rawvideo", "-vcodec", "rawvideo",
                "-s", f"{w}x{h}", "-pix_fmt", "rgb24",
                "-r", str(_RECORD_FPS),
                "-i", "-",
                "-vcodec", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
                filename,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Recording → {filename}")
        return proc
    except FileNotFoundError:
        print("ffmpeg not found — recording unavailable")
        return None


def _write_frame(recorder: subprocess.Popen, screen: pygame.Surface) -> None:
    assert recorder.stdin is not None
    recorder.stdin.write(pygame.surfarray.array3d(screen).swapaxes(0, 1).tobytes())


def _stop_recorder(recorder: subprocess.Popen) -> None:
    assert recorder.stdin is not None
    recorder.stdin.close()
    recorder.wait()
    print("Recording saved")


def _compute_round_stats(removed_bats: list[tuple]) -> list[tuple[str, str]]:
    scores = sorted(s for _, s in removed_bats)
    n = len(scores)
    mean = sum(scores) / n
    median = scores[n // 2]
    top_quarter = scores[-(n // 4 or 1):]
    top_avg = sum(top_quarter) / len(top_quarter)
    cleared = sum(1 for s in scores if s >= 1.0)
    best_bat = max(removed_bats, key=lambda x: x[1])[0]
    complexity = best_bat.network.calculate_complexity()
    return [
        ("Round best",    f"{scores[-1] * 100:.2f}"),
        ("Mean",          f"{mean * 100:.2f}"),
        ("Median",        f"{median * 100:.2f}"),
        ("Top quarter",   f"{top_avg * 100:.2f}"),
        ("Cleared ≥1",    f"{cleared} / {n}"),
        ("Best complexity", str(complexity)),
    ]


def run_simulation(
    bats_to_run: list[Bat],
    best_score: float,
    generation: int,
    *,
    display: bool,
    featured_network: Network | None = None,
    prev_round_stats: list[tuple[str, str]] | None = None,
    auto_record: bool = False,
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
    adaptive = False
    recorder: subprocess.Popen | None = _start_recorder(screen) if auto_record else None

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
    won = False

    # Pick the bat to track for the output arrow
    if display:
        tracked_bat: Bat | None = next(
            (b for b in bats_to_run if b.network is featured_network), None
        ) if featured_network is not None else None
        if tracked_bat is None and bats_to_run:
            tracked_bat = bats_to_run[0]
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
                if event.key == pygame.K_r and not auto_record:
                    if recorder is None:
                        recorder = _start_recorder(screen)
                    else:
                        _stop_recorder(recorder)
                        recorder = None

        reducer += 1
        bat_remover_helper_list = []
        deletion_value = None

        if len(bats_to_run) == 0:
            if display:
                end_stats = _compute_round_stats(removed_bats)
                _draw_frame(screen, towers, bats_to_run, best_score, generation, score, tracked_bat, tickrate, end_stats=end_stats, recording=recorder is not None, win=won)
                pygame.display.flip()
                if recorder is not None:
                    _write_frame(recorder, screen)
                    _stop_recorder(recorder)
            return removed_bats


        # Move towers; track which one passed the left edge
        for tower in towers:
            tower.move()
            if tower.check_if_tower_passed():
                deletion_value = tower

        if deletion_value is not None:
            towers.remove(deletion_value)
            score += 1
            if score >= _WIN_SCORE:
                won = True
                for bat in bats_to_run:
                    removed_bats.append((bat, float(_WIN_SCORE) * 0.01))
                bats_to_run.clear()
            else:
                towers.append(Towers(SCREEN_WIDTH, SCREEN_HEIGHT, reducer, gap=_gauntlet_gap(score + 3)))

        # Move each bat and collect any that hit something
        for bat in bats_to_run:
            bat.move_bat(towers[0], towers[1], SCREEN_HEIGHT)
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
                * 0.009
            )
            removed_bats.append((bat, score * 0.01 - mistake_value))

        if display:
            if adaptive:
                n = len(bats_to_run)
                if n > _ADAPTIVE_HIGH_BATS:
                    tickrate = 0
                else:
                    tickrate = _SLOW_TICKRATE
            if tracked_bat not in bats_to_run:
                tracked_bat = bats_to_run[0] if bats_to_run else None
            _draw_frame(screen, towers, bats_to_run, best_score, generation, score, tracked_bat, tickrate, end_stats=prev_round_stats, recording=recorder is not None, win=won)
            pygame.display.flip()
            if recorder is not None:
                _write_frame(recorder, screen)
            clock.tick(tickrate)


def _initial_bat_list(n: int) -> list[Bat]:
    """Return n Bats whose networks each pass quick_score."""
    bats: list[Bat] = []
    tested = 0
    last_logged = 0
    while len(bats) < n:
        network = Network(7, 1, [])
        tested += 1
        if quick_score(network):
            bats.append(Bat(network))
        if len(bats) - last_logged >= max(1, n // 10):
            print(f"  Initial search: {len(bats)}/{n} viable (tested {tested}, pass rate {len(bats)/tested:.1%})")
            last_logged = len(bats)
    print(f"  Initial search done: {n}/{n} viable found after testing {tested} networks (pass rate {n/tested:.1%})")
    return bats


def _save_network(network: Network, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    network.write(path)
    print(f"Saved best network → {path}")


def _reset_search() -> tuple[None, float, int, int, list[Bat]]:
    print("Stagnated, resetting the search")
    return (None, 0.0, STAGNATION_LIMIT, 0, _initial_bat_list(POPULATION_SIZE))


def main(
    save_path: str | None = None,
    load_path: str | None = None,
    auto_record: bool = False,
) -> None:
    best_score = 0.0
    evolution_object = Evolution()

    if load_path is not None:
        print(f"Loading network from {load_path}")
        best_bat_network: Network | None = Network.read_and_return(load_path)
        evolved = evolution_object.evolve_networks(best_bat_network, amount_of_networks=POPULATION_SIZE // 2)
        evolved += evolution_object.evolve_networks(best_bat_network, complexity=0, amount_of_networks=POPULATION_SIZE // 2)
        bat_list = [Bat(best_bat_network)] + [Bat(n) for n in evolved]
    else:
        best_bat_network = None
        bat_list = _initial_bat_list(POPULATION_SIZE)

    counter = 0
    reset_value = STAGNATION_LIMIT
    prev_round_stats = None

    while True:
        counter += 1
        results_of_simulation = run_simulation(
            bat_list, best_score, counter, display=True, featured_network=best_bat_network,
            prev_round_stats=prev_round_stats, auto_record=auto_record,
        )
        prev_round_stats = _compute_round_stats(results_of_simulation)
        results_of_simulation.sort(reverse=True, key=lambda x: x[1])

        # Reset seed so network evolution works. Seed is set to 1 in the actual game to shape the obstacle course.
        seed()

        if best_bat_network is None or results_of_simulation[0][1] > best_score:
            best_bat_network = results_of_simulation[0][0].network
            best_score = results_of_simulation[0][1]
            if save_path is not None:
                _save_network(best_bat_network, save_path)
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
