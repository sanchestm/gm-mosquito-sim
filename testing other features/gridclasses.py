import random as rd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
plt.style.use("ggplot")
from math import *
import numpy as np
import pickle as pkl
import skimage as ski
from skimage.color import rgb2gray
from scipy import misc
from PIL import Image
import PIL.ImageOps
from skimage.exposure import adjust_gamma
from randomwalkmaker import *

class Cell:
    def __init__(self, pop_list, veg_type, veg_value, hum_value, iswater, pixelXmeters, poplim_perkm2, gmotype): #pop_list is array, veg_type is string, veg_value is the vegetation index value, hum_value is the humidity value
        self.larvae_lim_per_box = poplim_perkm2*hum_value*(pixelXmeters**2)/1000000
        self.pop_list  = pop_list
        self.veg_type  = veg_type
        self.veg_value = veg_value
        self.hum_value = hum_value
        self.iswater = iswater
        self.gmotype = gmotype

        self.e = pop_list[0]  # e  = eggs    - aquatic steps
        self.l = pop_list[1]  # l  = larvae  - aquatic steps
        self.p = pop_list[2]  # p  = pupae   - aquatic steps

        self.ah = pop_list[3] # ah = host-seeking        adult - adult steps
        self.ar = pop_list[4] # ar = resting             adult - adult steps
        self.ao = pop_list[5] # ao = ovoposition-seeking adult - adult steps

        self.amale = sum(pop_list[3:])

        self.emut = 0 #emut = mutant eggs
        self.lmut = 0 #lmut = mutant larvae
        self.pmut = 0 #pmut = mutant pupae
        self.amut = 0 #amut = mutant adults

        self.n_total   = pop_list.sum()
        self.n_aquatic = sum(pop_list[0:3])
        self.n_adult   = sum(pop_list[3:])

        #U for dying P for passing
        self.B = 100     #number of eggs per ovoposition
        self.PE = .50    #prob of becoming a larvae
        self.UE = .56    #prob of dying as a egg
        self.novopo = 1.3 #novopositions per day #max =1.48, maxefficient=1.4
        self.UL1 = .44   #prob of dying larvae
        self.UL2 = .1  #prob of dying due to crowding
        self.PL = 0.14   #prob of
        self.PP = .50
        self.UP = .37
        self.PAH = .46
        self.UAH = .18
        self.PAR = .43
        self.UAR = .0043
        self.UAO = .41
        self.PAO = .5
        self.UAM = .15

    def update(self):

        a = 0; b =1
        if self.l < self.larvae_lim_per_box: a = (1 - (self.l+ self.lmut)/self.larvae_lim_per_box)
        allmale = self.amale + self.amut
        if (self.amale + self.amut) != 0:
            factor = (self.amale/allmale)
            mutfactor = (1 - factor)
        else: factor = 0; mutfactor = 0


        deltae = self.PAO*self.B*self.novopo*self.ao*factor - self.e*self.UE - self.e*self.PE   #egg value update
        deltal = self.PE*self.e      - self.l*self.UL1  - self.l*self.PL*a                                    # larvae value update
        deltap = self.PL*self.l*a    - self.p*self.UP   - self.p*self.PP                                      #pupae update value
        deltaah = self.PP*self.p/2   - self.ah*self.UAH - self.ah*self.PAH + self.PAO*self.ao           #host-seeking update value
        deltaar = self.PAH*self.ah   - self.ar*self.UAR - self.ar*self.PAR                                  #resting update value
        deltaao = self.ar*self.PAR   - self.PAO*self.ao - self.UAO*self.ao                                  #ovoposition seeking update value
        deltaamale =  self.PP*self.p/2 - self.amale*self.UAM

        deltaemut = self.PAO*self.B*self.novopo*self.ao*mutfactor - self.emut*self.UE - self.emut*self.PE #mutant egg value update
        deltalmut = self.PE*self.emut    - self.lmut*self.UL1  - self.lmut*self.PL*a*self.gmotype                                #mutant larvae value update
        deltapmut = self.PL*self.lmut*a*self.gmotype  - self.pmut*self.UP   - self.pmut*self.PP                                  #mutant pupae update value
        deltaamut = self.PP*self.pmut       - self.amut*self.UAM                                                       #mutant adult value update

        self.pop_list = self.pop_list.tolist() #change from array to list as array is imutable in function
        self.e     += deltae                      # egg   value update
        self.l     += deltal                      #larvae value update
        self.p     += deltap
        self.ah    += deltaah
        self.ar    += deltaar
        self.ao    += deltaao
        self.amale += deltaamale
        self.emut  += deltaemut
        self.lmut  += deltalmut
        self.pmut  += deltapmut
        self.amut  += deltaamut

        if self.e < 0  : self.e  = 0
        if self.l < 0  : self.l  = 0
        if self.p < 0  : self.p  = 0
        if self.ah < 0 : self.ah = 0
        if self.ar < 0 : self.ar = 0
        if self.ao < 0 : self.ao = 0
        if self.amale < 0 : self.amale = 0
        if self.emut < 0 : self.emut = 0
        if self.lmut < 0 : self.lmut = 0
        if self.pmut < 0 : self.pmut = 0
        if self.amut < 0 : self.amut = 0

        self.pop_list = np.array([self.e,self.l,self.p,self.ah,self.ar, self.ao])
        self.n_total   = self.pop_list.sum()
        self.n_aquatic = sum(self.pop_list[0:3])
        self.n_adult   = sum(self.pop_list[3:])

class Grid:
    def __init__(self, contour, vegimage, twiimage, cityimage, pixelXmeters, larvaelim, gmotype, eqsteps):
        self.internalclock = 0
        self.shape = contour.shape
        self.contour = contour
        self.vegimage = abs(vegimage-1)
        self.twiimage = abs(twiimage-1)
        self.cityimage = cityimage
        self.pixelSize = pixelXmeters
        self.history = []


        #build the migration dictionaries
        self.maxstep = MaxStep(pixelXmeters)
        print("migration dt = "+ str(self.maxstep/60))
        self.dict_matrix_to_num, self.dict_num_to_weights = weightDictmaker(self.maxstep, 10000,pixelXmeters)

        #calculate stable popvalues
        stable = Cell(np.array([100,100,100,100,100,100]),1,self.vegimage.mean(),self.twiimage.mean(),1, pixelXmeters, larvaelim, gmotype)
        for i in range(300): stable.update()
        print("initializing population with: ")
        print(stable.pop_list)

        #initializing grid of Cells
        self.GRID = [[Cell(np.array(stable.pop_list)*abs(1-contour[j][i]), cityimage[j][i], vegimage[j][i], twiimage[j][i], contour[j][i], pixelXmeters, larvaelim, gmotype) for i in range(self.shape[1])] for j in range(self.shape[0])]        #create grid of types of contour
        print()

        def neighbors_to_tuple(y,x):
            return(int(contour[y-1,x-1]), int(contour[y,x-1]), int(contour[y+1,x-1]), int(contour[y-1,x]), int(contour[y+1,x]), int(contour[y-1,x+1]), int(contour[y,x+1]), int(contour[y+1,x+1]))
        self.bordertype = [[self.dict_matrix_to_num[neighbors_to_tuple(j,i)] for i in range(1,self.shape[1]-1)] for j in range(1,self.shape[0]-1)]
        self.bordertype = np.pad(self.bordertype, pad_width=((1,1),(1,1)), mode='constant', constant_values=-1) #padding with zeros

        #equalize values
        for i in range(eqsteps):
            self.updateall()
        self.internalclock = 0
        self.history = []

        print("equilized population")
        print("equilized migration")

        self.maxafem = self.getSingleGrid("adult").max()
        self.maxmut  = self.getSingleGrid("amut").max()
        self.maxaqua = self.getSingleGrid("aqua").max() + self.getSingleGrid("aquamut").max()



    def getSingleGrid(self, ending):
        if ending == "e"    :  return np.array([[self.GRID[j][i].e  for i in range(self.shape[1])] for j in range(self.shape[0])])
        if ending == "l"    :  return np.array([[self.GRID[j][i].l  for i in range(self.shape[1])] for j in range(self.shape[0])])
        if ending == "p"    :  return np.array([[self.GRID[j][i].p  for i in range(self.shape[1])] for j in range(self.shape[0])])
        if ending == "ah"   :  return np.array([[self.GRID[j][i].ah for i in range(self.shape[1])] for j in range(self.shape[0])])
        if ending == "ar"   :  return np.array([[self.GRID[j][i].ar for i in range(self.shape[1])] for j in range(self.shape[0])])
        if ending == "ao"   :  return np.array([[self.GRID[j][i].ao for i in range(self.shape[1])] for j in range(self.shape[0])])
        if ending == "aqua" : return self.getSingleGrid("e")   + self.getSingleGrid("l") + self.getSingleGrid("p")
        if ending == "adult": return self.getSingleGrid("ah")  + self.getSingleGrid("ar")+ self.getSingleGrid("ao")
        if ending == "all"  : return self.getSingleGrid("aqua")+ self.getSingleGrid("adult")
        if ending == "amale": return np.array([[self.GRID[j][i].amale for i in range(self.shape[1])] for j in range(self.shape[0])])
        if ending == "amut" : return np.array([[self.GRID[j][i].amut for i in range(self.shape[1])] for j in range(self.shape[0])])
        if ending == "aquamut": return np.array([[self.GRID[j][i].emut+self.GRID[j][i].lmut+self.GRID[j][i].pmut  for i in range(self.shape[1])] for j in range(self.shape[0])])
        print("wrong command on getSingleGrid"); return np.array([[]])

    def grdsum(self, ending):
        grid_to_sum = self.getSingleGrid(ending)
        return grid_to_sum.sum()

    def update_pop(self):
        [[self.GRID[j][i].update() for i in range(self.shape[1])] for j in range(self.shape[0])]

    def update_migration(self):
        updatedah   = np.zeros(self.shape)
        updatedao   = np.zeros(self.shape)
        updatedamale = np.zeros(self.shape)
        updatedamut  = np.zeros(self.shape)
        for i in range(1, self.shape[0]-1):
            for j in range(1, self.shape[1]-1):
                if self.GRID[i][j].iswater == 0:
                    borderMatrix = np.array(self.dict_num_to_weights[self.bordertype[i][j]])

                    floatingah = self.GRID[i][j].ah * borderMatrix * self.vegimage[i-1:i+2,j-1:j+2]
                    if floatingah.sum() > 0.05:
                        updatedah[i-1:i+2,j-1:j+2]   += floatingah*(self.GRID[i][j].ah/floatingah.sum())
                    else: updatedah[i-1:i+2,j-1:j+2] += self.GRID[i][j].ah * borderMatrix

                    floatingao = self.GRID[i][j].ao * borderMatrix * self.twiimage[i-1:i+2,j-1:j+2]
                    if floatingao.sum() > 0.05:
                        updatedao[i-1:i+2,j-1:j+2]  += floatingao*(self.GRID[i][j].ao/floatingao.sum())
                    else:updatedah[i-1:i+2,j-1:j+2] += self.GRID[i][j].ao * borderMatrix

                    updatedamale[i-1:i+2,j-1:j+2]  += self.GRID[i][j].amale * borderMatrix
                    updatedamut[i-1:i+2,j-1:j+2]   += self.GRID[i][j].amut  * borderMatrix

        for i in range(1, self.shape[0]-1):
            for j in range(1, self.shape[1]-1):
                self.GRID[i][j].ah = updatedah[i][j]
                self.GRID[i][j].ao = updatedao[i][j]
                self.GRID[i][j].amale = updatedamale[i][j]
                self.GRID[i][j].amut = updatedamut[i][j]

    def updateall(self):
        for i in range(int(24*60/self.maxstep)):
            self.update_migration()
        self.update_pop()
        self.internalclock += 1
        self.history += [(self.grdsum("adult"),self.grdsum("amut") )]

    def images(self):
        f, (aquatics, ao, adults) = plt.subplots(ncols=3, figsize=(10,5)) # sharex=True, sharey=True
        caq = aquatics.imshow(self.getSingleGrid('aqua') + self.getSingleGrid('aquamut'), cmap=plt.get_cmap("gist_earth"), vmin = 0, vmax = .8*self.maxaqua)
        aquatics.set_title('Aquatics stages')
        divider1 = make_axes_locatable(aquatics)
        cax1 = divider1.append_axes("bottom", size="5%", pad=0.05)
        f.colorbar(caq,cax1,orientation="horizontal") #  a = int(self.grdsum("aqua") ,ticks = range(0, a, int(a/10)

        cao=ao.imshow(self.getSingleGrid('amut'), cmap=plt.get_cmap("gist_earth"),  vmin = 0, vmax = self.maxafem/.9)
        ao.set_title('Mutant males')
        divider3 = make_axes_locatable(ao)
        cax3 = divider3.append_axes("bottom", size="5%", pad=0.05)
        f.colorbar(cao,cax3, orientation="horizontal")

        caa=adults.imshow(self.getSingleGrid('adult'), cmap=plt.get_cmap("gist_earth"),  vmin = 0, vmax = self.maxafem)
        adults.set_title('Adult females')
        divider4 = make_axes_locatable(adults)
        cax4 = divider4.append_axes("bottom", size="5%", pad=0.05)
        f.colorbar(caa,cax4, orientation="horizontal")

        f.subplots_adjust(hspace=0)
        f.suptitle(str(self.internalclock)+" days after release", size = 17)
        plt.setp([a.get_xticklabels() for a in f.axes[:-3]], visible=False)
        plt.setp([a.get_yticklabels() for a in f.axes[:]], visible=False)
        f.tight_layout()
        f.subplots_adjust(top = 0.999)
        plt.savefig("timelapse/timelapse-"+ '{0:03d}'.format(self.internalclock)+".png")
        plt.close()

    def graph(self):
        femalehist, muthist = zip(*self.history)
        f, (graph1) = plt.subplots(ncols=1)
        graph1.plot(range(self.internalclock), femalehist , label = "females")
        graph1.plot(range(self.internalclock), muthist    , label = "mutants")
        plt.xlabel('days after mutant release')
        plt.ylabel('population size per square Km')
        graph1.set_title('variation in population size ')
        plt.legend(loc='best', prop={'size':10})
        plt.savefig("timelapse/popsize_variation.png")
        plt.close()
        f, (graph2) = plt.subplots(ncols=1)
        graph2.plot(range(self.internalclock), [femalehist[i]/(2*femalehist[i] + muthist[i]) for i in range(self.internalclock)], label = "females frequency")
        graph2.plot( range(self.internalclock),[muthist[i]/(2*femalehist[i]    + muthist[i]) for i in range(self.internalclock)], label = "mutant frequency")
        plt.xlabel('days after mutant release')
        plt.ylabel('percentages')
        plt.ylim(0,1)
        graph2.set_title('mutant and female percentages after release')
        plt.legend(loc='best', prop={'size':10})
        plt.savefig("timelapse/frequency_variation.png")
        plt.close()
