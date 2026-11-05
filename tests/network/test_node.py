import pytest
from math import tanh
import random

from flappy_bat.network.node import Node
from flappy_bat.network.network import Network
from flappy_bat.network.evolution import Evolution


class TestNode:
    def test_initial_state(self):
        node = Node(3, 0.7)
        assert node.index == 3
        assert node.weight == 0.7
        assert node.back_neighbours == []
        assert node.factors == []

    def test_append_neighbour(self):
        input_node = Node(0, 0.5)
        output_node = Node(1, 0.0)
        output_node.append_neighbour(input_node, 0.8)
        assert output_node.back_neighbours == [input_node]
        assert output_node.factors == [0.8]

    def test_append_multiple_neighbours(self):
        a = Node(0, 0.5)
        b = Node(1, -0.3)
        out = Node(2, 0.1)
        out.append_neighbour(a, 1.0)
        out.append_neighbour(b, 2.0)
        assert len(out.back_neighbours) == 2
        assert len(out.factors) == 2

    def test_solve_isolated_node_returns_weight(self):
        node = Node(0, 1.5)
        assert node.solve_network_output() == 1.5

    def test_solve_with_one_neighbour(self):
        input_node = Node(0, 0.5)
        output_node = Node(1, 0.0)
        output_node.append_neighbour(input_node, 2.0)
        expected = tanh(0.0 + 0.5 * 2.0)
        assert abs(output_node.solve_network_output() - expected) < 1e-10

    def test_solve_with_multiple_neighbours(self):
        a = Node(0, 0.5)
        b = Node(1, -0.3)
        out = Node(2, 0.1)
        out.append_neighbour(a, 1.0)
        out.append_neighbour(b, 2.0)
        expected = tanh(0.1 + 0.5 * 1.0 + (-0.3) * 2.0)
        assert abs(out.solve_network_output() - expected) < 1e-10

    def test_solve_zero_weight_zero_inputs(self):
        input_node = Node(0, 0.0)
        output_node = Node(1, 0.0)
        output_node.append_neighbour(input_node, 1.0)
        assert output_node.solve_network_output() == tanh(0.0)
