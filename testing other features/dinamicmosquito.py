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
from gridclasses import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

form_class = uic.loadUiType("gm_mosq.ui")[0]

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
        #print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %(event.button, event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            self.MutantLIST =np.array(self.MutantLIST.tolist() + [[int(event.ydata), int(event.xdata), int(str(self.MutValue.text()))]])
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
        self.toolbar = NavigationToolbar(self.canvas, self.widget, coordinates=True)
        self.mplvl.addWidget(self.toolbar)
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
        self.toolbar = NavigationToolbar(self.canvas, self.widget, coordinates=True)
        self.mplvl.addWidget(self.toolbar)
        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

    def rmmpl(self,):
        #plt.close()
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()

    def start_clicked(self):
        self.start.setText("Running")
        transgenic_type = 0
        if self.genedrive.isChecked() == True : transgenic_type = 1

        island_shape = misc.imread(str(self.regioncontour.text()))
        island_shape_gray = rgb2gray(island_shape)
        island_wet = ski.img_as_float(rgb2gray(misc.imread(str(self.twi.text()))))
        island_veg = adjust_gamma(ski.img_as_float(rgb2gray(misc.imread(str(self.vegindex.text())))), .2)
        if str(self.cityregion.text()) == '': island_city =np.zeros(grid_size)
        else: island_city = rgb2gray(misc.imread(str(self.cityregion.text())))

        mosquitos = Grid(island_shape_gray, island_veg, island_wet, island_city, float(self.pixelSize.text()),  int(str(self.populationLimit.text())), transgenic_type, int(self.Neq_step.text()))

        for single_point in self.MutantLIST:
            y,x,quantity = single_point
            mosquitos.GRID[y][x].amut = quantity

        CURSOR_UP_ONE = '\x1b[1A'
        ERASE_LINE = '\x1b[2K'
        mosquitos.images()
        for i in range( int(self.daysAfterRelease.text())):
            print("loading: " +str(i/int(self.daysAfterRelease.text())*100) + "% done")
            mosquitos.updateall()
            mosquitos.images()
            print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
        mosquitos.graph()
        print ("End of simulation")



app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass()
myWindow.show()
app.exec_()
