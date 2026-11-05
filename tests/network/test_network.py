import pytest
from math import tanh
import random

import numpy as np

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

    def test_return_network_solution_known_value(self):
        from math import tanh
        # Build a hand-crafted 5→1 network with known weights
        net = Network(5, 1, [])
        net.network_table[:] = np.nan
        net.network_table[0][5] = -2.0
        net.network_table[1][5] = 1.0
        net.network_table[3][5] = -1.0
        net.network_table[4][5] = 0.5
        net.network_table[5][5] = 0.1  # bias
        net._rebuild_node_graph()
        result = net.return_network_solution([1.0, 0.5, 0.0, -0.5, 0.25])
        expected = tanh(-2.0 * 1.0 + 1.0 * 0.5 + (-1.0) * (-0.5) + 0.5 * 0.25 + 0.1)
        assert result[0] == pytest.approx(expected)

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
        assert (
            abs(
                net.return_network_solution(inputs)[0]
                - loaded.return_network_solution(inputs)[0]
            )
            < 1e-6
        )

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

    # --- Phase 10: table helper tests ---

    def test_copy_table_is_independent(self):
        net = Network(3, 1, [])
        original_val = net.network_table[0][3]
        copy = net._copy_table()
        copy[0][3] = 999.0
        assert net.network_table[0][3] == original_val

    def test_expand_table_increases_size(self):
        net = Network(3, 1, [])
        n = net.number_of_nodes
        expanded = net._expand_table(2)
        assert len(expanded) == n + 1
        assert all(len(row) == n + 1 for row in expanded)

    def test_expand_table_new_row_col_blank(self):
        net = Network(3, 1, [])
        expanded = net._expand_table(2)
        assert np.all(np.isnan(expanded[2]))
        assert np.all(np.isnan(expanded[:, 2]))

    def test_compact_table_decreases_size(self):
        net = Network(3, 1, [])
        net.create_new_node()
        level = net.levels[0]
        n = net.number_of_nodes
        compacted = net._compact_table(level)
        assert len(compacted) == n - 1
        assert all(len(row) == n - 1 for row in compacted)

    # --- Phase 11: decomposed helper tests ---

    def test_wire_node_primitive_creates_incoming_and_outgoing_connections(self):
        random.seed(42)
        net = Network(3, 1, [])
        rv = net.begins[-1] + 1
        net.network_table = net._expand_table(rv)
        net.number_of_nodes += 1
        for i in range(len(net.ends)):
            net.ends[i] += 1
        net._wire_node_primitive(rv, 0.5)
        net.levels.append(rv)
        net._rebuild_node_graph()
        has_incoming = any(net.network_table[i][rv] is not None for i in range(rv))
        has_outgoing = any(net.network_table[rv][j] is not None for j in net.ends)
        assert has_incoming
        assert has_outgoing

    def test_wire_node_complex_creates_incoming_and_outgoing_connections(self):
        random.seed(42)
        net = Network(3, 1, [])
        net.create_new_node()
        rv = net.begins[-1]
        net.network_table = net._expand_table(rv + 1)
        net.number_of_nodes += 1
        net.levels.append(net.levels[-1] + 1)
        for i in range(len(net.ends)):
            net.ends[i] += 1
        rv += 1
        net._wire_node_complex(rv, 0.5)
        net._rebuild_node_graph()
        has_incoming = any(net.network_table[i][rv] is not None for i in range(rv))
        has_outgoing = any(net.network_table[rv][j] is not None for j in range(rv + 1, net.number_of_nodes))
        assert has_incoming
        assert has_outgoing

    def test_find_node_neighbors_upstream_and_downstream(self):
        random.seed(42)
        net = Network(3, 1, [])
        net.create_new_node()
        level = net.levels[0]
        upstream, downstream = net._find_node_neighbors(level)
        assert all(u < level for u in upstream)
        assert all(d > level for d in downstream)
        assert len(upstream) > 0
        assert len(downstream) > 0

    def test_mutate_network_preserves_none_positions(self):
        random.seed(7)
        net = Network(3, 1, [])
        nan_before = np.isnan(net.network_table).copy()
        net.mutate_network(3)
        assert np.array_equal(nan_before, np.isnan(net.network_table))

    # --- Phase 12: numpy integration tests ---

    def test_network_table_is_ndarray(self):
        net = Network(3, 1, [])
        assert isinstance(net.network_table, np.ndarray)

    def test_nan_means_no_connection(self):
        net = Network(3, 1, [])
        # Diagonal entries for input nodes should be nan (no self-bias)
        for i in net.begins:
            assert np.isnan(net.network_table[i][i])
        # begin→end connections should be valid floats
        for i in net.begins:
            for j in net.ends:
                assert not np.isnan(net.network_table[i][j])

    def test_calculate_complexity_matches_manual_count(self):
        random.seed(1)
        net = Network(3, 1, [])
        n = net.number_of_nodes
        manual = n + sum(
            1
            for i in range(n - 1)
            for j in range(i + 1, n)
            if not np.isnan(net.network_table[i][j])
        )
        assert net.calculate_complexity() == manual

    def test_check_connection_true_with_levels(self):
        net = Network(3, 1, [])
        net.create_new_node()
        # With 3 inputs and 1 hidden node only one input→hidden wired; others are nan
        assert net.check_connection() is True

    def test_check_for_connection_removal_true_after_extra_connection(self):
        random.seed(1)
        net = Network(3, 1, [])
        net.create_new_node()
        net.create_new_connection()
        assert net.check_for_connection_removal() is True

    def test_remove_connection_decreases_connection_count(self):
        random.seed(1)
        net = Network(3, 1, [])
        net.create_new_node()
        net.create_new_connection()
        connections_before = net.calculate_complexity() - net.number_of_nodes
        net.remove_connection()
        connections_after = net.calculate_complexity() - net.number_of_nodes
        assert connections_after == connections_before - 1

    def test_create_new_connection_no_op_when_fully_connected(self):
        random.seed(1)
        net = Network(2, 1, [])
        net.create_new_node()
        for _ in range(5):
            net.create_new_connection()
        complexity_before = net.calculate_complexity()
        net.create_new_connection()
        assert net.calculate_complexity() == complexity_before
        assert net.check_connection() is False

    def test_mutate_network_nan_positions_unchanged(self):
        random.seed(5)
        net = Network(3, 1, [])
        net.create_new_node()
        nan_before = np.isnan(net.network_table).copy()
        net.mutate_network(5)
        assert np.array_equal(nan_before, np.isnan(net.network_table))
