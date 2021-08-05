
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import functions as _functions


class PMBlock():
    """Permanent magnet block."""

    def __init__(
            self, shape, length, longitudinal_position, magnetization,
            subdivision=None, rectangular_shape=False,
            ksipar=0.06, ksiper=0.17, name='', init_radia_object=True):

        if _utils.depth(shape) != 3:
            shape = [shape]

        if length < 0:
            raise ValueError('The block length must be bigger than 0.')

        if len(magnetization) != 3:
            raise ValueError('Invalid magnetization argument.')

        if subdivision is None or len(subdivision) == 0:
            subdivision = [[1, 1, 1]]*len(shape)

        if _utils.depth(subdivision) != 2:
            subdivision = [subdivision]

        if len(subdivision) != len(shape):
            raise ValueError(
                'Inconsistent length between block_sudivision ' +
                'and block_shape arguments.')

        if rectangular_shape not in (True, False):
            raise ValueError('Invalid value for rectangular_shape argument.')

        self._shape = shape
        self._length = length
        self._longitudinal_position = longitudinal_position
        self._magnetization = magnetization
        self._subdivision = subdivision
        self._rectangular_shape = rectangular_shape
        self._ksipar = ksipar
        self._ksiper = ksiper
        self.name = name

        self._radia_object = None
        if init_radia_object:
            self.create_radia_object()

    def __str__(self):
        """Printable string representation of the object."""
        fmtstr = '{0:<18s} : {1}\n'
        r = ''
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                name = key[1:]
            else:
                name = key
            r += fmtstr.format(name, str(value))
        return r

    @property
    def shape(self):
        """Block list of shapes [mm]."""
        return _deepcopy(self._shape)

    @property
    def length(self):
        """Block length [mm]."""
        return self._length

    @property
    def longitudinal_position(self):
        """Block longitudinal position [mm]."""
        return self._longitudinal_position

    @property
    def magnetization(self):
        """Block magnetization vector [T]."""
        return _deepcopy(self._magnetization)

    @property
    def subdivision(self):
        """Block shape subdivision."""
        return _deepcopy(self._subdivision)

    @property
    def rectangular_shape(self):
        """True if the shape is rectangular, False otherwise."""
        return self._rectangular_shape

    @property
    def ksipar(self):
        """Parallel magnetic susceptibility."""
        return self._ksipar

    @property
    def ksiper(self):
        """Perpendicular magnetic susceptibility."""
        return self._ksiper

    @property
    def radia_object(self):
        """Number of the radia object."""
        return self._radia_object

    @staticmethod
    def get_predefined_shape(device_name):
        """Get predefined block shape for the device."""
        block_shape = None

        if device_name == 'delta_prototype':
            block_shape_a = [
                [-2.75, 0], [-11.2662, -8.9645], [-7.73071, -12.5],
                [7.73071, -12.5], [11.2662, -8.9645], [2.75, 0]]
            block_shape_b = [
                [-7.73071, -12.5], [-11.2662, -16.0355], [-2.75, -25],
                [2.75, -25], [11.2662, -16.0355], [7.73071, -12.5]]
            block_shape = [block_shape_a, block_shape_b]

        elif device_name == 'delta_sabia':
            block_shape_a = [
                [-5.25, 0], [-22.5, -19.3], [-22.5, -29.2], [-17.8, -33.2],
                [17.8, -33.2], [22.5, -29.2], [22.5, -19.3], [5.25, 0]]
            block_shape_b = [
                [-17.8, -33.2], [-17.8, -38.4], [17.8, -38.4], [17.8, -33.2]]
            block_shape_c = [
                [-17.8, -38.4], [-22.5, -42.4], [-22.5, -49], [-21.5, -50],
                [21.5, -50], [22.5, -49], [22.5, -42.4], [17.8, -38.4]]
            block_shape = [block_shape_a, block_shape_b, block_shape_c]

        elif device_name == 'delta_carnauba':
            block_shape_a = [
                [-2.55, 0.0], [-11.25, -9.65], [-11.25, -14.6],
                [-8.9, -16.6], [8.9, -16.6], [11.25, -14.6],
                [11.25, -9.65], [2.55, 0.0]]
            block_shape_b = [
                [-8.9, -16.6], [-8.9, -19.2], [8.9, -19.2], [8.9, -16.6]]
            block_shape_c = [
                [-8.9, -19.2], [-11.25, -21.2], [-11.25, -24.5],
                [-10.75, -25.0], [10.75, -25.0], [11.25, -24.5],
                [11.25, -21.2], [8.9, -19.2]]
            block_shape = [block_shape_a, block_shape_b, block_shape_c]

        elif device_name == 'apple_sabia':
            block_shape_a = [[0.1, 0], [50, 0], [50, -50], [0.1, -50]]
            block_shape = [block_shape_a]

        elif device_name == 'apple_carnauba':
            block_shape_a = [[0.1, 0], [25, 0], [25, -25], [0.1, -25]]
            block_shape = [block_shape_a]

        elif device_name == 'kyma_22':
            block_shape_a = [
                [15, 0], [18, -3], [18, -17], [15, -20],
                [-15, -20], [-18, -17], [-18, -3], [-15, 0]]
            block_shape = [block_shape_a]

        return block_shape

    @staticmethod
    def get_predefined_subdivision(device_name):
        """Get predefined block subdivision for the device."""
        block_subdivision = None

        if device_name == 'delta_prototype':
            block_subdivision_a = [3, 3, 2]
            block_subdivision_b = [3, 3, 2]
            block_subdivision = [
                block_subdivision_a, block_subdivision_b]

        elif device_name == 'delta_sabia':
            block_subdivision_a = [3, 3, 2]
            block_subdivision_b = [1, 1, 2]
            block_subdivision_c = [1, 1, 2]
            block_subdivision = [
                block_subdivision_a, block_subdivision_b, block_subdivision_c]

        elif device_name == 'delta_carnauba':
            block_subdivision_a = [3, 3, 2]
            block_subdivision_b = [1, 1, 1]
            block_subdivision_c = [1, 1, 1]
            block_subdivision = [
                block_subdivision_a, block_subdivision_b, block_subdivision_c]

        elif device_name == 'apple_sabia':
            block_subdivision_a = [3, 3, 3]
            block_subdivision = [block_subdivision_a]

        elif device_name == 'apple_carnauba':
            block_subdivision_a = [3, 3, 3]
            block_subdivision = [block_subdivision_a]

        elif device_name == 'kyma_22':
            block_subdivision_a = [6, 3, 3]
            block_subdivision = [block_subdivision_a]

        return block_subdivision

    @classmethod
    def load_state(cls, filename):
        """Load state from file."""

        with open(filename) as f:
            kwargs = _json.load(f)

        block = cls(init_radia_object=True, **kwargs)
        return block

    def create_radia_object(self):
        """Create radia object."""
        if self._radia_object is not None:
            _rad.UtiDel(self._radia_object)

        if self._length == 0:
            return

        mat = _rad.MatLin(
            [self._ksipar, self._ksiper],
            _np.linalg.norm(self._magnetization))

        if self._rectangular_shape:
            center = []
            width = []
            height = []
            for shp in self._shape:
                shp = _np.array(shp)
                min0 = _np.min(shp[:, 0])
                max0 = _np.max(shp[:, 0])
                min1 = _np.min(shp[:, 1])
                max1 = _np.max(shp[:, 1])
                center.append([(max0 + min0)/2, (max1 + min1)/2])
                width.append(max0 - min0)
                height.append(max1 - min1)

            subblock_list = []
            for ctr, wdt, hgt, div in zip(
                    center, width, height, self._subdivision):
                subblock = _rad.ObjRecMag(
                    [ctr[0], ctr[1], self._longitudinal_position],
                    [wdt, hgt, self._length], self._magnetization)
                subblock = _rad.MatApl(subblock, mat)
                subblock = _rad.ObjDivMag(subblock, div, 'Frame->Lab')
                subblock_list.append(subblock)
            self._radia_object = _rad.ObjCnt(subblock_list)

        else:
            subblock_list = []
            for shp, div in zip(self._shape, self._subdivision):
                subblock = _rad.ObjThckPgn(
                    self._longitudinal_position, self._length, shp, 'z',
                    self._magnetization)
                subblock = _rad.MatApl(subblock, mat)
                subblock = _rad.ObjDivMag(subblock, div, 'Frame->Lab')
                subblock_list.append(subblock)
            self._radia_object = _rad.ObjCnt(subblock_list)

    def draw(self):
        """Draw the radia object."""
        return _functions.draw(self._radia_object)

    def save_state(self, filename):
        """Save state to file."""
        data = {
            'shape': self._shape,
            'length': self._length,
            'longitudinal_position': self._longitudinal_position,
            'magnetization': self._magnetization,
            'subdivision': self._subdivision,
            'rectangular_shape': self._rectangular_shape,
            'ksipar': self._ksipar,
            'ksiper': self._ksiper,
            'name': self.name,
        }

        with open(filename, 'w') as f:
            _json.dump(data, f)

        return True

    def shift(self, value):
        """Shift the radia object."""
        if self._radia_object is not None:
            self._radia_object = _rad.TrfOrnt(
                self._radia_object, _rad.TrfTrsl(value))
            self._longitudinal_position += value[2]
