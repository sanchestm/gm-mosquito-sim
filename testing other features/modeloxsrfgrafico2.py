import matplotlib
from numpy import *
from random import *
from matplotlib.pyplot import *

n = 3000
px = 0.15
pxsr = 0.6
ngen = 20
razaoxsr = .8

#-------------------------------------------------functions----------------------------------------------------------------		
def seleciona(px, pxsr):
    a = random()
    if a<px : return 'x'
    if a < px + pxsr: return 'xsr'
    else: return 'y'

def calcula(m_lista, f_lista): 
    nx = 0.
    ny = 0.
    nxsr = 0.
    sizem = size(m_lista)/2
    sizef = size(f_lista)/2
    sizetot = (sizem + sizef)*2
    for i in range(sizem):
    	if m_lista[i][0] == 'x': nx += 1.
    	elif m_lista[i][0] == 'y': ny += 1.
    	elif m_lista[i][0] == 'xsr': nxsr += 1.
    	if m_lista[i][1] == 'x': nx += 1.
    	elif m_lista[i][1] == 'y': ny += 1.
    	elif m_lista[i][1] == 'xsr': nxsr += 1.
    for i in range(sizef):
    	if f_lista[i][0] == 'x': nx += 1.
    	elif f_lista[i][0] == 'y': ny += 1.
    	elif f_lista[i][0] == 'xsr': nxsr += 1.
    	if f_lista[i][1] == 'x': nx += 1.
    	elif f_lista[i][1] == 'y': ny += 1.
    	elif f_lista[i][1] == 'xsr': nxsr += 1.
    return (nx/sizetot, nxsr/sizetot, ny/sizetot, sizem*1., sizef*1.)

def next_gen(n,rzxsr, m_lista, f_lista):
	chanceXSR = rzxsr      #editar a chance para medir o grau de meiotic drive
	m_new = []
	f_new = []
	for i in range(n):
		sexo = 0
		m_sample = randint(0, size(m_lista)/2-1)
		if m_lista[m_sample][0] == 'xsr' or m_lista[m_sample][1] == 'xsr':
			if random() < chanceXSR: a = 'xsr'
			else: a = 'y'; sexo = 1
		else:
			if random() < .5: a = 'x'
			else: a = 'y'; sexo = 1
		
		f_sample = randint(0, size(f_lista)/2-1)
		if f_lista[f_sample][0] ==  f_lista[f_sample][1]:
			b = f_lista[f_sample][1] 
		else:
			if random() < chanceXSR: b = 'xsr'
			else: b = 'x'
		if sexo == 1: m_new += [(a,b)]
		else: f_new += [(a,b)] 
	return (m_new, f_new)


#-------------------------------------------------functions----------------------------------------------------------------			
			



def proporcao(rzxsr, ngen):
	macho = []
	femea = []
	for i in range(n):
		sexo = 0
		razaoXSR = pxsr/px       #editar a chance para medir o grau de meiotic drive
		a = seleciona(px,pxsr)
		if a == 'y':      #editar a chance para medir o grau de meiotic drive
			sexo = 1
			if random()< razaoXSR : b = 'xsr'
			else: b = 'x'
		else: b = seleciona(px,pxsr)
		if b == 'y' : sexo = 1
		if sexo == 1 : macho += [(a,b)]
		else: femea += [(a,b)]
	a = (macho, femea)
	for i in range(ngen): 
		a = next_gen(n, rzxsr,a[0],a[1])
		if size(a[0])==0 or size(a[1]) == 0: return 1.
	return size(a[1])/(n*2.)

Xsr_preference= [x/100. for x in range(50, 105, 5)]
frequencia_femea = [proporcao(x, ngen) for x in Xsr_preference]

plot(Xsr_preference, frequencia_femea)
title('Proporcao de femeas pela Preferencia-Xsr | N = '+ str(n) + 'ngen = '+ str(ngen))
ylabel('Frequencia de femeas')
ylim(.5,1)
xlim(.5,1)
grid(True)
xlabel('Preferencia pelo Xsr')
show()




