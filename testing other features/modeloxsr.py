import matplotlib
from numpy import *
from random import *
from matplotlib.pyplot import *

n = 1200
px = 0.749
pxsr = 0.01
ngen = 60
razaoxsr = .75

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

def next_gen(n, m_lista, f_lista):
	chanceXSR = razaoxsr      #editar a chance para medir o grau de meiotic drive
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


b = calcula(macho,femea)
px_list = [b[0]]
pxsr_list = [b[1]]
py_list = [b[2]]
msize_list= [b[3]]
fsize_list = [b[4]]
geracoes_list = [1]

a = next_gen(n,macho,femea)

for i in range(ngen):
    a = next_gen(n,a[0],a[1])
    b = calcula(a[0],a[1])
    px_list += [b[0]]
    pxsr_list += [b[1]]
    py_list += [b[2]]
    msize_list += [b[3]]
    fsize_list += [b[4]]
    geracoes_list += [geracoes_list[-1]+1]

plot(geracoes_list , px_list,  label= "frequencia X")
plot(geracoes_list , pxsr_list,  label= "frequencia Xsr")
plot(geracoes_list ,py_list,  label= "frequencia Y")
plot(geracoes_list , [x/n for x in msize_list], label= "frequencia macho", linestyle='--')
plot(geracoes_list , [x/n for x in fsize_list], label= "frequencia femea", linestyle='--')

title('Proporcao alelica pelo tempo | N = '+ str(n) + '; PXsr = '+ str(pxsr)+ '; razaoXSR = '+ str(razaoxsr))
ylabel('proporcao alelica')
ylim(0,1)
xlim(1, geracoes_list[-1])
xlabel('numero de geracoes')
legend(loc='best', prop={'size':10})
grid(True)
show()
