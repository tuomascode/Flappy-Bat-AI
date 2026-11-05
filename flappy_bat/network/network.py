from __future__ import annotations

import random as r

import numpy as np

from flappy_bat.network.node import Node

_WEIGHT_INIT_RANGE = (-1.0, 1.0)  # initial connection weights
_BIAS_INIT_RANGE = (-2.0, 2.0)  # output node bias


class Network:
    # The basic functionality of the network is in this class.
    # The class offers functions for creating networks and mutating them in various ways.
    # The class also provides with basic checking functions that ensure, that mutation functions don't break the networks.
    # Write and read functions are also provided to save the network. Not sure why anyone would do this but here we are.
    def __init__(
        self, input_nodes: int, output_nodes: int, table: list | np.ndarray
    ) -> None:
        if len(table) == 0:
            self.number_of_nodes = input_nodes + output_nodes
            self.levels: list[int] = []
            self.begins = list(range(input_nodes))
            self.ends = [i + input_nodes for i in range(output_nodes)]
            self.network_table = np.full(
                (self.number_of_nodes, self.number_of_nodes), np.nan
            )
            for i in self.begins:
                for j in self.ends:
                    self.network_table[i][j] = r.uniform(*_WEIGHT_INIT_RANGE)
            for i in self.ends:
                self.network_table[i][i] = r.uniform(*_BIAS_INIT_RANGE)
            self.primitive = True
            self.id = r.randint(0, 999999999)
            self._rebuild_node_graph()
        else:
            self.id = r.randint(0, 999999999)
            self.number_of_nodes = len(table)
            self.begins = list(range(input_nodes))
            self.levels = []
            if self.number_of_nodes != input_nodes + output_nodes:
                for i in range(input_nodes, len(table) - output_nodes):
                    self.levels.append(i)
            self.primitive = len(self.levels) == 0
            self.ends = list(
                range(len(self.begins) + len(self.levels), self.number_of_nodes)
            )
            # np.array copies if table is already ndarray; converts None → nan if list
            self.network_table = np.array(table, dtype=float)
            self._rebuild_node_graph()

    def _rebuild_node_graph(self) -> None:
        self.nodes = []
        for i in self.begins:
            self.nodes.append(Node(i, self.network_table[i][i]))
        for i in self.levels:
            self.nodes.append(Node(i, self.network_table[i][i]))
        for i in self.ends:
            self.nodes.append(Node(i, self.network_table[i][i]))
        for i in range(len(self.network_table) - 1, -1, -1):
            for j in range(i - 1, -1, -1):
                if not np.isnan(self.network_table[j][i]):
                    self.nodes[i].append_neighbour(
                        self.nodes[j], self.network_table[j][i]
                    )

    def _copy_table(self) -> np.ndarray:
        return self.network_table.copy()

    def _expand_table(self, at: int) -> np.ndarray:
        """Return a copy of network_table with a blank row and column inserted at `at`."""
        n = len(self.network_table)
        new_table = np.full((n + 1, n + 1), np.nan)
        idx = np.arange(n)
        shifted = np.where(idx >= at, idx + 1, idx)
        new_table[np.ix_(shifted, shifted)] = self.network_table
        return new_table

    def _compact_table(self, at: int) -> np.ndarray:
        """Return a copy of network_table with row and column `at` removed."""
        n = len(self.network_table)
        idx = np.concatenate([np.arange(at), np.arange(at + 1, n)])
        return self.network_table[np.ix_(idx, idx)].copy()

    def _wire_node_primitive(
        self, rv: int, lower_bound: float, upper_bound: float
    ) -> None:
        """Wire a newly inserted node at `rv` into a primitive (no hidden layers) network."""
        node = r.choice(self.ends)
        second_node = r.choice(self.nodes[node - 1].back_neighbours).index
        self.network_table[rv][node] = self.network_table[second_node][node]
        self.network_table[second_node][rv] = 1
        self.network_table[second_node][node] = np.nan
        self.network_table[rv][rv] = r.uniform(lower_bound, upper_bound)

    def _wire_node_complex(
        self, rv: int, lower_bound: float, upper_bound: float
    ) -> None:
        """Wire a newly inserted node at `rv` into a network that already has hidden layers."""
        while True:
            node = r.randint(rv + 1, self.ends[-1])
            candidate_sources = [
                i for i in range(rv) if not np.isnan(self.network_table[i][node])
            ]
            try:
                second_node = r.choice(candidate_sources)
                break
            except IndexError:
                continue
        self.network_table[rv][rv] = r.uniform(lower_bound, upper_bound)
        self.network_table[rv][node] = self.network_table[second_node][node]
        self.network_table[second_node][rv] = 1
        self.network_table[second_node][node] = np.nan

    def _find_node_neighbors(self, node: int) -> tuple[list[int], list[int]]:
        """Return (upstream, downstream) neighbor indices for `node`.

        upstream:   indices of nodes that have a connection pointing TO `node`
        downstream: indices of nodes that `node` connects TO
        """
        upstream: list[int] = []
        downstream: list[int] = []
        n = len(self.network_table)
        for i in range(n):
            for j in range(n):
                if j == node and j != i and not np.isnan(self.network_table[j][i]):
                    downstream.append(i)
                if i == node and j != i and not np.isnan(self.network_table[j][i]):
                    upstream.append(j)
        return upstream, downstream

    def calculate_complexity(self) -> int:
        n = len(self.network_table)
        i_idx, j_idx = np.triu_indices(n, k=1)
        connections = int(np.sum(~np.isnan(self.network_table[i_idx, j_idx])))
        return self.number_of_nodes + connections

    def return_network_solution(self, input: list[float]) -> list[float]:
        solutions = []
        for index in self.begins:
            self.nodes[index].weight = input[index]
        for i in self.ends:
            solutions.append(self.nodes[i].solve_network_output())
        return solutions

    def remove_node(self) -> None:
        node = r.choice(self.levels)
        upstream, downstream = self._find_node_neighbors(node)
        new_table = self._copy_table()
        for i in upstream:
            for j in downstream:
                new_table[i][j] = (
                    self.network_table[node][j] + self.network_table[i][node]
                ) / 2
        new_table[node, :] = np.nan
        new_table[:, node] = np.nan
        self.network_table = new_table
        self.network_table = self._compact_table(node)
        self.levels = self.levels[:-1]
        if len(self.levels) == 0:
            self.primitive = True
        for i in range(len(self.ends)):
            self.ends[i] -= 1
        self.number_of_nodes -= 1
        self._rebuild_node_graph()

    def create_new_node(self, mutability: int = 1) -> None:
        _ranges = [(0, 0.4), (0.4, 0.8), (0.8, 1.2), (1.2, 1.6), (1.6, 2.0)]
        variability = r.uniform(*_ranges[mutability - 1])
        lower_bound = -variability
        upper_bound = variability
        if len(self.levels) == 0:
            self.primitive = False
            rv = self.begins[-1] + 1
            self.network_table = self._expand_table(rv)
            self.number_of_nodes += 1
            for i in range(len(self.ends)):
                self.ends[i] += 1
            self._wire_node_primitive(rv, lower_bound, upper_bound)
            self.levels.append(rv)
            self._rebuild_node_graph()
        else:
            rv = r.randint(self.begins[-1], self.levels[-1])
            self.network_table = self._expand_table(rv + 1)
            self.number_of_nodes += 1
            self.levels.append(self.levels[-1] + 1)
            for i in range(len(self.ends)):
                self.ends[i] += 1
            rv += 1
            self._wire_node_complex(rv, lower_bound, upper_bound)
            self._rebuild_node_graph()

    def create_new_connection(self, mutability: int = 1) -> None:
        _ranges = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
        variability = r.uniform(*_ranges[mutability - 1])
        lower_bound = -variability
        upper_bound = variability
        sum = 0
        if len(self.levels) == 0:
            return
        for j in range(0, len(self.network_table) - 1):
            for i in range(self.levels[0], len(self.network_table)):
                if j >= i:
                    continue
                if np.isnan(self.network_table[j][i]):
                    sum += 1
        if sum == 0:
            return
        connection = r.randint(1, sum)
        index = 1
        new_table = self._copy_table()
        for j in range(len(new_table) - 1):
            for i in range(self.levels[0], len(new_table)):
                if j >= i:
                    continue
                if np.isnan(self.network_table[j][i]):
                    if index == connection:
                        new_table[j][i] = r.uniform(lower_bound, upper_bound)
                        self.network_table = new_table
                        self._rebuild_node_graph()
                        return
                    else:
                        index += 1
        self._rebuild_node_graph()

    def check_connection(self) -> bool:
        if len(self.levels) == 0:
            return False
        for j in range(0, len(self.network_table) - 1):
            for i in range(self.levels[0], len(self.network_table)):
                if j >= i:
                    continue
                if np.isnan(self.network_table[j][i]):
                    return True
        return False

    def check_for_connection_removal(self) -> bool:
        for i in range(len(self.network_table)):
            connections = 0
            for j in range(i + 1, len(self.network_table)):
                if j <= self.begins[-1]:
                    continue
                if not np.isnan(self.network_table[i][j]):
                    connections += 1
            if connections >= 2:
                return True
        return False

    def remove_connection(self) -> None:
        if not self.check_for_connection_removal():
            return
        removals = []
        for i in range(len(self.network_table) - 1):
            connections = []
            for j in range(i + 1, len(self.network_table)):
                if j <= self.begins[-1]:
                    continue
                if not np.isnan(self.network_table[i][j]):
                    connections.append((i, j))
            for i in connections:
                removals.append(i)
        removal = r.choice(removals)
        new_table = self._copy_table()
        new_table[removal[0]][removal[1]] = np.nan
        self.network_table = new_table
        self._rebuild_node_graph()

    def mutate_network(self, rate: int) -> None:
        variability = rate * 0.03
        lower_bound = 1 - variability
        upper_bound = 1 + variability
        new_table = self._copy_table()
        n = len(new_table)
        present = ~np.isnan(new_table)
        flip = np.random.randint(1, 11, size=(n, n)) <= rate
        mask = present & flip
        multipliers = np.random.uniform(lower_bound, upper_bound, size=(n, n))
        new_table[mask] *= multipliers[mask]
        self.network_table = new_table
        self._rebuild_node_graph()

    @staticmethod
    def return_mutated_network(
        neural_network: Network, count: int, rate: int
    ) -> list[Network]:
        network_table = []
        for i in range(count):
            network_table.append(
                Network(
                    neural_network.begins[-1] + 1,
                    len(neural_network.ends),
                    neural_network.network_table,
                )
            )
        for i in range(len(network_table)):
            network_table[i].mutate_network(rate)
        return network_table

    def write(self, filename: str) -> None:
        with open(filename, "w") as file:
            for row in self.network_table:
                parts = ["None" if np.isnan(v) else str(v) for v in row]
                file.write(";".join(parts) + "\n")
            file.write(str(len(self.begins)) + "\n")
            file.write(str(len(self.ends)))

    @staticmethod
    def read_and_return(filename: str) -> Network:
        with open(filename) as file:
            lines = file.readlines()
        input_nodes = int(lines[-2].strip())
        output_nodes = int(lines[-1].strip())
        rows = []
        for line in lines[:-2]:
            row = [
                np.nan if k.strip() == "None" else float(k.strip())
                for k in line.split(";")
            ]
            rows.append(row)
        return Network(input_nodes, output_nodes, np.array(rows, dtype=float))
