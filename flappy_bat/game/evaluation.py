from flappy_bat.constants import SCREEN_HEIGHT
from flappy_bat.network.network import Network

_BAT_HEIGHT = 28
_LOWER_BOUNDARY = 500
_HOLE = 200
_CAP_Y = _LOWER_BOUNDARY - _HOLE // 2  # gap centre: y=400
_NEAR_ZERO_THRESHOLD = 0.5


def _make_inputs(bat_y: float, speed: float, accel: float = 0.0) -> list[float]:
    relative_bat = bat_y / SCREEN_HEIGHT * 2 - 1
    lower_rel = (_LOWER_BOUNDARY - _BAT_HEIGHT) / SCREEN_HEIGHT * 2 - 1
    upper_rel = (_LOWER_BOUNDARY - _HOLE) / SCREEN_HEIGHT * 2 - 1
    return [relative_bat, lower_rel, upper_rel, speed, accel * 10]


def quick_score(network: Network) -> bool:
    """Return True if the network passes basic directional viability tests."""
    # Above the gap, speed >= 0: must accelerate toward gap (output > 0)
    for bat_y, speed in [(150, 0.0), (150, 2.0)]:
        if network.return_network_solution(_make_inputs(bat_y, speed))[0] <= 0:
            return False

    # Below the gap, speed <= 0: must accelerate toward gap (output < 0)
    for bat_y, speed in [(650, 0.0), (650, -2.0)]:
        if network.return_network_solution(_make_inputs(bat_y, speed))[0] >= 0:
            return False

    # At gap centre, moving down: must decelerate (output < 0)
    if network.return_network_solution(_make_inputs(_CAP_Y, 2.0))[0] >= 0:
        return False

    # At gap centre, moving up: must decelerate (output > 0)
    if network.return_network_solution(_make_inputs(_CAP_Y, -2.0))[0] <= 0:
        return False

    # At gap centre, nearly still: output must be near zero
    if abs(network.return_network_solution(_make_inputs(_CAP_Y, 0.0))[0]) > _NEAR_ZERO_THRESHOLD:
        return False

    return True
