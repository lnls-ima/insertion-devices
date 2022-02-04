
import numpy as _np
from scipy import signal as _signal
from scipy import optimize as _optimize
import radia as _rad


def set_len_tol(absolute=1e-12, relative=1e-12):
    return _rad.FldLenTol(absolute, relative)


def delete_all():
    return _rad.UtiDelAll()


def cosine_function(z, bamp, freq, phase):
    return bamp*_np.cos(freq*z + phase)


def calc_cosine_amplitude(
        pos_list, values_list, freq_guess, maxfev=5000):
    if len(pos_list) != len(values_list):
        raise ValueError(
            'Inconsistent length between values and position lists.')

    pos_list = _np.array(pos_list)
    values_list = _np.array(values_list)

    vx, vy, vz = _np.transpose(values_list)
    vx_amp_init = _np.max(_np.abs(vx))
    vy_amp_init = _np.max(_np.abs(vy))
    vz_amp_init = _np.max(_np.abs(vz))

    px = _optimize.curve_fit(
        cosine_function, pos_list, vx,
        p0=[vx_amp_init, freq_guess, 0],
        maxfev=maxfev)[0]
    vx_amp = _np.abs(px[0])
    vx_phase = px[2]

    py = _optimize.curve_fit(
        cosine_function, pos_list, vy,
        p0=[vy_amp_init, freq_guess, 0],
        maxfev=maxfev)[0]
    vy_amp = _np.abs(py[0])
    vy_phase = py[2]

    pz = _optimize.curve_fit(
        cosine_function, pos_list, vz,
        p0=[vz_amp_init, freq_guess, 0],
        maxfev=maxfev)[0]
    vz_amp = _np.abs(pz[0])
    vz_phase = pz[2]

    amp = [vx_amp, vy_amp, vz_amp]
    phase = [vx_phase, vy_phase, vz_phase]

    return amp, phase


def depth(lst):
    return isinstance(lst, list) and max(map(depth, lst)) + 1


def flatten(lst):
    return [item for sublist in lst for item in sublist]


def get_constants():
    electron_rest_energy = 510998.92811  # [eV]
    light_speed = 299792458  # [m/s]
    return electron_rest_energy, light_speed


def calc_beam_parameters(energy):
    electron_rest_energy, light_speed = get_constants()
    gamma = energy*1e9/electron_rest_energy
    beta = _np.sqrt(1 - 1/((energy*1e9/electron_rest_energy)**2))
    brho = energy*1e9/light_speed
    return beta, gamma, brho


def newton_lorentz_equation(a, r, b):
    drds = _np.zeros(6)
    drds[0] = r[3]
    drds[1] = r[4]
    drds[2] = r[5]
    drds[3] = -a*(r[4]*b[2] - r[5]*b[1])
    drds[4] = -a*(r[5]*b[0] - r[3]*b[2])
    drds[5] = -a*(r[3]*b[1] - r[4]*b[0])
    return drds


def rotation_matrix(axis, theta):
    axis = _np.asarray(axis)
    axis = axis / _np.sqrt(_np.dot(axis, axis))
    a = _np.cos(theta / 2.0)
    b, c, d = -axis * _np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    matrix = _np.array([
        [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
        [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
        [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc],
        ])
    return matrix


def find_peaks(data, prominence=0.05):
    peaks, _ = _signal.find_peaks(data, prominence=prominence)
    return peaks


def find_valleys(data, prominence=0.05):
    valleys, _ = _signal.find_peaks(data*(-1), prominence=prominence)
    return valleys


def find_peaks_and_valleys(data, prominence=0.05):
    peaks = find_peaks(data, prominence=prominence)
    valleys = find_valleys(data, prominence=prominence)
    return sorted(_np.append(peaks, valleys))


def find_zeros(pos, data):
    s = _np.sign(data)
    idxb = (s[0:-1] + s[1:] == 0).nonzero()[0]
    idxa = idxb + 1
    posb = pos[idxb]
    posa = pos[idxa]
    datab = data[idxb]
    dataa = data[idxa]
    pos_zeros = (dataa*posb - datab*posa)/(dataa - datab)
    return pos_zeros
