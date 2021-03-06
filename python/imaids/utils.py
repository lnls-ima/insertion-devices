
import numpy as _np


def depth(lst):
    return isinstance(lst, list) and max(map(depth, lst)) + 1


def flatten(lst):
    return [item for sublist in lst for item in sublist]


def get_constants():
    electron_rest_energy = 510998.92811  # [eV]
    light_speed = 299792458  # [m/s]
    return electron_rest_energy, light_speed


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
