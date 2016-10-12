import random as rd
from matplotlib.pyplot import *
from math import *
import numpy as np
import skimage as ski
from skimage.color import rgb2gray
from scipy import misc
from PIL import Image
import PIL.ImageOps


#######################################################################

class Cell:
    def __init__(self, pop_list, veg_type, veg_value, hum_value, iswater): #pop_list is array, veg_type is string, veg_value is the vegetation index value, hum_value is the humidity value
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

    def update(self):
        if self.e < 50 : B = rd.randint(50,300); PE = rd.uniform(.33, 1.); UE = rd.uniform(.32, .80); PAO = rd.randint(3,4)
        else :           B = 100               ; PE = .50                ; UE = .56                 ; PAO = 3.
        deltae = B*PAO*self.ao - self.e*UE - self.e*PE

        if self.l < 50 :  UL1 = rd.uniform(.3, .58); UL2 = rd.uniform(.0, .1); PL = rd.uniform(0.08, 0.17)
        else :            UL1 = .44                ; UL2 = .05               ; PL = 0.14
        deltal = PE*self.e - self.l*UL1 - self.l*UL2*self.l - self.l*PL                              # larvae value update

        if self.p < 50 :  UP = rd.uniform(.22, .52); PP = rd.uniform(.33, 1.);
        else :            UP = .37                 ; PP = .50
        deltap = PL*self.l - self.p*UP - self.p*PP                                                    #pupae update value

        if self.ah < 50 :  PAH = rd.uniform(.322, .598); UAH = rd.uniform(.125, .233);
        else :             PAH = .46                   ; UAH = .18
        if self.ao < 50 :  UAO = rd.uniform(.41, .56);
        else :             UAO = .41
        deltaah = PP*self.p - self.ah*UAH - self.ah*PAH + (1-UAO)*self.ao                              #host-seeking update value

        if self.ar < 50 :  PAR = rd.uniform(.3, .56); UAR = rd.uniform(.0034, .01);
        else :             PAR = .43                ; UAR = .0043
        deltaar = PAH*self.ah - self.ah*UAR - self.ah*PAR                                              #resting update value

        deltaao = self.ah*PAR - self.ar


        self.pop_list = self.pop_list.tolist() #change from array to list as array is imutable
        self.e  += deltae  # egg   value update
        self.l  += deltal  #larvae value update
        self.p  += deltal
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
        self.vegimage = vegimage
        self.twiimage = twiimage
        self.cityimage = cityimage
        self.pixelSize = pixelXmeters

        #initializing grid of Cells
        self.GRID = [[Cell(np.array(basearray), cityimage[i][j], vegimage[i][j], twiimage[i][j], contour[i][j]) for i in range(self.shape[0])] for j in range(self.shape[1])]
        global grdsum
        def grdsum(ending):
            result = 0
            for i in range(self.shape[1]):
                for j in range(self.shape[0]):
                    result +=eval("self.GRID["+str(i)+"]["+str(j)+"]."+ ending)
            return result

        self.egrid = grdsum( 'e')  # e  = eggs    - aquatic steps
        self.lgrid = grdsum( 'l')  # l  = larvae  - aquatic steps
        self.pgrid = grdsum( 'p')  # p  = pupae   - aquatic steps

        self.ahgrid = grdsum('ah') # ah = host-seeking        adult - adult steps
        self.argrid = grdsum('ar') # ar = resting             adult - adult steps
        self.aogrid = grdsum('ao') # ao = ovoposition-seeking adult - adult steps

        self.n_aquaticgrid = self.egrid + self.lgrid + self.pgrid
        self.n_adultgrid   = self.ahgrid + self.argrid + self.aogrid
        self.n_totalgrid   = self.n_aquaticgrid + self.n_adultgrid

    def update(self):
        [[newGrid.GRID[i][j].update() for i in range(newGrid.shape[1])] for j in range(newGrid.shape[0])]
        self.egrid = grdsum( 'e')  # e  = eggs    - aquatic steps
        self.lgrid = grdsum( 'l')  # l  = larvae  - aquatic steps
        self.pgrid = grdsum( 'p')  # p  = pupae   - aquatic steps

        self.ahgrid = grdsum('ah') # ah = host-seeking        adult - adult steps
        self.argrid = grdsum('ar') # ar = resting             adult - adult steps
        self.aogrid = grdsum('ao') # ao = ovoposition-seeking adult - adult steps

        self.n_aquaticgrid = self.egrid + self.lgrid + self.pgrid
        self.n_adultgrid   = self.ahgrid + self.argrid + self.aogrid
        self.n_totalgrid   = self.n_aquaticgrid + self.n_adultgrid







island_shape = misc.imread("../example_images/region_border_example.png")
island_shape_gray = rgb2gray(island_shape)
island_wet = ski.img_as_float(rgb2gray(misc.imread("../example_images/TWI_example.png")))
island_veg = adjust_gamma(ski.img_as_float(rgb2gray(misc.imread("../example_images/vegetation_index_example.png"))), .2)
island_city = rgb2gray(misc.imread("../example_images/city_delimitation_example.png"))







teste = Cell(np.array([1,2,3,4,5,6]), "city", 1,1, 1)
teste.e
teste.l
teste.p
teste.ah
teste.update()
teste.e
teste.l
teste.p

a = 0
antigo = teste.n_total
teste.update()
novo = teste.n_total
while 0.95*novo <= antigo <= 1.05*novo :
    antigo = novo
    teste.update()
    novo = teste.n_total
    a += 1
