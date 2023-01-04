import pygame
from random import randint
import NEMT as et

class tornit:
    def __init__(self,x,y,rajoitin):
        self.reika=325-rajoitin//25
        if self.reika<135:
            self.reika=135
        # print(self.reika)
        leveys=50
        ala=30
        self.alaraja=randint(self.reika+ala,y-ala)
        self.vari=107, 81, 79
        self.positio=(x+5, self.alaraja)        #Ala palkin koko ja sijainti
        self.koko=leveys,y-self.alaraja+5
        self.kokoy=leveys, self.alaraja-self.reika+5   #yläpalkin poskoko
        self.positioy=self.positio[0],-10
        self.rpositio=self.positio[0]-5,self.positio[1]-5   
        self.rkoko=self.koko[0]+10,self.koko[1]+10

        self.rkokoy=self.kokoy[0]+10,self.kokoy[1]+10
        self.rpositioy=self.positioy[0]-5,self.positioy[1]-5
  


    def hae_kokoposyla(self):
        return self.positioy,self.kokoy
    def hae_rkokoposyla(self):
        return self.rpositioy,self.rkokoy
    def hae_rkokoposala(self):
        return self.rpositio,self.rkoko
    def hae_kokoposala(self):
        return self.positio,self.koko
    def hae_vari(self):
        return self.vari
    def liikuta(self):
        luku=3
        self.rpositio=self.rpositio[0]-luku,self.rpositio[1]
        self.rpositioy=self.rpositioy[0]-luku,self.rpositioy[1]
        self.positio=self.positio[0]-luku,self.positio[1]
        self.positioy=self.positioy[0]-luku,self.positioy[1]
    def liikuta_taakse(self):
        luku=-200
        self.rpositio=self.rpositio[0]-luku,self.rpositio[1]
        self.rpositioy=self.rpositioy[0]-luku,self.rpositioy[1]
        self.positio=self.positio[0]-luku,self.positio[1]
        self.positioy=self.positioy[0]-luku,self.positioy[1]
    def liikuta_puolet(self,luku):
        luku+=50
        luku/=3
        self.rpositio=self.rpositio[0]-luku,self.rpositio[1]
        self.rpositioy=self.rpositioy[0]-luku,self.rpositioy[1]
        self.positio=self.positio[0]-luku,self.positio[1]
        self.positioy=self.positioy[0]-luku,self.positioy[1]
    def sijainti(self):

        return self.positio[0]<-50
def tormays(torni,y,x,leveys,korkeus):

    if torni.positio[0]<x+leveys:

        if torni.positio[0]+torni.koko[0] > x:
            
            if torni.positioy[1]+torni.kokoy[1] > y:
                return True
            if torni.positio[1] < y+korkeus:
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
    
    def siirra(self,torni,koko):
        yksi=torni.alaraja-self.height
        suhttorninalaraja=(torni.alaraja-self.height)/koko*2-1
        kaksi=torni.alaraja-torni.reika
        suhttorninylaraja=kaksi/koko*2-1
        suhtbaty=self.y/koko*2-1
        luku=self.verkko.ratkaise([suhtbaty,suhttorninalaraja,suhttorninylaraja,self.nopeus,self.kiihtyvyys*10])
        self.kiihtyvyys+=luku[0]*0.025
        self.nopeus+=self.kiihtyvyys
        self.y+=self.nopeus
    def tarkista(self,torni,korkeus):
        if self.y>korkeus or self.y<0:
            return True
        if torni.positio[0]<self.x+self.leveys:
            if torni.positio[0]+torni.koko[0] > self.x:
                if torni.positioy[1]+torni.kokoy[1] > self.y:
                    return True
                if torni.positio[1] < self.y+self.height:
                    return True
        return False

    def etaisyys(self,alaraja):
        return self.y-alaraja


def aja(lepakot,parastulos,sukupolvi):
    kokox=1000 
    kokoy=800
    aikavali=5000
    rajoitin=0
    pygame.init() 
    naytto = pygame.display.set_mode((kokox, kokoy))
    parastulos="%.2f" % parastulos
    y = kokoy//2
    kiihtyvyys=0.25
    nopeus=0
    kello = pygame.time.Clock()
    torneja=[tornit(kokox,kokoy,rajoitin) for i in range(3)]
    for i in range(len(torneja)):
        for j in range(i):
            torneja[i].liikuta_puolet(kokox)
    for i in torneja:
        i.liikuta_taakse()
    torneja=torneja[::-1]

    poistetut=[]
    score=0

    while True:
        rajoitin+=1
        kuolleet=[]
        poisto=0
        if len(lepakot)==0:
            return poistetut
        for tapahtuma in pygame.event.get():
            if tapahtuma.type==pygame.KEYDOWN:
                if tapahtuma.key == pygame.K_x:
                    aikavali=60
                if tapahtuma.key == pygame.K_c:
                    aikavali+=500
                if tapahtuma.key ==pygame.K_k:
                    kuolleet.append(lepakot[0])
                
            if tapahtuma.type == pygame.QUIT:
                lepakot[0].verkko.printti()
                exit()
        naytto.fill((100,100,100))
        for i in torneja:
            pygame.draw.rect(naytto,(0,0,0),i.hae_rkokoposyla(), border_radius=10)
            pygame.draw.rect(naytto,(0,0,0),i.hae_rkokoposala(), border_radius=10)
            pygame.draw.rect(naytto,i.hae_vari(),i.hae_kokoposala(), border_radius=10)
            pygame.draw.rect(naytto,i.hae_vari(),i.hae_kokoposyla(), border_radius=10)
            i.liikuta()
            if i.sijainti():
                poisto=i
                torneja.append(tornit(kokox,kokoy,rajoitin))
          
        if poisto!=0:
            torneja.remove(poisto)
            score+=1
        del poisto

        for i in lepakot:
            naytto.blit(i.bat1,(i.x,i.y))
            i.siirra(torneja[0],kokoy)
            if i.tarkista(torneja[0],kokoy):
                if i not in kuolleet:
                    kuolleet.append(i)
        # naytto.blit(i.bat1,(i.x,i.y))

        for i in kuolleet:
            lepakot.remove(i)
            virhe=abs((torneja[0].alaraja*2-torneja[0].reika)/2-i.y)/kokoy
            poistetut.append((i,score-virhe))

       
        del kuolleet
        fontti = pygame.font.SysFont("Times New Roman", 24)
        kirjoitus=str(len(lepakot))+" lepakkoa elossa"
        kirjoitus2=str(score)+" tulos ja parastulos on "+str(parastulos)+ " ja sukupolvi on: "+str(sukupolvi) +" ja reika on "+str(torneja[0].reika)

        teksti = fontti.render(kirjoitus, True, (255, 255, 255))
        teksti2 = fontti.render(kirjoitus2, True, (255, 255, 255))

        naytto.blit(teksti, (25, 25))
        naytto.blit(teksti2, (250, 25))
        pygame.display.flip()
        kello.tick(aikavali)
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
        tulokset=aja(lista,parastulos,laskuri)
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
                print("RESETOIDAAN PERKELE")
                print()
                paraslepakko=False
                parastulos=0
                lista=[]
                resetti=10
                laskuri=0
                for i in range(maara+800):
                    lista.append(bat(et.Hermoverkko(5,1,[])))
    






if __name__=="__main__":
    main()
    # taulu=[-0.3762505634544734, None, None, None, None, 1.082797760474402, -0.983521887641549]      ,[None, -0.4225, None, None, None, -0.6028335194733179, 1.11371859207329],[None, None, -0.69, None, None, -0.7165432380404355, -0.3757353654720033],[None, None, None, 0.43180948852656087, None, 0.1436646409937286, -0.09704064134593915]   ,[None, None, None, None, -1.027640626288342, 0.4635572751233232, -0.07501057322029492]    ,[None, None, None, None, None, 0.17494820278566164, -0.34956391861775366],[None, None, None, None, None, None, -0.18651832182041386]
    # aja([bat(et.Hermoverkko(5,1,taulu))],0,0)

    

    