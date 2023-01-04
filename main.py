import pygame
from random import randint,seed
import NEMT as et


#Welcome to my self-written topologically evolving AI algorithm program!


# In this project, I built a learning algorithm to play the game. 
# It's a neural network with a capacity to evolve new hidden nodes and connections. 
# The network is represented as a table.
# The network calculates the values recursively. How fun!

# The reasoning behind this project was to learn how to build a neural network from scratch and from first principles.
# The one difference between the Flappy Bird and Flappy Bat games is that the AI controls the acceleration of the bat, rather than making it jump. 
# This added an extra challenge for the AI, as jump algorithms are relatively easy to find.

#Features:
#  1. A flappy bat game that only an AI can play.
#  2. An AI to play the game.

#Performance:
#  Depending on your luck you can find a solution to the problem in less than 100 generations
#  However, the performance varies wildly. Sometimes you don't even get a minimum viable candidate for 100 generations.
#  Still fun to look at.

class Towers:
    def __init__(self,x,y,reducer):
        #Reducer will grow as the game goes on to make the gaps between towers smaller
        self.hole_between_towers=325-reducer//25
        if self.hole_between_towers<135:
            self.hole_between_towers=135

        #Define tower width
        width=50
        #Define the minimimum distance from floor and ceiling of towers
        boundary_from_edge=30
        self.lower_boundary=randint(self.hole_between_towers+boundary_from_edge,y-boundary_from_edge)
        #Define colors
        self.color=107, 81, 79

        #Position of the floortower
        self.position_lower=x-5, self.lower_boundary 
        self.position_upper=self.position_lower[0],-10
        
        #Define sizes for draw function
        self.lower_size=width,y-self.lower_boundary+5
        self.upper_size=width, self.lower_boundary-self.hole_between_towers+5 

        #Define the border sizes and positions. These serves as the black boarders of the towers
        self.lower_boarder_position=self.position_lower[0]-5,self.position_lower[1]-5
        self.lower_boarder_size=self.lower_size[0]+10,self.lower_size[1]+10

        self.upper_boarder_position=self.position_upper[0]-5,self.position_upper[1]-5
        self.upper_boarder_size=self.upper_size[0]+10,self.upper_size[1]+10
    #Getter functions to get values required by drawing and impact_checking functions
    def get_upper_sizepos(self):
        return self.position_upper,self.upper_size
    def get_upper_boarder_sizepos(self):
        return self.upper_boarder_position,self.upper_boarder_size
    def get_lower_boarder_sizepos(self):
        return self.lower_boarder_position,self.lower_boarder_size
    def get_lower_sizepos(self):
        return self.position_lower,self.lower_size
    def get_color(self):
        return self.color
    def check_if_tower_passed(self):
        return self.position_lower[0]<-50
    #Move functions to move the towers around.
    def move(self):
        move_value=3
        self.lower_boarder_position=self.lower_boarder_position[0]-move_value,self.lower_boarder_position[1]
        self.upper_boarder_position=self.upper_boarder_position[0]-move_value,self.upper_boarder_position[1]
        self.position_lower=self.position_lower[0]-move_value,self.position_lower[1]
        self.position_upper=self.position_upper[0]-move_value,self.position_upper[1]
    def move_backwards(self):
        move_value=-200
        self.lower_boarder_position=self.lower_boarder_position[0]-move_value,self.lower_boarder_position[1]
        self.upper_boarder_position=self.upper_boarder_position[0]-move_value,self.upper_boarder_position[1]
        self.position_lower=self.position_lower[0]-move_value,self.position_lower[1]
        self.position_upper=self.position_upper[0]-move_value,self.position_upper[1]
    def move_half(self,move_value):
        move_value+=50
        move_value/=3
        self.lower_boarder_position=self.lower_boarder_position[0]-move_value,self.lower_boarder_position[1]
        self.upper_boarder_position=self.upper_boarder_position[0]-move_value,self.upper_boarder_position[1]
        self.position_lower=self.position_lower[0]-move_value,self.position_lower[1]
        self.position_upper=self.position_upper[0]-move_value,self.position_upper[1]
class Bat:
    def __init__(self,network):
        #Randomize the images so the bats look different
        if randint(0,1)==1:
            self.bat1=pygame.image.load("flap1.png")
            self.bat2=pygame.image.load("flap2.png")
        else: 
            self.bat1=pygame.image.load("flap2.png")
            self.bat2=pygame.image.load("flap1.png")

        #Define values such as size, position, speed, acceleration and the network
        self.height=self.bat1.get_height()-10
        self.width=self.bat1.get_width()
        self.speed=0
        self.y=500
        self.x=60
        self.network=network
        self.acceleration=0
    def move_bat(self,tower,size):
        #The network gets the relative vales for positions rather than absolute values. Seems to ease the work of the network

        #Solve relative positions of towers
        lower_relative_tower_position=(tower.lower_boundary-self.height)/size*2-1
        upper_relative_tower_position=(tower.lower_boundary-tower.hole_between_towers)/size*2-1

        #Solve relative position of bat
        relative_bat_location=self.y/size*2-1

        #Give the network some values to solve. Values are tower positions, bat position, speed and acceleration * 10
        network_output=self.network.return_network_solution([relative_bat_location,lower_relative_tower_position,upper_relative_tower_position,self.speed,self.acceleration*10])
        
        #Change acceleration adjusted by a lot
        self.acceleration+=network_output[0]*0.025
        #Apply effects
        self.speed+=self.acceleration
        self.y+=self.speed
    def check_impact(self,tower,height):
        #Check if the bat collides with a tower

        #Check floor and ceiling
        if self.y>height or self.y<0:
            return True
        #Check contact with towers
        if tower.position_lower[0]<self.x+self.width:
            if tower.position_lower[0]+tower.lower_size[0] > self.x:
                if tower.position_upper[1]+tower.upper_size[1] > self.y:
                    return True
                if tower.position_lower[1] < self.y+self.height:
                    return True
        return False
def run_with_pygame(bats_to_run,best_score,generation):
    #A pygame function to simulate the competition
    #Basically does the following things
    #  1. Move towers
    #  2. Move bats
    #  3. check for collisions
    #  4. score the bats performance

    #Seed is set to one, because it produces a hard obstacle in the beginning of the course.
    #Better to find one network who can actually react to the obstacles than get randomly obstacles,
    #which you can get through just by staying still

    seed(1)

    #reducer variable allows the reduction of the gap size between towers, making it progressively harder.
    reducer=0

    #Define screen size and tickrate
    size_x=1000 
    upper_size=800
    tickrate=0
    
    #init and set screen and clock
    pygame.init() 
    screen = pygame.display.set_mode((size_x, upper_size))
    clock = pygame.time.Clock()

    #Define towers and adjust the positions for the start
    towers=[Towers(size_x,upper_size,reducer) for i in range(3)]

    for i in range(len(towers)):
        for j in range(i):
            towers[i].move_half(size_x)
    for i in towers:
        i.move_backwards()
    towers=towers[::-1]

    #Format best score
    best_score="%.2f" % best_score

    #removed_bats holds the ones who've died. The list will also hold the relative score of the dead bat
    removed_bats=[]
    score=0


    #Pygame style while loop
    while True:
        reducer+=1
        
        #remover helper list stores dead bats within to push them to removed bats
        bat_remover_helper_list=[]
        deletion_value=0
        
        #If all the bats have died, stop simulation by returning the removed_bats
        if len(bats_to_run)==0:
            return removed_bats

        #Check for events
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                #Change framerate, x to normalize and c to accelerate
                if event.key == pygame.K_x:
                    tickrate=60
                if event.key == pygame.K_c:
                    tickrate=0
            #Quit button
            if event.type == pygame.QUIT:
                exit()
        
        #Time for pygame stuff. Fill screen and draw towers. Check if tower has passed to remove it and add a new one
        screen.fill((100,100,100))
        for i in towers:
            pygame.draw.rect(screen,(0,0,0),i.get_upper_boarder_sizepos(), border_radius=10)
            pygame.draw.rect(screen,(0,0,0),i.get_lower_boarder_sizepos(), border_radius=10)
            pygame.draw.rect(screen,i.get_color(),i.get_lower_sizepos(), border_radius=10)
            pygame.draw.rect(screen,i.get_color(),i.get_upper_sizepos(), border_radius=10)
            i.move()
            if i.check_if_tower_passed():
                deletion_value=i
                towers.append(Towers(size_x,upper_size,reducer))
        
        #remove the passed towers and also increment the score
        if deletion_value!=0:
            towers.remove(deletion_value)
            score+=1
        del deletion_value  #Not sure if this is needed

        #Iterate over the bats
        for i in bats_to_run:

            #Draw the bat
            screen.blit(i.bat1,(i.x,i.y))

            #Move the bat using fancy neural network
            i.move_bat(towers[0],upper_size)

            #Check if bat has hit a tower, floor or ceiling. If so, add to helper list
            if i.check_impact(towers[0],upper_size):
                if i not in bat_remover_helper_list:
                    bat_remover_helper_list.append(i)

        #Remove the failed bats, adjust the score by how much the bat was off from the window and add it to the remove bats list with it's score
        for i in bat_remover_helper_list:
            bats_to_run.remove(i)
            mistake_value=abs((towers[0].lower_boundary*2-towers[0].hole_between_towers)/2-i.y)/upper_size
            removed_bats.append((i,score-mistake_value))

       
        del bat_remover_helper_list

        #Write basic info on screen to get a sense of what has happened
        font = pygame.font.SysFont("Times New Roman", 24)
        writing_one=str(len(bats_to_run))+" Bats alive. Current Score: "+str(score) + " Generation: "+str(generation)
        writing_2="Best_score: "+str(best_score) +" Hole_between_towers: "+str(towers[0].hole_between_towers)

        text = font.render(writing_one, True, (255, 255, 255))
        text2 = font.render(writing_2, True, (255, 255, 255))

        screen.blit(text, (25, 25))
        screen.blit(text2, (25, 50))
        pygame.display.flip()
        clock.tick(tickrate)
def run_without_pygame(bats_to_run,generation):
    #A copy of the other run function without displaying the progress.

    seed(1)
    #reducer variable allows the restriction of the 'window' size. Note if you run the program, the distance between the upper and lower tower gets smaller
    reducer=0

    #Define screen size and tickrate
    size_x=1000 
    upper_size=800
    pygame.init() 
    screen = pygame.display.set_mode((size_x, upper_size))
    screen.fill((0,0,0))
    font = pygame.font.SysFont("Times New Roman", 24)
    writing_one="Finding minimun viable network. Generation:"+str(generation)+". This can take up to 40-100 generations"
    text = font.render(writing_one, True, (255, 255, 255))
    screen.blit(text, (25, 25))
    writing_one="Each generation has 1000 networks. The min viable network prevents local maximum 'stuckness'"
    text = font.render(writing_one, True, (255, 255, 255))
    screen.blit(text, (25, 60))
    pygame.display.flip()

    

    #Define towers and adjust the positions for the start
    towers=[Towers(size_x,upper_size,reducer) for i in range(3)]
    for i in range(len(towers)):
        for j in range(i):
            towers[i].move_half(size_x)
    for i in towers:
        i.move_backwards()
    towers=towers[::-1]

    #removed_bats holds the ones who've died. The list will also hold the relative score of the dead bat
    removed_bats=[]
    score=0


    #Pygame style while loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        reducer+=1
        
        #remover helper list stores dead bats within a to push them to removed bats
        bat_remover_helper_list=[]
        deletion_value=0
        
        #If all the bats have died, stop simulation by returning the removed_bats
        if len(bats_to_run)==0:
            return removed_bats

        #Move towers and check for removals
        for i in towers:
            i.move()
            if i.check_if_tower_passed():
                deletion_value=i
                towers.append(Towers(size_x,upper_size,reducer))
        
        #remove the passed towers and also increment the score
        if deletion_value!=0:
            towers.remove(deletion_value)
            score+=1
        del deletion_value  #Not sure if this is needed

        #Iterate over the bats
        for i in bats_to_run:
            #Move the bat using fancy neural network
            i.move_bat(towers[0],upper_size)
            #Check if bat has hit a tower, floor or ceiling. If so, add to helper list
            if i.check_impact(towers[0],upper_size):
                if i not in bat_remover_helper_list:
                    bat_remover_helper_list.append(i)

        #Remove the failed bats, adjust the score by how much the bat was off from the window and add it to the remove bats list with it's score
        for i in bat_remover_helper_list:
            bats_to_run.remove(i)
            mistake_value=abs((towers[0].lower_boundary*2-towers[0].hole_between_towers)/2-i.y)/upper_size
            removed_bats.append((i,score-mistake_value))

        #Delete the list to ensure no errors
        del bat_remover_helper_list
def main():
    #Begin AI program

    #Set values
    best_score=0
    number_of_initial_bats=500
    bat_list=[]
    best_bat_network=False

    #Initialize the evolution object:
    evolution_object=et.Evolution()

    #Define a boolean for running pygame. This won't be done untill a first viable candidate has been found
    miminum_viable_network_found=False

    bat_list=[Bat(network) for network in evolution_object.create_new_networks(5,1,number_of_networks=number_of_initial_bats*2)]
    counter=0
    reset_value=10
    while True:
        counter+=1
        #If minimum viable network found, we begin simulating the learning process. No point wasting cpu power on simulating failures
        if miminum_viable_network_found:
            results_of_simulation=run_with_pygame(bat_list,best_score,counter)
        else:
            results_of_simulation=run_without_pygame(bat_list,counter)

        #Sort the bats in reverse. Best is first
        results_of_simulation.sort(reverse=True,key = lambda x:x[1])

        #Reset seed so network evolution works. Seed is set to 1 in the actual game to shape the obstacle course.
        seed()

        #If one of the bats get beyond 8 towers, we have found a viable candidate.
        if results_of_simulation[0][1]<8:
            #If not, keep simulating
            bat_list=[Bat(network) for network in evolution_object.create_new_networks(5,1,number_of_networks=number_of_initial_bats*2)]
        else:
            miminum_viable_network_found=True
            #Some boolean checks.
            #Best_bat_network is false when the first minimal viable candidate has been found.
            if best_bat_network == False:
                #The best bat is used to produce more networks
                best_bat_network=results_of_simulation[0][0].network
                best_score=results_of_simulation[0][1]

            elif results_of_simulation[0][1]>best_score:
                #Stagnation check basically. If new highscore, update the score and best_bat
                best_bat_network=results_of_simulation[0][0].network
                best_score=results_of_simulation[0][1]
            else:
                #If stagnatated, the reset value get decremented
                reset_value-=1
            
            #If the round didn't produce any improvements, then second best bat is the best bat from this round
            #Basically the first two bats are either best two from this round, or best one from both this round and last round
            if results_of_simulation[0][0].network==best_bat_network:
                #Or if there was an improvement, then we get the second bat from this round.
                second_best_bat_network=results_of_simulation[1][0].network
            else: second_best_bat_network=results_of_simulation[0][0].network
            

            #Making new networks with best and second best bat
            #Some use complexity=0 to reduce the growing size and complexity of the new network
            evolved_bats=evolution_object.evolve_networks(best_bat_network,amount_of_networks=number_of_initial_bats//4)
            evolved_bats+=evolution_object.evolve_networks(best_bat_network,complexity=0,amount_of_networks=number_of_initial_bats//4)
            evolved_bats+=evolution_object.evolve_networks(second_best_bat_network,amount_of_networks=number_of_initial_bats//4)
            evolved_bats+=evolution_object.evolve_networks(second_best_bat_network,complexity=0,amount_of_networks=number_of_initial_bats//4)

            #Make new bat objects and give them some networks.
            bat_list=[Bat(best_bat_network),Bat(second_best_bat_network)]
            bat_list+=[Bat(network) for network in  evolved_bats]

            if reset_value==0:
                #This implicates stagnation. I bet no-one has the patiency to get to this point.
                print("Stagnated, resetting the search")
                best_bat_network=False
                miminum_viable_network_found=False
                best_score=0
                reset_value=10
                counter=0
                bat_list=[Bat(et.Network(5,1,[])) for bat in range(number_of_initial_bats*2)]
if __name__=="__main__":
    main()

    

    