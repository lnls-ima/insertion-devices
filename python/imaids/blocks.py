
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import materials as _materials
from . import fieldsource as _fieldsource


class Block(_fieldsource.RadiaModel):
    """Magnetic material block."""

    PREDEFINED_SHAPES = {
        'delta_prototype': [
            [
                [-2.75, 0], [-11.2662, -8.9645], [-7.73071, -12.5],
                [7.73071, -12.5], [11.2662, -8.9645], [2.75, 0]],
            [
                [-7.73071, -12.5], [-11.2662, -16.0355], [-2.75, -25],
                [2.75, -25], [11.2662, -16.0355], [7.73071, -12.5]]],
        'delta_sabia': [
            [
                [-5.25, 0], [-22.5, -19.3], [-22.5, -29.2], [-17.8, -33.2],
                [17.8, -33.2], [22.5, -29.2], [22.5, -19.3], [5.25, 0]],
            [
                [-17.8, -33.2], [-17.8, -38.4], [17.8, -38.4], [17.8, -33.2]],
            [
                [-17.8, -38.4], [-22.5, -42.4], [-22.5, -49], [-21.5, -50],
                [21.5, -50], [22.5, -49], [22.5, -42.4], [17.8, -38.4]]],
        'delta_carnauba': [
            [
                [-2.55, 0.0], [-11.25, -9.65], [-11.25, -14.6],
                [-8.9, -16.6], [8.9, -16.6], [11.25, -14.6],
                [11.25, -9.65], [2.55, 0.0]],
            [
                [-8.9, -16.6], [-8.9, -19.2], [8.9, -19.2], [8.9, -16.6]],
            [
                [-8.9, -19.2], [-11.25, -21.2], [-11.25, -24.5],
                [-10.75, -25.0], [10.75, -25.0], [11.25, -24.5],
                [11.25, -21.2], [8.9, -19.2]]],
        'apple_sabia': [
            [
                [0.1, 0], [50, 0], [50, -50], [0.1, -50]]],
        'apple_carnauba': [
            [
                [0.1, 0], [25, 0], [25, -25], [0.1, -25]]],
        'kyma_22': [
            [
                [15, 0], [18, -3], [18, -17], [15, -20],
                [-15, -20], [-18, -17], [-18, -3], [-15, 0]]],
        'hybrid_block': [
            [
                [30, 0], [30, -40], [-30, -40], [-30, 0]]],
        'hybrid_pole': [
            [
                [20, 0], [20, -40], [-20, -40], [-20, 0]]],
        }

    PREDEFINED_SUBDIVISION = {
        'delta_prototype': [[3, 3, 2], [3, 3, 2]],
        'delta_sabia': [[3, 3, 2], [1, 1, 2], [1, 1, 2]],
        'delta_carnauba': [[3, 3, 2], [1, 1, 1], [1, 1, 1]],
        'apple_sabia': [[3, 3, 3]],
        'apple_carnauba': [[3, 3, 3]],
        'kyma_22': [[6, 3, 3]],
        'hybrid_block': [[3, 3, 3]],
        'hybrid_pole': [[6, 6, 3]],
    }

    def __init__(
            self, shape, length, longitudinal_position,
            magnetization=[0, 1.37, 0], subdivision=None, rectangular=False,
            init_radia_object=True, name='',
            material=None, **kwargs):

        if _utils.depth(shape) != 3:
            self._shape = [shape]
        else:
            self._shape = shape

        if length < 0:
            raise ValueError('The block length must be bigger than 0.')
        self._length = length

        if len(magnetization) != 3:
            raise ValueError('Invalid magnetization argument.')
        self._magnetization = magnetization

        if subdivision is None or len(subdivision) == 0:
            sub = [[1, 1, 1]]*len(self._shape)
        else:
            sub = subdivision

        if _utils.depth(sub) != 2:
            sub = [sub]

        if len(sub) != len(self._shape):
            raise ValueError(
                'Inconsistent length between block_sudivision ' +
                'and block_shape arguments.')
        self._subdivision = sub

        if rectangular not in (True, False):
            raise ValueError('Invalid value for rectangular argument.')
        self._rectangular = rectangular

        self._longitudinal_position = longitudinal_position

        if material is None:
            self._material = _materials.Material(
                mr=_np.linalg.norm(self._magnetization), **kwargs)
        else:
            self._material = material

        self.name = name

        self._radia_object = None
        if init_radia_object:
            self.create_radia_object()

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
        """Initial block longitudinal position [mm]."""
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
    def rectangular(self):
        """True if the shape is rectangular, False otherwise."""
        return self._rectangular

    @property
    def state(self):
        data = {
            'shape': self._shape,
            'length': self._length,
            'longitudinal_position': self._longitudinal_position,
            'magnetization': self._magnetization,
            'subdivision': self._subdivision,
            'rectangular': self._rectangular,
            'name': self.name,
        }
        data.update(self._material.state)
        return data

    @classmethod
    def get_predefined_shape(cls, device_name):
        """Get predefined block shape for the device."""
        return cls.PREDEFINED_SHAPES.get(device_name)

    @classmethod
    def get_predefined_subdivision(cls, device_name):
        """Get predefined block subdivision for the device."""
        return cls.PREDEFINED_SUBDIVISION.get(device_name)

    @classmethod
    def load_state(cls, filename):
        """Load state from file."""
        with open(filename) as f:
            kwargs = _json.load(f)
        return cls(init_radia_object=True, **kwargs)

    def create_radia_object(self):
        """Create radia object."""
        if self._radia_object is not None:
            _rad.UtiDel(self._radia_object)

        if self._length == 0:
            return

        if self._rectangular:
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
                subblock = _rad.MatApl(subblock, self._material.radia_object)
                subblock = _rad.ObjDivMag(subblock, div, 'Frame->Lab')
                subblock_list.append(subblock)
            self._radia_object = _rad.ObjCnt(subblock_list)

        else:
            subblock_list = []
            for shp, div in zip(self._shape, self._subdivision):
                subblock = _rad.ObjThckPgn(
                    self._longitudinal_position, self._length, shp, 'z',
                    self._magnetization)
                subblock = _rad.MatApl(subblock, self._material.radia_object)
                subblock = _rad.ObjDivMag(subblock, div, 'Frame->Lab')
                subblock_list.append(subblock)
            self._radia_object = _rad.ObjCnt(subblock_list)

    def save_state(self, filename):
        """Save state to file."""
        with open(filename, 'w') as f:
            _json.dump(self.state, f)
        return True
