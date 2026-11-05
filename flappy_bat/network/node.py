from __future__ import annotations

from math import tanh


class Node:
    def __init__(self, index: int, weight: float | None) -> None:
        self.index = index
        self.back_neighbours: list[Node] = []
        self.factors: list[float] = []
        self.weight = weight

    def append_neighbour(self, neighbour: Node, factor: float) -> None:
        self.factors.append(factor)
        self.back_neighbours.append(neighbour)

    def solve_network_output(self) -> float:
        sum = self.weight
        if len(self.back_neighbours) == 0:
            return sum
        else:
            for i in range(len(self.back_neighbours)):
                value = self.back_neighbours[i].solve_network_output()
                try:
                    sum += value * self.factors[i]
                except (TypeError, OverflowError):
                    raise ValueError
            return tanh(sum)
