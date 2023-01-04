
import random as r
from math import tanh
import time
class Hermosolu():
    def __init__(self,index,weight):
        self.index=index
        self.back_neighbours=[]
        self.factors=[]
        self.weight=weight
    def append_neighbour(self,naapuri,kerroin):
        # print(f"lisattiin kytkös joka saapuu soluun numero {self.index} solusta numero {naapuri.index}")
        self.factors.append(kerroin)
        self.back_neighbours.append(naapuri)
    def solve_network_output(self):
        sum=self.weight
        if len(self.back_neighbours)==0:
            return sum
        else:
            for i in range(len(self.back_neighbours)):
                luku=self.back_neighbours[i].solve_network_output()
                try:
                    sum+=(luku*self.factors[i])
                except:
       
                    raise ValueError
            return tanh(sum)

class Hermoverkko:
    def __init__(self,aloitussolmut,lopetussolmut,taulukko):
        if len(taulukko)==0:
            self.solumaara=aloitussolmut+lopetussolmut
            self.tasot=[]
            self.alut=[i for i in range(aloitussolmut)]
            self.loput=[i+aloitussolmut for i in range(lopetussolmut)]
            self.taulukko=[[None for j in range(self.solumaara)] for i in range(self.solumaara)]
            for i in self.alut:
                for j in self.loput:
                    self.taulukko[i][j]=r.uniform(-1, 1)
            for i in self.loput:
                self.taulukko[i][i]=r.uniform(-2, 2)
            self.primitive=True
            self.id=r.randint(0,999999999)
            self.luo_hermoverkko()
        else:
            self.id=r.randint(0,999999999)
            self.solumaara=len(taulukko)
            self.alut=[i for i in range(aloitussolmut)]
            self.tasot=[]
            if self.solumaara!=aloitussolmut+lopetussolmut:
                for i in range(aloitussolmut,len(taulukko)-lopetussolmut):
                    self.tasot.append(i)
            self.primitive=False
            if len(self.tasot)==0:
                self.primitive=True
            self.loput=[luku for luku in range(len(self.alut)+len(self.tasot),self.solumaara)]
            self.taulukko=taulukko
            self.luo_hermoverkko()
    def luo_hermoverkko(self):
        self.solut=[]
        for i in self.alut:
            self.solut.append(Hermosolu(i,self.taulukko[i][i]))
        for i in self.tasot:
            self.solut.append(Hermosolu(i,self.taulukko[i][i]))
        for i in self.loput:
            self.solut.append(Hermosolu(i,self.taulukko[i][i]))
        for i in range(len(self.taulukko)-1,-1,-1):
            for j in range(i-1,-1,-1):
                if self.taulukko[j][i]!=None:
                    self.solut[i].append_neighbour(self.solut[j],self.taulukko[j][i])
    def laske_kompleksisuus(self):
        sum=0
        sum+=self.solumaara
        for i in range(len(self.taulukko)-1):
            for j in range(i+1,len(self.taulukko)):
                if self.taulukko[i][j]!=None:
                    sum+=1
        return sum
    def laske_mahdolliset_yhteydet(self):
        sum=0
        for i in range(len(self.taulukko)-1):
            for j in range(i+1,len(self.taulukko)):
                if self.taulukko[i][j]==None:
                    sum+=1
        return sum
    def ratkaise(self,input):
        ratkaisut=[]
        for index in self.alut:
            self.solut[index].weight=input[index]
        for i in self.loput:
            ratkaisut.append(self.solut[i].solve_network_output())
        return ratkaisut
    def tarkista_solmun_poisto(self):
        if len(self.tasot)!=0:
            return True
        else: return False
    def poista_solmu(self):
        solmu=r.choice(self.tasot)
        uusitaulu=[[self.taulukko[i][j] for j in range(len(self.taulukko))]for i in range(len(self.taulukko))]
        loppusolmut=[]
        alkusolmut=[]
        for i in range(len(uusitaulu)):
            for j in range(len(uusitaulu)):
                if j==solmu:
                    if j!=i:
                        if self.taulukko[j][i]!=None:
                            alkusolmut.append(i)
                if i==solmu:
                    if j!=i:
                        if self.taulukko[j][i]!=None:
                            loppusolmut.append(j)
        for i in loppusolmut:
            for j in alkusolmut:
                uusitaulu[i][j]=(self.taulukko[solmu][j]+self.taulukko[i][solmu])/2
        for i in range(len(uusitaulu)):
            uusitaulu[solmu][i]=None
            uusitaulu[i][solmu]=None
        uusitaulukaksi=[[None for j in range(len(uusitaulu)-1)]for i in range(len(uusitaulu)-1)]
        for i in range(len(uusitaulukaksi)):
            for j in range(len(uusitaulukaksi)):
                if j>=solmu:
                    if i>=solmu:
                        uusitaulukaksi[i][j]=uusitaulu[i+1][j+1]
                    else:
                        uusitaulukaksi[i][j]=uusitaulu[i][j+1]
                else:
                    if i<solmu:
                        uusitaulukaksi[i][j]=uusitaulu[i][j]
        self.taulukko=uusitaulukaksi
        self.tasot=self.tasot[:-1]
        for i in range(len(self.loput)):
            self.loput[i]-=1
        self.solumaara-=1
        self.luo_hermoverkko()
    def luo_uusi_solmu(self,mutability):
        if mutability==1:
            heitto=r.uniform(0,0.4)
        elif mutability==2:
            heitto=r.uniform(0.4,0.8)
        elif mutability==3:
            heitto=r.uniform(0.8,1.2)
        elif mutability==4:
            heitto=r.uniform(1.2,1.6)
        elif mutability==5:
            heitto=r.uniform(1.6,2)
        ala=0-heitto
        yla=0+heitto
        if len(self.tasot)==0:
            self.primitive=False
            lukema=self.alut[-1]+1
            self.solumaara+=1
            uusitaulu=[[None for j in range(self.solumaara)] for i in range(self.solumaara)]
            for index, rivi in enumerate((self.taulukko)):
                for jindex, luku in enumerate(rivi):
                    if luku!=None:
                        if jindex>=lukema:
                            if index>=lukema:
                                uusitaulu[index+1][jindex+1]=self.taulukko[index][jindex]
                            else:
                                uusitaulu[index][jindex+1]=self.taulukko[index][jindex]
            self.taulukko=uusitaulu
            for i in range(len(self.loput)):
                self.loput[i]+=1
            solmu=r.choice(self.loput)
            toinensolmu=r.choice(self.solut[solmu-1].back_neighbours).index
            self.taulukko[lukema][solmu]=self.taulukko[toinensolmu][solmu]
            self.taulukko[toinensolmu][lukema]=1
            self.taulukko[toinensolmu][solmu]=None
            self.taulukko[lukema][lukema]=r.uniform(ala, yla)
            self.tasot.append(lukema)
            self.luo_hermoverkko()
        else:
            lukema=r.randint(self.alut[-1],self.tasot[-1])
            self.solumaara+=1
            uusitaulu=[[None for j in range(self.solumaara)] for i in range(self.solumaara)]
            for index, rivi in enumerate((self.taulukko)):
                for jindex, luku in enumerate(rivi):
                    if luku!=None:
                        if index<=lukema and jindex<=lukema:
                            uusitaulu[index][jindex]=self.taulukko[index][jindex]
                        elif lukema<jindex and index<=lukema:
                            uusitaulu[index][jindex+1]=self.taulukko[index][jindex]
                        elif lukema<jindex and index>lukema:
                            uusitaulu[index+1][jindex+1]=self.taulukko[index][jindex]
            self.tasot.append(self.tasot[-1]+1)
            for i in range(len(self.loput)):
                self.loput[i]+=1
            lukema+=1
            self.taulukko=uusitaulu
            while True:
                solmu=r.randint(lukema+1,self.loput[-1])
                apulista=[]
                for i in range(lukema):
                    if self.taulukko[i][solmu]!=None:
                        apulista.append(i)
                try:
                    toinensolmu=r.choice(apulista)
                    break
                except: continue
            self.taulukko[lukema][lukema]=r.uniform(ala, yla)
            self.taulukko[lukema][solmu]=self.taulukko[toinensolmu][solmu]
            self.taulukko[toinensolmu][lukema]=1
            self.taulukko[toinensolmu][solmu]=None
            self.luo_hermoverkko()
    def luo_uusi_yhteys(self,mutability):
        if mutability==1:
            heitto=r.uniform(0,0.2)
        elif mutability==2:
            heitto=r.uniform(0.2,0.4)
        elif mutability==3:
            heitto=r.uniform(0.4,0.6)
        elif mutability==4:
            heitto=r.uniform(0.6,0.8)
        elif mutability==5:
            heitto=r.uniform(0.8,1)
        ala=0-heitto
        yla=0+heitto
        sum=0
        if len(self.tasot)==0:
            return
        for j in range(0,len(self.taulukko)-1):
            for i in range(self.tasot[0],len(self.taulukko)):
                if j>=i:
                    continue
                if self.taulukko[j][i]==None:
                    sum+=1
        if sum==0:
            return
        kytkos=r.randint(1,sum)
        index=1
        uusitaulu=[[None for j in range(len(self.taulukko))] for i in range(len(self.taulukko))]
        for i in range(len(self.taulukko)):
            for j in range(len(self.taulukko)):
                if self.taulukko[i][j]!=None:
                    uusitaulu[i][j]=self.taulukko[i][j]
        for j in range(len(uusitaulu)-1):
            for i in range(self.tasot[0],len(uusitaulu)):
                if j>=i:
                    continue
                if self.taulukko[j][i]==None:
                    if index==kytkos:
                        uusitaulu[j][i]=r.uniform(ala,yla)
                        self.taulukko=uusitaulu
                        self.luo_hermoverkko()
                        return
                    else:
                        index+=1
        self.luo_hermoverkko()
    def tarkista_yhteys(self):
        if len(self.tasot)==0:
            return False
        for j in range(0,len(self.taulukko)-1):
            for i in range(self.tasot[0],len(self.taulukko)):
                if j>=i:
                    continue
                if self.taulukko[j][i]==None:
                    return True
        return False
    def tarkista_yhteys_poisto(self):
        for i in range(len(self.taulukko)):
            yhteyksia=0
            for j in range(i+1,len(self.taulukko)):
                if j<=self.alut[-1]:
                    continue
                if self.taulukko[i][j]!=None:
                    yhteyksia+=1
            if yhteyksia>=2:
                return True
        return False
    def poista_yhteys(self):
        if not self.tarkista_yhteys_poisto():
            return
        poistettavat=[]
        for i in range(len(self.taulukko)-1):
            yhteydet=[]
            for j in range(i+1,len(self.taulukko)):
                if j<=self.alut[-1]:
                    continue
                if self.taulukko[i][j]!=None:
                    yhteydet.append((i,j))
            for i in yhteydet:
                poistettavat.append(i)
        poisto=r.choice(poistettavat)
        uusitaulu=[[self.taulukko[i][j] for j in range(len(self.taulukko))] for i in range(len(self.taulukko))]
        
        uusitaulu[poisto[0]][poisto[1]]=None
        self.taulukko=uusitaulu
        self.luo_hermoverkko()
    def mutaatio(self,rate):
        if rate==1:
            lista=[i for i in range(100)]
        elif rate==2:
            lista=[i for i in range(80)]
        elif rate==3:
            lista=[i for i in range(60)]
        elif rate==4:
            lista=[i for i in range(40)]
        elif rate==5:
            lista=[i for i in range(20)]
        heitto=rate*0.03
        ala=1-heitto
        yla=1+heitto
        uusitaulu=[[None for j in range(len(self.taulukko))] for i in range(len(self.taulukko))]
        for index,lista in enumerate(self.taulukko):
            for jindex,luku in enumerate(lista):
                if luku!=None:
                    uusitaulu[index][jindex]=self.taulukko[index][jindex]
                    if r.choice(lista)==0:
                        uusitaulu[index][jindex]*=-1
                    if r.randint(1,10)<=rate:
                        uusitaulu[index][jindex]*=r.uniform(ala,yla)
        self.taulukko=uusitaulu
        self.luo_hermoverkko()
    def risteytys(morefit: 'Hermoverkko',lessfit: 'Hermoverkko'):
        erotus=morefit.solumaara-lessfit.solumaara
        if erotus>=0:
            uusitaulu=[[None for j in range(morefit.solumaara)] for i in range(morefit.solumaara)]
            for index, rivi in enumerate((lessfit.taulukko)):
                for jindex, luku in enumerate(rivi):
                    if luku!=None:
                        if jindex>morefit.alut[-1]:
                            if index>morefit.alut[-1]:
                                uusitaulu[index+erotus][jindex+erotus]=lessfit.taulukko[index][jindex]
                            else:
                                uusitaulu[index][jindex+erotus]=lessfit.taulukko[index][jindex]
            puoli=len(morefit.taulukko)//+1
            for index, lista in enumerate(morefit.taulukko):
                for j, luku in enumerate(lista):
                    if index>puoli or j > puoli:
                        continue
                    else:
                        if uusitaulu[index][j]==None:
                            if morefit.taulukko[index][j]==None:
                                pass
                            else:
                                uusitaulu[index][j]=morefit.taulukko[index][j]
                        else:
                            if morefit.taulukko[index][j]==None:
                                pass
                            else:
                                uusitaulu[index][j]=r.choice([morefit.taulukko[index][j],uusitaulu[index][j]])
            return Hermoverkko(len(morefit.alut),len(morefit.loput),uusitaulu)
        else:
            uusitaulu=[[None for j in range(lessfit.solumaara)] for i in range(lessfit.solumaara)]
            for i in range(len(uusitaulu)):
                uusitaulu[i][i]=r.uniform(-2,2)
            for index, rivi in enumerate((morefit.taulukko)):
                for jindex, luku in enumerate(rivi):
                    if luku!=None:
                        if jindex>lessfit.alut[-1]:
                            if index>lessfit.alut[-1]:
                                uusitaulu[index-erotus][jindex-erotus]=morefit.taulukko[index][jindex]
                            else:
                                uusitaulu[index][jindex-erotus]=morefit.taulukko[index][jindex]
            puoli=len(morefit.taulukko)//2+1
            rajoitin=0
            for i in range(len(uusitaulu)-1):
                rajoitin+=1
                for j in range(rajoitin,len(uusitaulu)):
                    if uusitaulu[i][j]==None:
                        uusitaulu[i][j]=lessfit.taulukko[i][j]
                    else:
                        if lessfit.taulukko[i][j]!=None:
                            uusitaulu[index][j]=r.choice([lessfit.taulukko[index][j],uusitaulu[index][j]])
            # laskuri=0
            # while erotus<0:
            #     index=r.randint(0,len(uusitaulu)-1)
            #     luku = uusitaulu[index].count(None)
            #     laskuri+=1
            #     if laskuri>15:
            #         break
            #     if luku < len(uusitaulu)-2:
            #         while True:
            #             poisto=r.choice(uusitaulu[index][index+1:])
            #             if poisto is not None:
            #                 pindex=uusitaulu[index][index+1:].index(poisto)
            #                 pindex+=index+1
            #                 uusitaulu[index][pindex]=None
            #                 erotus+=1
            #                 break
            erotus=int(abs(erotus))
            uusiverkko=Hermoverkko(len(morefit.alut),len(morefit.loput),uusitaulu)
            for i in range(erotus):
                if uusiverkko.tarkista_solmun_poisto:
                    uusiverkko.poista_solmu()  
            return uusiverkko
    def printtaa(self):
        # apulista=[]
        # for i, x in enumerate( self.taulukko):
        #     apulista.append([])
        #     for j, luku in enumerate(x):
        #         if luku==None:
        #             apulista[i].append("0")
        #         elif luku==1:
        #             apulista[i].append("1")
        #         elif j==i:
        #             apulista[i].append("B")
        #         else: apulista[i].append("X")
        # for i in apulista:
        #     print(i)
        # print()
        print("Olen hermoverkko, jolla on\n",len(self.alut),"alkusolmua,\n",len(self.tasot),"välisolmua\n",len(self.loput),"loppusolmua")
        print("suhteellinen weightni on",self.weightsum())
        print("Kompleksisuus arvo on",self.laske_kompleksisuus())
        print("Yhteyksiä on yhteensä",self.laske_kompleksisuus()-self.solumaara)
    def printti(self):
        for i in self.taulukko:
            print(i)
        print()
    def weightsum(self):
        sum=0
        for i in range(len(self.alut)):
            self.taulukko[i][i]=1
        for i,x in enumerate(self.taulukko):
            for j in range(len(x)):
                if x[j]!=None:
                    sum+=x[j]
        return sum
    def palauta_topologia(verkko,maara):
        lista=[]
        for i in range(maara):
            lista.append(Hermoverkko(verkko.alut[-1]+1,len(verkko.loput),verkko.taulukko))
        for i in range(len(lista)):
            if r.randint(0,2)==0:
                if lista[i].tarkista_solmun_poisto():
                    lista[i].poista_solmu()
                else:
                    lista[i].luo_uusi_solmu()
            else:
                lista[i].luo_uusi_solmu()
        return lista
    def palauta_mutaatio(verkko,maara,rate):
        lista=[]
        for i in range(maara):
            # print(verkko.alut[-1]+1)
            lista.append(Hermoverkko(verkko.alut[-1]+1,len(verkko.loput),verkko.taulukko))
        for i in range(len(lista)):
            lista[i].mutaatio(rate)
        return lista
    def palauta_kytkos(verkko,maara):
        lista=[]
        for i in range(maara):
            lista.append(Hermoverkko(verkko.alut[-1]+1,len(verkko.loput),verkko.taulukko))
        for i in range(len(lista)):
            luku=lista[i].tarkista_yhteys()
            if not luku:
                valitsin=r.randint(0,6)
                if valitsin==0:
                    lista[i].mutaatio()
                elif valitsin==1:
                    lista[i].poista_yhteys()
                else:
                    lista[i].luo_uusi_solmu()
            
            else:
                lista[i].luo_uusi_yhteys()
                  
        return lista
    def evoluutio_strategia_yksi(lista:list,maara):
        if len(lista)==0:
            raise ValueError('Evoluutio strategia yksi vaatii vähintään kaksi verkkoa, jotta risteyttäminen on mahdollista')
        if maara%100==0:
            kerrat=int(maara/100)
        else: kerrat = maara //100+1
        solut=0
        kytkokset=0
        mutit=0
        risteytykset=0
        uudet=[]
        for i in range(kerrat):
            mutaatiot=40
            index=0
            while mutaatiot>1:
                for i in Hermoverkko.palauta_mutaatio(lista[index],mutaatiot//2):
                    uudet.append(i)
                    mutit+=1
                mutaatiot//=2
                index+=1
                if index==len(lista):
                    index=0
            pituus=mutaatiot-len(uudet)
            for i in Hermoverkko.palauta_mutaatio(lista[0],pituus):
                uudet.append(i)
                mutit+=1
            rist=20
            while True:
                for i in range(len(lista)):
                    for j in range(i,len(lista)):
                        uudet.append(Hermoverkko.risteytys(lista[i],lista[j]))
                        risteytykset+=1
                        rist-=1
                        if rist==0:
                            break
                    if rist==0:
                            break
                if rist==0:
                            break
            index=0
            for i in range(6,0,-1):
                tiedot=Hermoverkko.palauta_kytkos(lista[index],i)
                for j in tiedot:
                    uudet.append(j)
                index+=1
                if index==len(lista):
                    index=0
            index=0
            for j in range(5):
                for i in Hermoverkko.palauta_topologia(lista[index],4):
                    uudet.append(i)
                    solut+=1
                index+=1
                if index==len(lista):
                    index=0
        return uudet[:maara]
    def evoluutio_strategia_kaksi(verkko:'Hermoverkko',maara):
        uudet=[]
        while len(uudet)<maara:
            for i in Hermoverkko.palauta_kytkos(verkko,15):
                uudet.append(i)
            for i in Hermoverkko.palauta_mutaatio(verkko,15):
                uudet.append(i)
            for i in Hermoverkko.palauta_topologia(verkko,15):
                uudet.append(i)
            r.shuffle(uudet)
            apulista=[]
            for i in range(5):
                for j in range(3):
                    apulista.append(Hermoverkko.risteytys(verkko,uudet[i+j]))
            for i in apulista:
                uudet.append(i)
        r.shuffle(uudet)
        return uudet[:maara]
    def evoluutio_strategia_kolme(verkko:'Hermoverkko',maara,mutaatiot):
        lista=[]
        for i in range(maara-5):
            lista.append(Hermoverkko(verkko.alut[-1]+1,len(verkko.loput),verkko.taulukko))
        for i in range(len(lista)):
            random=r.randint(1,3)
            for kertaa in range(random):
                random2=r.randint(0,4)
                if random2==0 or random==1:
                    lista[i].mutaatio()
                elif random2== 2:
                    lista[i].luo_uusi_solmu(mutaatiot)
                elif random2==3 or random2==4:
                    lista[i].luo_uusi_yhteys(mutaatiot)
        lista.append(  Hermoverkko.risteytys(r.choice(lista),verkko) )
        lista.append(  Hermoverkko.risteytys(r.choice(lista),verkko) )
        lista.append(  Hermoverkko.risteytys(r.choice(lista),verkko) )
        lista.append(  Hermoverkko.risteytys(r.choice(lista),verkko) )
        lista.append(  Hermoverkko.risteytys(r.choice(lista),verkko) )
        return lista
    def evoluutio_strategia_neljä(verkko:'Hermoverkko',maara,mutaatiot):
        lista=[]
        for i in range(maara):
            lista.append(Hermoverkko(verkko.alut[-1]+1,len(verkko.loput),verkko.taulukko))
        for i in range(len(lista)):
            random=r.randint(1+mutaatiot,3+mutaatiot)
            for kertaa in range(random):
                random2=r.randint(0,4)
                if random2==0:
                    lista[i].mutaatio()
                elif random2==2 or random==3:
                    if lista[i].tarkista_yhteys():
                        lista[i].luo_uusi_yhteys(mutaatiot)
                    else:
                        lista[i].luo_uusi_solmu(mutaatiot)
                else:
                    lista[i].luo_uusi_solmu(mutaatiot)
        return lista
    def luo_uusia_verkko(koko,maara):
        apulista=[]
        while len(apulista)<maara:
            lista=[]
            for i in range(200):
                lista.append(Hermoverkko(koko[0],koko[1],[]))
            for i in range(50):
                lista[i].luo_uusi_solmu()
            for i in range(25):
                lista[i].luo_uusi_yhteys()
            apulista+=lista
        r.shuffle(apulista)
        return apulista[:maara]
    def kirjoita(self,tiedostonimi):
        with open(tiedostonimi,"w") as tiedosto:
            for i in self.taulukko:
                merkit=""
                for j in i:
                    merkit+=str(j)
                    merkit+=";"
                merkit=merkit[:-1]
                merkit+="\n"
                tiedosto.write(merkit)
            tiedosto.write((str(len(self.alut))+"\n"))
            tiedosto.write(str(len(self.loput)))
    def lue_ja_palauta(tiedostonimi):
        lista=[]
        index=0
        with open(tiedostonimi) as tiedosto:
            for i in tiedosto:
                lista.append([])
                i=i.split(";")
                for k in i:
                    k=k.replace("\n","")
                    if k=="None":
                        lista[index].append(None)
                    else:
                        lista[index].append(float(k))
                    
                index+=1
        aloitussolmut=int(lista[-2][0])
        lopetussolmut=int(lista[-1][0])
        return Hermoverkko(aloitussolmut,lopetussolmut,lista[:-2])


class Evoluutio:
    def __init__(self):
        self.mutatibility=5
    def luo_uusia_verkkoja(self,alkusolmut,loppusolmut,kompleksisuuskerroin,yhtkerroin,maara):
        raportti=False
        alku=time.time()
        verkkolista=[]
        for i in range(maara):
            mahdolliset_yhteydet=0
            verkko=Hermoverkko(alkusolmut,loppusolmut,[])
            kompleksisuus_nyt=verkko.laske_kompleksisuus()
            kompleksisuus=kompleksisuus_nyt*kompleksisuuskerroin
            yhteydet=0
            while kompleksisuus_nyt<kompleksisuus:
                if len(verkko.tasot)==0:
                    verkko.luo_uusi_solmu(5)
                    mahdolliset_yhteydet+=alkusolmut
                    yhteydet+=1
                else:
                    relaatio=yhteydet/mahdolliset_yhteydet
                    if relaatio>yhtkerroin:
                
                        yhteydet+=1
                        mahdolliset_yhteydet+=alkusolmut+len(verkko.tasot)
                        verkko.luo_uusi_solmu(5)
                    else:
       
                        if verkko.tarkista_yhteys():
                            verkko.luo_uusi_yhteys(5)
                            yhteydet+=1
                        else:
                            yhteydet+=1
                            mahdolliset_yhteydet+=alkusolmut+len(verkko.tasot)
                            verkko.luo_uusi_solmu(5)
                kompleksisuus_nyt=verkko.laske_kompleksisuus()
            verkkolista.append(verkko)
        loppu=time.time()
        if raportti:
            print()
            print("Verkkojenluonti raportti:")
            print("Luotiin",maara,"verkkoa ja aikaa kului",loppu-alku)
            print("Verkkojen kompleksisuus on", kompleksisuus,"ja yhteyksien suhde on",yhtkerroin)
            r.choice(verkkolista).printtaa()
            print()
            print()
            print()
        return verkkolista

    def lue_ja_palauta(self,tiedostonimi):
        return Hermoverkko.lue_ja_palauta(tiedostonimi)

    def mutaatio_strategia_equals(self,verkkolista,maara):
        uusilista=[]
        while len(uusilista)<maara:
            for i in verkkolista:
                for j in Hermoverkko.evoluutio_strategia_neljä(i,50,self.mutatibility):
                    uusilista.append(j)
                for j in Hermoverkko.evoluutio_strategia_kolme(i,20,self.mutatibility):
                    uusilista.append(j)
                uusilista.append(Hermoverkko.risteytys(verkkolista[0],i))
        r.shuffle(uusilista)
        return uusilista[:maara]

    def evoluutio_strategia_2dim(self,verkko,kompleksisuus,mutaatiorate,maara):
        #Tämä strategia säilyttää solmujen ja kytkösten suhteen
        #Strategia, joka ei säilytä on kolme-ulotteinen
        if kompleksisuus==0:
            lista=Hermoverkko.palauta_mutaatio(verkko,maara,mutaatiorate)
            return lista
        else:
            lisa=r.uniform(-0.05,0.05)
            if len(verkko.tasot)==0:
                kerroin=1
            else:
                kerroin=(verkko.laske_kompleksisuus()-verkko.solumaara)/len(verkko.tasot)+lisa
            lista=[]
            for i in range(maara):
                lista.append(Hermoverkko(verkko.alut[-1]+1,len(verkko.loput),verkko.taulukko))
           
            for i in range(len(lista)):
                if r.randint(0,1)==1: #Kasvatetaan verkon kokoa
                    for k in range(kompleksisuus):
                        if len(lista[i].tasot)==0:
                            lista[i].luo_uusi_solmu(mutaatiorate)
                            continue
                        if (lista[i].laske_kompleksisuus()-lista[i].solumaara)/len(lista[i].tasot)>=kerroin:
                            lista[i].luo_uusi_solmu(mutaatiorate)
                        else:
                            lista[i].luo_uusi_yhteys(mutaatiorate)
                      
                else:
                    for k in range(kompleksisuus):
                        if len(lista[i].tasot)==0:
                            lista[i].poista_yhteys()
                            continue
                        if (lista[i].laske_kompleksisuus()-lista[i].solumaara)/len(lista[i].tasot)>=kerroin:
                            lista[i].poista_yhteys()
                        else:
                            lista[i].poista_solmu()
                for b in range(mutaatiorate-1):
                    lista[i].mutaatio(mutaatiorate)
        return lista



            

        

        




def main():
    verkot=[Hermoverkko(49,1,[]),Hermoverkko(49,1,[])]
    lista=[]
    lista.append(  Hermoverkko.risteytys(r.choice(verkot),verkot[0]) )
    print(lista)


if __name__=="__main__":
    main()