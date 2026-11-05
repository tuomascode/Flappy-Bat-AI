import pytest
from math import tanh
import random

from flappy_bat.network.node import Node
from flappy_bat.network.network import Network
from flappy_bat.network.evolution import Evolution


class TestNetwork:
    def test_primitive_network_shape(self):
        net = Network(3, 2, [])
        assert net.number_of_nodes == 5
        assert net.begins == [0, 1, 2]
        assert net.ends == [3, 4]
        assert net.primitive is True
        assert net.levels == []

    def test_single_output_network(self):
        net = Network(5, 1, [])
        assert net.number_of_nodes == 6
        assert net.begins == [0, 1, 2, 3, 4]
        assert net.ends == [5]

    def test_network_table_is_square(self):
        net = Network(4, 1, [])
        n = net.number_of_nodes
        assert len(net.network_table) == n
        assert all(len(row) == n for row in net.network_table)

    def test_input_to_output_connections_exist(self):
        net = Network(3, 1, [])
        for i in net.begins:
            for j in net.ends:
                assert net.network_table[i][j] is not None

    def test_return_network_solution_output_count(self):
        net = Network(5, 1, [])
        result = net.return_network_solution([0.1, 0.2, 0.3, 0.4, 0.5])
        assert len(result) == 1

    def test_return_network_solution_multiple_outputs(self):
        net = Network(3, 2, [])
        result = net.return_network_solution([0.1, 0.2, 0.3])
        assert len(result) == 2

    def test_output_bounded_by_tanh(self):
        net = Network(5, 1, [])
        result = net.return_network_solution([1.0, 1.0, 1.0, 1.0, 1.0])
        assert -1.0 <= result[0] <= 1.0

    def test_output_bounded_negative_inputs(self):
        net = Network(5, 1, [])
        result = net.return_network_solution([-1.0, -1.0, -1.0, -1.0, -1.0])
        assert -1.0 <= result[0] <= 1.0

    def test_calculate_complexity_primitive_3in_1out(self):
        net = Network(3, 1, [])
        # 4 nodes + 3 connections (each input -> output)
        assert net.calculate_complexity() == 7

    def test_calculate_complexity_increases_with_node(self):
        net = Network(3, 1, [])
        before = net.calculate_complexity()
        net.create_new_node()
        after = net.calculate_complexity()
        assert after > before

    def test_create_new_node_increments_node_count(self):
        net = Network(3, 1, [])
        net.create_new_node()
        assert net.number_of_nodes == 5
        assert len(net.levels) == 1
        assert net.primitive is False

    def test_create_new_node_multiple_times(self):
        net = Network(3, 1, [])
        net.create_new_node()
        net.create_new_node()
        assert net.number_of_nodes == 6
        assert len(net.levels) == 2

    def test_create_new_node_all_mutability_levels(self):
        for mutability in range(1, 6):
            net = Network(3, 1, [])
            net.create_new_node(mutability)
            assert net.number_of_nodes == 5

    def test_remove_node_decrements_node_count(self):
        net = Network(3, 1, [])
        net.create_new_node()
        net.remove_node()
        assert net.number_of_nodes == 4
        assert len(net.levels) == 0

    def test_remove_node_restores_primitive(self):
        net = Network(3, 1, [])
        net.create_new_node()
        assert net.primitive is False
        net.remove_node()
        assert len(net.levels) == 0
        assert net.primitive is True

    def test_network_solvable_after_node_added(self):
        net = Network(5, 1, [])
        net.create_new_node()
        result = net.return_network_solution([0.1, 0.2, 0.3, 0.4, 0.5])
        assert len(result) == 1
        assert -1.0 <= result[0] <= 1.0

    def test_network_solvable_after_node_removed(self):
        net = Network(5, 1, [])
        net.create_new_node()
        net.remove_node()
        result = net.return_network_solution([0.1, 0.2, 0.3, 0.4, 0.5])
        assert len(result) == 1
        assert -1.0 <= result[0] <= 1.0

    def test_network_table_shape_preserved_after_node_operations(self):
        net = Network(3, 1, [])
        net.create_new_node()
        n = net.number_of_nodes
        assert len(net.network_table) == n
        assert all(len(row) == n for row in net.network_table)

    def test_mutate_network_preserves_node_count(self):
        net = Network(3, 1, [])
        net.create_new_node()
        before = net.number_of_nodes
        net.mutate_network(3)
        assert net.number_of_nodes == before

    def test_mutate_all_rates_produce_valid_output(self):
        for rate in range(1, 6):
            random.seed(rate)
            net = Network(3, 1, [])
            net.mutate_network(rate)
            result = net.return_network_solution([0.1, 0.2, 0.3])
            assert len(result) == 1
            assert -1.0 <= result[0] <= 1.0

    def test_create_new_connection_no_levels_no_error(self):
        net = Network(3, 1, [])
        net.create_new_connection()  # Should silently return when no levels

    def test_create_new_connection_all_mutability_levels(self):
        for mutability in range(1, 6):
            net = Network(3, 1, [])
            net.create_new_node()
            net.create_new_connection(mutability)  # Should not raise

    def test_check_connection_false_when_no_levels(self):
        net = Network(3, 1, [])
        assert net.check_connection() is False

    def test_remove_connection_safe_when_nothing_to_remove(self):
        net = Network(2, 1, [])
        net.remove_connection()  # Should not raise even if nothing to remove

    def test_check_for_connection_removal_false_on_primitive(self):
        # Primitive 2-input, 1-output: each input has only 1 connection
        net = Network(2, 1, [])
        assert net.check_for_connection_removal() is False

    def test_write_and_read_roundtrip(self, tmp_path):
        net = Network(3, 1, [])
        path = str(tmp_path / "net.txt")
        net.write(path)
        loaded = Network.read_and_return(path)
        assert loaded.number_of_nodes == net.number_of_nodes
        assert loaded.begins == net.begins
        assert loaded.ends == net.ends

    def test_write_and_read_with_hidden_nodes(self, tmp_path):
        net = Network(5, 1, [])
        net.create_new_node()
        net.create_new_node()
        path = str(tmp_path / "net_hidden.txt")
        net.write(path)
        loaded = Network.read_and_return(path)
        assert loaded.number_of_nodes == net.number_of_nodes
        assert len(loaded.levels) == len(net.levels)

    def test_loaded_network_produces_same_output(self, tmp_path):
        random.seed(42)
        net = Network(3, 1, [])
        path = str(tmp_path / "net_output.txt")
        net.write(path)
        loaded = Network.read_and_return(path)
        inputs = [0.5, -0.3, 0.1]
        assert abs(net.return_network_solution(inputs)[0] - loaded.return_network_solution(inputs)[0]) < 1e-6

    def test_return_mutated_network_count(self):
        net = Network(3, 1, [])
        mutated = Network.return_mutated_network(net, 5, 2)
        assert len(mutated) == 5

    def test_return_mutated_network_all_solvable(self):
        net = Network(5, 1, [])
        mutated = Network.return_mutated_network(net, 3, 3)
        for m in mutated:
            result = m.return_network_solution([0.1, 0.2, 0.3, 0.4, 0.5])
            assert len(result) == 1
            assert -1.0 <= result[0] <= 1.0

    def test_return_mutated_network_independent_copies(self):
        net = Network(3, 1, [])
        mutated = Network.return_mutated_network(net, 3, 1)
        # Each copy should have a distinct id (almost certainly)
        ids = [m.id for m in mutated]
        assert len(set(ids)) > 1  # very unlikely all ids are the same
