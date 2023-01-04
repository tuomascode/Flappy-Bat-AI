import pygame
from random import randint,seed
import NEMT as et

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
        network_output=self.network.ratkaise([relative_bat_location,lower_relative_tower_position,upper_relative_tower_position,self.speed,self.acceleration*10])
        
        #Change acceleration adjusted by a lot
        self.acceleration+=network_output[0]*0.025
        #Apply effects
        self.speed+=self.acceleration
        self.y+=self.speed
    def check_impact(self,tower,height):
        #Check if the bat collides with a tower

        if self.y>height or self.y<0:
            return True
        if tower.position_lower[0]<self.x+self.width:
            if tower.position_lower[0]+tower.lower_size[0] > self.x:
                if tower.position_upper[1]+tower.upper_size[1] > self.y:
                    return True
                if tower.position_lower[1] < self.y+self.height:
                    return True
        return False
def run(bats_to_run,best_score,generation):
    #A pygame function to simulate the competition
    #Basically does the following things
    #  1. Move towers
    #  2. Move bats
    #  3. check for collisions
    #  4. score the bats performance

    seed(1)
    #reducer variable allows the restriction of the 'window' size. Note if you run the program, the distance between the upper and lower tower gets smaller
    reducer=0

    #Define screen size and tickrate
    size_x=1000 
    upper_size=800
    tickrate=5000
    
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
        
        #remover helper list stores dead bats within a to push them to removed bats
        bat_remover_helper_list=[]
        deletion_value=0
        
        #If all the bats have died, stop simulation by returning the removed_bats
        if len(bats_to_run)==0:
            return removed_bats

        #Check for events
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                #Change framerate
                if event.key == pygame.K_x:
                    tickrate=60
                if event.key == pygame.K_c:
                    tickrate+=500

            if event.type == pygame.QUIT:
                exit()
        
        #Time for pygame stuff. Fill screen and draw towers. Check if tower has passed to remove it and a new one
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
         

def main():
    #Begin AI program
    #Set values
    best_score=0
    number_of_initial_bats=500
    bat_list=[]
    best_bat_network=False

    #Initialize the evolution object:
    evolution_object=et.Evoluutio()

    for i in range(number_of_initial_bats):
        bat_list.append(Bat(et.Hermoverkko(5,1,[])))
    counter=0
    reset_value=10
    while True:
        counter+=1
        results_of_simulation=run(bat_list,best_score,counter)
        results_of_simulation.sort(reverse=True,key = lambda x:x[1])
        seed()

        if results_of_simulation[0][1]<8:
            bat_list=[Bat(et.Hermoverkko(5,1,[])) for bat in range(number_of_initial_bats)]
        else:
            if best_bat_network == False:
                best_bat_network=results_of_simulation[0][0].network
                best_score=results_of_simulation[0][1]
            elif results_of_simulation[0][1]>best_score:
                best_bat_network=results_of_simulation[0][0].network
                best_score=results_of_simulation[0][1]
            else:
                reset_value-=1
            if results_of_simulation[0][0].network==best_bat_network:
                second_best_bat_network=results_of_simulation[1][0].network
            else: second_best_bat_network=results_of_simulation[0][0].network
            
          
   
        
            evolved_bats=evolution_object.evoluutio_strategia_2dim(best_bat_network,maara=number_of_initial_bats//2)
            evolved_bats+=evolution_object.evoluutio_strategia_2dim(second_best_bat_network,maara=number_of_initial_bats//2)

    
            bat_list=[]
            bat_list.append(Bat(best_bat_network))
            bat_list.append(Bat(second_best_bat_network))
            bat_list+= [Bat(network) for network in  evolved_bats]

            if reset_value==0:
                print()
                print("Stagnation, resetting the search")
                print()
                best_bat_network=False
                best_score=0
                bat_list=[]
                reset_value=10
                counter=0
                for i in range(number_of_initial_bats):
                    bat_list.append(Bat(et.Hermoverkko(5,1,[])))
    





if __name__=="__main__":
    main()

    

    