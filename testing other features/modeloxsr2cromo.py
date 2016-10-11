import matplotlib
from numpy import *
from random import *
from matplotlib.pyplot import *

n = 1000
px = 0.700
pxsr = 0.005
ngen =  50
ngen2 = 250
razaoxsr = .75
p_repressor = 0.
efeito_repressor =  1.

#-------------------------------------------------functions----------------------------------------------------------------     
def seleciona(px, pxsr):
    a = random()
    if a<px : return 'x'
    if a < px + pxsr: return 'xsr'
    else: return 'y'

def seleciona2(prepressao):
    a = random()
    if a < prepressao : return 'repressor'
    else: return 'wt'

def calcula(m_lista, f_lista): 
    nx = 0.
    ny = 0.
    nxsr = 0.
    nrepressor = 0.
    sizem = size(m_lista)/4
    sizef = size(f_lista)/4
    sizetot = (sizem + sizef)*4
    for i in range(sizem):
        if m_lista[i][0] == 'x': nx += 1.
        elif m_lista[i][0] == 'y': ny += 1.
        elif m_lista[i][0] == 'xsr': nxsr += 1.
        if m_lista[i][1] == 'x': nx += 1.
        elif m_lista[i][1] == 'y': ny += 1.
        elif m_lista[i][1] == 'xsr': nxsr += 1.
        if m_lista[i][2] == 'repressor': nrepressor += 1.
        if m_lista[i][3] == 'repressor': nrepressor += 1.
    for i in range(sizef):
        if f_lista[i][0] == 'x': nx += 1.
        elif f_lista[i][0] == 'y': ny += 1.
        elif f_lista[i][0] == 'xsr': nxsr += 1.
        if f_lista[i][1] == 'x': nx += 1.
        elif f_lista[i][1] == 'y': ny += 1.
        elif f_lista[i][1] == 'xsr': nxsr += 1.
        if f_lista[i][2] == 'repressor': nrepressor += 1.
        if f_lista[i][3] == 'repressor': nrepressor += 1.
    return (2*nx/sizetot, 2*nxsr/sizetot, 2*ny/sizetot, sizem*1., sizef*1., 2*nrepressor/sizetot)

def next_gen(n, m_lista, f_lista):
    m_new = []
    f_new = []
    for i in range(n):
        
        sexo = 0
        m_sample = randint(0, size(m_lista)/4-1) #escolhe um macho
        chanceXSR = razaoxsr # reseta a chance XSR
        if m_lista[m_sample][0] == 'xsr' or m_lista[m_sample][1] == 'xsr':
            if m_lista[m_sample][2] == 'repressor' or m_lista[m_sample][3] == 'repressor':  #efeitos do repressor
                if m_lista[m_sample][2] == m_lista[m_sample][3] : chanceXSR =  chanceXSR - (chanceXSR - .5)*efeito_repressor
                else: chanceXSR =  chanceXSR - (chanceXSR - .5)*(efeito_repressor/2.)
            if random() < chanceXSR: a = 'xsr' #escolhe a
            else: a = 'y'; sexo = 1
        else:
            if random() < .5: a = 'x'
            else: a = 'y'; sexo = 1
        c = m_lista[m_sample][randint(2,3)] #escolhe c
        
        chanceXSR = razaoxsr # reseta a chance XSR
        f_sample = randint(0, size(f_lista)/4-1) #escolhe uma femea
        if f_lista[f_sample][0] ==  f_lista[f_sample][1]:
            b = f_lista[f_sample][1] 
        else:
            if f_lista[f_sample][2] == 'repressor' or f_lista[f_sample][3] == 'repressor':  #efeitos do repressor
                if f_lista[f_sample][2] == f_lista[f_sample][3] : chanceXSR =  chanceXSR - (chanceXSR - .5)*efeito_repressor
                else: chanceXSR =  chanceXSR - (chanceXSR - .5)*(efeito_repressor/2.)
            if random() < chanceXSR: b = 'xsr'
            else: b = 'x'
        d = f_lista[f_sample][randint(2,3)] #escolhe d
        if sexo == 1: m_new += [[a,b,c ,d]]
        else: f_new += [[a,b,c,d]] 
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
    c = seleciona2(p_repressor)
    d = seleciona2(p_repressor)
    if sexo == 1 : macho += [(a,b, c, d)]
    else: femea += [(a,b, c,d)]


b = calcula(macho,femea)
px_list = [b[0]]
pxsr_list = [b[1]]
py_list = [b[2]]
msize_list= [b[3]]
fsize_list = [b[4]]
repressor_list = [b[5]]
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
    repressor_list += [b[5]]
    geracoes_list += [geracoes_list[-1]+1]


a[1][randint(0,size(a[1])/4. - 1 )][3] = 'repressor'
a[0][randint(0,size(a[0])/4. - 1 )][2] = 'repressor'
a[1][randint(0,size(a[1])/4. - 1 )][3] = 'repressor'
a[0][randint(0,size(a[0])/4. - 1 )][2] = 'repressor'
a[1][randint(0,size(a[1])/4. - 1 )][3] = 'repressor'
a[0][randint(0,size(a[0])/4. - 1 )][2] = 'repressor'
a[1][randint(0,size(a[1])/4. - 1 )][3] = 'repressor'
a[0][randint(0,size(a[0])/4. - 1 )][2] = 'repressor'

for i in range(ngen2):
    a = next_gen(n,a[0],a[1])
    b = calcula(a[0],a[1])
    px_list += [b[0]]
    pxsr_list += [b[1]]
    py_list += [b[2]]
    msize_list += [b[3]]
    fsize_list += [b[4]]
    repressor_list += [b[5]]
    geracoes_list += [geracoes_list[-1]+1]

plot(geracoes_list , px_list,  label= "frequencia X")
plot(geracoes_list , pxsr_list,  label= "frequencia Xsr")
plot(geracoes_list ,py_list,  label= "frequencia Y")
plot(geracoes_list,repressor_list, label = "frequencia repressor" )
plot(geracoes_list , [x/n for x in msize_list], label= "frequencia macho", linestyle='--')
plot(geracoes_list , [x/n for x in fsize_list], label= "frequencia femea", linestyle='--')
plot([ ngen for x in range(0,100)], [x*.01 for x in range(0,100)], color = 'black')

title('Alelos por tempo | N = '+ str(n) + '; PXsr = '+ str(pxsr)+ '; razaoXSR = '+ str(razaoxsr)+ '; efeito_repre = ' + str(efeito_repressor))
ylabel('proporcao alelica')
ylim(0,1)
xlim(1, geracoes_list[-1])
xlabel('numero de geracoes')
legend(loc='best', prop={'size':7})
annotate('surge repressor',  xytext=(ngen, .95), xy=(ngen, .95) )
grid(True)
show()
