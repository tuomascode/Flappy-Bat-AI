import pytest
from math import tanh
import random

from flappy_bat.network.node import Node
from flappy_bat.network.network import Network
from flappy_bat.network.evolution import Evolution


class TestEvolution:
    def test_create_networks_correct_count(self):
        evo = Evolution()
        nets = evo.create_new_networks(5, 1, number_of_networks=4)
        assert len(nets) == 4

    def test_created_networks_correct_io(self):
        evo = Evolution()
        nets = evo.create_new_networks(5, 1, number_of_networks=1)
        assert len(nets[0].begins) == 5
        assert len(nets[0].ends) == 1

    def test_created_networks_solvable(self):
        evo = Evolution()
        nets = evo.create_new_networks(5, 1, number_of_networks=2)
        for net in nets:
            result = net.return_network_solution([0.1, 0.2, 0.3, 0.4, 0.5])
            assert len(result) == 1
            assert -1.0 <= result[0] <= 1.0

    def test_evolve_networks_correct_count(self):
        evo = Evolution()
        source = evo.create_new_networks(5, 1, number_of_networks=1)[0]
        evolved = evo.evolve_networks(source, amount_of_networks=5)
        assert len(evolved) == 5

    def test_evolve_complexity_zero_count(self):
        evo = Evolution()
        source = evo.create_new_networks(5, 1, number_of_networks=1)[0]
        evolved = evo.evolve_networks(source, complexity=0, amount_of_networks=3)
        assert len(evolved) == 3

    def test_evolved_networks_solvable(self):
        evo = Evolution()
        source = evo.create_new_networks(5, 1, number_of_networks=1)[0]
        evolved = evo.evolve_networks(source, amount_of_networks=3)
        for net in evolved:
            result = net.return_network_solution([0.1, 0.2, 0.3, 0.4, 0.5])
            assert len(result) == 1
            assert -1.0 <= result[0] <= 1.0

    def test_evolve_complexity_zero_solvable(self):
        evo = Evolution()
        source = evo.create_new_networks(5, 1, number_of_networks=1)[0]
        evolved = evo.evolve_networks(source, complexity=0, amount_of_networks=3)
        for net in evolved:
            result = net.return_network_solution([0.1, 0.2, 0.3, 0.4, 0.5])
            assert len(result) == 1
            assert -1.0 <= result[0] <= 1.0

    def test_evolve_with_hidden_nodes(self):
        evo = Evolution()
        source = evo.create_new_networks(5, 1, number_of_networks=1)[0]
        source.create_new_node()
        source.create_new_node()
        evolved = evo.evolve_networks(source, amount_of_networks=3)
        for net in evolved:
            result = net.return_network_solution([0.1, 0.2, 0.3, 0.4, 0.5])
            assert len(result) == 1

    def test_read_and_return(self, tmp_path):
        random.seed(1)
        evo = Evolution()
        source = evo.create_new_networks(5, 1, number_of_networks=1)[0]
        path = str(tmp_path / "evo_net.txt")
        source.write(path)
        loaded = evo.read_and_return(path)
        assert loaded.number_of_nodes == source.number_of_nodes
        assert loaded.begins == source.begins
        assert loaded.ends == source.ends
