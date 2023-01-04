import pygame
from random import randint
import NEMT as et

class Towers:
    def __init__(self,x,y,reducer):
        #Reducer will grow as the game goes on to make the gaps between towers smaller
        self.hole_between_towers=325-reducer//25
        if self.hole_between_towers<135:
            self.hole_between_towers=135

            
        width=50
        boundary_from_edge=30
        self.lower_boundary=randint(self.hole_between_towers+boundary_from_edge,y-boundary_from_edge)
        self.color=107, 81, 79
        self.lower_position=(x+5, self.lower_boundary) 

        self.size=width,y-self.lower_boundary+5
        self.size_y=width, self.lower_boundary-self.hole_between_towers+5 
        self.position_upper=self.lower_position[0],-10
        self.border_position_lower=self.lower_position[0]-5,self.lower_position[1]-5   
        self.rsize=self.size[0]+10,self.size[1]+10

        self.rsize_y=self.size_y[0]+10,self.size_y[1]+10
        self.border_position_upper=self.position_upper[0]-5,self.position_upper[1]-5

    def get_upper_sizepos(self):
        return self.position_upper,self.size_y
    def get_upper_boarder_sizepos(self):
        return self.border_position_upper,self.rsize_y
    def get_lower_boarder_sizepos(self):
        return self.lower_position,self.rsize
    def get_lower_sizepos(self):
        return self.lower_position,self.size
    def get_color(self):
        return self.color
    def move(self):
        move_value=3
        self.border_position_lower=self.border_position_lower[0]-move_value,self.border_position_lower[1]
        self.border_position_upper=self.border_position_upper[0]-move_value,self.border_position_upper[1]
        self.lower_position=self.lower_position[0]-move_value,self.lower_position[1]
        self.position_upper=self.position_upper[0]-move_value,self.position_upper[1]
    def move_backwards(self):
        move_value=-200
        self.border_position_lower=self.border_position_lower[0]-move_value,self.border_position_lower[1]
        self.border_position_upper=self.border_position_upper[0]-move_value,self.border_position_upper[1]
        self.lower_position=self.lower_position[0]-move_value,self.lower_position[1]
        self.position_upper=self.position_upper[0]-move_value,self.position_upper[1]
    def move_half(self,move_value):
        move_value+=50
        move_value/=3
        self.border_position_lower=self.border_position_lower[0]-move_value,self.border_position_lower[1]
        self.border_position_upper=self.border_position_upper[0]-move_value,self.border_position_upper[1]
        self.lower_position=self.lower_position[0]-move_value,self.lower_position[1]
        self.position_upper=self.position_upper[0]-move_value,self.position_upper[1]
    def location(self):
        return self.lower_position[0]<-50

def check_impact(tower,y,x,leveys,korkeus):

    if tower.lower_position[0]<x+leveys:

        if tower.lower_position[0]+tower.size[0] > x:
            
            if tower.position_upper[1]+tower.size_y[1] > y:
                return True
            if tower.lower_position[1] < y+korkeus:
                return True

class bat:
    def __init__(self,verkko):
        if randint(0,1)==1:
            self.bat1=pygame.image.load("flap1.png")
            self.bat2=pygame.image.load("flap2.png")
        else: 
            self.bat1=pygame.image.load("flap2.png")
            self.bat2=pygame.image.load("flap1.png")
        self.height=self.bat1.get_height()-10
        self.leveys=self.bat1.get_width()
        self.y=500
        self.nopeus=0
        self.x=60
        self.verkko=verkko
        self.kiihtyvyys=0
        self.luku=0
    
    def siirra(self,tower,size):
        suhttowernalaraja=(tower.lower_boundary-self.height)/size*2-1
        kaksi=tower.lower_boundary-tower.hole_between_towers
        suhttowern_upperraja=kaksi/size*2-1
        suhtbaty=self.y/size*2-1
        luku=self.verkko.ratkaise([suhtbaty,suhttowernalaraja,suhttowern_upperraja,self.nopeus,self.kiihtyvyys*10])
        self.kiihtyvyys+=luku[0]*0.025
        self.nopeus+=self.kiihtyvyys
        self.y+=self.nopeus
    def tarkista(self,tower,korkeus):
        if self.y>korkeus or self.y<0:
            return True
        if tower.lower_position[0]<self.x+self.leveys:
            if tower.lower_position[0]+tower.size[0] > self.x:
                if tower.position_upper[1]+tower.size_y[1] > self.y:
                    return True
                if tower.lower_position[1] < self.y+self.height:
                    return True
        return False

    def etaisyys(self,alaraja):
        return self.y-alaraja


def run(lepakot,parastulos,sukupolvi):
    size_x=1000 
    size_y=800
    tickrate=5000
    reducer=0
    pygame.init() 
    naytto = pygame.display.set_mode((size_x, size_y))
    parastulos="%.2f" % parastulos
    kello = pygame.time.Clock()
    torneja=[Towers(size_x,size_y,reducer) for i in range(3)]
    for i in range(len(torneja)):
        for j in range(i):
            torneja[i].move_half(size_x)
    for i in torneja:
        i.move_backwards()
    torneja=torneja[::-1]

    poistetut=[]
    score=0

    while True:
        reducer+=1
        kuolleet=[]
        poisto=0
        if len(lepakot)==0:
            return poistetut
        for tapahtuma in pygame.event.get():
            if tapahtuma.type==pygame.KEYDOWN:
                if tapahtuma.key == pygame.K_x:
                    tickrate=60
                if tapahtuma.key == pygame.K_c:
                    tickrate+=500
                if tapahtuma.key ==pygame.K_k:
                    kuolleet.append(lepakot[0])
                
            if tapahtuma.type == pygame.QUIT:
                lepakot[0].verkko.printti()
                exit()
        naytto.fill((100,100,100))
        for i in torneja:
            pygame.draw.rect(naytto,(0,0,0),i.get_upper_boarder_sizepos(), border_radius=10)
            pygame.draw.rect(naytto,(0,0,0),i.get_lower_boarder_sizepos(), border_radius=10)
            pygame.draw.rect(naytto,i.get_color(),i.get_lower_sizepos(), border_radius=10)
            pygame.draw.rect(naytto,i.get_color(),i.get_upper_sizepos(), border_radius=10)
            i.move()
            if i.location():
                poisto=i
                torneja.append(Towers(size_x,size_y,reducer))
          
        if poisto!=0:
            torneja.remove(poisto)
            score+=1
        del poisto

        for i in lepakot:
            naytto.blit(i.bat1,(i.x,i.y))
            i.siirra(torneja[0],size_y)
            if i.tarkista(torneja[0],size_y):
                if i not in kuolleet:
                    kuolleet.append(i)
        # naytto.blit(i.bat1,(i.x,i.y))

        for i in kuolleet:
            lepakot.remove(i)
            virhe=abs((torneja[0].lower_boundary*2-torneja[0].hole_between_towers)/2-i.y)/size_y
            poistetut.append((i,score-virhe))

       
        del kuolleet
        fontti = pygame.font.SysFont("Times New Roman", 24)
        kirjoitus=str(len(lepakot))+" Bats alive. Current Score: "+str(score) + " Generation: "+str(sukupolvi)
        kirjoitus2="Best_score: "+str(parastulos) +" Hole_between_towers: "+str(torneja[0].hole_between_towers)

        teksti = fontti.render(kirjoitus, True, (255, 255, 255))
        teksti2 = fontti.render(kirjoitus2, True, (255, 255, 255))

        naytto.blit(teksti, (25, 25))
        naytto.blit(teksti2, (25, 50))
        pygame.display.flip()
        kello.tick(tickrate)
        # score+=1
         

def main():
    parastulos=0
    maara=200
    lista=[]
    paraslepakko=False
    for i in range(maara+800):
        lista.append(bat(et.Hermoverkko(5,1,[])))
    laskuri=0
    resetti=10
    while True:
        laskuri+=1
        tulokset=run(lista,parastulos,laskuri)
        tulokset.sort(reverse=True,key = lambda x:x[1])
        if tulokset[0][1]<8:
            lista=[]
            laskuri-=1
            for i in range(maara+800):
                lista.append(bat(et.Hermoverkko(5,1,[])))
        else:
            
            if paraslepakko == False:
                paraslepakko=tulokset[0][0].verkko
                parastulos=tulokset[0][1]
            elif tulokset[0][1]>parastulos:
                paraslepakko=tulokset[0][0].verkko
                # paraslepakko.printtaa()
                print("Löytyi uusi parannus, joka on:")
                parastulos=tulokset[0][1]
            else:
                resetti-=1
            if tulokset[0][0].verkko==paraslepakko:
                toinenlepakko=tulokset[1][0].verkko
            else: toinenlepakko=tulokset[0][0].verkko
            
            print(paraslepakko.painosumma(),"Paraslepakko")
            paraslepakko.printtaa()
            print(toinenlepakko.painosumma(),"Toinenlepakko")
            toinenlepakko.printtaa()

   
           
            # uudet=et.Hermoverkko.evoluutio_strategia_yksi(evoluutiolista,maara)
            stratkaksi=et.Hermoverkko.evoluutio_strategia_kaksi(paraslepakko,maara//2)
            stratkolme=et.Hermoverkko.evoluutio_strategia_kaksi(toinenlepakko,maara//2)
            
       
    

    
            lista=[]
            lista.append(bat(paraslepakko))
            lista.append(bat(toinenlepakko))
            for i in stratkaksi:
                lista.append(bat(i))
            for i in stratkolme:
                lista.append(bat(i))
            for i in range(450):
                lista.append(bat(et.Hermoverkko(5,1,[])))
            if resetti==0:
                print()
                print("Resetting the search")
                print()
                paraslepakko=False
                parastulos=0
                lista=[]
                resetti=10
                laskuri=0
                for i in range(maara+800):
                    lista.append(bat(et.Hermoverkko(5,1,[])))
    




#THIS IS FORKPUSHTESTTOSEEIFWORKSORNOT

if __name__=="__main__":
    main()
    # taulu=[-0.3762505634544734, None, None, None, None, 1.082797760474402, -0.983521887641549]      ,[None, -0.4225, None, None, None, -0.6028335194733179, 1.11371859207329],[None, None, -0.69, None, None, -0.7165432380404355, -0.3757353654720033],[None, None, None, 0.43180948852656087, None, 0.1436646409937286, -0.09704064134593915]   ,[None, None, None, None, -1.027640626288342, 0.4635572751233232, -0.07501057322029492]    ,[None, None, None, None, None, 0.17494820278566164, -0.34956391861775366],[None, None, None, None, None, None, -0.18651832182041386]
    # aja([bat(et.Hermoverkko(5,1,taulu))],0,0)

    

    