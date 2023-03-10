
import random as r
from math import tanh
class Node():
    def __init__(self,index,weight):
        self.index=index
        self.back_neighbours=[]
        self.factors=[]
        self.weight=weight
    def append_neighbour(self,neighbour,factor):
        self.factors.append(factor)
        self.back_neighbours.append(neighbour)
    def solve_network_output(self):
        sum=self.weight
        if len(self.back_neighbours)==0:
            return sum
        else:
            for i in range(len(self.back_neighbours)):
                value=self.back_neighbours[i].solve_network_output()
                try:
                    sum+=(value*self.factors[i])
                except:
       
                    raise ValueError
            return tanh(sum)

class Network:
    #The basic functionality of the network is in this class.
    #The class offers functions for creating networks and mutating them in various ways.
    #The class also provides with basic checking functions that ensure, that mutation functions don't break the networks.
    #Write and read functions are also provided to save the network. Not sure why anyone would do this but here we are.
    def __init__(self,input_nodes,output_nodes,table):
        if len(table)==0:
            self.number_of_nodes=input_nodes+output_nodes
            self.levels=[]
            self.begins=[i for i in range(input_nodes)]
            self.ends=[i+input_nodes for i in range(output_nodes)]
            self.network_table=[[None for j in range(self.number_of_nodes)] for i in range(self.number_of_nodes)]
            for i in self.begins:
                for j in self.ends:
                    self.network_table[i][j]=r.uniform(-1, 1)
            for i in self.ends:
                self.network_table[i][i]=r.uniform(-2, 2)
            self.primitive=True
            self.id=r.randint(0,999999999)
            self.create_new_network()
        else:
            self.id=r.randint(0,999999999)
            self.number_of_nodes=len(table)
            self.begins=[i for i in range(input_nodes)]
            self.levels=[]
            if self.number_of_nodes!=input_nodes+output_nodes:
                for i in range(input_nodes,len(table)-output_nodes):
                    self.levels.append(i)
            self.primitive=False
            if len(self.levels)==0:
                self.primitive=True
            self.ends=[value for value in range(len(self.begins)+len(self.levels),self.number_of_nodes)]
            self.network_table=table
            self.create_new_network()
    def create_new_network(self):
        self.nodes=[]
        for i in self.begins:
            self.nodes.append(Node(i,self.network_table[i][i]))
        for i in self.levels:
            self.nodes.append(Node(i,self.network_table[i][i]))
        for i in self.ends:
            self.nodes.append(Node(i,self.network_table[i][i]))
        for i in range(len(self.network_table)-1,-1,-1):
            for j in range(i-1,-1,-1):
                if self.network_table[j][i]!=None:
                    self.nodes[i].append_neighbour(self.nodes[j],self.network_table[j][i])
    def calculate_complexicity(self):
        sum=0
        sum+=self.number_of_nodes
        for i in range(len(self.network_table)-1):
            for j in range(i+1,len(self.network_table)):
                if self.network_table[i][j]!=None:
                    sum+=1
        return sum
    def return_network_solution(self,input):
        solutions=[]
        for index in self.begins:
            self.nodes[index].weight=input[index]
        for i in self.ends:
            solutions.append(self.nodes[i].solve_network_output())
        return solutions
    def remove_node(self):
        node=r.choice(self.levels)
        new_table=[[self.network_table[i][j] for j in range(len(self.network_table))]for i in range(len(self.network_table))]
        end_nodes=[]
        first_order_nodes=[]
        for i in range(len(new_table)):
            for j in range(len(new_table)):
                if j==node:
                    if j!=i:
                        if self.network_table[j][i]!=None:
                            first_order_nodes.append(i)
                if i==node:
                    if j!=i:
                        if self.network_table[j][i]!=None:
                            end_nodes.append(j)
        for i in end_nodes:
            for j in first_order_nodes:
                new_table[i][j]=(self.network_table[node][j]+self.network_table[i][node])/2
        for i in range(len(new_table)):
            new_table[node][i]=None
            new_table[i][node]=None
        new_table_two=[[None for j in range(len(new_table)-1)]for i in range(len(new_table)-1)]
        for i in range(len(new_table_two)):
            for j in range(len(new_table_two)):
                if j>=node:
                    if i>=node:
                        new_table_two[i][j]=new_table[i+1][j+1]
                    else:
                        new_table_two[i][j]=new_table[i][j+1]
                else:
                    if i<node:
                        new_table_two[i][j]=new_table[i][j]
        self.network_table=new_table_two
        self.levels=self.levels[:-1]
        for i in range(len(self.ends)):
            self.ends[i]-=1
        self.number_of_nodes-=1
        self.create_new_network()
    def create_new_node(self,mutability=1):
        if mutability==1:
            variablity=r.uniform(0,0.4)
        elif mutability==2:
            variablity=r.uniform(0.4,0.8)
        elif mutability==3:
            variablity=r.uniform(0.8,1.2)
        elif mutability==4:
            variablity=r.uniform(1.2,1.6)
        elif mutability==5:
            variablity=r.uniform(1.6,2)
        lower_bound=0-variablity
        upper_bound=0+variablity
        if len(self.levels)==0:
            self.primitive=False
            reading_value=self.begins[-1]+1
            self.number_of_nodes+=1
            new_table=[[None for j in range(self.number_of_nodes)] for i in range(self.number_of_nodes)]
            for index, line in enumerate((self.network_table)):
                for jindex, value in enumerate(line):
                    if value!=None:
                        if jindex>=reading_value:
                            if index>=reading_value:
                                new_table[index+1][jindex+1]=self.network_table[index][jindex]
                            else:
                                new_table[index][jindex+1]=self.network_table[index][jindex]
            self.network_table=new_table
            for i in range(len(self.ends)):
                self.ends[i]+=1
            node=r.choice(self.ends)
            second_node=r.choice(self.nodes[node-1].back_neighbours).index
            self.network_table[reading_value][node]=self.network_table[second_node][node]
            self.network_table[second_node][reading_value]=1
            self.network_table[second_node][node]=None
            self.network_table[reading_value][reading_value]=r.uniform(lower_bound, upper_bound)
            self.levels.append(reading_value)
            self.create_new_network()
        else:
            reading_value=r.randint(self.begins[-1],self.levels[-1])
            self.number_of_nodes+=1
            new_table=[[None for j in range(self.number_of_nodes)] for i in range(self.number_of_nodes)]
            for index, line in enumerate((self.network_table)):
                for jindex, value in enumerate(line):
                    if value!=None:
                        if index<=reading_value and jindex<=reading_value:
                            new_table[index][jindex]=self.network_table[index][jindex]
                        elif reading_value<jindex and index<=reading_value:
                            new_table[index][jindex+1]=self.network_table[index][jindex]
                        elif reading_value<jindex and index>reading_value:
                            new_table[index+1][jindex+1]=self.network_table[index][jindex]
            self.levels.append(self.levels[-1]+1)
            for i in range(len(self.ends)):
                self.ends[i]+=1
            reading_value+=1
            self.network_table=new_table
            while True:
                node=r.randint(reading_value+1,self.ends[-1])
                apunetwork_list=[]
                for i in range(reading_value):
                    if self.network_table[i][node]!=None:
                        apunetwork_list.append(i)
                try:
                    second_node=r.choice(apunetwork_list)
                    break
                except: continue
            self.network_table[reading_value][reading_value]=r.uniform(lower_bound,upper_bound)
            self.network_table[reading_value][node]=self.network_table[second_node][node]
            self.network_table[second_node][reading_value]=1
            self.network_table[second_node][node]=None
            self.create_new_network()
    def create_new_connection(self,mutability=1):
        if mutability==1:
            variablity=r.uniform(0,0.2)
        elif mutability==2:
            variablity=r.uniform(0.2,0.4)
        elif mutability==3:
            variablity=r.uniform(0.4,0.6)
        elif mutability==4:
            variablity=r.uniform(0.6,0.8)
        elif mutability==5:
            variablity=r.uniform(0.8,1)
        lower_bound=0-variablity
        upper_bound=0+variablity
        sum=0
        if len(self.levels)==0:
            return
        for j in range(0,len(self.network_table)-1):
            for i in range(self.levels[0],len(self.network_table)):
                if j>=i:
                    continue
                if self.network_table[j][i]==None:
                    sum+=1
        if sum==0:
            return
        connection=r.randint(1,sum)
        index=1
        new_table=[[None for j in range(len(self.network_table))] for i in range(len(self.network_table))]
        for i in range(len(self.network_table)):
            for j in range(len(self.network_table)):
                if self.network_table[i][j]!=None:
                    new_table[i][j]=self.network_table[i][j]
        for j in range(len(new_table)-1):
            for i in range(self.levels[0],len(new_table)):
                if j>=i:
                    continue
                if self.network_table[j][i]==None:
                    if index==connection:
                        new_table[j][i]=r.uniform(lower_bound,upper_bound)
                        self.network_table=new_table
                        self.create_new_network()
                        return
                    else:
                        index+=1
        self.create_new_network()
    def check_connection(self):
        if len(self.levels)==0:
            return False
        for j in range(0,len(self.network_table)-1):
            for i in range(self.levels[0],len(self.network_table)):
                if j>=i:
                    continue
                if self.network_table[j][i]==None:
                    return True
        return False
    def check_for_connection_removal(self):
        for i in range(len(self.network_table)):
            connections=0
            for j in range(i+1,len(self.network_table)):
                if j<=self.begins[-1]:
                    continue
                if self.network_table[i][j]!=None:
                    connections+=1
            if connections>=2:
                return True
        return False
    def remove_connection(self):
        if not self.check_for_connection_removal():
            return
        removals=[]
        for i in range(len(self.network_table)-1):
            connections=[]
            for j in range(i+1,len(self.network_table)):
                if j<=self.begins[-1]:
                    continue
                if self.network_table[i][j]!=None:
                    connections.append((i,j))
            for i in connections:
                removals.append(i)
        poisto=r.choice(removals)
        new_table=[[self.network_table[i][j] for j in range(len(self.network_table))] for i in range(len(self.network_table))]
        
        new_table[poisto[0]][poisto[1]]=None
        self.network_table=new_table
        self.create_new_network()
    def mutate_network(self,rate):
        if rate==1:
            network_list=[i for i in range(100)]
        elif rate==2:
            network_list=[i for i in range(80)]
        elif rate==3:
            network_list=[i for i in range(60)]
        elif rate==4:
            network_list=[i for i in range(40)]
        elif rate==5:
            network_list=[i for i in range(20)]
        variablity=rate*0.03
        lower_bound=1-variablity
        upper_bound=1+variablity
        new_table=[[None for j in range(len(self.network_table))] for i in range(len(self.network_table))]
        for index,network_list in enumerate(self.network_table):
            for jindex,value in enumerate(network_list):
                if value!=None:
                    new_table[index][jindex]=self.network_table[index][jindex]
                    if r.choice(network_list)==0:
                        new_table[index][jindex]*=-1
                    if r.randint(1,10)<=rate:
                        new_table[index][jindex]*=r.uniform(lower_bound,upper_bound)
        self.network_table=new_table
        self.create_new_network()
    def return_mutated_network(neural_network,maara,rate):
        network_table=[]
        for i in range(maara):
            # print(neural_network.begins[-1]+1)
            network_table.append(Network(neural_network.begins[-1]+1,len(neural_network.ends),neural_network.network_table))
        for i in range(len(network_table)):
            network_table[i].mutate_network(rate)
        return network_table
    def write(self,filename):
        with open(filename,"w") as file:
            for i in self.network_table:
                write_string=""
                for j in i:
                    write_string+=str(j)
                    write_string+=";"
                write_string=write_string[:-1]
                write_string+="\n"
                file.write(write_string)
            file.write((str(len(self.begins))+"\n"))
            file.write(str(len(self.ends)))
    def read_and_return(filename):
        network_list=[]
        index=0
        with open(filename) as file:
            for i in file:
                network_list.append([])
                i=i.split(";")
                for k in i:
                    k=k.replace("\n","")
                    if k=="None":
                        network_list[index].append(None)
                    else:
                        network_list[index].append(float(k))
                    
                index+=1
        input_nodes=int(network_list[-2][0])
        output_nodes=int(network_list[-1][0])
        return Network(input_nodes,output_nodes,network_list[:-2])


class Evolution:
    #Evolution class hold basic functionality, which ease the use of the learning networks.
    # 1. create_new_networks gives you the new networks with the number of input and output nodes you wish to have.
    # 2. Evolve networks takes in a network and spits out as many networks as you wish.
    # 3. Read and return can be used to read a network from a textfile
    def __init__(self):
        self.mutatibility=5
    def create_new_networks(self,first_order_nodes,end_nodes,complexity_factor=1.1,connection_factor=1.2,number_of_networks=1):
        list_of_networks=[]
        for i in range(number_of_networks):
            possible_connections=0
            neural_network=Network(first_order_nodes,end_nodes,[])
            complexity_now=neural_network.calculate_complexicity()
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
                complexity_now=neural_network.calculate_complexicity()
            list_of_networks.append(neural_network)
        return list_of_networks
    def read_and_return(self,filename):
        return Network.read_and_return(filename)
    def evolve_networks(self,neural_network,complexity=2,mutation_rate=2,amount_of_networks=1):

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
                mutation_factor=(neural_network.calculate_complexicity()-neural_network.number_of_nodes)/len(neural_network.levels)+addition_value
            network_list=[]
            for i in range(amount_of_networks):
                network_list.append(Network(neural_network.begins[-1]+1,len(neural_network.ends),neural_network.network_table))
           
            for i in range(len(network_list)):
                if r.randint(0,1)==1: 
                    for k in range(complexity):
                        if len(network_list[i].levels)==0:
                            network_list[i].create_new_node(mutation_rate)
                            continue
                        if (network_list[i].calculate_complexicity()-network_list[i].number_of_nodes)/len(network_list[i].levels)>=mutation_factor:
                            network_list[i].create_new_node(mutation_rate)
                        else:
                            network_list[i].create_new_connection(mutation_rate)
                else:
                    for k in range(complexity):
                        if len(network_list[i].levels)==0:
                            network_list[i].remove_connection()
                            continue
                        if (network_list[i].calculate_complexicity()-network_list[i].number_of_nodes)/len(network_list[i].levels)>=mutation_factor:
                            network_list[i].remove_connection()
                        else:
                            network_list[i].remove_node()
                for b in range(mutation_rate-1):
                    network_list[i].mutate_network(mutation_rate)
        return network_list



            

        

        




def main():
    verkot=[Network(49,1,[]),Network(49,1,[])]
    network_list=[]
    print(network_list)


if __name__=="__main__":
    main()