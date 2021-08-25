
import time as _time
from copy import deepcopy as _deepcopy
import json as _json

from . import functions as _functions
from . import fieldsource as _fieldsource


class PMDevice(_fieldsource.FieldSource):
    """Permanent magnet insertion device."""

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
    def device_length(self):
        """device length."""
        start_len = sum(self.start_blocks_distance) + sum(
            self.start_blocks_length)
        end_len = sum(self.end_blocks_distance) + sum(
            self.end_blocks_length)
        return start_len + self.nr_periods*self.period_length + end_len

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

    def get_fieldmap_header(
            self, kh, kv, field_phase, polarization_name):
        if polarization_name == '':
            polarization_name = '--'

        timestamp = _time.strftime('%Y-%m-%d_%H-%M-%S', _time.localtime())

        device_name = self.name
        if device_name == '':
            device_name = '--'

        k = (kh**2 + kv**2)**(1/2)

        header = []
        header.append('timestamp:\t{0:s}\n'.format(timestamp))
        header.append('magnet_name:\t{0:s}\n'.format(device_name))
        header.append('gap[mm]:\t{0:g}\n'.format(self.gap))
        header.append('period_length[mm]:\t{0:g}\n'.format(self.period_length))
        header.append('magnet_length[mm]:\t{0:g}\n'.format(self.device_length))
        header.append('polarization:\t{0:s}\n'.format(polarization_name))
        header.append('field_phase[deg]:\t{0:.0f}\n'.format(field_phase))
        header.append('K_Horizontal:\t{0:.1f}\n'.format(kh))
        header.append('K_Vertical:\t{0:.1f}\n'.format(kv))
        header.append('K:\t{0:.1f}\n'.format(k))
        header.append('\n')

        return header
