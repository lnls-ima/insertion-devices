
from copy import deepcopy as _deepcopy
import json as _json
import radia as _rad

from . import functions as _functions


class PMDevice():
    """Permanent magnet insertion device base class."""

    def __init__(
            self, block_shape, nr_periods,
            period_length, gap, mr,
            block_subdivision=None,
            rectangular_shape=False, block_distance=0,
            ksipar=0.06, ksiper=0.17,
            start_blocks_length=None, start_blocks_distance=None,
            end_blocks_length=None, end_blocks_distance=None,
            name='', init_radia_object=True):

        if gap <= 0:
            raise ValueError('gap must be > 0.')

        self._block_shape = block_shape
        self._nr_periods = nr_periods
        self._period_length = period_length
        self._gap = gap
        self._mr = mr
        self._block_subdivision = block_subdivision
        self._rectangular_shape = rectangular_shape
        self._block_distance = block_distance
        self._ksipar = ksipar
        self._ksiper = ksiper
        self._start_blocks_length = start_blocks_length
        self._start_blocks_distance = start_blocks_distance
        self._end_blocks_length = end_blocks_length
        self._end_blocks_distance = end_blocks_distance
        self.name = name

        self._cassettes = {}
        self._radia_object = None
        if init_radia_object:
            self.create_radia_object()

    @property
    def block_shape(self):
        """Block list of shapes [mm]."""
        return _deepcopy(self._block_shape)

    @property
    def nr_periods(self):
        """Number of complete periods."""
        return self._nr_periods

    @property
    def period_length(self):
        """Period length [mm]."""
        return self._period_length

    @property
    def gap(self):
        """Magnetic gap [mm]."""
        return self._gap

    @property
    def mr(self):
        """Remanent magnetization [T]."""
        return self._mr

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
    def radia_object(self):
        """Number of the radia object."""
        return self._radia_object

    @property
    def cassettes(self):
        """Cassettes dictionary."""
        return _deepcopy(self._cassettes)

    @property
    def cassette_properties(self):
        """Common cassettes properties."""
        props = {
            'nr_periods': self._nr_periods,
            'period_length': self._period_length,
            'mr': self._mr,
            'ksipar': self._ksipar,
            'ksiper': self._ksiper,
            'block_subdivision': self._block_subdivision,
            'rectangular_shape': self._rectangular_shape,
            'block_distance': self._block_distance,
            'start_blocks_length': self._start_blocks_length,
            'start_blocks_distance': self._start_blocks_distance,
            'end_blocks_length': self._end_blocks_length,
            'end_blocks_distance': self._end_blocks_distance,
        }
        return props

    @property
    def magnetization_dict(self):
        mag_dict = {}

        for key, value in self._cassettes.items():
            mag_dict[key] = value.magnetization_list

        return mag_dict

    @property
    def horizontal_pos_err_dict(self):
        herr_dict = {}

        for key, value in self._cassettes.items():
            herr_dict[key] = value.horizontal_pos_err

        return herr_dict

    @property
    def vertical_pos_err_dict(self):
        verr_dict = {}

        for key, value in self._cassettes.items():
            verr_dict[key] = value.vertical_pos_err

        return verr_dict

    @classmethod
    def load_state(cls, filename):
        """Load state from file."""

        with open(filename) as f:
            kwargs = _json.load(f)

        magnetization_dict = kwargs.pop('magnetization_dict', None)
        horizontal_pos_err_dict = kwargs.pop('horizontal_pos_err_dict', None)
        vertical_pos_err_dict = kwargs.pop('vertical_pos_err_dict', None)

        device = cls(init_radia_object=False, **kwargs)
        device.create_radia_object(
            magnetization_dict=magnetization_dict,
            horizontal_pos_err_dict=horizontal_pos_err_dict,
            vertical_pos_err_dict=vertical_pos_err_dict)

        return device

    def create_radia_object(self):
        raise NotImplementedError

    def calc_field_amplitude(self, *args, **kwargs):
        return _functions.calc_field_amplitude(
            self._radia_object, self._period_length,
            self._nr_periods, *args, **kwargs)

    def calc_field_integrals(self, *args, **kwargs):
        return _functions.calc_field_integrals(
            self._radia_object, *args, **kwargs)

    def calc_trajectory(self, *args, **kwargs):
        return _functions.calc_trajectory(
            self._radia_object, *args, **kwargs)

    def draw(self):
        return _functions.draw(self._radia_object)

    def get_field(self, *args, **kwargs):
        return _functions.get_field(self._radia_object, *args, **kwargs)

    def save_fieldmap(self, *args, **kwargs):
        return _functions.save_fieldmap(self._radia_object, *args, **kwargs)

    def save_fieldmap_spectra(self, *args, **kwargs):
        return _functions.save_fieldmap_spectra(
            self._radia_object, *args, **kwargs)

    def save_kickmap(self, *args, **kwargs):
        return _functions.save_kickmap(self._radia_object, *args, **kwargs)

    def save_state(self, filename):
        horizontal_pos_err_dict = {}
        vertical_pos_err_dict = {}

        for key, value in self._cassettes.items():
            horizontal_pos_err_dict[key] = value.horizontal_pos_err
            vertical_pos_err_dict[key] = value.vertical_pos_err

        data = {
            'block_shape': self._block_shape,
            'nr_periods': self._nr_periods,
            'period_length': self._period_length,
            'gap': self._gap,
            'mr': self._mr,
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
            'magnetization_dict': self.magnetization_dict,
            'horizontal_pos_err_dict': horizontal_pos_err_dict,
            'vertical_pos_err_dict': vertical_pos_err_dict,
        }

        with open(filename, 'w') as f:
            _json.dump(data, f)

        return True

    def solve(self, *args, **kwargs):
        return _functions.solve(self._radia_object, *args, **kwargs)

    def shift(self, value):
        self._radia_object = _rad.TrfOrnt(
            self._radia_object, _rad.TrfTrsl(value))

    def rotate(self, point, vector, angle):
        self._radia_object = _rad.TrfOrnt(
            self._radia_object, _rad.TrfRot(point, vector, angle))
