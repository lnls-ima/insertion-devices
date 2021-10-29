
import os
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from imaids import models
from imaids import utils


plt.rcParams['figure.figsize'] = [18, 9]
plt.rcParams['font.size'] = 16
plt.rcParams['legend.fontsize'] = 14
plt.rcParams['lines.markersize'] = 10


def create_and_save_model(
        filename, nr_periods, mag_amp=0, mag_ang=0,
        herr=0, verr=0, lerr=0,
        term_err=True, core_err=True):
    model = models.DeltaSabia(nr_periods=nr_periods)

    mag_dict = {}
    perr_dict = {}
    for name, cassette in model.cassettes.items():
        mag = cassette.get_random_errors_magnetization_list(
            max_amplitude_error=mag_amp,
            max_angular_error=mag_ang,
            termination_errors=term_err,
            core_errors=core_err)
        perr = cassette.get_random_errors_position(
            max_horizontal_error=herr,
            max_vertical_error=verr,
            max_longitudinal_error=lerr,
            termination_errors=term_err,
            core_errors=core_err)
        mag_dict[name] = mag
        perr_dict[name] = perr

    model.create_radia_object(
        magnetization_dict=mag_dict,
        position_err_dict=perr_dict)
    model.save_state(filename)

    return model


def load_model(filename):
    model = models.DeltaSabia.load_state(filename)
    model.dgv = model.period_length/2
    return model


def get_segments_fit(
        model, zmin, zmax, zpos_segs,
        energy=3, rkstep=0.5, x=0, y=0):
    traj = model.calc_trajectory(
        energy, [x, y, zmin, 0, 0, 1], zmax, rkstep)
    avgtraj = model.calc_trajectory_avg_over_period(traj)

    seg_start, seg_end, poly_x, poly_y = model.fit_trajectory_segments(
        avgtraj, zpos_segs, model.period_length)

    return traj, avgtraj, seg_start, seg_end, poly_x, poly_y


def get_zpos_segs(model, zmin, zmax, znpts):
    z = np.linspace(zmin, zmax, znpts)
    b = model.get_field(z=z)
    pvs = utils.find_peaks_and_valleys(b[:, 1], prominence=0.05)
    block_pos = z[pvs] - model.period_length/4
    zpos_segs = list(block_pos[::2])
    zpos_segs.append(zpos_segs[-1] + model.period_length)
    zpos_segs.append(zpos_segs[0] - model.period_length)
    zpos_segs = sorted(zpos_segs)
    return zpos_segs


def get_ba_blocks(model, cassette):
    cassette = model.cassettes[cassette]
    mag = np.array(cassette.magnetization_list)
    tol = 0.2
    filt = mag[:, 1] > (model.mr - tol)
    bas = np.array(cassette.blocks)[filt]
    return bas


def calc_response_matrix(
        filename_model, filename_matrix,
        zmin, zmax, znpts, cassettes,
        energy=3, rkstep=0.5, shim=0.5, x=0, y=0):
    utils.set_len_tol()

    model = load_model(filename_model)
    model.solve()
    zpos_segs = get_zpos_segs(model, zmin, zmax, znpts)
    _, _, _, _, poly_x0, poly_y0 = get_segments_fit(
        model, zmin, zmax, zpos_segs,
        energy=energy, rkstep=rkstep, x=x, y=y)
    cassette = list(model.cassettes.keys())[0]
    nr_bas = len(get_ba_blocks(model, cassette))

    ext = '.' + filename_matrix.split('.')[-1]
    filename_mx = filename_matrix.replace(ext, '_mx' + ext)
    filename_my = filename_matrix.replace(ext, '_my' + ext)
    open(filename_mx, 'w').close()
    open(filename_my, 'w').close()

    mx = []
    my = []
    for cassette in cassettes:
        for idx in range(nr_bas):
            model = load_model(filename_model)
            model.solve()
            bas = get_ba_blocks(model, cassette)
            bas[idx].shift([0, shim, 0])

            _, _, _, _, poly_x, poly_y = get_segments_fit(
                model, zmin, zmax, zpos_segs,
                energy=energy, rkstep=rkstep, x=x, y=y)

            dpx = (poly_x[:, 1] - poly_x0[:, 1])/shim
            dpy = (poly_y[:, 1] - poly_y0[:, 1])/shim

            with open(filename_mx, 'a+') as fx:
                strx = '\t'.join('{0:g}'.format(v) for v in dpx)
                fx.write(strx + '\n')

            with open(filename_my, 'a+') as fy:
                stry = '\t'.join('{0:g}'.format(v) for v in dpy)
                fy.write(stry + '\n')

            mx.append(dpx)
            my.append(dpy)

            print(cassette, ' idx: ', idx)

    mx = np.array(mx)
    my = np.array(my)
    m = np.transpose(np.concatenate([mx, my], axis=1))
    np.savetxt(filename_matrix, m)


def plot_segs(
        traj, avgtraj, seg_start, seg_end, poly_x, poly_y):
    spec = gridspec.GridSpec(
        ncols=2, nrows=1,
        wspace=0.25, hspace=0.25,
        left=0.07, right=0.85, top=0.95, bottom=0.1)
    fig = plt.figure()
    ax0 = fig.add_subplot(spec[0, 0])
    ax1 = fig.add_subplot(spec[0, 1])

    colorx = 'tab:blue'
    ax0.plot(traj[:, 2], traj[:, 0]*1000, label='x', color=colorx)
    ax0.plot(
        avgtraj[:, 2], avgtraj[:, 0]*1000, '--', label='avg x',
        color=colorx, linewidth=3)

    colory = 'tab:red'
    ax1.plot(traj[:, 2], traj[:, 1]*1000, label='y', color=colory)
    ax1.plot(
        avgtraj[:, 2], avgtraj[:, 1]*1000, '--', label='avg y',
        color=colory, linewidth=3)

    nsegs = len(seg_start)

    for i in range(nsegs):
        tz = [seg_start[i, 2], seg_end[i, 2]]
        tx = np.polynomial.polynomial.polyval(tz, poly_x[i])
        ty = np.polynomial.polynomial.polyval(tz, poly_y[i])
        ax0.plot(tz, tx*1000)
        ax1.plot(tz, ty*1000)

    ax0.set_ylabel(r'TrajX [$\mu$m]')
    ax0.grid(True)

    ax1.set_ylabel(r'TrajY [$\mu$m]')
    ax1.grid(True)


def plot_two_trajectories(
        traj1, avgtraj1, traj2, avgtraj2):
    spec = gridspec.GridSpec(
        ncols=2, nrows=3,
        wspace=0.25, hspace=0.25,
        left=0.07, right=0.85, top=0.95, bottom=0.1)
    fig = plt.figure()
    ax0 = fig.add_subplot(spec[0, 0])
    ax1 = fig.add_subplot(spec[0, 1])
    ax2 = fig.add_subplot(spec[1, 0])
    ax3 = fig.add_subplot(spec[1, 1])
    ax4 = fig.add_subplot(spec[2, 0])
    ax5 = fig.add_subplot(spec[2, 1])

    colorx1 = 'lightblue'
    colory1 = 'pink'

    colorx2 = 'tab:blue'
    colory2 = 'tab:red'

    ax0.plot(
        traj1[:, 2], traj1[:, 0]*1000, label='x', color=colorx1)
    ax0.plot(
        avgtraj1[:, 2], avgtraj1[:, 0]*1000,
        '--', label='avg x', color=colorx1, linewidth=3)

    ax1.plot(
        traj1[:, 2], traj1[:, 1]*1000, label='y', color=colory1)
    ax1.plot(
        avgtraj1[:, 2], avgtraj1[:, 1]*1000,
        '--', label='avg y', color=colory1, linewidth=3)

    ax2.plot(
        traj2[:, 2], traj2[:, 0]*1000, label='x', color=colorx2)
    ax2.plot(
        avgtraj2[:, 2], avgtraj2[:, 0]*1000,
        '--', label='avg x', color=colorx2, linewidth=3)

    ax3.plot(
        traj2[:, 2], traj2[:, 1]*1000, label='y', color=colory2)
    ax3.plot(
        avgtraj2[:, 2], avgtraj2[:, 1]*1000,
        '--', label='avg y', color=colory2, linewidth=3)

    trajx2_func = interpolate.interp1d(
        traj2[:, 2], traj2[:, 0], bounds_error=False, fill_value=0)
    trajy2_func = interpolate.interp1d(
        traj2[:, 2], traj2[:, 1], bounds_error=False, fill_value=0)
    avgtrajx2_func = interpolate.interp1d(
        avgtraj2[:, 2], avgtraj2[:, 0], bounds_error=False, fill_value=0)
    avgtrajy2_func = interpolate.interp1d(
        avgtraj2[:, 2], avgtraj2[:, 1], bounds_error=False, fill_value=0)

    cut = 10
    z = traj1[cut:-cut, 2]
    trajx2_interp = trajx2_func(z)
    trajy2_interp = trajy2_func(z)

    zavg = avgtraj1[cut:-cut, 2]
    avgtrajx2_interp = avgtrajx2_func(zavg)
    avgtrajy2_interp = avgtrajy2_func(zavg)

    diffx = trajx2_interp - traj1[cut:-cut, 0]
    diffy = trajy2_interp - traj1[cut:-cut, 1]
    diffavgx = avgtrajx2_interp - avgtraj1[cut:-cut, 0]
    diffavgy = avgtrajy2_interp - avgtraj1[cut:-cut, 1]

    ax4.plot(z, diffx*1000, label='x', color=colorx2)
    ax4.plot(
        zavg, diffavgx*1000, '--', label='avg x',
        color=colorx2, linewidth=3)

    ax5.plot(z, diffy*1000, label='y', color=colory2)
    ax5.plot(
        zavg, diffavgy*1000, '--', label='avg y',
        color=colory2, linewidth=3)

    ax0.set_ylabel(r'TrajX1 [$\mu$m]')
    ax0.grid(True)

    ax1.set_ylabel(r'TrajY1 [$\mu$m]')
    ax1.grid(True)

    ax2.set_ylabel(r'TrajX2 [$\mu$m]')
    ax2.grid(True)

    ax3.set_ylabel(r'TrajY2 [$\mu$m]')
    ax3.grid(True)

    ax4.set_ylabel(r'X2 - X1 [$\mu$m]')
    ax4.set_xlabel('z [mm]')
    ax4.grid(True)

    ax5.set_ylabel(r'Y2 - Y1 [$\mu$m]')
    ax5.set_xlabel('z [mm]')
    ax5.legend(bbox_to_anchor=[1, 1], loc='upper left')
    ax5.grid(True)


nr_periods = 3
energy = 3
rkstep = 0.5
shim = 0.5
x = 0
y = 0
zmin = -300
zmax = 300
znpts = 601

mag_amp = 1/100  # [%]
mag_ang = 1*np.pi/180  # [rad]
herr = 0.05  # [mm]
verr = 0.05  # [mm]
lerr = 0.05  # [mm]
term_err = True
core_err = True

calc_matrix = False
cassettes = ['csd', 'cse']

filename = 'model_with_errors_2.txt'
filename_ideal = 'model_ideal.txt'
filename_matrix = 'response_matrix.txt'

directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(directory, filename)
filename_ideal = os.path.join(directory, filename_ideal)
filename_matrix = os.path.join(directory, filename_matrix)

utils.set_len_tol()

if calc_matrix:
    calc_response_matrix(
        filename_ideal, filename_matrix,
        zmin, zmax, znpts, cassettes,
        energy=energy, rkstep=rkstep,
        shim=shim, x=x, y=y)
else:
    m = np.loadtxt(filename_matrix)
    minv = np.linalg.pinv(m)

if not os.path.isfile(filename_ideal):
    model = create_and_save_model(filename_ideal, nr_periods)
else:
    model = load_model(filename_ideal)

z = np.linspace(zmin, zmax, znpts)
zpos_segs = get_zpos_segs(model, zmin, zmax, znpts)
cassette = list(model.cassettes.keys())[0]
nr_bas = len(get_ba_blocks(model, cassette))

model.solve()
traj0, avgtraj0, seg_start0, seg_end0, poly_x0, poly_y0 = get_segments_fit(
    model, zmin, zmax, zpos_segs,
    energy=energy, rkstep=rkstep, x=x, y=y)
ib0, iib0 = model.calc_field_integrals(z_list=z, x=x, y=y)

if not os.path.isfile(filename):
    model = create_and_save_model(
        filename, nr_periods, mag_amp=mag_amp,
        mag_ang=mag_ang, herr=herr, verr=verr, lerr=lerr,
        term_err=term_err, core_err=core_err)
else:
    model = load_model(filename)

model.solve()
traj1, avgtraj1, seg_start1, seg_end1, poly_x1, poly_y1 = get_segments_fit(
    model, zmin, zmax, zpos_segs,
    energy=energy, rkstep=rkstep, x=x, y=y)
ib1, iib1 = model.calc_field_integrals(z_list=z, x=x, y=y)

slope_error_x = poly_x0[:, 1] - poly_x1[:, 1]
slope_error_y = poly_y0[:, 1] - poly_y1[:, 1]
slope_error = np.concatenate([slope_error_x, slope_error_y])

shims = minv @ slope_error
print('Shims [mm]: ', shims)

model = load_model(filename)
count = 0
for cassette in cassettes:
    for idx in range(nr_bas):
        bas = get_ba_blocks(model, cassette)
        bas[idx].shift([0, shims[count], 0])
        count += 1
model.solve()
traj2, avgtraj2, seg_start2, seg_end2, poly_x2, poly_y2 = get_segments_fit(
    model, zmin, zmax, zpos_segs,
    energy=energy, rkstep=rkstep, x=x, y=y)
ib2, iib2 = model.calc_field_integrals(z_list=z, x=x, y=y)

str1 = '\t'.join(['{0:.2f}'.format(v) for v in ib1[-1]])
str2 = '\t'.join(['{0:.2f}'.format(v) for v in ib2[-1]])
print('IB before [G.cm]: ' + str1)
print('IB after [G.cm]: ' + str2)

plot_two_trajectories(traj1, avgtraj1, traj2, avgtraj2)

plt.show()
