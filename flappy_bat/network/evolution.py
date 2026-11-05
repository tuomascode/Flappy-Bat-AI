from __future__ import annotations

import random as r

from flappy_bat.network.network import Network


class Evolution:
    #Evolution class hold basic functionality, which ease the use of the learning networks.
    # 1. create_new_networks gives you the new networks with the number of input and output nodes you wish to have.
    # 2. Evolve networks takes in a network and spits out as many networks as you wish.
    # 3. Read and return can be used to read a network from a textfile
    def __init__(self) -> None:
        self.mutatibility=5

    def create_new_networks(self, first_order_nodes: int, end_nodes: int, complexity_factor: float = 1.1, connection_factor: float = 1.2, number_of_networks: int = 1) -> list[Network]:
        list_of_networks=[]
        for i in range(number_of_networks):
            possible_connections=0
            neural_network=Network(first_order_nodes,end_nodes,[])
            complexity_now=neural_network.calculate_complexity()
            complexity=complexity_now*complexity_factor
            connections=0
            while complexity_now<complexity:
                if len(neural_network.levels)==0:
                    neural_network.create_new_node(r.randint(1,5))
                    possible_connections+=first_order_nodes
                    connections+=1
                else:
                    connectivity_relation=connections/possible_connections
                    if connectivity_relation>connection_factor:

                        connections+=1
                        possible_connections+=first_order_nodes+len(neural_network.levels)
                        neural_network.create_new_node(r.randint(1,5))
                    else:

                        if neural_network.check_connection():
                            neural_network.create_new_connection(r.randint(1,5))
                            connections+=1
                        else:
                            connections+=1
                            possible_connections+=first_order_nodes+len(neural_network.levels)
                            neural_network.create_new_node(r.randint(1,5))
                complexity_now=neural_network.calculate_complexity()
            list_of_networks.append(neural_network)
        return list_of_networks

    def read_and_return(self, filename: str) -> Network:
        return Network.read_and_return(filename)

    def evolve_networks(self, neural_network: Network, complexity: int = 2, mutation_rate: int = 2, amount_of_networks: int = 1) -> list[Network]:

        #Hello fellow programmer! You've made it this far, for which I congratulate you!
        #However, I'm going to be perfectly honest here. I wrote this code in the summer of 2022, when I had approximately
        #6 months of coding under my belt. Now, about 7 months later I haven't got the faintest clue what the code here does.

        #I know the factors such as complexity and mutation rate determine how wildly the new networks vary,
        #however, trying to work the workings of this code post-familiarity is beyond me.

        #So if you are reading this, I solemnly sweat that I have improved my commenting habits!


        if complexity==0:
            network_list=Network.return_mutated_network(neural_network,amount_of_networks,r.randint(1,5))
            return network_list
        else:
            addition_value=r.uniform(-0.05,0.05)
            if len(neural_network.levels)==0:
                mutation_factor=1
            else:
                mutation_factor=(neural_network.calculate_complexity()-neural_network.number_of_nodes)/len(neural_network.levels)+addition_value
            network_list=[]
            for i in range(amount_of_networks):
                network_list.append(Network(neural_network.begins[-1]+1,len(neural_network.ends),neural_network.network_table))

            for i in range(len(network_list)):
                if r.randint(0,1)==1:
                    for k in range(complexity):
                        if len(network_list[i].levels)==0:
                            network_list[i].create_new_node(mutation_rate)
                            continue
                        if (network_list[i].calculate_complexity()-network_list[i].number_of_nodes)/len(network_list[i].levels)>=mutation_factor:
                            network_list[i].create_new_node(mutation_rate)
                        else:
                            network_list[i].create_new_connection(mutation_rate)
                else:
                    for k in range(complexity):
                        if len(network_list[i].levels)==0:
                            network_list[i].remove_connection()
                            continue
                        if (network_list[i].calculate_complexity()-network_list[i].number_of_nodes)/len(network_list[i].levels)>=mutation_factor:
                            network_list[i].remove_connection()
                        else:
                            network_list[i].remove_node()
                for b in range(mutation_rate-1):
                    network_list[i].mutate_network(mutation_rate)
        return network_list
