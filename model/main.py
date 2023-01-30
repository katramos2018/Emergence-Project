from __future__ import division
from random import shuffle, seed, randint
from os.path import expanduser
import sys
import numpy as np
import multiprocessing as mp

mydir = expanduser("~/")
sys.path.append(mydir + "/Emergence/model")

from processes import *
from diversity_metrics import *
from spatial_functions import *
from input_output import *

labels.clear()
procs = labels.processes()

def iter_procs(procs, iD, sD, rD, ps, ct, pr = 0, ceil = 2000):

    shuffle(procs)
    for p in procs:

        if p is 'resource_inflow': # Inflow of resources
            rD = bide.ResIn(rD, ps)

        elif p is 'resource_flow': # Resource flow
            rD = bide.res_flow(rD, ps)

        elif p is 'immigration' and ps[2] > 0: # Inflow of individuals (immigration)
            sD, iD = bide.immigration(sD, iD, ps)

        elif p is 'passive_dispersal': # flowthrough of individuals
            iD = bide.ind_flow(iD, ps)

        elif p is 'active_dispersal': # Active dispersal
            iD = bide.ind_disp(iD, ps)

        elif p is 'consume': # Consume
            iD, rD = bide.consume(iD, rD, ps)

        elif p is 'growth': # Grow
            iD = bide.grow(iD)

        elif p is 'transition': # Transition
            iD = bide.transition(iD)

        elif p is 'maintenance': # Maintenance
            iD = bide.maintenance(iD)

        elif p is 'reproduction': # Reproduction
            sD, iD, pr = bide.reproduce(sD, iD, ps)

        elif p is 'disturb' and len(list(iD)) > ceil:
            iD = bide.disturb(iD, ceil)

    N, R = len(list(iD)), len(list(rD))
    return [iD, sD, rD, N, R, ct+1, pr]



def run_model(p_s_list, rD = {}, sD = {}, iD = {}, ct = 0, splist2 = []):
    procs, sim = p_s_list # Changed the way that run_model takes in args bc map only accepts a single arg
    print '\n'
    r = randint(1, 100)
    h = randint(10, 100)
    l = int(h)

    ps = h, l, r, 10**np.random.RandomState().uniform(-4, 0) # fix bug that causes random seed to be the same for all sims during parallelization
    sD, iD = bide.immigration(sD, iD, ps, 1000)

    while ct < 600:
        iD, sD, rD, N, R, ct, prod = iter_procs(procs, iD, sD, rD, ps, ct)
        if N == 0: break
        if ct > 100 and ct%10 == 0: splist2 = output.output(iD, sD, rD, ps, sim, N, R, ct, prod, splist2)

# Generate a list of tuples to pass into run_model()

how_many = 100 #how many sims to run
names = []
counter = 0 

for i in range(0, how_many):
    value = [procs, counter]
    names.append(value)
    counter = counter+1

# Paralellize the run model function for faster sim generation
pool = mp.Pool(20)
pool.map(run_model, names)
