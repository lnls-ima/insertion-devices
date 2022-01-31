
import time as _time
from copy import deepcopy as _deepcopy
import json as _json

from . import fieldsource as _fieldsource


class InsertionDeviceData(
        _fieldsource.FieldData, _fieldsource.SinusoidalFieldSource):
    """Insertion device field data."""

    def __init__(
            self, nr_periods=None, period_length=None,
            gap=None, name='', filename=None,
            raw_data=None, selected_y=0):
        if gap <= 0:
            raise ValueError('gap must be > 0.')

        self._gap = gap
        self.name = name

        _fieldsource.SinusoidalFieldSource.__init__(
            self, nr_periods=nr_periods, period_length=period_length)

        _fieldsource.FieldData.__init__(
            self, filename=filename, raw_data=raw_data, selected_y=selected_y)

    @property
    def gap(self):
        """Magnetic gap [mm]."""
        return self._gap

    @gap.setter
    def gap(self, value):
        self._gap = value

    def get_fieldmap_header(
            self, kh, kv, field_phase=None, polarization_name=None):
        if field_phase is None:
            field_phase_str = '--'
        else:
            field_phase_str = '{0:.0f}'.format(field_phase)

        if polarization_name is None:
            polarization_name = '--'

        device_name = self.name
        if device_name is None:
            device_name = '--'

        if self.gap is not None:
            gap_str = '{0:g}'.format(self.gap)
        else:
            gap_str = '--'

        timestamp = _time.strftime('%Y-%m-%d_%H-%M-%S', _time.localtime())

        k = (kh**2 + kv**2)**(1/2)

        header = []
        header.append('timestamp:\t{0:s}\n'.format(timestamp))
        header.append('magnet_name:\t{0:s}\n'.format(device_name))
        header.append('gap[mm]:\t{0:s}\n'.format(gap_str))
        header.append('period_length[mm]:\t{0:g}\n'.format(self.period_length))
        header.append('nr_periods:\t{0:d}\n'.format(self.nr_periods))
        header.append('polarization:\t{0:s}\n'.format(polarization_name))
        header.append('field_phase[deg]:\t{0:s}\n'.format(field_phase_str))
        header.append('K_Horizontal:\t{0:.1f}\n'.format(kh))
        header.append('K_Vertical:\t{0:.1f}\n'.format(kv))
        header.append('K:\t{0:.1f}\n'.format(k))
        header.append('\n')

        return header


class InsertionDeviceModel(
        _fieldsource.FieldModel, _fieldsource.SinusoidalFieldSource):
    """Insertion device model."""

    def __init__(
            self, nr_periods=None, period_length=None, gap=None, name=None,
            init_radia_object=True, **kwargs):
        _fieldsource.SinusoidalFieldSource.__init__(
            self, nr_periods=nr_periods, period_length=period_length)

        if gap <= 0:
            raise ValueError('gap must be > 0.')
        self._gap = gap
        self.name = name

        self._cassette_properties = kwargs
        self._cassettes = {}
        self._radia_object = None
        if init_radia_object:
            self.create_radia_object()

    @property
    def gap(self):
        """Magnetic gap [mm]."""
        return self._gap

    @property
    def cassettes(self):
        """Cassettes dictionary."""
        return _deepcopy(self._cassettes)

    @property
    def cassette_properties(self):
        """Common cassettes properties."""
        return self._cassette_properties

    @property
    def block_names_dict(self):
        name_dict = {}

        for key, value in self._cassettes.items():
            name_dict[key] = value.block_names

        return name_dict

    @property
    def magnetization_dict(self):
        mag_dict = {}

        for key, value in self._cassettes.items():
            mag_dict[key] = value.magnetization_list

        return mag_dict

    @property
    def position_err_dict(self):
        pos_err_dict = {}

        for key, value in self._cassettes.items():
            pos_err_dict[key] = value.position_err

        return pos_err_dict

    @property
    def state(self):
        data = {
            'nr_periods': self.nr_periods,
            'period_length': self.period_length,
            'gap': self.gap,
            'name': self.name,
            'block_names_dict': self.block_names_dict,
            'magnetization_dict': self.magnetization_dict,
            'position_err_dict': self.position_err_dict,
        }
        data.update(self.cassette_properties)
        return data

    @classmethod
    def load_state(cls, filename):
        """Load state from file."""
        with open(filename) as f:
            kwargs = _json.load(f)

        block_names_dict = kwargs.pop('block_names_dict', None)
        magnetization_dict = kwargs.pop('magnetization_dict', None)
        position_err_dict = kwargs.pop('position_err_dict', None)

        device = cls(init_radia_object=False, **kwargs)
        device.create_radia_object(
            block_names_dict=block_names_dict,
            magnetization_dict=magnetization_dict,
            position_err_dict=position_err_dict)

        return device

    def create_radia_object(self):
        raise NotImplementedError

    def get_fieldmap_header(
            self, kh, kv, field_phase=None, polarization_name=None):
        if field_phase is None:
            field_phase_str = '--'
        else:
            field_phase_str = '{0:.0f}'.format(field_phase)

        if polarization_name is None:
            polarization_name = '--'

        device_name = self.name
        if device_name is None:
            device_name = '--'

        if self.gap is not None:
            gap_str = '{0:g}'.format(self.gap)
        else:
            gap_str = '--'

        timestamp = _time.strftime('%Y-%m-%d_%H-%M-%S', _time.localtime())

        k = (kh**2 + kv**2)**(1/2)

        header = []
        header.append('timestamp:\t{0:s}\n'.format(timestamp))
        header.append('magnet_name:\t{0:s}\n'.format(device_name))
        header.append('gap[mm]:\t{0:s}\n'.format(gap_str))
        header.append('period_length[mm]:\t{0:g}\n'.format(self.period_length))
        header.append('nr_periods:\t{0:d}\n'.format(self.nr_periods))
        header.append('polarization:\t{0:s}\n'.format(polarization_name))
        header.append('field_phase[deg]:\t{0:s}\n'.format(field_phase_str))
        header.append('K_Horizontal:\t{0:.1f}\n'.format(kh))
        header.append('K_Vertical:\t{0:.1f}\n'.format(kv))
        header.append('K:\t{0:.1f}\n'.format(k))
        header.append('\n')

        return header

    def save_state(self, filename):
        """Save state to file."""
        with open(filename, 'w') as f:
            _json.dump(self.state, f)
        return True
