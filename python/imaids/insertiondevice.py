
import time as _time
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np

from . import utils as _utils
from . import fieldsource as _fieldsource


class InsertionDevice(_fieldsource.FieldSource):
    """Base class for insertion devices model and data."""

    def __init__(self):
        self._nr_periods = None
        self._period_length = None
        self._gap = None
        self.name = ''

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

    def calc_avg_period_length(
            self, z_list, field_list=None, x=0, y=0,
            period_length_guess=20, maxfev=5000, prominence=1):
        if field_list is None:
            field_list = self.get_field(x=x, y=y, z=z_list)

        freq_guess = 2*_np.pi/period_length_guess
        amp, _ = _utils.calc_cosine_amplitude(
            z_list, field_list, freq_guess, maxfev=maxfev)

        idx_max = _np.argmax(amp)
        idx_peaks_valleys = _utils.find_peaks_and_valleys(
            field_list[:, idx_max], prominence=prominence)

        dz = _np.diff(z_list[idx_peaks_valleys])
        avg_period_length = _np.mean(dz)*2
        nr_periods = int(len(dz)/2)
        return avg_period_length, nr_periods

    def calc_field_amplitude(
            self, z_list=None, field_list=None,
            x=0, y=0, npts_per_period=101, maxfev=5000):
        if self.nr_periods > 1:
            zmin = -self._period_length*(self.nr_periods - 1)/2
            zmax = self._period_length*(self.nr_periods - 1)/2
            znpts = npts_per_period*(self.nr_periods-1)
        else:
            zmin = -self.period_length/2
            zmax = self.period_length/2
            znpts = npts_per_period

        if z_list is not None and field_list is not None:
            z_list = _np.array(z_list)
            field_list = _np.array(field_list)

            cond = (z_list >= zmin) & (z_list <= zmax)
            z_list = z_list[cond]
            field_list = field_list[cond]

        else:
            z_list = _np.linspace(zmin, zmax, znpts)
            field_list = self.get_field(x=x, y=y, z=z_list)

        freq_guess = 2*_np.pi/self.period_length
        amp, phase = _utils.calc_cosine_amplitude(
            z_list, field_list, freq_guess, maxfev=maxfev)

        bx_amp = amp[0]
        by_amp = amp[1]
        bz_amp = amp[2]
        bxy_phase = (phase[0] - phase[1]) % _np.pi

        return bx_amp, by_amp, bz_amp, bxy_phase

    def calc_deflection_parameter(self, bx_amp, by_amp):
        kh = 0.934*by_amp*(self.period_length/10)
        kv = 0.934*bx_amp*(self.period_length/10)
        return kh, kv

    def calc_trajectory_length(self, trajectory):
        traj_pos = trajectory[:, 0:3]
        traj_diff = _np.diff(traj_pos, axis=0)
        traj_len = _np.append(
            0, _np.cumsum(_np.sqrt(_np.sum(traj_diff**2, axis=1))))
        return traj_len

    def calc_radiation_phase(self, energy, trajectory, wavelength):
        beta, *_ = _utils.calc_beam_parameters(energy)
        traj_z = trajectory[:, 2]
        traj_len = self.calc_trajectory_length(trajectory)
        return (2*_np.pi/(wavelength))*(traj_len/beta - (traj_z - traj_z[0]))

    def calc_radiation_wavelength(
            self, energy, bx_amp, by_amp, harmonic=1):
        _, gamma, _ = _utils.calc_beam_parameters(energy)
        kh, kv = self.calc_deflection_parameter(bx_amp, by_amp)
        wl = (self.period_length/(2*harmonic*(gamma**2)))*(
            1 + (kh**2 + kv**2)/2)
        return wl

    def calc_phase_error(
            self, energy, trajectory, bx_amp, by_amp,
            skip_poles=0, zmin=None, zmax=None):
        if by_amp >= bx_amp:
            z_list = _utils.find_zeros(trajectory[:, 2], trajectory[:, 3])
        else:
            z_list = _utils.find_zeros(trajectory[:, 2], trajectory[:, 4])

        if zmin is not None:
            z_list = z_list[z_list >= zmin]

        if zmax is not None:
            z_list = z_list[z_list <= zmax]

        if skip_poles != 0:
            z_list = z_list[skip_poles:-skip_poles]

        wavelength = self.calc_radiation_wavelength(
            energy, bx_amp, by_amp, harmonic=1)
        phase = self.calc_radiation_phase(energy, trajectory, wavelength)
        phase_poles = _np.interp(z_list, trajectory[:, 2], phase)

        coeffs = _np.polynomial.polynomial.polyfit(z_list, phase_poles, 1)
        phase_fit = _np.polynomial.polynomial.polyval(z_list, coeffs)
        phase_error = phase_poles - phase_fit

        phase_error_rms = _np.sqrt(_np.mean(phase_error**2))

        return z_list, phase_error, phase_error_rms

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

    def get_filename(
            self, date, x_list, y_list, z_list, kh, kv,
            polarization_name=None, add_label=None,
            file_extension='.fld'):
        filename = '{0:s}'.format(date)

        if isinstance(x_list, (float, int)):
            x_list = [x_list]

        if isinstance(y_list, (float, int)):
            y_list = [y_list]

        if isinstance(z_list, (float, int)):
            z_list = [z_list]

        x_list = _np.round(x_list, decimals=8)
        y_list = _np.round(y_list, decimals=8)
        z_list = _np.round(z_list, decimals=8)

        device_name = self.name
        if device_name is not None:
            filename += '_' + device_name

        if polarization_name is not None:
            filename += '_' + polarization_name

        filename += '_Kh={0:.1f}_Kv={1:.1f}'.format(kh, kv)

        if add_label is not None:
            filename += '_' + add_label

        if len(x_list) > 1:
            filename += '_X={0:g}_{1:g}mm'.format(x_list[0], x_list[-1])

        if len(y_list) > 1:
            filename += '_Y={0:g}_{1:g}mm'.format(y_list[0], y_list[-1])

        if len(z_list) > 1:
            filename += '_Z={0:g}_{1:g}mm'.format(z_list[0], z_list[-1])

        filename += file_extension

        return filename


class InsertionDeviceData(_fieldsource.FieldData, InsertionDevice):
    """Insertion device field data."""

    def __init__(self):
        self._nr_periods = None
        self._period_length = None
        self._gap = None
        self.name = ''
        _fieldsource.FieldData.__init__(self)

    @property
    def nr_periods(self):
        """Number of complete periods."""
        if self._nr_periods is None and self._filename is not None:
            period_length, nr_periods = self.calc_avg_period_length(self._pz)
            self._period_length = period_length
            self._nr_periods = nr_periods
        return self._nr_periods

    @property
    def period_length(self):
        """Period length [mm]."""
        if self._period_length is None and self._filename is not None:
            period_length, nr_periods = self.calc_avg_period_length(self._pz)
            self._period_length = period_length
            self._nr_periods = nr_periods
        return self._period_length


class InsertionDeviceModel(_fieldsource.RadiaModel, InsertionDevice):
    """Permanent magnet insertion device model."""

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

        block_names_dict = kwargs.pop('block_names_dict', None)
        magnetization_dict = kwargs.pop('magnetization_dict', None)
        horizontal_pos_err_dict = kwargs.pop('horizontal_pos_err_dict', None)
        vertical_pos_err_dict = kwargs.pop('vertical_pos_err_dict', None)

        device = cls(init_radia_object=False, **kwargs)
        device.create_radia_object(
            block_names_dict=block_names_dict,
            magnetization_dict=magnetization_dict,
            horizontal_pos_err_dict=horizontal_pos_err_dict,
            vertical_pos_err_dict=vertical_pos_err_dict)

        return device

    def create_radia_object(self):
        raise NotImplementedError

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
            'block_names_dict': self.block_names_dict,
            'magnetization_dict': self.magnetization_dict,
            'horizontal_pos_err_dict': horizontal_pos_err_dict,
            'vertical_pos_err_dict': vertical_pos_err_dict,
        }

        with open(filename, 'w') as f:
            _json.dump(data, f)

        return True
