
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import blocks as _blocks
from . import fieldsource as _fieldsource


class Cassette(
        _fieldsource.FieldModel, _fieldsource.SinusoidalFieldSource):
    """Insertion device cassette."""

    def __init__(
            self, nr_periods=None, period_length=None, mr=None,
            block_shape=None, upper_cassette=False, longitudinal_distance=0,
            block_subdivision=None, rectangular=False,
            ksipar=0.06, ksiper=0.17, hybrid=False,
            pole_shape=None, pole_length=None, pole_material=None,
            pole_subdivision=None,
            start_blocks_length=None, start_blocks_distance=None,
            end_blocks_length=None, end_blocks_distance=None,
            name='', init_radia_object=True):
        """_summary_

        Args:
            nr_periods (int, optional): Number of complete periods.
                Defaults to None.
            period_length (float, optional): Period length in mm.
                Defaults to None.
            mr (float, optional): magnitude of the remanent magnetization
                vector in Tesla. Defaults to None.
            block_shape (list, optional): _description_. Defaults to None.
            upper_cassette (bool, optional): _description_. Defaults to False.
            longitudinal_distance (int, optional): _description_. Defaults to 0.
            block_subdivision (_type_, optional): _description_. Defaults to None.
            rectangular (bool, optional): _description_. Defaults to False.
            ksipar (float, optional): _description_. Defaults to 0.06.
            ksiper (float, optional): _description_. Defaults to 0.17.
            hybrid (bool, optional): _description_. Defaults to False.
            pole_shape (_type_, optional): _description_. Defaults to None.
            pole_length (_type_, optional): _description_. Defaults to None.
            pole_material (_type_, optional): _description_. Defaults to None.
            pole_subdivision (_type_, optional): _description_. Defaults to None.
            start_blocks_length (_type_, optional): _description_. Defaults to None.
            start_blocks_distance (_type_, optional): _description_. Defaults to None.
            end_blocks_length (_type_, optional): _description_. Defaults to None.
            end_blocks_distance (_type_, optional): _description_. Defaults to None.
            name (str, optional): _description_. Defaults to ''.
            init_radia_object (bool, optional): _description_. Defaults to True.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        _fieldsource.SinusoidalFieldSource.__init__(
            self, nr_periods=nr_periods, period_length=period_length)

        if mr is not None and mr < 0:
            raise ValueError('mr must be >= 0.')
        self._mr = float(mr)

        if longitudinal_distance is not None and longitudinal_distance < 0:
            raise ValueError('longitudinal_distance must be >= 0.')
        self._longitudinal_distance = longitudinal_distance

        if upper_cassette not in (True, False):
            raise ValueError('Invalid value for upper_cassette argument.')
        self._upper_cassette = upper_cassette

        self._block_shape = block_shape
        self._rectangular = rectangular

        if start_blocks_length and start_blocks_distance:
            if len(start_blocks_length) != len(start_blocks_distance):
                raise ValueError('Incosistent start blocks arguments.')
            self._start_blocks_length = start_blocks_length
            self._start_blocks_distance = start_blocks_distance
        else:
            self._start_blocks_length = []
            self._start_blocks_distance = []

        if end_blocks_length and end_blocks_distance:
            if len(end_blocks_length) != len(end_blocks_distance):
                raise ValueError('Incosistent end blocks arguments.')
            self._end_blocks_length = end_blocks_length
            self._end_blocks_distance = end_blocks_distance
        else:
            self._end_blocks_length = []
            self._end_blocks_distance = []

        self._hybrid = hybrid
        if self._hybrid:
            if pole_shape is None:
                pole_shape = block_shape

        self._pole_shape = pole_shape
        self._pole_length = pole_length
        self._pole_material = pole_material
        self._pole_subdivision = pole_subdivision

        self._block_subdivision = block_subdivision
        self._ksipar = ksipar
        self._ksiper = ksiper
        self.name = name

        self._position_err = []
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
    def hybrid(self):
        """True for hybrid cassette, False otherwise."""
        return self._hybrid

    @property
    def pole_length(self):
        """Pole length [mm]."""
        return self._pole_length

    @property
    def pole_shape(self):
        """Pole list of shapes [mm]."""
        return _deepcopy(self._pole_shape)

    @property
    def pole_subdivision(self):
        """Pole shape subdivision."""
        return _deepcopy(self._pole_subdivision)

    @property
    def upper_cassette(self):
        """True for upper cassette, False otherwise."""
        return self._upper_cassette

    @property
    def longitudinal_distance(self):
        """Longitudinal distance between regular blocks [mm]."""
        return self._longitudinal_distance

    @property
    def block_subdivision(self):
        """Block shape subdivision."""
        return _deepcopy(self._block_subdivision)

    @property
    def rectangular(self):
        """True if the shape is rectangular, False otherwise."""
        return self._rectangular

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
        """List of Block objects."""
        return self._blocks

    @property
    def position_err(self):
        """Position errors [mm]."""
        return _deepcopy(self._position_err)

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
    def cassette_length(self):
        """Cassette length."""
        start_len = sum(self.start_blocks_distance) + sum(
            self.start_blocks_length)
        end_len = sum(self.end_blocks_distance) + sum(
            self.end_blocks_length)
        return start_len + self.nr_periods*self.period_length + end_len

    @property
    def block_names(self):
        """List of block names."""
        name_list = [block.name for block in self._blocks]
        return name_list

    @property
    def magnetization_list(self):
        """List of magnetization vectors [T]."""
        mag_list = [block.magnetization for block in self._blocks]
        return mag_list

    @property
    def longitudinal_position_list(self):
        """List of initial longitudinal position of blocks [mm]."""
        pos_list = [block.longitudinal_position for block in self._blocks]
        return pos_list

    @property
    def state(self):
        data = {
            'block_shape': self.block_shape,
            'nr_periods': self.nr_periods,
            'period_length': self.period_length,
            'mr': self.mr,
            'upper_cassette': self.upper_cassette,
            'longitudinal_distance': self.longitudinal_distance,
            'block_subdivision': self.block_subdivision,
            'rectangular': self.rectangular,
            'ksipar': self.ksipar,
            'ksiper': self.ksiper,
            'start_blocks_length': self.start_blocks_length,
            'start_blocks_distance': self.start_blocks_distance,
            'end_blocks_length': self.end_blocks_length,
            'end_blocks_distance': self.end_blocks_distance,
            'hybrid': self.hybrid,
            'pole_shape': self.pole_shape,
            'pole_length': self.pole_length,
            'pole_subdivision': self.pole_subdivision,
            'name': self.name,
            'block_names': list(self.block_names),
            'magnetization_list': list(self.magnetization_list),
            'position_err': list(self._position_err),
        }
        return data

    @classmethod
    def load_state(cls, filename):
        """Load state from file.

        Args:
            filename (_type_): _description_

        Returns:
            _type_: _description_
        """
        with open(filename) as f:
            kwargs = _json.load(f)

        block_names = kwargs.pop('block_names', None)
        magnetization_list = kwargs.pop('magnetization_list', None)
        position_err = kwargs.pop('position_err', None)

        cassette = cls(init_radia_object=False, **kwargs)
        cassette.create_radia_object(
            magnetization_list=magnetization_list,
            position_err=position_err, block_names=block_names)

        return cassette

    def create_radia_object(
            self,
            block_names=None,
            magnetization_list=None,
            position_err=None):
        """Create radia object.

        Args:
            block_names (_type_, optional): _description_. Defaults to None.
            magnetization_list (_type_, optional): _description_. Defaults to None.
            position_err (_type_, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
        """
        if self._radia_object is not None:
            _rad.UtiDel(self._radia_object)

        if block_names is None:
            block_names = ['']*self.nr_blocks
        if len(block_names) != self.nr_blocks:
            raise ValueError(
                'Invalid length for block name list.')

        if position_err is None:
            position_err = [[0, 0, 0]]*self.nr_blocks
        if len(position_err) != self.nr_blocks:
            raise ValueError(
                'Invalid length for position errors list.')
        self._position_err = position_err

        if self.hybrid:
            block_length = (
                self._period_length/2 - self._pole_length -
                self._longitudinal_distance)
        else:
            block_length = self._period_length/4 - self._longitudinal_distance

        if magnetization_list is None:
            magnetization_list = self.get_ideal_magnetization_list()

        if self.hybrid:
            mag0 = magnetization_list[0]
            if _np.abs(mag0[1]) > _np.abs(mag0[2]):
                length_list = _utils.flatten([
                    self._start_blocks_length,
                    [self._pole_length, block_length]*int(
                        self.nr_core_blocks/2),
                    self._end_blocks_length])
            else:
                length_list = _utils.flatten([
                    self._start_blocks_length,
                    [block_length, self._pole_length]*int(
                        self.nr_core_blocks/2),
                    self._end_blocks_length])
        else:
            length_list = _utils.flatten([
                self._start_blocks_length,
                [block_length]*self.nr_core_blocks,
                self._end_blocks_length])

        distance_list = _utils.flatten([
            self._start_blocks_distance,
            [self._longitudinal_distance]*(self.nr_core_blocks-1),
            self._end_blocks_distance])

        position_list = [0]
        for i in range(1, self.nr_blocks):
            position_list.append((
                length_list[i] + length_list[i-1])/2 + distance_list[i-1])
        position_list = _np.cumsum(position_list)
        position_list -= (position_list[0] + position_list[-1])/2

        self._blocks = []
        count = 0
        for length, position, magnetization in zip(
                length_list, position_list, magnetization_list):
            if self.hybrid and not count % 2:
                block = _blocks.Block(
                    self._pole_shape, length, position, [0, 0, 0],
                    subdivision=self._pole_subdivision,
                    rectangular=self._rectangular,
                    material=self._pole_material)
            else:
                block = _blocks.Block(
                    self._block_shape, length, position, magnetization,
                    subdivision=self._block_subdivision,
                    rectangular=self._rectangular,
                    ksipar=self._ksipar, ksiper=self._ksiper)
            self._blocks.append(block)
            count += 1

        for idx, block in enumerate(self._blocks):
            block.shift(position_err[idx])

        for name, block in zip(block_names, self._blocks):
            block.name = name

        rad_obj_list = []
        for block in self._blocks:
            if block.radia_object is not None:
                rad_obj_list.append(block.radia_object)
        self._radia_object = _rad.ObjCnt(rad_obj_list)

    def get_ideal_magnetization_list(self):
        """List of magnetization vector without amplitude and
        angular errors.

        Returns:
            _type_: _description_
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
        """List of magnetization vector with random amplitude
        and angular errors.

        Args:
            max_amplitude_error (int, optional): _description_. Defaults to 0.
            max_angular_error (int, optional): _description_. Defaults to 0.
            termination_errors (bool, optional): _description_. Defaults to True.
            core_errors (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
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
            self, max_horizontal_error=0,
            max_vertical_error=0, max_longitudinal_error=0,
            termination_errors=True, core_errors=True):
        """_summary_

        Args:
            max_horizontal_error (int, optional): _description_. Defaults to 0.
            max_vertical_error (int, optional): _description_. Defaults to 0.
            max_longitudinal_error (int, optional): _description_. Defaults to 0.
            termination_errors (bool, optional): _description_. Defaults to True.
            core_errors (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        position_err = []

        nr_start = self.nr_start_blocks
        nr_blocks = self.nr_blocks
        nr_end = self.nr_end_blocks

        for idx in range(nr_blocks):
            is_termination = idx < nr_start or idx >= nr_blocks - nr_end
            if is_termination and not termination_errors:
                position_err.append([0, 0, 0])
            elif not is_termination and not core_errors:
                position_err.append([0, 0, 0])
            else:
                herr = _np.random.uniform(-1, 1)*max_horizontal_error
                verr = _np.random.uniform(-1, 1)*max_vertical_error
                lerr = _np.random.uniform(-1, 1)*max_longitudinal_error
                position_err.append([herr, verr, lerr])

        return position_err
