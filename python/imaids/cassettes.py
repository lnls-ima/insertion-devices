
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import blocks as _blocks
from . import fieldsource as _fieldsource


class PMCassette(_fieldsource.FieldSource):
    """Permanent magnet cassette."""

    def __init__(
            self, block_shape, nr_periods, period_length, mr,
            upper_cassette=False, block_distance=0,
            block_subdivision=None, rectangular_shape=False,
            ksipar=0.06, ksiper=0.17,
            start_blocks_length=None, start_blocks_distance=None,
            end_blocks_length=None, end_blocks_distance=None,
            name='', init_radia_object=True):

        pos_args = [
            nr_periods, period_length, mr, block_distance]
        if any([arg < 0 for arg in pos_args]):
            raise ValueError('Invalid argument value.')

        if upper_cassette not in (True, False):
            raise ValueError('Invalid value for upper_cassette argument.')

        if start_blocks_length and start_blocks_distance:
            if len(start_blocks_length) != len(start_blocks_distance):
                raise ValueError('Incosistent start blocks arguments.')
        else:
            start_blocks_length = []
            start_blocks_distance = []

        if end_blocks_length and end_blocks_distance:
            if len(end_blocks_length) != len(end_blocks_distance):
                raise ValueError('Incosistent end blocks arguments.')
        else:
            end_blocks_length = []
            end_blocks_distance = []

        self._block_shape = block_shape
        self._nr_periods = nr_periods
        self._period_length = period_length
        self._mr = float(mr)
        self._upper_cassette = upper_cassette
        self._block_distance = block_distance
        self._block_subdivision = block_subdivision
        self._rectangular_shape = rectangular_shape
        self._ksipar = ksipar
        self._ksiper = ksiper
        self._start_blocks_length = start_blocks_length
        self._start_blocks_distance = start_blocks_distance
        self._end_blocks_length = end_blocks_length
        self._end_blocks_distance = end_blocks_distance
        self.name = name

        self._horizontal_pos_err = []
        self._vertical_pos_err = []
        self._blocks = []
        self._radia_object = None
        if init_radia_object:
            self.create_radia_object()

    @property
    def block_shape(self):
        """Block list of shapes [mm]."""
        return _deepcopy(self._block_shape)

    @property
    def nr_period(self):
        """Number of complete periods."""
        return self._nr_periods

    @property
    def period_length(self):
        """Period length [mm]."""
        return self._period_length

    @property
    def mr(self):
        """Remanent magnetization [T]."""
        return self._mr

    @property
    def upper_cassette(self):
        """True for upper cassette, False otherwise."""
        return self._upper_cassette

    @property
    def block_distance(self):
        """Longitudinal distance between regular blocks [mm]."""
        return self._block_distance

    @property
    def block_subdivision(self):
        """Block shape subdivision."""
        return _deepcopy(self._block_subdivision)

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
    def start_blocks_length(self):
        """List of block lengths in the start of the cassette."""
        return _deepcopy(self._start_blocks_length)

    @property
    def start_blocks_distance(self):
        """List of distance between blocks in the start of the cassette."""
        return _deepcopy(self._start_blocks_distance)

    @property
    def end_blocks_length(self):
        """List of block lengths in the end of the cassette."""
        return _deepcopy(self._end_blocks_length)

    @property
    def end_blocks_distance(self):
        """List of distance between blocks in the end of the cassette."""
        return _deepcopy(self._end_blocks_distance)

    @property
    def blocks(self):
        """List of PMBlock objects."""
        return self._blocks

    @property
    def horizontal_pos_err(self):
        """Horizontal position errors [mm]."""
        return _deepcopy(self._horizontal_pos_err)

    @property
    def vertical_pos_err(self):
        """Vertical position errors [mm]."""
        return _deepcopy(self._vertical_pos_err)

    @property
    def nr_start_blocks(self):
        """Number of blocks in the start of the cassette."""
        return len(self._start_blocks_length)

    @property
    def nr_core_blocks(self):
        """Number of blocks in the core the cassette."""
        return 4*self._nr_periods

    @property
    def nr_end_blocks(self):
        """Number of blocks in the end of the cassette."""
        return len(self._end_blocks_length)

    @property
    def nr_blocks(self):
        """Total number of blocks in the cassette."""
        nr_blocks = (
            self.nr_start_blocks + self.nr_core_blocks + self.nr_end_blocks)
        return nr_blocks

    @property
    def magnetization_list(self):
        """List of magnetization vectors [T]."""
        magnetization_list = [block.magnetization for block in self._blocks]
        return magnetization_list

    @classmethod
    def load_state(cls, filename):
        """Load state from file."""

        with open(filename) as f:
            kwargs = _json.load(f)

        magnetization_list = kwargs.pop('magnetization_list', None)
        horizontal_pos_err = kwargs.pop('horizontal_pos_err', None)
        vertical_pos_err = kwargs.pop('vertical_pos_err', None)

        cassette = cls(init_radia_object=False, **kwargs)
        cassette.create_radia_object(
            magnetization_list=magnetization_list,
            horizontal_pos_err=horizontal_pos_err,
            vertical_pos_err=vertical_pos_err)

        return cassette

    def create_radia_object(
            self, magnetization_list=None,
            horizontal_pos_err=None,
            vertical_pos_err=None):
        """Create radia object."""
        if self._radia_object is not None:
            _rad.UtiDel(self._radia_object)

        if horizontal_pos_err is None:
            horizontal_pos_err = [0]*self.nr_blocks
        if len(horizontal_pos_err) != self.nr_blocks:
            raise ValueError(
                'Invalid length for horizontal errors list.')
        self._horizontal_pos_err = horizontal_pos_err

        if vertical_pos_err is None:
            vertical_pos_err = [0]*self.nr_blocks
        if len(vertical_pos_err) != self.nr_blocks:
            raise ValueError(
                'Invalid length for vertical errors list.')
        self._vertical_pos_err = vertical_pos_err

        block_length = self._period_length/4 - self._block_distance

        length_list = _utils.flatten([
            self._start_blocks_length,
            [block_length]*self.nr_core_blocks,
            self._end_blocks_length])

        distance_list = _utils.flatten([
            self._start_blocks_distance,
            [self._block_distance]*(self.nr_core_blocks-1),
            self._end_blocks_distance])

        position_list = [0]
        for i in range(1, self.nr_blocks):
            position_list.append((
                length_list[i] + length_list[i-1])/2 + distance_list[i-1])
        position_list = list(_np.cumsum(position_list))

        if magnetization_list is None:
            magnetization_list = self.get_ideal_magnetization_list()

        self._blocks = []
        for length, position, magnetization in zip(
                length_list, position_list, magnetization_list):
            block = _blocks.PMBlock(
                self._block_shape, length, position, magnetization,
                subdivision=self._block_subdivision,
                rectangular_shape=self._rectangular_shape,
                ksipar=self._ksipar, ksiper=self._ksiper)
            self._blocks.append(block)

        for idx, block in enumerate(self._blocks):
            block.shift([
                horizontal_pos_err[idx],
                vertical_pos_err[idx],
                0])

        rad_obj_list = []
        for block in self._blocks:
            if block.radia_object is not None:
                rad_obj_list.append(block.radia_object)
        self._radia_object = _rad.ObjCnt(rad_obj_list)

        self.shift([0, 0, -(position_list[0] + position_list[-1])/2])

    def get_ideal_magnetization_list(self):
        """
        List of magnetization vector without amplitude and angular errors.
        """
        if self._upper_cassette:
            first_core_block = 2
        else:
            first_core_block = 0

        direction_list = [[0, 1, 0], [0, 0, -1], [0, -1, 0], [0, 0, 1]]

        first_block = (4 + first_core_block - self.nr_start_blocks) % 4

        magnetization_list = direction_list*int(
            _np.ceil(self.nr_blocks/len(direction_list))+1)
        magnetization_list = magnetization_list[
            first_block:self.nr_blocks+first_block]
        magnetization_list = self.mr*_np.array(magnetization_list)

        return magnetization_list.tolist()

    def get_random_errors_magnetization_list(
            self, max_amplitude_error=0, max_angular_error=0,
            termination_errors=True, core_errors=True):
        """
        List of magnetization vector with random amplitude
        and angular errors.
        """
        magnetization_list = self.get_ideal_magnetization_list()

        nr_start = self.nr_start_blocks
        nr_blocks = self.nr_blocks
        nr_end = self.nr_end_blocks

        magnetization_list_with_errors = []
        for idx, magnetization in enumerate(magnetization_list):
            is_termination = idx < nr_start or idx >= nr_blocks - nr_end
            if is_termination and not termination_errors:
                magnetization_list_with_errors.append(magnetization)
            elif not is_termination and not core_errors:
                magnetization_list_with_errors.append(magnetization)
            else:
                f = 1 + _np.random.uniform(-1, 1)*max_amplitude_error
                rot_angle = _np.random.uniform(-1, 1)*max_angular_error
                rot_axis = _np.random.uniform(-1, 1, size=3)
                rot_matrix = _utils.rotation_matrix(rot_axis, rot_angle)
                magnetization_list_with_errors.append(list(
                    _np.dot(rot_matrix, f*_np.array(magnetization))))

        return magnetization_list_with_errors

    def get_random_errors_position(
            self, max_horizontal_error=0, max_vertical_error=0,
            termination_errors=True, core_errors=True):
        horizontal_pos_err = []
        vertical_pos_err = []

        nr_start = self.nr_start_blocks
        nr_blocks = self.nr_blocks
        nr_end = self.nr_end_blocks

        for idx in range(nr_blocks):
            is_termination = idx < nr_start or idx >= nr_blocks - nr_end
            if is_termination and not termination_errors:
                horizontal_pos_err.append(0)
                vertical_pos_err.append(0)
            elif not is_termination and not core_errors:
                horizontal_pos_err.append(0)
                vertical_pos_err.append(0)
            else:
                horizontal_pos_err.append(
                    _np.random.uniform(-1, 1)*max_horizontal_error)
                vertical_pos_err.append(
                    _np.random.uniform(-1, 1)*max_vertical_error)

        return horizontal_pos_err, vertical_pos_err

    def save_state(self, filename):
        """Save state to file."""
        data = {
            'block_shape': self._block_shape,
            'nr_periods': self._nr_periods,
            'period_length': self._period_length,
            'mr': self._mr,
            'upper_cassette': self._upper_cassette,
            'block_distance': self._block_distance,
            'block_subdivision': self._block_subdivision,
            'rectangular_shape': self._rectangular_shape,
            'ksipar': self._ksipar,
            'ksiper': self._ksiper,
            'start_blocks_length': self._start_blocks_length,
            'start_blocks_distance': self._start_blocks_distance,
            'end_blocks_length': self._end_blocks_length,
            'end_blocks_distance': self._end_blocks_distance,
            'name': self.name,
            'magnetization_list': list(self.magnetization_list),
            'horizontal_pos_err': list(
                self._horizontal_pos_err),
            'vertical_pos_err': list(self._vertical_pos_err),
        }

        with open(filename, 'w') as f:
            _json.dump(data, f)

        return True
