
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import functions as _functions
from . import blocks as _blocks
from . import cassettes as _cassettes


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
    def bx_amp(self):
        return _functions.get_field_amplitude(
            self._radia_object, "bx", self._period_length, self._nr_periods)

    @property
    def by_amp(self):
        return _functions.get_field_amplitude(
            self._radia_object, "by", self._period_length, self._nr_periods)

    @property
    def deflection_parameter(self):
        kparam = _functions.calc_deflection_parameter(
            self.bx_amp, self.by_amp, self._period_length)
        return kparam

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

    def create_radia_object(
            self,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None):
        raise NotImplementedError

    def calc_field_integrals(self, *args, **kwargs):
        return _functions.calc_field_integrals(
            self._radia_object, *args, **kwargs)

    def calc_phase_error(self):
        return _functions.calc_phase_error()

    def calc_trajectory(self, *args, **kwargs):
        return _functions.calc_trajectory(
            self._radia_object, *args, **kwargs)

    def draw(self):
        return _functions.draw(self._radia_object)

    def get_field(self, *args, **kwargs):
        return _functions.get_field(self._radia_object, *args, **kwargs)

    def save_fieldmap(self, *args, **kwargs):
        return _functions.save_fieldmap(self._radia_object, *args, **kwargs)

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


class Delta(PMDevice):
    """Delta model."""

    def __init__(self, *args, **kwargs):
        """Create radia model."""
        self._dp = 0
        self._dcp = 0
        self._dgv = 0
        self._dgh = 0
        super().__init__(*args, **kwargs)

    @property
    def dp(self):
        """Phase displacement in mm."""
        return self._dp

    @dp.setter
    def dp(self, value):
        self.set_cassete_positions(dp=value)

    @property
    def dcp(self):
        """Opposite phase displacement in mm."""
        return self._dcp

    @dcp.setter
    def dcp(self, value):
        self.set_cassete_positions(dcp=value)

    @property
    def dgv(self):
        """Energy adjust (GV) in mm."""
        return self._dgv

    @dgv.setter
    def dgv(self, value):
        self.set_cassete_positions(dgv=value)

    @property
    def dgh(self):
        """Energy adjust (GH) in mm."""
        return self._dgh

    @dgh.setter
    def dgh(self, value):
        self.set_cassete_positions(dgh=value)

    @property
    def cassette_properties(self):
        """Common cassettes properties."""
        props = super().cassette_properties
        props['block_shape'] = self._block_shape
        return props

    def create_radia_object(
            self,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None):
        _rad.UtiDelAll()
        self._cassettes = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if horizontal_pos_err_dict is None:
            horizontal_pos_err_dict = {}

        if vertical_pos_err_dict is None:
            vertical_pos_err_dict = {}

        name = 'csd'
        csd = _cassettes.PMCassette(
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        csd.shift([0, -self._gap/2, 0])
        csd.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = csd

        name = 'cse'
        cse = _cassettes.PMCassette(
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cse.shift([0, -self._gap/2, 0])
        cse.rotate([0, 0, 0], [0, 0, 1], -_np.pi/2)
        self._cassettes[name] = cse

        name = 'cid'
        cid = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cid.shift([0, -self._gap/2, 0])
        cid.rotate([0, 0, 0], [0, 0, 1], _np.pi/2)
        self._cassettes[name] = cid

        name = 'cie'
        cie = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cie.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cie

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [csd, cse, cid, cie]])
        self.rotate([0, 0, 0], [0, 0, 1], -_np.pi/4)

    def set_cassete_positions(self, dp=None, dcp=None, dgv=None, dgh=None):
        """
        Change longitudinal cassette positions to adjust
        polarization and energy.
        """
        if dp is None:
            dp = self._dp

        if dcp is None:
            dcp = self._dcp

        if dgv is None:
            dgv = self._dgv

        if dgh is None:
            dgh = self._dgh

        csd = self._cassettes['csd']
        cse = self._cassettes['cse']
        cid = self._cassettes['cid']
        cie = self._cassettes['cie']

        csd_z = _np.array(_rad.ObjM(csd.radia_object))[:, 0, 2]
        csd_shift = - (_np.max(csd_z) + _np.min(csd_z))/2 + dgv

        cse_z = _np.array(_rad.ObjM(cse.radia_object))[:, 0, 2]
        cse_shift = - (
            _np.max(cse_z) + _np.min(cse_z))/2 + dgv + dgh + dp + dcp

        cid_z = _np.array(_rad.ObjM(cid.radia_object))[:, 0, 2]
        cid_shift = - (_np.max(cid_z) + _np.min(cid_z))/2 + dp - dcp

        cie_z = _np.array(_rad.ObjM(cie.radia_object))[:, 0, 2]
        cie_shift = - (_np.max(cie_z) + _np.min(cie_z))/2 + dgh

        csd.shift([0, 0, csd_shift])
        cse.shift([0, 0, cse_shift])
        cid.shift([0, 0, cid_shift])
        cie.shift([0, 0, cie_shift])

        self._dp = dp
        self._dcp = dcp
        self._dgv = dgv
        self._dgh = dgh
        return True


class AppleX(PMDevice):
    """AppleX model."""

    def __init__(self, *args, **kwargs):
        """Create radia model."""
        self._dp = 0
        self._dcp = 0
        self._dg = 0
        super().__init__(*args, **kwargs)

    @property
    def dp(self):
        """Phase displacement in mm."""
        return self._dp

    @dp.setter
    def dp(self, value):
        self.set_cassete_positions(dp=value)

    @property
    def dcp(self):
        """Opposite phase displacement in mm."""
        return self._dcp

    @dcp.setter
    def dcp(self, value):
        self.set_cassete_positions(dcp=value)

    @property
    def dg(self):
        """Energy adjust in mm."""
        return self._dg

    @dg.setter
    def dg(self, value):
        self.set_cassete_positions(dg=value)

    @property
    def cassette_properties(self):
        """Common cassettes properties."""
        props = super().cassette_properties
        props['block_shape'] = self._block_shape
        return props

    def create_radia_object(
            self,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None):
        _rad.UtiDelAll()
        self._cassettes = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if horizontal_pos_err_dict is None:
            horizontal_pos_err_dict = {}

        if vertical_pos_err_dict is None:
            vertical_pos_err_dict = {}

        name = 'csd'
        csd = _cassettes.PMCassette(
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        csd.shift([0, -self._gap/2, 0])
        csd.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = csd

        name = 'cse'
        cse = _cassettes.PMCassette(
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cse.shift([0, -self._gap/2, 0])
        cse.rotate([0, 0, 0], [0, 0, 1], -_np.pi/2)
        self._cassettes[name] = cse

        name = 'cid'
        cid = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cid.shift([0, -self._gap/2, 0])
        cid.rotate([0, 0, 0], [0, 0, 1], _np.pi/2)
        self._cassettes[name] = cid

        name = 'cie'
        cie = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cie.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cie

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [csd, cse, cid, cie]])
        self.rotate([0, 0, 0], [0, 0, 1], -_np.pi/4)

    def set_cassete_positions(self, dp=None, dcp=None, dg=None):
        """
        Change longitudinal cassette positions to adjust
        polarization and energy.
        """
        if dp is None:
            dp = self._dp

        if dcp is None:
            dcp = self._dcp

        if dg is None:
            dg = self._dg

        csd = self._cassettes['csd']
        cse = self._cassettes['cse']
        cid = self._cassettes['cid']
        cie = self._cassettes['cie']

        diff_dp = dp - self._dp
        diff_dcp = dcp - self._dcp
        diff_dg = dg - self._dg

        csd_shift = 0
        cse_shift = diff_dp + diff_dcp
        cid_shift = diff_dp - diff_dcp
        cie_shift = 0

        csd.shift([0, diff_dg/2, csd_shift])
        cse.shift([-diff_dg/2, 0, cse_shift])
        cid.shift([diff_dg/2, 0, cid_shift])
        cie.shift([0, -diff_dg/2, cie_shift])

        self._dp = dp
        self._dcp = dcp
        self._dg = dg
        return True


class AppleII(PMDevice):
    """AppleII model."""

    def __init__(self, *args, **kwargs):
        """Create radia model."""
        self._dp = 0
        self._dcp = 0
        self._dg = 0
        super().__init__(*args, **kwargs)

    @property
    def dp(self):
        """Phase displacement in mm."""
        return self._dp

    @dp.setter
    def dp(self, value):
        self.set_cassete_positions(dp=value)

    @property
    def dcp(self):
        """Opposite phase displacement in mm."""
        return self._dcp

    @dcp.setter
    def dcp(self, value):
        self.set_cassete_positions(dcp=value)

    @property
    def dg(self):
        """Gap oppening in mm."""
        return self._dg

    @dg.setter
    def dg(self, value):
        self.set_cassete_positions(dg=value)

    def create_radia_object(
            self,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None):
        _rad.UtiDelAll()
        self._cassettes = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if horizontal_pos_err_dict is None:
            horizontal_pos_err_dict = {}

        if vertical_pos_err_dict is None:
            vertical_pos_err_dict = {}

        if _utils.depth(self._block_shape) != 3:
            self._block_shape = [self._block_shape]

        mirror_block_shape = [
            [(-1)*pts[0], pts[1]] for shp in self._block_shape for pts in shp]

        name = 'csd'
        csd = _cassettes.PMCassette(
            block_shape=mirror_block_shape,
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        csd.shift([0, -self._gap/2, 0])
        csd.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = csd

        name = 'cse'
        cse = _cassettes.PMCassette(
            block_shape=self._block_shape,
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cse.shift([0, -self._gap/2, 0])
        cse.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cse

        name = 'cid'
        cid = _cassettes.PMCassette(
            block_shape=self._block_shape,
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cid.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cid

        name = 'cie'
        cie = _cassettes.PMCassette(
            block_shape=mirror_block_shape,
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cie.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cie

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [csd, cse, cid, cie]])

    def set_cassete_positions(self, dp=None, dcp=None, dg=None):
        """Change longitudinal cassette positions and gap."""
        if dp is None:
            dp = self._dp

        if dcp is None:
            dcp = self._dcp

        if dg is None:
            dg = self._dg

        csd = self._cassettes['csd']
        cse = self._cassettes['cse']
        cid = self._cassettes['cid']
        cie = self._cassettes['cie']

        diff_dp = dp - self._dp
        diff_dcp = dcp - self._dcp
        diff_dg = dg - self._dg
        csd_shift = 0
        cse_shift = diff_dp + diff_dcp
        cid_shift = diff_dp - diff_dcp
        cie_shift = 0

        csd.shift([0, diff_dg/2, csd_shift])
        cse.shift([0, diff_dg/2, cse_shift])
        cid.shift([0, -diff_dg/2, cid_shift])
        cie.shift([0, -diff_dg/2, cie_shift])

        self._dp = dp
        self._dcp = dcp
        self._dg = dg
        return True


class APU(PMDevice):
    """Adjustable phase undulador model."""

    def __init__(self, *args, **kwargs):
        """Create radia model."""
        self._dg = 0
        super().__init__(*args, **kwargs)

    @property
    def dg(self):
        """Longitudinal cassette displacement in mm."""
        return self._dg

    @dg.setter
    def dg(self, value):
        self.set_cassete_positions(dg=value)

    @property
    def cassette_properties(self):
        """Common cassettes properties."""
        props = super().cassette_properties
        props['block_shape'] = self._block_shape
        return props

    def create_radia_object(
            self,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None):
        _rad.UtiDelAll()
        self._cassettes = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if horizontal_pos_err_dict is None:
            horizontal_pos_err_dict = {}

        if vertical_pos_err_dict is None:
            vertical_pos_err_dict = {}

        name = 'cs'
        cs = _cassettes.PMCassette(
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        cs.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cs.shift([0, -self._gap/2, 0])
        cs.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cs

        name = 'ci'
        ci = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        ci.create_radia_object(
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        ci.shift([0, -self._gap/2, 0])
        self._cassettes[name] = ci

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [cs, ci]])

    def set_cassete_positions(self, dg=None):
        """Change longitudinal cassette position."""
        if dg is None:
            dg = self._dg

        diff_dg = dg - self._dg

        cs = self._cassettes['cs']
        cs.shift([0, 0, diff_dg])

        self._dg = dg
        return True


class DeltaPrototype(Delta):
    """Delta Prototype model."""

    def __init__(
            self, block_shape='default',
            nr_periods=60, period_length=20, gap=7, mr=1.36,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='delta_prototype', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'delta_prototype')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'delta_prototype')

        if start_blocks_length == 'default':
            start_blocks_length = None

        if start_blocks_distance == 'default':
            start_blocks_distance = None

        if end_blocks_length == 'default':
            end_blocks_length = None

        if end_blocks_distance == 'default':
            end_blocks_distance = None

        super().__init__(
            block_shape, nr_periods, period_length, gap, mr,
            block_subdivision=block_subdivision,
            rectangular_shape=rectangular_shape,
            block_distance=block_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class DeltaSabia(Delta):
    """Delta for Sirius Sabia beamline."""

    def __init__(
            self,
            block_shape='default', nr_periods=21,
            period_length=52.5, gap=13.6, mr=1.37,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.125,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='delta_sabia', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'delta_sabia')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'delta_sabia')

        block_len = period_length/4 - block_distance
        lenghts = [
            block_len/4, block_len/4, 3*block_len/4, 3*block_len/4, block_len]
        distances = [8.7, 2, 3.3, 1, block_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            block_shape, nr_periods, period_length, gap, mr,
            block_subdivision=block_subdivision,
            rectangular_shape=rectangular_shape,
            block_distance=block_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class Delta22(Delta):
    """Delta 22."""

    def __init__(
            self,
            block_shape='default', nr_periods=53,
            period_length=22, gap=7, mr=1.37,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='delta_22', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'delta_22')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'delta_22')

        block_len = period_length/4 - block_distance
        lenghts = [
            block_len/4, block_len/4, 3*block_len/4, 3*block_len/4, block_len]
        distances = [3.64, 0.84, 1.38, 0.42, block_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            block_shape, nr_periods, period_length, gap, mr,
            block_subdivision=block_subdivision,
            rectangular_shape=rectangular_shape,
            block_distance=block_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class TestUndulatorSabia(APU):
    """APU with the same blocks as Delta Sabia."""

    def __init__(
            self,
            block_shape='default', nr_periods=3,
            period_length=52.5, gap=13.6, mr=1.37,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.125,
            start_blocks_length=None, start_blocks_distance=None,
            end_blocks_length=None, end_blocks_distance=None,
            name='test_undulator_sabia', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'delta_sabia')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'delta_sabia')

        super().__init__(
            block_shape, nr_periods, period_length, gap, mr,
            block_subdivision=block_subdivision,
            rectangular_shape=rectangular_shape,
            block_distance=block_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class AppleXSabia(AppleX):
    """AppleX for Sirius Sabia beamline."""

    def __init__(
            self,
            block_shape='default', nr_periods=21,
            period_length=52.5, gap=13.6, mr=1.37,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.125,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='applex_sabia', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'delta_sabia')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'delta_sabia')

        block_len = period_length/4 - block_distance
        lenghts = [
            block_len/4, block_len/4, 3*block_len/4, 3*block_len/4, block_len]
        distances = [8.7, 2, 3.3, 1, block_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            block_shape, nr_periods, period_length, gap, mr,
            block_subdivision=block_subdivision,
            rectangular_shape=rectangular_shape,
            block_distance=block_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class AppleX22(AppleX):
    """AppleX 22."""

    def __init__(
            self,
            block_shape='default', nr_periods=53,
            period_length=22, gap=7, mr=1.37,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.05,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='applex_22', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'delta_22')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'delta_22')

        block_len = period_length/4 - block_distance
        lenghts = [
            block_len/4, block_len/4, 3*block_len/4, 3*block_len/4, block_len]
        distances = [3.64, 0.84, 1.38, 0.42, block_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            block_shape, nr_periods, period_length, gap, mr,
            block_subdivision=block_subdivision,
            rectangular_shape=rectangular_shape,
            block_distance=block_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class AppleIISabia(AppleII):
    """AppleII with same parameters as DeltaSabia."""

    def __init__(
            self, block_shape='default',
            nr_periods=21, period_length=52.5, gap=13.6, mr=1.37,
            block_subdivision='default',
            rectangular_shape=True, block_distance=0.125,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='apple_sabia', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'apple_sabia')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'apple_sabia')

        block_len = period_length/4 - block_distance
        lenghts = [block_len/4, block_len/2, 3*block_len/4, block_len]
        distances = [block_len/2, block_len/4, 0, block_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[::-1]

        super().__init__(
            block_shape, nr_periods, period_length, gap, mr,
            block_subdivision=block_subdivision,
            rectangular_shape=rectangular_shape,
            block_distance=block_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class Kyma22(APU):
    """Kyma commissioning undulador."""

    def __init__(
            self, block_shape='default',
            nr_periods=51, period_length=22, gap=8, mr=1.32,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='kyma_22', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'kyma_22')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'kyma_22')

        block_len = period_length/4 - block_distance
        lenghts = [
            block_len/2, 0, block_len, block_len/2,
            block_len, block_len]
        distances = [
            block_len/4, 0, block_len/4, block_len/4,
            block_distance, block_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            block_shape, nr_periods, period_length, gap, mr,
            block_subdivision=block_subdivision,
            rectangular_shape=rectangular_shape,
            block_distance=block_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)
