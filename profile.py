#! /usr/bin/env python

import time
import math
import numpy
from functools import partial
from ecell4 import *


radius = 5e-9
with species_attributes():
    A | { 'radius':  str(radius), 'D': '1.0e-12' }
model = get_model()

ns = numpy.logspace(1.5, 4.5, 7).astype(int)

#NUM_STEPS = 10000
NUM_STEPS = 100
RUN_LIMIT = 500.0 # sec
def measure_run_time(simulator, steps):
    elapsed = 0
    start = time.time()
    for i in range(steps):
        simulator.step()
        elapsed = time.time() - start
        if (elapsed >= RUN_LIMIT):
            elapsed *= float(steps) / (i+1)
            break
    print("steps:{}, t:{}".format(steps, simulator.t()))
    return elapsed / simulator.t()

def num_partitions(L, N):
    return int(min(L/(2*radius), max(3, cbrt(N))))

def create_world(factory, L, num):
    world = factory.create_world(Real3(L, L, L))
    world.bind_to(model)
    world.add_molecules(Species('A'), num)
    return world

def profile(edge_length_method, rng, constructor, scaled_step, *args):
    elapsed_time = []
    for num in ns:
        edge_length = edge_length_method(num)
        factory = constructor(edge_length, num, rng, *args)
        world = create_world(factory, edge_length, num)
        simulator = factory.create_simulator(model, world)
        steps_per_cycle = num if scaled_step else 1
        elapsed_time.append(measure_run_time(simulator, int(steps_per_cycle * NUM_STEPS)))
    return elapsed_time

def get_edge_length_with_40fL(num):
    return 3.42e-6

def get_edge_length_with_100nM(num):
    return cbrt(num/60.0*1.0e-18)

def create_partitioned_constructor(constructor):
    def make_instance(L, num, rng, *args):
        m = num_partitions(L, num)
        return constructor(Integer3(m,m,m), *(args + (rng,)))
    return make_instance

def create_non_partitioned_constructor(constructor):
    def make_instance(L, num, rng, *args):
        return constructor(*(args + (rng,)))
    return make_instance


factories = {
    "spatiocyte" : [create_non_partitioned_constructor(spatiocyte.SpatiocyteFactory), False, radius],
    "egfrd"      : [create_partitioned_constructor(egfrd.EGFRDFactory),               True],
    "egfrd.bd"   : [create_partitioned_constructor(egfrd.BDFactory),                  False],
    "bd.bd"      : [create_partitioned_constructor(bd.BDFactory),                     False],
    "meso"       : [create_non_partitioned_constructor(meso.MesoscopicFactory),       True,  100e-9]
}
profile_methods = {
    "vol"  : partial(profile, get_edge_length_with_40fL),
    "conc" : partial(profile, get_edge_length_with_100nM)
}

def print_usage(methods, factories):
    print("USAGE: python profile.py [" + "|".join(methods) + "] [" + "|".join(factories) + "] <int>")

if __name__ == '__main__':
    import sys
    argc = len(sys.argv)
    if argc < 3:
        print_usage(profile_methods.keys(), factories.keys())
        sys.exit(1)

    method = sys.argv[1]
    system = sys.argv[2]

    rng = GSLRandomNumberGenerator()
    if argc >= 4:
        rng.seed(int(sys.argv[3]))

    if method not in profile_methods:
        print("Invalid method")
        print_usage(profile_methods.keys(), factories.keys())
        sys.exit(2)

    if system not in factories:
        print("Invalid system")
        print_usage(profile_methods.keys(), factories.keys())
        sys.exit(3)

    elapsed_time = profile_methods[method](rng, *factories[system])
    with open("tsv/%s_fixed_%s.tsv" % (system, method), 'w') as f:
        for (num, time) in zip(ns, elapsed_time):
            print >> f,  num, time
