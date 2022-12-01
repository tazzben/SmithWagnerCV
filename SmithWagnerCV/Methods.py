from __future__ import division, print_function, absolute_import
import numpy
import pandas as pd
from multiprocessing import Pool
from itertools import product
from tqdm import tqdm

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

def RunSimulation(cs, mu, numoptions=4, criticalValues=[0.90,0.95], confInterval=[0.025, 0.975], R=10000):
    """ 
    Produces a Monte Carlo simulation of student guessing on a pre- and post-test based the specified class size, mu value, and question options.

	Parameters
	----------
	cs : int
        Class size 
    mu : float
        Proportion of the class with stock knowledge
    numoptions : int
        Number of options on the exam. Defaults to four.
    criticalValues : list
        List of critical values to extract from the learning distributions.  Defaults to [0.90,0.95].
    confInterval: : list
        List of values to extract from the mu distribution.  Defaults to [0.025, 0.975].
    R : int
        Number of iterations for each simulation.  Defaults to 10,000.
    
    Returns
    -------
    Dictionary:
        'gamma'
        'alpha'
        'flow'
        'gain'
    
    Each learning type contains a nested dictionary of:
        'mu' : float
        'classSize' : int
        'criticalValues' : dict
        'muCI' : dict
    """
    r = Simulation(cs,mu,numoptions,R)
    resultDict = {}
    ci = [r['mu'].quantile(q=civ) for civ in confInterval]
    for col in r:
        if col in ('gamma','alpha','flow','gain'):
            cvs = []
            for val in criticalValues:
                ng =  r[r[col] <= r[col].quantile(q=val)]
                ng = ng.sort_values([col,'mu'], ascending=[False,True])
                cvs.append(ng.iloc[0][col])
            resultDict[col] = {'mu':mu, 'classSize':cs, 'criticalValues': dict(zip(criticalValues, cvs)), 'muCI': dict(zip(confInterval, ci))}
    return resultDict

def SimulationTable(csList, muList, numoptions = 4, criticalValues = [0.90,0.95], confInterval = [0.025, 0.975], R = 10000):
    """ 
    Saves a tables of Monte Carlo simulations of student guessing on a pre- and post-test based the specified class size, mu value, and question options.

	Parameters
	----------
	csList : list
        List of class sizes 
    muList : list
        List of mu values
    numoptions : int
        Number of options on the exam. Defaults to four.
    criticalValues : list
        List of critical values to extract from the learning distributions.  Defaults to [0.90,0.95].
    confInterval: : list
        List of values to extract from the mu distribution.  Defaults to [0.025, 0.975].
    R : int
        Number of iterations for each simulation.  Defaults to 10,000.
    
    Returns
    -------
    Dictionary:
        'gamma'
        'alpha'
        'flow'
        'gain'
    
    Each learning type contains a nested list of dictionaries with:
        'mu' : float
        'classSize' : int
        'criticalValues' : dict
        'muCI' : dict
    """
    
    r = []
    l = list(product(csList,muList))
    for row in tqdm(l):
        r.append(RunSimulation(row[0], row[1], numoptions, criticalValues, confInterval, R))
    
    returnDict = {'gamma':[],'alpha':[],'flow':[],'gain':[]}
    for e in r:
        for dice in ('gamma','alpha','flow','gain'):
            returnDict[dice].append(e[dice])
    
    return returnDict

def SaveSimulationTable (csList, muList, numoptions = 4, criticalValues = [0.90,0.95], confInterval = [0.025, 0.975], R = 10000):
    """ 
    Produces a a table of Monte Carlo simulations of student guessing on a pre- and post-test based the specified class size, mu value, and question options.

	Parameters
	----------
	csList : list
        List of class sizes 
    muList : list
        List of mu values
    numoptions : int
        Number of options on the exam. Defaults to four.
    criticalValues : list
        List of critical values to extract from the learning distributions.  Defaults to [0.90,0.95].
    confInterval: : list
        List of values to extract from the mu distribution.  Defaults to [0.025, 0.975].
    R : int
        Number of iterations for each simulation.  Defaults to 10,000.
            
    Returns
    -------
        None
            Saves four CSV files.
    """
    resultsDictionary = SimulationTable(csList, muList, numoptions, criticalValues, confInterval, R)
    for col in ('gamma','alpha','flow','gain'):
        d = pd.DataFrame(resultsDictionary[col])
        df = pd.DataFrame(d)
        filename = col + "Results.csv"
        df.to_csv(filename)