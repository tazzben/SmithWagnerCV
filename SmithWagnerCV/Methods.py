from __future__ import division, print_function, absolute_import
import os
import sys
import numpy
import pandas as pd
from multiprocessing import Pool

def GuessPre(x,numoptions):
    if x['pretest']==1:
        return 1
    if x['guesspre'] <= 1.0/numoptions:
        return 1
    else:
        return 0

def GuessPost(x,numoptions):
    if x['posttest']==1:
        return 1
    if x['guesspost'] <= 1.0/numoptions:
        return 1
    else:
        return 0

Known = lambda x, mu: 1 if x['draw'] <= mu else 0
NL = lambda x: 1 if x['posttest']==0 and x['pretest']==1 else 0
PL = lambda x: 1 if x['posttest']==1 and x['pretest']==0 else 0
ZL = lambda x: 1 if x['posttest']==0 and x['pretest']==0 else 0
RL = lambda x: 1 if x['posttest']==1 and x['pretest']==1 else 0

def GenerateClass(students,mu,numoptions):
    df = pd.DataFrame({'draw':numpy.random.uniform(0,1,students).tolist(),'guesspre':numpy.random.uniform(0,1,students).tolist(),'guesspost':numpy.random.uniform(0,1,students).tolist(),'pretest':0,'posttest':0,'pl':0,'nl':0,'zl':0,'rl':0})
    df['pretest'] = df.apply(Known, axis=1, args=(mu,))
    df['posttest'] = df['pretest']
    df['pretest'] = df.apply(GuessPre, axis=1, args=(numoptions,))
    df['posttest'] = df.apply(GuessPost, axis=1, args=(numoptions,))
    df['pl'] = df.apply(PL, axis=1)
    df['nl'] = df.apply(NL, axis=1)
    df['zl'] = df.apply(ZL, axis=1)
    df['rl'] = df.apply(RL, axis=1)
    return (df['pl'].mean(),df['nl'].mean(),df['zl'].mean(),df['rl'].mean())


def SimulationLoop(csize,mu,numoptions):
    pl, nl, zl, rl = GenerateClass(csize,mu,numoptions)
    emu = ((nl+rl)-1)/(numoptions-1)+nl+rl
    egamma = (numoptions*(nl+pl*numoptions+rl-1))/((numoptions-1)**2)
    ealpha = (numoptions*(nl*numoptions+pl+rl-1))/((numoptions-1)**2)
    eflow = (numoptions*(pl-nl))/(numoptions-1)
    if emu == 1:
        egain = numpy.inf
    else:
        egain = egamma/(1-emu)
    return [pl,nl,zl,rl,egamma,ealpha,emu,eflow,egain]

def Simulation(csize,mu,numoptions,R):
    args = ((csize,mu,numoptions) for i in range(R))
    with Pool() as p:
        r = p.starmap(SimulationLoop, args)
    return pd.DataFrame(data=r,columns=('pl', 'nl', 'zl','rl','gamma','alpha','mu','flow','gain'))

def SimulateDist(cs, mu, numoptions=4, criticalValues=[0.90,0.95], confInt=[0.025, 0.975], R=10000):
    r = Simulation(cs,mu,numoptions,R)
    resultDict = {}
    ci = [r['mu'].quantile(q=civ) for civ in confInt]
    for col in r:
        if col in ('gamma','alpha','flow','gain'):
            cvs = []
            for val in criticalValues:
                ng =  r[r[col] <= r[col].quantile(q=val)]
                ng = ng.sort_values([col,'mu'], ascending=[False,True])
                cvs.append(ng.iloc[0][col])
            resultDict[col] = {'mu':mu, 'class':cs, 'criticalValues': dict(zip(criticalValues, cvs)), 'ci': dict(zip(confInt, ci))}
    return resultDict