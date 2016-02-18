#! /usr/bin/env python

import time
import math
import numpy
from ecell4 import *

DURATION = 1.0 # sec
NUM_STEPS = 10000
RUN_LIMIT = 10.0 # sec

def measure_run_time(simulator, steps):
    elapsed = 0
    start = time.time()
    for i in range(steps):
        simulator.step()
        elapsed = time.time() - start
        if (elapsed >= RUN_LIMIT):
            elapsed *= float(steps) / (i+1)
            break

    return elapsed

ns = numpy.power(10, numpy.arrange(1.5, 5.0, 0.5)).astype(int)

with species_attributes():
    A | { 'radius': '1e-8', 'D': '1.0e-12' }

m = get_model()

def profile_fixed_volume(factories):
    world_size = Real3(3.42e-6, 3.42e-6, 3.42e-6) # V = 40fL
    fixed_volume_elapsed = {}
    for solver, (f, is_scale) in factories.items():
        fixed_volume_elapsed[solver] = []
        for num in ns:
            world = f.create_world(world_size)
            world.bind_to(m)
            world.add_molecules(Species('A'), num)
            s = factory.create_simulator(model, world)
            num_steps = num*NUM_STEPS if is_scale else NUM_STEPS
            elapsed = measure_run_time(s, num_steps)
            fixed_volume_elapsed[solver].append(elapsed)

def profile_fixed_concentration(factories):
    fixed_concentration_elapsed = {}
    for solver, (f, is_scale) in factories.items():
        fixed_concentration_elapsed[solver] = []
        for num in ns:
            edge = math.pow(num/60.0, 1./3.)*1.0e-6
            world = f.create_world(Real3(edge, edge, edge))
            world.bind_to(m)
            world.add_molecules(Species('A'), num)
            s = factory.create_simulator(model, world)
            num_steps = num*NUM_STEPS if is_scale else NUM_STEPS
            elapsed = measure_run_time(s, num_steps)
            fixed_concentration_elapsed[solver].append(elapsed)

if __name__ == '__main__':
    factories = {
        "spatiocyte" : (spatiocyte.SpatiocyteFactory(voxel_radius=1.0e-8), False),
        "egfrd"      : (egfrd.EGFRDFactory(matrix_sizes=Integer3(3,3,3)), True),
        "bd"         : (bd.BDFactory(), True)
    }
    profile_fixed_volume(factories)
    profile_fixed_concentration(factories[:1])
