
import numpy as _np
from scipy import signal as _signal
import radia as _rad


def set_len_tol(absolute=1e-12, relative=1e-12):
    return _rad.FldLenTol(absolute, relative)


def cosine_function(z, bamp, freq, phase):
    return bamp*_np.cos(freq*z + phase)


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
