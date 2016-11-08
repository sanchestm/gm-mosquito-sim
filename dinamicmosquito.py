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

class Cell:
    def __init__(self, pop_list, veg_type, veg_value, hum_value, iswater): #pop_list is array, veg_type is string, veg_value is the vegetation index value, hum_value is the humidity value
        self.larvae_lim_per_box = 100000
        self.pop_list  = pop_list
        self.veg_type  = veg_type
        self.veg_value = veg_value
        self.hum_value = hum_value
        self.iswater = iswater

        self.e = pop_list[0]  # e  = eggs    - aquatic steps
        self.l = pop_list[1]  # l  = larvae  - aquatic steps
        self.p = pop_list[2]  # p  = pupae   - aquatic steps

        self.ah = pop_list[3] # ah = host-seeking        adult - adult steps
        self.ar = pop_list[4] # ar = resting             adult - adult steps
        self.ao = pop_list[5] # ao = ovoposition-seeking adult - adult steps

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

    def update(self):

        a = 0; b =1
        if self.l < self.larvae_lim_per_box: a = (1 - (self.l)/self.larvae_lim_per_box)

        deltae = self.PAO*self.B*self.novopo*self.ao/2  - self.e*self.UE         - self.e*self.PE     #egg value update
        deltal = self.PE*self.e    - self.l*self.UL1  - self.l*self.PL*a                            # larvae value update
        deltap = self.PL*self.l*a    - self.p*self.UP   - self.p*self.PP                            #pupae update value
        deltaah = self.PP*self.p   - self.ah*self.UAH - self.ah*self.PAH       + self.PAO*self.ao   #host-seeking update value
        deltaar = self.PAH*self.ah - self.ar*self.UAR - self.ar*self.PAR                            #resting update value
        deltaao = self.ar*self.PAR - self.PAO*self.ao - self.UAO*self.ao                            #ovoposition seeking udate value
        self.delta = [int (deltae) , int(deltal) , int(deltap) , int(deltaah) , int(deltaar) , int(deltaao)]

        self.pop_list = self.pop_list.tolist() #change from array to list as array is imutable in function
        self.e  += deltae                      # egg   value update
        self.l  += deltal                      #larvae value update
        self.p  += deltap
        self.ah += deltaah
        self.ar += deltaar
        self.ao += deltaao
        if self.e < 0  : self.e  = 0
        if self.l < 0  : self.l  = 0
        if self.p < 0  : self.p  = 0
        if self.ah < 0 : self.ah = 0
        if self.ar < 0 : self.ar = 0
        if self.ao < 0 : self.ao = 0
        self.pop_list = np.array([self.e,self.l,self.p,self.ah,self.ar, self.ao])
        self.n_total   = self.pop_list.sum()
        self.n_aquatic = sum(self.pop_list[0:3])
        self.n_adult   = sum(self.pop_list[3:])

class Grid:
    def __init__(self, basearray, contour, vegimage, twiimage, cityimage, pixelXmeters):
        self.shape = contour.shape
        self.contour = contour
        self.vegimage = abs(vegimage-1)
        self.twiimage = abs(twiimage-1)
        self.cityimage = cityimage
        self.pixelSize = pixelXmeters
        size = pixelXmeters

        #initializing grid of Cells
        self.GRID = [[Cell(np.array(basearray)*abs(1-contour[j][i]), cityimage[j][i], vegimage[j][i], twiimage[j][i], contour[j][i]) for i in range(self.shape[1])] for j in range(self.shape[0])]

        #create grid of types of contour
        def neighbors_to_tuple(y,x):
            return(int(contour[y-1,x-1]), int(contour[y,x-1]), int(contour[y+1,x-1]), int(contour[y-1,x]), int(contour[y+1,x]), int(contour[y-1,x+1]), int(contour[y,x+1]), int(contour[y+1,x+1]))
        self.bordertype = [[dict_matrix_to_num[neighbors_to_tuple(j,i)] for i in range(1,self.shape[1]-1)] for j in range(1,self.shape[0]-1)]
        self.bordertype = np.pad(self.bordertype, pad_width=((1,1),(1,1)), mode='constant', constant_values=-1) #padding with zeros
        


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
        print("wrong command on getSingleGrid"); return np.array([[]])

    def grdsum(self, ending):
        grid_to_sum = self.getSingleGrid(ending)
        return grid_to_sum.sum()

    def update_pop(self):
        [[self.GRID[j][i].update() for i in range(self.shape[1])] for j in range(self.shape[0])]

    def update_migration(self):
        updatedah = np.zeros(self.shape)
        updatedao = np.zeros(self.shape)
        for i in range(1, self.shape[0]-1):
            for j in range(1, self.shape[1]-1):
                if self.GRID[i][j].iswater == 0:
                    borderMatrix = np.array(dict_num_to_weights[self.bordertype[i][j]])

                    floatingah = self.GRID[i][j].ah * borderMatrix * self.vegimage[i-1:i+2,j-1:j+2]
                    if floatingah.sum() > 0.05:
                        updatedah[i-1:i+2,j-1:j+2]   += floatingah*(self.GRID[i][j].ah/floatingah.sum())
                    else: updatedah[i-1:i+2,j-1:j+2] += self.GRID[i][j].ah * borderMatrix

                    floatingao = self.GRID[i][j].ao * borderMatrix * self.twiimage[i-1:i+2,j-1:j+2]
                    if floatingao.sum() > 0.05:
                        updatedao[i-1:i+2,j-1:j+2]  += floatingao*(self.GRID[i][j].ao/floatingao.sum())
                    else:updatedah[i-1:i+2,j-1:j+2] += self.GRID[i][j].ao * borderMatrix

        for i in range(1, self.shape[0]-1):
            for j in range(1, self.shape[1]-1):
                self.GRID[i][j].ah = updatedah[i][j]
                self.GRID[i][j].ao = updatedao[i][j]

    def updateall(self):
        self.update_migration()
        self.update_migration()
        self.update_migration()
        self.update_pop()

    def images(self):
        f, (aquatics, ah, ao, adults) = plt.subplots(ncols=4, figsize=(15,15)) # sharex=True, sharey=True
        caq = aquatics.imshow(self.getSingleGrid('aqua'), cmap=plt.get_cmap("gist_earth"))
        aquatics.set_title('Aquatics stages')
        divider1 = make_axes_locatable(aquatics)
        cax1 = divider1.append_axes("bottom", size="5%", pad=0.05)
        f.colorbar(caq,cax1,orientation="horizontal") #  a = int(self.grdsum("aqua") ,ticks = range(0, a, int(a/10)


        cah=ah.imshow(self.getSingleGrid('ah'), cmap=plt.get_cmap("gist_earth"))
        ah.set_title('host-seeking')
        divider2 = make_axes_locatable(ah)
        cax2 = divider2.append_axes("bottom", size="5%", pad=0.05)
        f.colorbar(cah,cax2, orientation="horizontal")

        cao=ao.imshow(self.getSingleGrid('ao'), cmap=plt.get_cmap("gist_earth"))
        ao.set_title('ovoposition-seeking')
        divider3 = make_axes_locatable(ao)
        cax3 = divider3.append_axes("bottom", size="5%", pad=0.05)
        f.colorbar(cao,cax3, orientation="horizontal")

        caa=adults.imshow(self.getSingleGrid('adult'), cmap=plt.get_cmap("gist_earth"))
        adults.set_title('Adult females')
        divider4 = make_axes_locatable(adults)
        cax4 = divider4.append_axes("bottom", size="5%", pad=0.05)
        f.colorbar(caa,cax4, orientation="horizontal")

        f.subplots_adjust(hspace=0)
        plt.setp([a.get_xticklabels() for a in f.axes[:]], visible=False)
        #for a in f.axes[:]: a.axis([0, self.shape[1],0, self.shape[0]])
        plt.setp([a.get_yticklabels() for a in f.axes[:]], visible=False)
        plt.tight_layout()
        plt.show()
