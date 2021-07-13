
import time as _time
import numpy as _np
from scipy import integrate as _integrate
from scipy import optimize as _optimize
from scipy import signal as _signal
import radia as _rad

from . import utils as _utils


def find_peaks_and_valleys(data, prominence=0.05):
    peaks, _ = _signal.find_peaks(data, prominence=prominence)
    valleys, _ = _signal.find_peaks(data*(-1), prominence=prominence)
    return sorted(_np.append(peaks, valleys))


def find_zeros(pos, data):
    s = _np.sign(data)
    idxb = (s[0:-1] + s[1:] == 0).nonzero()[0]
    idxa = idxb + 1
    posb = pos[idxb]
    posa = pos[idxa]
    datab = data[idxb]
    dataa = data[idxa]
    pos = (dataa*posb - datab*posa)/(dataa - datab)
    return pos[:-1]


def cosine_function(z, bamp, freq, phase):
    return bamp*_np.cos(freq*z + phase)


def calc_beam_parameters(energy):
    electron_rest_energy, light_speed = _utils.get_constants()
    gamma = energy*1e9/electron_rest_energy
    beta = _np.sqrt(1 - 1/((energy*1e9/electron_rest_energy)**2))
    brho = energy*1e9/light_speed
    return beta, gamma, brho


def calc_field_integrals(
        radia_object, z_list, x=0, y=0, field_list=None):
    if radia_object is None:
        return None, None

    if field_list is not None:
        if len(field_list) != len(z_list):
            raise ValueError(
                'Inconsistent length between field and position lists.')
    else:
        field_list = get_field(radia_object, x=x, y=y, z=z_list)

    bx, by, bz = _np.transpose(field_list)

    z_list_m = _np.array(z_list)/1000
    ibx = _integrate.cumtrapz(bx, z_list_m, initial=0)
    iby = _integrate.cumtrapz(by, z_list_m, initial=0)
    ibz = _integrate.cumtrapz(bz, z_list_m, initial=0)
    iibx = _integrate.cumtrapz(ibx, z_list_m, initial=0)
    iiby = _integrate.cumtrapz(iby, z_list_m, initial=0)
    iibz = _integrate.cumtrapz(ibz, z_list_m, initial=0)

    ib = _np.transpose([ibx, iby, ibz])*1e6
    iib = _np.transpose([iibx, iiby, iibz])*1e5

    return ib, iib


def calc_field_amplitude(
        radia_object, period_length,
        nr_periods, x=0, y=0, z_list=None,
        field_list=None, npts_per_period=101):
    if radia_object is None:
        return None, None, None, None

    if nr_periods > 1:
        zmin = -period_length*(nr_periods - 1)/2
        zmax = period_length*(nr_periods - 1)/2
        znpts = npts_per_period*(nr_periods-1)
    else:
        zmin = -period_length/2
        zmax = period_length/2
        znpts = npts_per_period

    if z_list is not None and field_list is not None:
        if len(field_list) != len(z_list):
            raise ValueError(
                'Inconsistent length between field and position lists.')

        z_list = _np.array(z_list)
        field_list = _np.array(field_list)

        cond = (z_list >= zmin) & (z_list <= zmax)
        z_list = z_list[cond]
        field_list = field_list[cond]

    else:
        z_list = _np.linspace(zmin, zmax, znpts)
        field_list = get_field(radia_object, x=x, y=y, z=z_list)

    bx, by, bz = _np.transpose(field_list)
    bx_amp_init = _np.max(_np.abs(bx))
    by_amp_init = _np.max(_np.abs(by))
    bz_amp_init = _np.max(_np.abs(bz))

    px = _optimize.curve_fit(
        cosine_function, z_list, bx,
        p0=[bx_amp_init, 2*_np.pi/period_length, 0])[0]
    bx_amp = _np.abs(px[0])
    bx_phase = px[2]

    py = _optimize.curve_fit(
        cosine_function, z_list, by,
        p0=[by_amp_init, 2*_np.pi/period_length, 0])[0]
    by_amp = _np.abs(py[0])
    by_phase = py[2]

    pz = _optimize.curve_fit(
        cosine_function, z_list, bz,
        p0=[bz_amp_init, 2*_np.pi/period_length, 0])[0]
    bz_amp = _np.abs(pz[0])

    bxy_phase = (bx_phase - by_phase) % _np.pi

    return bx_amp, by_amp, bz_amp, bxy_phase


def calc_trajectory(
        radia_object, energy, r0, zmax, rkstep, dz=0, on_axis_field=False):
    if radia_object is None:
        return None

    r1 = _np.zeros(6, dtype=float)
    r2 = _np.zeros(6, dtype=float)
    r3 = _np.zeros(6, dtype=float)

    beta, _, brho = calc_beam_parameters(energy)
    a = 1/brho/beta

    # from mm to m
    r = _np.array(r0, dtype=float)
    r[0] = r[0]/1000
    r[1] = r[1]/1000
    r[2] = (r[2] + dz)/1000
    step = rkstep/1000

    trajectory = []
    trajectory.append([
        r[0]*1000, r[1]*1000, r[2]*1000, r[3], r[4], r[5]
    ])

    while r[2] < zmax/1000:
        pos = [p*1000 for p in r[:3]]
        if on_axis_field:
            pos[0], pos[1] = 0, 0
        b = _rad.Fld(radia_object, "b", pos)
        drds1 = newton_lorentz_equation(a, r, b)
        r1 = r + (step/2)*drds1

        pos1 = [p*1000 for p in r1[:3]]
        if on_axis_field:
            pos1[0], pos1[1] = 0, 0
        b1 = _rad.Fld(radia_object, "b", pos1)
        drds2 = newton_lorentz_equation(a, r1, b1)
        r2 = r + (step/2)*drds2

        pos2 = [p*1000 for p in r2[:3]]
        if on_axis_field:
            pos2[0], pos2[1] = 0, 0
        b2 = _rad.Fld(radia_object, "b", pos2)
        drds3 = newton_lorentz_equation(a, r2, b2)
        r3 = r + step*drds3

        pos3 = [p*1000 for p in r3[:3]]
        if on_axis_field:
            pos3[0], pos3[1] = 0, 0
        b3 = _rad.Fld(radia_object, "b", pos3)
        drds4 = newton_lorentz_equation(a, r3, b3)

        r = r + (step/6)*(drds1 + 2*drds2 + 2*drds3 + drds4)

        trajectory.append([
            r[0]*1000, r[1]*1000, r[2]*1000, r[3], r[4], r[5]
        ])

    trajectory = _np.array(trajectory)

    return trajectory


def calc_deflection_parameter(bx_amp, by_amp, period_length):
    kh = 0.934*by_amp*(period_length/10)
    kv = 0.934*bx_amp*(period_length/10)
    return kh, kv


def calc_trajectory_length(trajectory):
    traj_pos = trajectory[:, 0:3]
    traj_diff = _np.diff(traj_pos, axis=0)
    traj_len = _np.append(
        0, _np.cumsum(_np.sqrt(_np.sum(traj_diff**2, axis=1))))
    return traj_len


def calc_radiation_phase(
        energy, trajectory, wavelength):
    beta, *_ = calc_beam_parameters(energy)
    traj_z = trajectory[:, 2]
    traj_len = calc_trajectory_length(trajectory)
    return (2*_np.pi/(wavelength))*(traj_len/beta - (traj_z - traj_z[0]))


def calc_radiation_wavelength(
        energy, bx_amp, by_amp, period_length, harmonic=1):
    _, gamma, _ = calc_beam_parameters(energy)
    kh, kv = calc_deflection_parameter(bx_amp, by_amp, period_length)
    wl = (period_length/(2*harmonic*(gamma**2)))*(1 + (kh**2 + kv**2)/2)
    return wl


def calc_phase_error(
        energy, trajectory, wavelength,
        skip_poles=1, zmin=None, zmax=None):
    z_list = find_zeros(trajectory[:, 2], trajectory[:, 3])

    if zmin is not None:
        z_list = z_list[z_list >= zmin]

    if zmax is not None:
        z_list = z_list[z_list <= zmax]

    if skip_poles != 0:
        z_list = z_list[skip_poles:-skip_poles]

    phase = calc_radiation_phase(energy, trajectory, wavelength)
    phase_poles = _np.interp(z_list, trajectory[:, 2], phase)

    coeffs = _np.polynomial.polynomial.polyfit(z_list, phase_poles, 1)
    phase_fit = _np.polynomial.polynomial.polyval(z_list, coeffs)
    phase_error = phase_poles - phase_fit

    phase_error_rms = _np.sqrt(_np.mean(phase_error**2))

    return z_list, phase_error, phase_error_rms


def draw(radia_object):
    if radia_object is None:
        return False

    _rad.ObjDrwAtr(radia_object, [0, 0.5, 1], 0.001)
    _rad.ObjDrwOpenGL(radia_object)
    return True


def get_field(radia_object, x=0, y=0, z=0):
    if isinstance(x, (float, int)):
        x = [x]
    if isinstance(y, (float, int)):
        y = [y]
    if isinstance(z, (float, int)):
        z = [z]

    if sum([len(i) > 1 for i in [x, y, z]]) > 1:
        raise ValueError('Invalid position arguments.')

    if len(x) > 1:
        field = [_rad.Fld(radia_object, 'b', [xi, y, z]) for xi in x]
    elif len(y) > 1:
        field = [_rad.Fld(radia_object, 'b', [x, yi, z]) for yi in y]
    elif len(z) > 1:
        field = [_rad.Fld(radia_object, 'b', [x, y, zi]) for zi in z]
    else:
        field = [_rad.Fld(radia_object, 'b', [x, y, z])]

    return _np.array(field)


def get_file_header_delta(
        date, device_name, polarization_name, kh, kv,
        gap, period_length, magnet_length, field_phase,
        dp=0, dcp=0, dgv=0, dgh=0):
    header = []

    if device_name == '':
        device_name = '--'

    if polarization_name == '':
        polarization_name = '--'

    timestamp = date + _time.strftime('_%H-%M-%S', _time.localtime())

    pos_csd = dgv
    pos_cse = dgv + dgh + dp + dcp
    pos_cie = dgh
    pos_cid = dp - dcp

    k = _np.sqrt(kh**2 + kv**2)

    header.append('timestamp:\t{0:s}\n'.format(timestamp))
    header.append('magnet_name:\t{0:s}\n'.format(device_name))
    header.append('gap[mm]:\t{0:g}\n'.format(gap))
    header.append('period_length[mm]:\t{0:g}\n'.format(period_length))
    header.append('magnet_length[mm]:\t{0:g}\n'.format(magnet_length))
    header.append('dP[mm]:\t{0:g}\n'.format(dp))
    header.append('dCP[mm]:\t{0:g}\n'.format(dcp))
    header.append('dGV[mm]:\t{0:g}\n'.format(dgv))
    header.append('dGH[mm]:\t{0:g}\n'.format(dgh))
    header.append('posCSD[mm]:\t{0:g}\n'.format(pos_csd))
    header.append('posCSE[mm]:\t{0:g}\n'.format(pos_cse))
    header.append('posCID[mm]:\t{0:g}\n'.format(pos_cid))
    header.append('posCIE[mm]:\t{0:g}\n'.format(pos_cie))
    header.append('polarization:\t{0:s}\n'.format(polarization_name))
    header.append('field_phase[deg]:\t{0:.0f}\n'.format(field_phase))
    header.append('K_Horizontal:\t{0:.1f}\n'.format(kh))
    header.append('K_Vertical:\t{0:.1f}\n'.format(kv))
    header.append('K:\t{0:.1f}\n'.format(k))
    header.append('\n')

    return header


def get_file_header_applex(
        date, device_name, polarization_name, kh, kv,
        gap, period_length, magnet_length, field_phase,
        dp=0, dcp=0, dg=0):
    header = []

    if device_name == '':
        device_name = '--'

    if polarization_name == '':
        polarization_name = '--'

    timestamp = date + _time.strftime('_%H-%M-%S', _time.localtime())

    pos_csd = 0
    pos_cse = dp + dcp
    pos_cie = 0
    pos_cid = dp - dcp

    k = _np.sqrt(kh**2 + kv**2)

    header.append('timestamp:\t{0:s}\n'.format(timestamp))
    header.append('magnet_name:\t{0:s}\n'.format(device_name))
    header.append('gap[mm]:\t{0:g}\n'.format(gap))
    header.append('period_length[mm]:\t{0:g}\n'.format(period_length))
    header.append('magnet_length[mm]:\t{0:g}\n'.format(magnet_length))
    header.append('dP[mm]:\t{0:g}\n'.format(dp))
    header.append('dCP[mm]:\t{0:g}\n'.format(dcp))
    header.append('dG[mm]:\t{0:g}\n'.format(dg))
    header.append('posCSD[mm]:\t{0:g}\n'.format(pos_csd))
    header.append('posCSE[mm]:\t{0:g}\n'.format(pos_cse))
    header.append('posCID[mm]:\t{0:g}\n'.format(pos_cid))
    header.append('posCIE[mm]:\t{0:g}\n'.format(pos_cie))
    header.append('polarization:\t{0:s}\n'.format(polarization_name))
    header.append('field_phase[deg]:\t{0:.0f}\n'.format(field_phase))
    header.append('K_Horizontal:\t{0:.1f}\n'.format(kh))
    header.append('K_Vertical:\t{0:.1f}\n'.format(kv))
    header.append('K:\t{0:.1f}\n'.format(k))
    header.append('\n')

    return header


def get_filename(
        date, device_name, polarization_name, xrange, yrange, zrange, kh, kv,
        file_extension='.fld', displacement_name=''):

    filename = '{0:s}'.format(date)

    if device_name != '':
        filename += '_' + device_name

    if polarization_name != '':
        filename += '_' + polarization_name

    filename += '_Kh={0:.1f}_Kv={1:.1f}'.format(kh, kv)

    if displacement_name != '':
        filename += '_' + displacement_name

    if xrange[0] != xrange[1]:
        filename += '_X={0:g}_{1:g}mm'.format(xrange[0], xrange[1])

    if yrange[0] != yrange[1]:
        filename += '_Y={0:g}_{1:g}mm'.format(yrange[0], yrange[1])

    if zrange[0] != zrange[1]:
        filename += '_Z={0:g}_{1:g}mm'.format(zrange[0], zrange[1])

    filename += file_extension

    return filename


def newton_lorentz_equation(a, r, b):
    drds = _np.zeros(6)
    drds[0] = r[3]
    drds[1] = r[4]
    drds[2] = r[5]
    drds[3] = -a*(r[4]*b[2] - r[5]*b[1])
    drds[4] = -a*(r[5]*b[0] - r[3]*b[2])
    drds[5] = -a*(r[3]*b[1] - r[4]*b[0])
    return drds


def save_fieldmap(
        radia_object, filename, xlist, ylist, zlist, header=None):

    t0 = _time.time()

    if header is None:
        header = []

    if isinstance(xlist, (float, int)):
        xlist = [xlist]

    if isinstance(ylist, (float, int)):
        ylist = [ylist]

    if isinstance(zlist, (float, int)):
        zlist = [zlist]

    xlist = _np.round(xlist, decimals=8)
    ylist = _np.round(ylist, decimals=8)
    zlist = _np.round(zlist, decimals=8)

    with open(filename, 'w') as fieldmap:
        for line in header:
            fieldmap.write(line)

        fieldmap.write('X[mm]\tY[mm]\tZ[mm]\tBx[T]\tBy[T]\tBz[T]\n')
        fieldmap.write(
            '----------------------------------------' +
            '----------------------------------------' +
            '----------------------------------------' +
            '----------------------------------------\n')

        line_fmt = '{0:g}\t{1:g}\t{2:g}\t{3:g}\t{4:g}\t{5:g}\n'

        for z in zlist:
            for y in ylist:
                for x in xlist:
                    bx, by, bz = _rad.Fld(radia_object, "b", [x, y, z])
                    line = line_fmt.format(x, y, z, bx, by, bz)
                    fieldmap.write(line)

    t1 = _time.time()
    dt = t1-t0

    return dt


def save_fieldmap_spectra(
        radia_object, filename, xlist, ylist, zlist):

    t0 = _time.time()

    if isinstance(xlist, (float, int)):
        xlist = [xlist]

    if isinstance(ylist, (float, int)):
        ylist = [ylist]

    if isinstance(zlist, (float, int)):
        zlist = [zlist]

    xlist = _np.round(xlist, decimals=8)
    ylist = _np.round(ylist, decimals=8)
    zlist = _np.round(zlist, decimals=8)

    nx = len(xlist)
    ny = len(ylist)
    nz = len(zlist)

    if len(xlist) == 1:
        xstep = 0
    else:
        xstep = xlist[1] - xlist[0]

    if len(ylist) == 1:
        ystep = 0
    else:
        ystep = ylist[1] - ylist[0]

    if len(zlist) == 1:
        zstep = 0
    else:
        zstep = zlist[1] - zlist[0]

    header_data = [xstep, ystep, zstep, nx, ny, nz]
    header = '{0:g} {1:g} {2:g} {3:d} {4:d} {5:d}\n'.format(*header_data)

    with open(filename, 'w') as fieldmap:
        fieldmap.write(header)

        line_fmt = '{0:g}\t{1:g}\t{2:g}\n'

        for x in xlist:
            for y in ylist:
                for z in zlist:
                    bx, by, bz = _rad.Fld(radia_object, "b", [x, y, z])
                    line = line_fmt.format(bx, by, bz)
                    fieldmap.write(line)

    t1 = _time.time()
    dt = t1-t0

    return dt


def save_kickmap(
        radia_object, filename, energy, xrange, yrange, zrange, nx, ny, zstep):
    t0 = _time.time()

    _, light_speed = _utils.get_constants()
    brho = energy*1e9/light_speed

    xmin = xrange[0]
    xmax = xrange[1]

    ymin = yrange[0]
    ymax = yrange[1]

    zmin = zrange[0]
    zmax = zrange[1]

    xstep = (xmax - xmin)/(nx - 1) if xmax != xmin else 0
    ystep = (ymax - ymin)/(ny - 1) if ymax != ymin else 0

    x_list = []
    for i in range(nx):
        x_list.append(xmin + xstep*i)

    y_list = []
    for j in range(ny):
        y_list.append(ymin + ystep*j)

    y_list_rev = y_list[::-1]

    kickx_map = _np.zeros([ny, nx])
    kicky_map = _np.zeros([ny, nx])
    finalx_map = _np.zeros([ny, nx])
    finaly_map = _np.zeros([ny, nx])

    for j in range(ny):
        yi = y_list_rev[j]
        for i in range(nx):
            xi = x_list[i]
            traj = calc_trajectory(
                radia_object, energy, [xi, yi, zmin, 0, 0, 1], zmax, zstep)
            xf = traj[-1, 0]
            yf = traj[-1, 1]
            xl = traj[-1, 3]
            yl = traj[-1, 4]
            zl = traj[-1, 5]
            kickx = (xl/zl)*(brho**2)
            kicky = (yl/zl)*(brho**2)

            kickx_map[j, i] = kickx
            kicky_map[j, i] = kicky
            finalx_map[j, i] = xf/1000
            finaly_map[j, i] = yf/1000

    with open(filename, 'w') as kickmap:
        kickmap.write('# Author:Radia User CNPEM\n#\n')
        kickmap.write(
            '# Total Length of Longitudinal Interval [m]\n{0:g}\n'.format(
                (zmax - zmin)/1000))
        kickmap.write('# Number of Horizontal Points \n{0:d}\n'.format(nx))
        kickmap.write('# Number of Vertical Points \n{0:d}\n'.format(ny))

        posx_str = '\t\t'
        posx_str += '\t'.join('{0:g}'.format(x/1000) for x in x_list)
        posx_str += '\n'

        kickmap.write('# Total Horizontal 2nd Order Kick [T2m2]\nSTART\n')
        kickmap.write(posx_str)
        for j in range(ny):
            line = '{0:g}\t'.format(y_list_rev[j]/1000)
            line += '\t'.join('{0:g}'.format(k) for k in kickx_map[j, :])
            line += '\n'
            kickmap.write(line)

        kickmap.write('# Total Vertical 2nd Order Kick [T2m2]\nSTART\n')
        kickmap.write(posx_str)
        for j in range(ny):
            line = '{0:g}\t'.format(y_list_rev[j]/1000)
            line += '\t'.join('{0:g}'.format(k) for k in kicky_map[j, :])
            line += '\n'
            kickmap.write(line)

        kickmap.write('# Horizontal Final Position [m]\nSTART\n')
        kickmap.write(posx_str)
        for j in range(ny):
            line = '{0:g}\t'.format(y_list_rev[j]/1000)
            line += '\t'.join('{0:g}'.format(k) for k in finalx_map[j, :])
            line += '\n'
            kickmap.write(line)

        kickmap.write('# Vertical Final Position [m]\nSTART\n')
        kickmap.write(posx_str)
        for j in range(ny):
            line = '{0:g}\t'.format(y_list_rev[j]/1000)
            line += '\t'.join('{0:g}'.format(k) for k in finaly_map[j, :])
            line += '\n'
            kickmap.write(line)

    t1 = _time.time()
    dt = t1 - t0

    return kickx_map, kicky_map, finalx_map, finaly_map, dt


def solve(radia_object, prec=0.00001, max_iter=1000):
    return _rad.Solve(radia_object, prec, max_iter)


def set_len_tol(absolute=1e-12, relative=1e-12):
    return _rad.FldLenTol(absolute, relative)
