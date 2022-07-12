"""Example - Calculate field map using multiprocessing

A 3D field map is calculated in coordinates defined by the arrays x, y and z
for a built-in undulator model. 

Multiprocesing parameters are:
    nproc: number of processes used. Generally, the more processes, the better
        up to the available threads in the computer's cpu. However, performance
        gain is not linear with nproc in general.
        By using nproc==None, the package switches to a serial calculation.
    chunksize: each one of the parallel calculations submitted by the python
        implementation will contain a number of individual field evaluations
        given by this number.
        A number >1 will often be more efficient than submitting each field
        evaluation individually, specially for large evaluation arrays.
        This argument is optional in the imaids methods and chunksize=100 is
        the default value, which is usually fine. For parallel calculations
        with few points, this value might be decreased.

Note that python multiprocessing only works in a __main__ module, inside a
clause "if __name__ == '__main__':", so it cannot be used interactively.
"""

import numpy as np
from imaids import models
import time

z = np.linspace(-700,700,1401)
x = np.linspace(-5,5,11)
y = np.linspace(-1,1,3)
nproc = 8
chunksize = 100

und = models.DeltaSabia()
und.set_cassete_positions(dgv=und.period_length/2)

if __name__ == '__main__':

    t1 = time.perf_counter()

    und.save_fieldmap('map.dat', x, y, z, nproc=nproc, chunksize=chunksize)

    t2 = time.perf_counter()

    print(f'Time (nproc={nproc}): {round(t2-t1,3)} sec')
