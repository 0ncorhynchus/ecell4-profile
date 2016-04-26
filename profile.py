#! /usr/bin/env python

import time
import math
import numpy
from ecell4 import *

NUM_STEPS = 10000
RUN_LIMIT = 500.0 # sec

radius = 5e-9

with species_attributes():
    A | { 'radius':  str(radius), 'D': '1.0e-12' }

model = get_model()

def print_usage(methods, factories):
    print("USAGE: python profile.py [" + "|".join(methods) + "] [" + "|".join(factories) + "] <int>")

# per simulation time
def measure_run_time(simulator, steps):
    elapsed = 0
    start = time.time()
    for i in range(steps):
        simulator.step()
        elapsed = time.time() - start
        if (elapsed >= RUN_LIMIT):
            elapsed *= float(steps) / (i+1)
            break

    return elapsed / simulator.t()

def num_partitions(L, N):
    return int(min(L/(2*radius), max(3, cbrt(N))))

def create_factory(constructor, L, num, partition, *args):
    if partition:
        m = num_partitions(L, num)
        return constructor(Integer3(m, m, m), rng)
    return constructor(*args)

def create_world(factory, L, num):
    world = factory.create_world(Real3(L, L, L))
    world.bind_to(model)
    world.add_molecules(Species('A'), num)
    return world

def profile_fixed_volume(ns, constructor, partition, scaled_step, *args):
    edge_length = 3.42e-6 # V = 40fL
    elapsed_time = []
    for num in ns:
        factory = create_factory(constructor, edge_length, num, partition, *args)
        world = create_world(factory, edge_length, num)
        s = factory.create_simulator(model, world)
        num_steps = num * NUM_STEPS if scaled_step else NUM_STEPS
        try:
            elapsed = measure_run_time(s, num_steps)
        except:
            elapsed_time.append(0.0)
            break
        elapsed_time.append(elapsed)
    return elapsed_time

def profile_fixed_concentration(ns, constructor, partition, scaled_step, *args):
    elapsed_time = []
    for num in ns:
        volume = num/60.0*1.0e-18
        edge_length = cbrt(volume)
        factory = create_factory(constructor, edge_length, num, partition, *args)
        world = create_world(factory, edge_length, num)
        s = factory.create_simulator(model, world)
        num_steps = num * NUM_STEPS if scaled_step else NUM_STEPS
        try:
            elapsed = measure_run_time(s, num_steps)
        except:
            elapsed_time.append(0.0)
            break
        elapsed_time.append(elapsed)
    return elapsed_time

if __name__ == '__main__':
    rng = GSLRandomNumberGenerator()
    factories = {
        "spatiocyte" : [spatiocyte.SpatiocyteFactory, False, False, radius, rng],
        "egfrd"      : [egfrd.EGFRDFactory, True, True, rng],
        "egfrd.bd"   : [egfrd.BDFactory, True, True, rng],
        "bd.bd"      : [bd.BDFactory, True, True, rng],
        "meso"       : [meso.MesoscopicFactory, False, True, 100e-9, rng]
    }
    profile_methods = {
        "vol"  : profile_fixed_volume,
        "conc" : profile_fixed_concentration
    }

    import sys
    argc = len(sys.argv)
    if argc < 3:
        print_usage(profile_methods.keys(), factories.keys())
        sys.exit(1)

    method = sys.argv[1]
    system = sys.argv[2]

    if argc >= 4:
        seed = int(sys.argv[3])
    else:
        seed = 0
    rng.seed(seed)

    if method not in profile_methods:
        print("Invalid method")
        print_usage(profile_methods.keys(), factories.keys())
        sys.exit(2)

    if system not in factories:
        print("Invalid system")
        print_usage(profile_methods.keys(), factories.keys())
        sys.exit(3)

    ns = numpy.power(10, numpy.arange(1.5, 5.0, 0.5)).astype(int)
    elapsed_time = profile_methods[method](ns, *(factories[system]))
    with open("tsv/%s_fixed_%s_%d.tsv" % (system, method, seed), 'w') as f:
        for (num, time) in zip(ns, elapsed_time):
            print >> f,  num, time
