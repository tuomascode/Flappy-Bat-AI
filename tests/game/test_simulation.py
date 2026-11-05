import pytest

from flappy_bat.game.simulation import _reset_search
from flappy_bat.game.bat import Bat
from flappy_bat.constants import STAGNATION_LIMIT, POPULATION_SIZE


class TestResetSearch:
    def test_returns_none_for_best_network(self):
        best_bat_network, *_ = _reset_search()
        assert best_bat_network is None

    def test_minimum_viable_is_false(self):
        _, minimum_viable, *_ = _reset_search()
        assert minimum_viable is False

    def test_best_score_reset_to_zero(self):
        _, _, best_score, *_ = _reset_search()
        assert best_score == 0

    def test_reset_value_restored_to_stagnation_limit(self):
        _, _, _, reset_value, *_ = _reset_search()
        assert reset_value == STAGNATION_LIMIT

    def test_counter_reset_to_zero(self):
        _, _, _, _, counter, *_ = _reset_search()
        assert counter == 0

    def test_bat_list_has_correct_size(self):
        _, _, _, _, _, bat_list = _reset_search()
        assert len(bat_list) == POPULATION_SIZE * 2

    def test_bat_list_contains_bat_instances(self):
        _, _, _, _, _, bat_list = _reset_search()
        assert all(isinstance(b, Bat) for b in bat_list)
