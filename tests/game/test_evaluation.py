import numpy as np
import pytest

from flappy_bat.network.network import Network
from flappy_bat.game.evaluation import (
    quick_score,
    _make_inputs,
    _CAP_Y,
    _NEAR_ZERO_THRESHOLD,
    _LOWER_BOUNDARY,
    _HOLE,
    _BAT_HEIGHT,
)
from flappy_bat.constants import SCREEN_HEIGHT


def _build_net(bat_pos_w: float, speed_w: float, bias: float = 0.0) -> Network:
    """Minimal 5→1 network with specific bat-position and speed weights."""
    net = Network(5, 1, [])
    net.network_table[:] = np.nan
    net.network_table[0][5] = bat_pos_w
    net.network_table[3][5] = speed_w
    net.network_table[5][5] = bias
    net._rebuild_node_graph()
    return net


class TestMakeInputs:
    def test_length(self):
        assert len(_make_inputs(400, 0.0)) == 5

    def test_bat_at_cap_relative_position(self):
        inputs = _make_inputs(_CAP_Y, 0.0)
        assert inputs[0] == pytest.approx(_CAP_Y / SCREEN_HEIGHT * 2 - 1)

    def test_speed_passed_through(self):
        assert _make_inputs(400, 3.5)[3] == pytest.approx(3.5)

    def test_accel_scaled_by_ten(self):
        assert _make_inputs(400, 0.0, accel=0.5)[4] == pytest.approx(5.0)

    def test_lower_boundary_normalised(self):
        expected = (_LOWER_BOUNDARY - _BAT_HEIGHT) / SCREEN_HEIGHT * 2 - 1
        assert _make_inputs(400, 0.0)[1] == pytest.approx(expected)

    def test_upper_boundary_normalised(self):
        expected = (_LOWER_BOUNDARY - _HOLE) / SCREEN_HEIGHT * 2 - 1
        assert _make_inputs(400, 0.0)[2] == pytest.approx(expected)


class TestQuickScore:
    def test_returns_bool(self):
        assert isinstance(quick_score(Network(5, 1, [])), bool)

    def test_correct_weights_pass(self):
        # bat_pos_w=-5: dominant position signal (above cap -> positive, below -> negative)
        # speed_w=-1: stabilises at cap without overwhelming position signal far from cap
        assert quick_score(_build_net(bat_pos_w=-5.0, speed_w=-1.0)) is True

    def test_inverted_bat_direction_fails(self):
        # Positive bat-position weight -> above cap -> negative output -> fails scenario 1
        assert quick_score(_build_net(bat_pos_w=5.0, speed_w=-1.0)) is False

    def test_inverted_speed_direction_fails(self):
        # Positive speed weight → at cap moving down → positive output → fails stabiliser
        assert quick_score(_build_net(bat_pos_w=-5.0, speed_w=5.0)) is False

    def test_zero_weights_fail(self):
        # All-zero weights → tanh(0) = 0 → all directional tests fail
        net = _build_net(bat_pos_w=0.0, speed_w=0.0, bias=0.0)
        assert quick_score(net) is False
