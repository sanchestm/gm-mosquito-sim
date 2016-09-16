#!/usr/bin/python3
import random as rd
import matplotlib
matplotlib.use("Qt4Agg")
from matplotlib.pyplot import *
from math import *
import numpy as np
import skimage as ski
from skimage.exposure import adjust_gamma
from skimage.color import rgb2gray
from scipy import misc
import PIL.ImageOps
style.use('ggplot')
import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ast import literal_eval as make_tuple
import re
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

form_class = uic.loadUiType("transgenic_mosquito_sim_v1.ui")[0]

class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.start.clicked.connect(self.start_clicked)
        self.regioncontourbutton.clicked.connect(self.openfile1)
        self.twibutton.clicked.connect(self.openfile2)
        self.cityregionbutton.clicked.connect(self.openfile3)
        self.vegindexbutton.clicked.connect(self.openfile4)
        self.imageviewbutton.clicked.connect(self.openMainFig)
        self.rmvPointButton.clicked.connect(self.removeCell)
        self.MutValue.setText("5000")
        self.MutantQuantity.setText("0")
        self.table.setColumnCount(2)
        self.layout.addWidget(self.table, 1, 0)
        self.table.setHorizontalHeaderLabels(['index', 'mutant size'])
        self.MutantLIST = np.array([])
        self.THEimage = np.array([])
        self.fig = Figure()



    def openfile1(self):
        self.regioncontour.setText(QtGui.QFileDialog.getOpenFileName(self, 'Single File', '~/Desktop/', "Image files (*.jpg *.png *.tif)"))

    def openfile2(self):
        self.twi.setText(QtGui.QFileDialog.getOpenFileName(self, 'Single File', '~/Desktop/', "Image files (*.jpg *.png *.tif)"))

    def openfile3(self):
        self.cityregion.setText(QtGui.QFileDialog.getOpenFileName(self, 'Single File', '~/Desktop/', "Image files (*.jpg *.png *.tif)"))

    def openfile4(self):
        self.vegindex.setText(QtGui.QFileDialog.getOpenFileName(self, 'Single File', '~/Desktop/', "Image files (*.jpg *.png *.tif)"))

    def removeCell(self):
        print('cellremoved')
        pointNumber = int(self.rmvPointN.text())
        self.MutantLIST[pointNumber:-1] = self.MutantLIST[pointNumber+1:]
        self.MutantLIST = self.MutantLIST[:-1]
        self.MutantQuantity.setText(str(int(self.MutantQuantity.text() )-int(self.table.item(pointNumber, 1).text()) ) )
        self.table.removeRow(pointNumber)
        for i in range(len(self.MutantLIST)):
            self.table.setItem(i, 0, QtGui.QTableWidgetItem(str(i)))
        self.ImgAddPatches()
        self.rmvPointN.setText('')

    def onclick(self, event):
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %(event.button, event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            self.MutantLIST =np.array(self.MutantLIST.tolist() + [[int(event.ydata), int(event.xdata), int(str(self.MutValue.text()))]])
            print(self.MutantLIST)
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)
            self.table.setItem(rowPosition , 0, QtGui.QTableWidgetItem(str(rowPosition)))
            self.table.setItem(rowPosition , 1, QtGui.QTableWidgetItem(str(self.MutValue.text())))
            self.MutantQuantity.setText(str(int(self.MutantQuantity.text()) + int(str(self.MutValue.text()))))
            self.ImgAddPatches()

    def openMainFig(self):
        if self.THEimage.any() == True:
            self.rmmpl()
            for i in range(len(self.MutantLIST)):
                self.table.removeRow(0)
            self.MutantLIST = np.array([])

        name = QtGui.QFileDialog.getOpenFileName(self, 'Single File', '~/Desktop/', "Image files (*.jpg *.png *.tif)")
        image = misc.imread(str(name))
        self.THEimage = image
        baseimage = self.fig.add_subplot(111)
        baseimage.axis('off')
        baseimage.grid(False)
        baseimage.imshow(image)
        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        #self.toolbar = NavigationToolbar(self.canvas, self.widget, coordinates=True)
        #self.mplvl.addWidget(self.toolbar)
        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)


    def ImgAddPatches(self):
        self.fig, ax = subplots(1, 1)
        ax.imshow(self.THEimage)
        ax.grid(False)
        ax.axis('off')
        for number, blob in enumerate(self.MutantLIST):
            y, x, r = blob
            c = Circle((x, y) ,self.THEimage.shape[0]*(log(r)**1.5)/1000, color='r', linewidth=2, alpha = 0.5)
            ax.add_patch(c)
            ax.text(x,y, str(number), color = 'white')
        self.changeFIGURE(self.fig)

    def changeFIGURE(self, newFIG):
        self.rmmpl()
        self.canvas = FigureCanvas(newFIG)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        #self.toolbar = NavigationToolbar(self.canvas, self.widget, coordinates=True)
        #self.mplvl.addWidget(self.toolbar)
        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)


    def rmmpl(self,):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        #self.mplvl.removeWidget(self.toolbar)
        #self.toolbar.close()


    def start_clicked(self):
        self.start.setText("Running")
        transgenic_type = 0
        if self.genedrive.isChecked() == True : transgenic_type = 1
        island_shape = misc.imread(str(self.regioncontour.text()))
        island_shape_gray = rgb2gray(island_shape)
        island_wet = ski.img_as_float(rgb2gray(misc.imread(str(self.twi.text()))))
        island_veg = adjust_gamma(ski.img_as_float(rgb2gray(misc.imread(str(self.vegindex.text())))), .2)
        ################################################################
        #parameters

        #sizes
        box = float(self.pixelSize.text())/1000   #0.06866823529

        grid_size = island_shape_gray.shape

        if str(self.cityregion.text()) == '': island_city =np.zeros(grid_size)
        else: island_city = rgb2gray(misc.imread(str(self.cityregion.text())))

        #inverse image

        inverse_map = abs(island_shape_gray - np.ones(grid_size))
        island_wet = adjust_gamma(abs(island_wet - np.ones(grid_size)), .5)

        island_size = island_shape_gray.size*inverse_map.mean()*box*box #lenth n' width in km -> use float

        #population limit
        pop_lim = int(str(self.populationLimit.text()))*10./3
        pop_lim_per_box = pop_lim*box*box

        #time
        dtime = (box*sqrt(2)/2./61)*1000 # in hours
        total_time = 24*int(self.daysAfterRelease.text())
        N_iterations = 1.*total_time/dtime
        eq_steps = int(str(self.Neq_step.text()))#steps used for reaching equilibria on normal insects

        #rates in dtime (hours)
        population_growth_rate = float(self.populationGrowthRate.text())
        population_growth_rate += .001

        death_rate = -(.1/24)*dtime #death rate per cycle
        female_reproduction_percentage = .2 #percentage of fertile females (no unit)
        N_ovopositions = dtime*3./24 #number of ovopositions per cycle per female
        density_larvae_death = 0.1 #larvae death rate per day
        larvae_survival = (1/0.5)*(population_growth_rate - 1 - death_rate)*(2./female_reproduction_percentage)/(N_ovopositions*100.)
        egg_to_fertile_adult = 24*8. #time from egg to mature mosquito in hours
        emigration_rate = .104 #rate of emigration per cycle
        delta_fitness = 1. #percentage
        birth_rate = N_ovopositions* 100.*larvae_survival*female_reproduction_percentage# per female per cycle

        ################################################################
        #Functions

        def emigration(N, N_neighbors, true_neighbors):
            return -(N-death(N))*emigration_rate*N_neighbors*true_neighbors/16.  ######## colocar q ninguem imigra pro mar

        def imigration(grid, i, j):
            variable = (grid[i][j-1] + grid[i][j+1] + grid[i+1][j] + grid[i-1][j])
            return (1./4)*(variable - death(variable))*emigration_rate

        def birth(Nf, Nm, NMut, city):
            if Nm <= 0 and NMut <= 0: return (0,0)
            if (1 - (Nf+Nm+NMut)/pop_lim_per_box) < 0 : a = 0
            else: a = Nf*birth_rate*(1 - (Nf+Nm+NMut)/pop_lim_per_box)
            mutant = a*(1.*NMut/(NMut+Nm))*transgenic_type
            normal = a*(1./2)*(1.*Nm/(NMut+Nm))
            if city == True : mutant *= 1.2 ; normal *=1.2
            return  (normal, mutant)

        def death(N):
            return N*death_rate

        def passo(grid_female, grid_male, grid_mutant):
            #nonlocal grid_female_stack, grid_male_stack, grid_mutant_stack
            grid_female_old = grid_female_stack.pop(0)
            grid_male_old = grid_male_stack.pop(0)
            grid_mutant_old = grid_mutant_stack.pop(0)

            delta_male = np.zeros(grid_size)
            delta_female = np.zeros(grid_size)
            delta_mutant = np.zeros(grid_size)
            for i in range(1 ,grid_size[0]-1):
                for j in range(1 ,grid_size[1]-1):
                    (birth_normal, birth_mutant) = birth(grid_female_old[i][j], grid_male_old[i][j], grid_mutant_old[i][j], island_city[i][j])
                    delta_male[i,j]   = emigration(  grid_male[i][j], neighbor(i,j,neighbors_map), neighbor(i,j,inverse_map)) + imigration(  grid_male, i, j) + birth_normal*(island_wet[i,j]) + death(grid_male[i][j])*island_veg[i,j]
                    delta_female[i,j] = emigration(grid_female[i][j], neighbor(i,j,neighbors_map), neighbor(i,j,inverse_map)) + imigration(grid_female, i, j) + birth_normal*(island_wet[i,j]) + death(grid_female[i][j])*island_veg[i,j]
                    delta_mutant[i,j] = emigration(grid_mutant[i][j], neighbor(i,j,neighbors_map), neighbor(i,j,inverse_map)) + imigration(grid_mutant, i, j) + birth_mutant*(island_wet[i,j]) + death(grid_mutant[i][j])*island_veg[i,j]
            grid_male += delta_male
            grid_male *= inverse_map
            grid_female += delta_female
            grid_female *= inverse_map
            grid_mutant += delta_mutant
            grid_mutant *= inverse_map


        def map_bondary(area):
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    if i == 0 or j == 0 or i == grid_size[0]-1 or j == grid_size[1]-1: area[i][j] = 0
                    else: area[i][j] = 1

        def map_corect_border(area):
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    if i == 0 or j == 0 or i == grid_size[0]-1 or j == grid_size[1]-1: area[i][j] = 0

        def neighbor(i,j, area):
            return area[i][j-1] + area[i][j+1] + area[i+1][j] + area[i-1][j]

        def figure(i):
            subplot(1, 2, 1,  aspect= 1.*grid_size[0]/grid_size[1])
            pcolormesh(grid_mutant, cmap=cm.OrRd, vmax=colorbar_max/3., vmin=0)
            title('mutant density')
            axis([1, grid_size[1]-1, grid_size[0]-1, 1])
            #grid(True)
            colorbar(shrink = 6.4/10.9)

            subplot(1, 2, 2,  aspect= 1.*grid_size[0]/grid_size[1]) #, adjustable='box'
            pcolormesh(grid_female, cmap=cm.gist_earth, vmax=colorbar_max, vmin=0)
            colorbar(shrink = 6.4/10.9)
            grid(True)
            axis([1, grid_size[1]-1, grid_size[0]-1, 1])
            title('females density')
            suptitle('%.2f' % (1.*i*dtime/24 + 1) +' days after mutant release')
            tight_layout()
            savefig('timelapse/mosquitos-' + '{0:03d}'.format(int(i/24+1))+ '.png', dpi = 500/4. , figsize = (11/4.,7/4.)) #
            close()

        def plot_nmosq_time():
            tot_list = np.array(male_history)+ np.array(mutant_history)+ np.array(female_history)
            subplot(1,1,1)
            plot([x*dtime/24. for x in range(len(male_history))],[float(x)/(island_size) for x in male_history], label = 'wt male')
            plot([x*dtime/24. for x in range(len(female_history))],[float(x)/(island_size) for x in tot_list.tolist()], label = 'total population')
            plot([x*dtime/24. for x in range(len(mutant_history))],[float(x)/(island_size) for x in mutant_history], label = 'mutant')

            xlabel('days after mutant release')
            ylabel('population size per square Km')
            title('variation in population size ')
            grid(True)
            legend(loc='best', prop={'size':10})
            savefig("graphs/popsize ndays: " + str(total_time/24.)+ ' dtime: ' + str(dtime)+ ' boxsize: '+ str(box)+ '.png')
            close()
            subplot(1,1,1)
            plot([x*dtime/24. for x in range(len(mutant_history))],(np.array(mutant_history)/tot_list).tolist(), label= 'mutant percentage')
            plot([x*dtime/24. for x in range(len(mutant_history))],(np.array(female_history)/tot_list).tolist(), label= 'female percentage')

            xlabel('days after mutant release')
            ylabel('percentages')
            ylim(0,1)
            title('mutant and female percentages after realease')
            grid(True)
            legend(loc='best', prop={'size':10})
            savefig("graphs/percentages ndays: " + str(total_time/24.)+ ' dtime: ' + str(dtime)+ ' boxsize: '+ str(box)+ '.png') #, bbox_inches='tight',dpi=100
            close()

        ################################################################
        #initializing grids

        grid_male = np.random.randint(low = pop_lim_per_box*.15 -1 , high = pop_lim_per_box*.30, size = grid_size)*abs(island_shape_gray - np.ones(grid_size))
        grid_female = grid_male[:]
        grid_mutant = np.zeros(grid_size)
        neighbors_map = np.ones(grid_size)

        grid_male_stack = [grid_male[:] for i in range(int(egg_to_fertile_adult/dtime))]
        grid_female_stack = [grid_female[:] for i in range(int(egg_to_fertile_adult/dtime))]
        grid_mutant_stack = [np.zeros(grid_size) for i in range(int(egg_to_fertile_adult/dtime))]

        map_bondary(neighbors_map)
        map_corect_border(grid_male)
        map_corect_border(grid_female)
        map_corect_border(grid_mutant)

        ##############################################################
        # starting program



        CURSOR_UP_ONE = '\x1b[1A'
        ERASE_LINE = '\x1b[2K'

        print("Equilibrium steps started")
        for i in range(eq_steps):
            grid_male_stack += [grid_male]
            grid_female_stack += [grid_female]
            grid_mutant_stack += [grid_mutant]
            loading = "%.2f" % (float(i)*100./eq_steps) + "%"
            print("loading: " + loading + " completed")
            self.progressBareq.setText(loading)
            passo(grid_female, grid_male, grid_mutant)
            print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)


        print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
        print("Equilibrium steps completed")

        colorbar_max = grid_female.max()*.95


        for single_point in self.MutantLIST:
            y,x,quantity = single_point
            grid_mutant[y,x] = quantity
        grid_mutant_stack[-1] = grid_mutant


        #mosquito population size history
        male_history = []
        female_history = []
        mutant_history = []

        close()
        figure(-1)
        for i in range(int(N_iterations)):
            loading = "%.2f" % (float(i)/N_iterations*100) + "%"
            self.progressBarsim.setText(loading)
            print("loading: " + loading + " completed")
            grid_male_stack += [grid_male]
            grid_female_stack += [grid_female]
            grid_mutant_stack += [grid_mutant]

            passo(grid_female, grid_male, grid_mutant)

            female_history += [np.sum(grid_female)]
            mutant_history += [np.sum(grid_mutant)]
            male_history += [np.sum(grid_male)]

            if i%48==0:
                figure(i)

            print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
            if grid_female.sum() <= 400: break

        print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
        print("___________________________________ \n \n")


        plot_nmosq_time()
        self.progressBareq.setText("0%")
        self.progressBarsim.setText("0%")
        self.start.setText("Run Simulation")




app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass()
myWindow.show()
app.exec_()
