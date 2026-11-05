from __future__ import annotations

import random as r

from flappy_bat.network.node import Node

_WEIGHT_INIT_RANGE = (-1.0, 1.0)  # initial connection weights
_BIAS_INIT_RANGE = (-2.0, 2.0)  # output node bias


class Network:
    # The basic functionality of the network is in this class.
    # The class offers functions for creating networks and mutating them in various ways.
    # The class also provides with basic checking functions that ensure, that mutation functions don't break the networks.
    # Write and read functions are also provided to save the network. Not sure why anyone would do this but here we are.
    def __init__(
        self, input_nodes: int, output_nodes: int, table: list[list[float | None]]
    ) -> None:
        if len(table) == 0:
            self.number_of_nodes = input_nodes + output_nodes
            self.levels: list[int] = []
            self.begins = [i for i in range(input_nodes)]
            self.ends = [i + input_nodes for i in range(output_nodes)]
            self.network_table = [
                [None for j in range(self.number_of_nodes)]
                for i in range(self.number_of_nodes)
            ]
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
            self.begins = [i for i in range(input_nodes)]
            self.levels = []
            if self.number_of_nodes != input_nodes + output_nodes:
                for i in range(input_nodes, len(table) - output_nodes):
                    self.levels.append(i)
            self.primitive = False
            if len(self.levels) == 0:
                self.primitive = True
            self.ends = [
                value
                for value in range(
                    len(self.begins) + len(self.levels), self.number_of_nodes
                )
            ]
            self.network_table = table
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
                if self.network_table[j][i] != None:
                    self.nodes[i].append_neighbour(
                        self.nodes[j], self.network_table[j][i]
                    )

    def calculate_complexity(self) -> int:
        sum = 0
        sum += self.number_of_nodes
        for i in range(len(self.network_table) - 1):
            for j in range(i + 1, len(self.network_table)):
                if self.network_table[i][j] != None:
                    sum += 1
        return sum

    def return_network_solution(self, input: list[float]) -> list[float]:
        solutions = []
        for index in self.begins:
            self.nodes[index].weight = input[index]
        for i in self.ends:
            solutions.append(self.nodes[i].solve_network_output())
        return solutions

    def remove_node(self) -> None:
        node = r.choice(self.levels)
        new_table = [
            [self.network_table[i][j] for j in range(len(self.network_table))]
            for i in range(len(self.network_table))
        ]
        end_nodes = []
        first_order_nodes = []
        for i in range(len(new_table)):
            for j in range(len(new_table)):
                if j == node:
                    if j != i:
                        if self.network_table[j][i] != None:
                            first_order_nodes.append(i)
                if i == node:
                    if j != i:
                        if self.network_table[j][i] != None:
                            end_nodes.append(j)
        for i in end_nodes:
            for j in first_order_nodes:
                new_table[i][j] = (
                    self.network_table[node][j] + self.network_table[i][node]
                ) / 2
        for i in range(len(new_table)):
            new_table[node][i] = None
            new_table[i][node] = None
        new_table_two = [
            [None for j in range(len(new_table) - 1)] for i in range(len(new_table) - 1)
        ]
        for i in range(len(new_table_two)):
            for j in range(len(new_table_two)):
                if j >= node:
                    if i >= node:
                        new_table_two[i][j] = new_table[i + 1][j + 1]
                    else:
                        new_table_two[i][j] = new_table[i][j + 1]
                else:
                    if i < node:
                        new_table_two[i][j] = new_table[i][j]
        self.network_table = new_table_two
        self.levels = self.levels[:-1]
        if len(self.levels) == 0:
            self.primitive = True
        for i in range(len(self.ends)):
            self.ends[i] -= 1
        self.number_of_nodes -= 1
        self._rebuild_node_graph()

    def create_new_node(self, mutability: int = 1) -> None:
        if mutability == 1:
            variability = r.uniform(0, 0.4)
        elif mutability == 2:
            variability = r.uniform(0.4, 0.8)
        elif mutability == 3:
            variability = r.uniform(0.8, 1.2)
        elif mutability == 4:
            variability = r.uniform(1.2, 1.6)
        elif mutability == 5:
            variability = r.uniform(1.6, 2)
        lower_bound = 0 - variability
        upper_bound = 0 + variability
        if len(self.levels) == 0:
            self.primitive = False
            reading_value = self.begins[-1] + 1
            self.number_of_nodes += 1
            new_table = [
                [None for j in range(self.number_of_nodes)]
                for i in range(self.number_of_nodes)
            ]
            for index, line in enumerate((self.network_table)):
                for jindex, value in enumerate(line):
                    if value != None:
                        if jindex >= reading_value:
                            if index >= reading_value:
                                new_table[index + 1][jindex + 1] = self.network_table[
                                    index
                                ][jindex]
                            else:
                                new_table[index][jindex + 1] = self.network_table[
                                    index
                                ][jindex]
            self.network_table = new_table
            for i in range(len(self.ends)):
                self.ends[i] += 1
            node = r.choice(self.ends)
            second_node = r.choice(self.nodes[node - 1].back_neighbours).index
            self.network_table[reading_value][node] = self.network_table[second_node][
                node
            ]
            self.network_table[second_node][reading_value] = 1
            self.network_table[second_node][node] = None
            self.network_table[reading_value][reading_value] = r.uniform(
                lower_bound, upper_bound
            )
            self.levels.append(reading_value)
            self._rebuild_node_graph()
        else:
            reading_value = r.randint(self.begins[-1], self.levels[-1])
            self.number_of_nodes += 1
            new_table = [
                [None for j in range(self.number_of_nodes)]
                for i in range(self.number_of_nodes)
            ]
            for index, line in enumerate((self.network_table)):
                for jindex, value in enumerate(line):
                    if value != None:
                        if index <= reading_value and jindex <= reading_value:
                            new_table[index][jindex] = self.network_table[index][jindex]
                        elif reading_value < jindex and index <= reading_value:
                            new_table[index][jindex + 1] = self.network_table[index][
                                jindex
                            ]
                        elif reading_value < jindex and index > reading_value:
                            new_table[index + 1][jindex + 1] = self.network_table[
                                index
                            ][jindex]
            self.levels.append(self.levels[-1] + 1)
            for i in range(len(self.ends)):
                self.ends[i] += 1
            reading_value += 1
            self.network_table = new_table
            while True:
                node = r.randint(reading_value + 1, self.ends[-1])
                candidate_sources = []
                for i in range(reading_value):
                    if self.network_table[i][node] != None:
                        candidate_sources.append(i)
                try:
                    second_node = r.choice(candidate_sources)
                    break
                except IndexError:
                    continue
            self.network_table[reading_value][reading_value] = r.uniform(
                lower_bound, upper_bound
            )
            self.network_table[reading_value][node] = self.network_table[second_node][
                node
            ]
            self.network_table[second_node][reading_value] = 1
            self.network_table[second_node][node] = None
            self._rebuild_node_graph()

    def create_new_connection(self, mutability: int = 1) -> None:
        if mutability == 1:
            variability = r.uniform(0, 0.2)
        elif mutability == 2:
            variability = r.uniform(0.2, 0.4)
        elif mutability == 3:
            variability = r.uniform(0.4, 0.6)
        elif mutability == 4:
            variability = r.uniform(0.6, 0.8)
        elif mutability == 5:
            variability = r.uniform(0.8, 1)
        lower_bound = 0 - variability
        upper_bound = 0 + variability
        sum = 0
        if len(self.levels) == 0:
            return
        for j in range(0, len(self.network_table) - 1):
            for i in range(self.levels[0], len(self.network_table)):
                if j >= i:
                    continue
                if self.network_table[j][i] == None:
                    sum += 1
        if sum == 0:
            return
        connection = r.randint(1, sum)
        index = 1
        new_table = [
            [None for j in range(len(self.network_table))]
            for i in range(len(self.network_table))
        ]
        for i in range(len(self.network_table)):
            for j in range(len(self.network_table)):
                if self.network_table[i][j] != None:
                    new_table[i][j] = self.network_table[i][j]
        for j in range(len(new_table) - 1):
            for i in range(self.levels[0], len(new_table)):
                if j >= i:
                    continue
                if self.network_table[j][i] == None:
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
                if self.network_table[j][i] == None:
                    return True
        return False

    def check_for_connection_removal(self) -> bool:
        for i in range(len(self.network_table)):
            connections = 0
            for j in range(i + 1, len(self.network_table)):
                if j <= self.begins[-1]:
                    continue
                if self.network_table[i][j] != None:
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
                if self.network_table[i][j] != None:
                    connections.append((i, j))
            for i in connections:
                removals.append(i)
        removal = r.choice(removals)
        new_table = [
            [self.network_table[i][j] for j in range(len(self.network_table))]
            for i in range(len(self.network_table))
        ]
        new_table[removal[0]][removal[1]] = None
        self.network_table = new_table
        self._rebuild_node_graph()

    def mutate_network(self, rate: int) -> None:
        variability = rate * 0.03
        lower_bound = 1 - variability
        upper_bound = 1 + variability
        new_table = [
            [None for j in range(len(self.network_table))]
            for i in range(len(self.network_table))
        ]
        for index, row in enumerate(self.network_table):
            for jindex, value in enumerate(row):
                if value != None:
                    new_table[index][jindex] = self.network_table[index][jindex]
                    if r.choice(row) == 0:
                        new_table[index][jindex] *= -1
                    if r.randint(1, 10) <= rate:
                        new_table[index][jindex] *= r.uniform(lower_bound, upper_bound)
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
            for i in self.network_table:
                write_string = ""
                for j in i:
                    write_string += str(j)
                    write_string += ";"
                write_string = write_string[:-1]
                write_string += "\n"
                file.write(write_string)
            file.write((str(len(self.begins)) + "\n"))
            file.write(str(len(self.ends)))

    @staticmethod
    def read_and_return(filename: str) -> Network:
        network_list = []
        index = 0
        with open(filename) as file:
            for i in file:
                network_list.append([])
                i = i.split(";")
                for k in i:
                    k = k.replace("\n", "")
                    if k == "None":
                        network_list[index].append(None)
                    else:
                        network_list[index].append(float(k))

                index += 1
        input_nodes = int(network_list[-2][0])
        output_nodes = int(network_list[-1][0])
        return Network(input_nodes, output_nodes, network_list[:-2])
