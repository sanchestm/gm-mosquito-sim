from random import *
import numpy as np
import matplotlib.pyplot as plt
from math import *
from itertools import product, repeat
import pickle as pkl
plt.style.use("ggplot")


def check(a):
    for i in a:
        if abs(i[0] > 1.5*box) or abs(i[1] > 1.5*box): return 0
    else: return 1

def check_howmany(a, box):
    result = 0
    for i in a:
        if abs(i[0] > 1.5*box) or abs(i[1] > 1.5*box): result += 1
    return result/a.shape[0]

def findquadrant(point,size):
    y,x = point
    halfsize = size/2
    if x < -halfsize:
        if y > halfsize: return [0,0]
        if y < -halfsize: return [2,0]
        return [1,0]
    if x > halfsize:
        if y > halfsize: return [0,2]
        if y < -halfsize: return [2,2]
        return [1,2]
    if y > halfsize: return [0,1]
    if y < -halfsize: return [2,1]
    return [1,1]

def findStep(points, box):
    tempo = 0
    dt = 1
    V = 300/60
    while check_howmany(points, box) < 0.05:
        for i in points:
            a = uniform(0, 2*pi)
            vvar, hvar = V*dt*sin(a), V*dt*cos(a)
            i[0] += vvar; i[1] += hvar
        tempo += dt
    return tempo

def randomWalk(points, nonacessquadrants, time):
    dt = 1
    V = 300/60
    for atime in range(time):
        for i in points:
            a = uniform(0, 2*pi)
            vvar, hvar = V*dt*sin(a), V*dt*cos(a)
            i[0] += vvar; i[1] += hvar
            #if findquadrant(i, size) in nonacessquadrants: i[0] -= 2*vvar
            #if findquadrant(i, size) in nonacessquadrants: i[0] += 2*vvar; i[1] -= 2*hvar
            #if findquadrant(i, size) in nonacessquadrants: i[0] -= 2*vvar
    return points

def gridify(somelist, size):
    shape = (3,3)
    grid = np.zeros(shape)
    for point in somelist:
        quadrant = findquadrant(point,size)
        grid[quadrant[0]][quadrant[1]] += 1
    grid = grid/grid.sum()
    return np.array(grid)

npoints = 30000
def newpoints(n, size):
    return np.array([[uniform(-size/2,size/2),uniform(-size/2,size/2)] for i in range(n)])

def MaxStep(box):
    a = 0
    for i in range(7):
        a += findStep(newpoints(npoints, box), box)
    a = a/5
    for i in range(int(a),0, -1):
        if 24*60 % i == 0: return i
    return("deu ruim")


def weightDictmaker(maxstep, npoints,size):
    allmatrices = list(product(*(repeat((0, 1), 8))))
    print(len(allmatrices))
    dictionary_matrix_to_num = {}
    dict_num_to_weights = {}
    nowalls = gridify(randomWalk(newpoints(npoints,size), [], maxstep), size)
    avgcorner = (nowalls[0,0]+nowalls[2,2]+nowalls[2,0]+nowalls[0,2])/4
    avgwall = (nowalls[1,0]+nowalls[0,1]+nowalls[2,1]+nowalls[1,2])/4
    nowalls[0,0], nowalls[2,2], nowalls[2,0], nowalls[0,2] = [avgcorner for i in range(4)]
    nowalls[1,0], nowalls[0,1], nowalls[2,1], nowalls[1,2] = [avgwall   for i in range(4)]
    for index, case in enumerate(allmatrices):
        dictionary_matrix_to_num[case] = index
        multiplier = np.ones((3,3))
        if case[0] == 1: multiplier[0,0] = 0
        if case[1] == 1: multiplier[1,0] = 0
        if case[2] == 1: multiplier[2,0] = 0
        if case[3] == 1: multiplier[0,1] = 0
        if case[4] == 1: multiplier[2,1] = 0
        if case[5] == 1: multiplier[0,2] = 0
        if case[6] == 1: multiplier[1,2] = 0
        if case[7] == 1: multiplier[2,2] = 0
        dict_num_to_weights[index] = nowalls*multiplier/(nowalls*multiplier).sum()
    MyDicts = [dictionary_matrix_to_num, dict_num_to_weights]
    pkl.dump( MyDicts, open( "myDicts.p", "wb" ) )
    return MyDicts
