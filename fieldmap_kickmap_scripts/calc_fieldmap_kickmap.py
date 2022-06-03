
import os
import time
import numpy as np
import imaids


def run_calc_fieldmap_kickmap(
        phase_shift, gap_opening, fieldmap_name, kickmap_name):
    t0 = time.time()

    xmin = -5.0
    xmax = 5.0
    xstep = 0.5

    ymin = -3.0
    ymax = 3.0
    ystep = 0.5

    zmin = -800
    zmax = 800
    zstep = 1.0

    energy = 3.0
    rkstep = 1.0

    directory = os.path.dirname(os.path.abspath(__file__))
    fieldmap_path = os.path.join(directory, fieldmap_name)
    kickmap_path = os.path.join(directory, kickmap_name)

    imaids.utils.set_len_tol()

    device = imaids.models.AppleIISabia()
    device.set_cassete_positions(dp=phase_shift, dg=gap_opening)
    device.solve()

    t1 = time.time()
    print('solve time [s]: ', t1-t0)

    x_list = np.linspace(xmin, xmax, int((xmax - xmin)/xstep) + 1)
    y_list = np.linspace(ymin, ymax, int((ymax - ymin)/ystep) + 1)
    z_list = np.linspace(zmin, zmax, int((zmax - zmin)/zstep) + 1)

    device.save_fieldmap(
        fieldmap_path, x_list, y_list, z_list, header=None)

    t2 = time.time()
    print('fieldmap time [s]: ', t2-t1)

    device.save_kickmap(
        kickmap_path, energy, x_list, y_list, zmin, zmax, rkstep)

    t3 = time.time()
    print('kickmap time [s]: ', t3-t2)


phase_shift = 0  # Phase shift in mm. Zero for horizontal polarization.
gap_opening = 0  # Gap opening in mm. Zero for the minimum gap.

fieldmap_name = 'apple2_sabia_example.fld'
kickmap_name = 'apple2_sabia_example.kck'

run_calc_fieldmap_kickmap(
    phase_shift, gap_opening, fieldmap_name, kickmap_name)