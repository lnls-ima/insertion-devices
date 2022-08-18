'''
ITERATIVE SOLVE IN HYBRID PLANNAR UNDULATOR

This example shows how the radia.RlxPre and radia.RlxAuto functions may
be used instead of radia.Solve for relaxing a large system in sections
for minimizing memory usage.

The undulator blocks are separated in sections. In every iteration, all
section is relaxed independently and successively until the convergence
is achieved.

Convergence is tested by calculating the average magnetization modulus of all 
the blocks before and after the iteration. If such value is smaller than
a set threshold, convergence is achieved.

Since at the beginning of the problem the magnetizations are farther from
their final values, convergence is usually sped up by performing the first
relaxations with a "coarser" larger threshold, which is increased at each
iteration up to the target convergence threshold.
'''

import time
from copy import deepcopy
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

import radia as rad
import imaids


# -------------- C A L C U L A T I O N   P A R A M E T E R S -------------- #


# Specifying undulator model.
und = imaids.models.HybridPlanar(nr_periods=10,
                                     period_length=20,
                                     gap=5,
                                     mr=1.37)

# For later field calculations.
z = np.linspace(-1200, 1200, 4801)


# ---------------- R E L A X A T I O N   P A R A M E T E R S ---------------- #


# Number of sections in which the list of blocks is divided.
n_sections = 3
# Maximum number of iterations and target convergence threshold.
# Calculation stops if target_thr OR max_iterations is achieved.
max_iterations = 20
target_thr = 1E-5

# Start value for convergence threshold used at the sections relaxations in 
# each step. This value is reduced at each iteration up to target_thr.
# Must be > target_thr.
iteration_thr = 1E-2
# Number of initial iterations in which the threshold will be decreased.
nr_init_thr = 3

# If True, 3d model will be displayed at each section relaxation.
draw_steps = True


# --------------------------- R E L A X A T I O N --------------------------- #


# Get list of all blocks in the undulator.
cassette_ints = []
block_ints = []
for cassette_obj in rad.ObjCntStuf(und.radia_object):
    cassette_ints.append(cassette_obj)
    for block_obj in rad.ObjCntStuf(cassette_obj):
        block_ints.append(block_obj)
# Turn lists into numpy arrays.
cassette_ints = np.array(cassette_ints)
block_ints = np.array(block_ints)

# Divide list of block integer references in chunks and show info.
sections = [a.tolist() for a in np.array_split(block_ints, n_sections)]
print('Device name: {0}'.format(und.name))
print('{:d} sections'.format(len(sections)))
print('Number of blocks in each section:')
print([len(x) for x in sections])
print('')

# Switch for testing if convergence was achieved.
converged = False

# Factor by which iteration_thr iteration threshold will be multiplied in the
# first nr_init_thr steps.
iteration_thr_step = (target_thr/iteration_thr)**(1/nr_init_thr)

t0 = time.time()
for iteration in range(max_iterations):

    print('Iteration {:d}'.format(iteration+1))    
    print(datetime.now())
    print('sections relaxation threshold: {:.2e}'.format(iteration_thr))    

    # Get average magnetization before:
    abs_mags_before = []
    for block in block_ints:
        mags = np.array(rad.ObjM(block))[:,1]
        mag = np.mean(mags, axis=0)
        abs_mag = np.linalg.norm(mag)
        abs_mags_before.append(abs_mag)
    avg_mags_before = np.mean(abs_mags_before)
        
    # List for monitoring convergence in the current iteration step
    results = []

    for section in range(len(sections)):

        print('\tsection {:d} of {:d}'.format(section+1, len(sections)))

        # obj contains the blocks in a given section.
        # srcobj contains the remaining blocks.
        # First, setting up the list if integer references:
        srcobj_objs = deepcopy(sections)
        obj_objs = srcobj_objs.pop(section)
        srcobj_objs = imaids.utils.flatten(srcobj_objs)
        # Than, creating the objects.
        srcobj = rad.ObjCnt(srcobj_objs)
        obj = rad.ObjCnt(obj_objs)

        # Show model and highlight current active objects:
        if draw_steps:
            rad.ObjDrwAtr(obj, [0, 0.5, 1], 0.0001)
            rad.ObjDrwAtr(srcobj, [0.9, 0.9, 0.9], 0.0001)
            rad.ObjDrwOpenGL(rad.ObjCnt([obj, srcobj]))       

        # Perform relaxation of object in relation to fixed srcobj.
        print('\t\tsetting up interaction matrix...')
        t1 = time.time()
        inter_mat = rad.RlxPre(obj, srcobj)
        print('\t\tmatrix done ({:.4f} s)'.format(time.time()-t1))
        print('\t\tperforming section relaxation...')
        t2 = time.time()
        result = rad.RlxAuto(inter_mat, iteration_thr, 1000)        
        results.append(result)
        print('\t\trelaxation done ({:.4f} s)'.format(time.time()-t2))

        # Some clean-up
        rad.UtiDel(obj)
        rad.UtiDel(srcobj)
        rad.UtiDel(inter_mat)

    # Get average magnetization after:
    abs_mags_after = []
    for block in block_ints:
        mags = np.array(rad.ObjM(block))[:,1]
        mag = np.mean(mags, axis=0)
        abs_mag = np.linalg.norm(mag)
        abs_mags_after.append(abs_mag)
    avg_mags_after = np.mean(abs_mags_after)

    # How did the average magnetization change in this iteration?
    avg_mags_delta = abs(avg_mags_after - avg_mags_before)

    # Print magnetization variation overview.
    print('\t{:20s}{:.12f}'.format('<|m|> before: ', avg_mags_before))
    print('\t{:20s}{:.12f}'.format('<|m|> after: ', avg_mags_after))
    print('\t{:20s}{:.12f}'.format('<|m|> variation: ', avg_mags_delta))
    print('\t{:20s}{:.12f}'.format('target threshold: ', target_thr))

    # If there are still steps in which the iteration_thr should be altered,
    # alter it and reduce such number os steps.
    if nr_init_thr > 0:
        iteration_thr *= iteration_thr_step
        nr_init_thr -= 1

    # Check if convergence threshold was achieved
    if avg_mags_delta < target_thr:
        converged = True 
        break

# Final prints.
print('-'*50)
print('Relaxation finished ({:.4f} s)'.format(time.time()-t0))
print('Iterations {:d}'.format(iteration+1))
if converged:
    print('Relaxation CONVERGED with respect to threshold')
else:
    print('Relaxation DID NOT converge with respect to threshold')
print('Proceeding to next calculations...')


# ------------------- F I E L D   C A L C U L A T I O N S ------------------- #


field = und.get_field(x=0, y=0, z=z)
plt.plot(field)
plt.show()
