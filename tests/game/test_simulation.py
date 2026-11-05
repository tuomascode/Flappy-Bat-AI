import random

import pytest

from flappy_bat.game.simulation import _reset_search, _initial_bat_list, run_simulation
from flappy_bat.game.bat import Bat
from flappy_bat.game.evaluation import quick_score
from flappy_bat.network.network import Network
from flappy_bat.network.evolution import Evolution
from flappy_bat.constants import STAGNATION_LIMIT, POPULATION_SIZE


def _fresh_bats(count: int, seed: int = 42) -> list[Bat]:
    random.seed(seed)
    nets = Evolution().create_new_networks(5, 1, number_of_networks=count)
    return [Bat(n) for n in nets]


def _copy_bats(nets: list[Network]) -> list[Bat]:
    return [Bat(Network(n.begins[-1] + 1, len(n.ends), n.network_table)) for n in nets]


class TestResetSearch:
    def test_returns_none_for_best_network(self):
        best_bat_network, *_ = _reset_search()
        assert best_bat_network is None

    def test_best_score_reset_to_zero(self):
        _, best_score, *_ = _reset_search()
        assert best_score == 0

    def test_reset_value_restored_to_stagnation_limit(self):
        _, _, reset_value, *_ = _reset_search()
        assert reset_value == STAGNATION_LIMIT

    def test_counter_reset_to_zero(self):
        _, _, _, counter, *_ = _reset_search()
        assert counter == 0


class TestInitialBatList:
    def test_returns_requested_count(self):
        assert len(_initial_bat_list(3)) == 3

    def test_contains_bat_instances(self):
        assert all(isinstance(b, Bat) for b in _initial_bat_list(3))

    def test_all_networks_pass_quick_score(self):
        assert all(quick_score(b.network) for b in _initial_bat_list(3))


class TestRunSimulation:
    def test_returns_list(self):
        results = run_simulation(_fresh_bats(3), 0, 1, display=False)
        assert isinstance(results, list)

    def test_all_bats_scored(self):
        results = run_simulation(_fresh_bats(5), 0, 1, display=False)
        assert len(results) == 5

    def test_each_result_is_bat_float_tuple(self):
        results = run_simulation(_fresh_bats(4), 0, 1, display=False)
        for bat, score in results:
            assert isinstance(bat, Bat)
            assert isinstance(score, float)

    def test_input_list_emptied_after_run(self):
        bats = _fresh_bats(4)
        run_simulation(bats, 0, 1, display=False)
        assert len(bats) == 0

    def test_empty_population_returns_immediately(self):
        results = run_simulation([], 0, 1, display=False)
        assert results == []

    def test_results_deterministic_across_runs(self):
        # run_simulation seeds to 1 internally, so identical networks
        # always produce identical scores regardless of external random state
        random.seed(99)
        nets = Evolution().create_new_networks(5, 1, number_of_networks=4)
        scores_a = [
            s for _, s in run_simulation([Bat(n) for n in nets], 0, 1, display=False)
        ]
        scores_b = [s for _, s in run_simulation(_copy_bats(nets), 0, 1, display=False)]
        assert scores_a == scores_b

    def test_generation_does_not_affect_scores(self):
        random.seed(77)
        nets = Evolution().create_new_networks(5, 1, number_of_networks=3)
        scores_1 = [
            s for _, s in run_simulation([Bat(n) for n in nets], 0, 1, display=False)
        ]
        scores_5 = [
            s for _, s in run_simulation(_copy_bats(nets), 0, 50, display=False)
        ]
        assert scores_1 == scores_5

    def test_best_score_param_does_not_affect_scores(self):
        random.seed(55)
        nets = Evolution().create_new_networks(5, 1, number_of_networks=3)
        scores_low = [
            s for _, s in run_simulation([Bat(n) for n in nets], 0, 1, display=False)
        ]
        scores_high = [
            s for _, s in run_simulation(_copy_bats(nets), 999, 1, display=False)
        ]
        assert scores_low == scores_high
