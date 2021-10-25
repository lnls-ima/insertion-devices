
import time as _time
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import insertiondevice as _insertiondevice
from . import blocks as _blocks
from . import cassettes as _cassettes


class Delta(_insertiondevice.InsertionDeviceModel):
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
            block_names_dict=None,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None, delete_all=True):
        if delete_all:
            _rad.UtiDelAll()

        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if horizontal_pos_err_dict is None:
            horizontal_pos_err_dict = {}

        if vertical_pos_err_dict is None:
            vertical_pos_err_dict = {}

        name = 'cse'
        cse = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cse.shift([0, -self._gap/2, 0])
        cse.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cse

        name = 'csd'
        csd = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        csd.shift([0, -self._gap/2, 0])
        csd.rotate([0, 0, 0], [0, 0, 1], -_np.pi/2)
        self._cassettes[name] = csd

        name = 'cie'
        cie = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cie.shift([0, -self._gap/2, 0])
        cie.rotate([0, 0, 0], [0, 0, 1], _np.pi/2)
        self._cassettes[name] = cie

        name = 'cid'
        cid = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cid.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cid

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

    def get_fieldmap_header(
            self, kh, kv, field_phase, polarization_name):
        if polarization_name == '':
            polarization_name = '--'

        timestamp = _time.strftime('%Y-%m-%d_%H-%M-%S', _time.localtime())

        device_name = self.name
        if device_name == '':
            device_name = '--'

        pos_csd = self.dgv
        pos_cse = self.dgv + self.dgh + self.dp + self.dcp
        pos_cie = self.dgh
        pos_cid = self.dp - self.dcp

        k = (kh**2 + kv**2)**(1/2)

        header = []
        header.append('timestamp:\t{0:s}\n'.format(timestamp))
        header.append('magnet_name:\t{0:s}\n'.format(device_name))
        header.append('gap[mm]:\t{0:g}\n'.format(self.gap))
        header.append('period_length[mm]:\t{0:g}\n'.format(self.period_length))
        header.append('magnet_length[mm]:\t{0:g}\n'.format(self.device_length))
        header.append('dP[mm]:\t{0:g}\n'.format(self.dp))
        header.append('dCP[mm]:\t{0:g}\n'.format(self.dcp))
        header.append('dGV[mm]:\t{0:g}\n'.format(self.dgv))
        header.append('dGH[mm]:\t{0:g}\n'.format(self.dgh))
        header.append('posCSD[mm]:\t{0:g}\n'.format(pos_csd))
        header.append('posCSE[mm]:\t{0:g}\n'.format(pos_cse))
        header.append('posCID[mm]:\t{0:g}\n'.format(pos_cid))
        header.append('posCIE[mm]:\t{0:g}\n'.format(pos_cie))
        header.append('polarization:\t{0:s}\n'.format(polarization_name))
        header.append('field_phase[deg]:\t{0:.0f}\n'.format(field_phase))
        header.append('K_Horizontal:\t{0:.1f}\n'.format(kh))
        header.append('K_Vertical:\t{0:.1f}\n'.format(kv))
        header.append('K:\t{0:.1f}\n'.format(k))
        header.append('\n')

        return header


class AppleX(_insertiondevice.InsertionDeviceModel):
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
            block_names_dict=None,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None, delete_all=True):
        if delete_all:
            _rad.UtiDelAll()

        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if horizontal_pos_err_dict is None:
            horizontal_pos_err_dict = {}

        if vertical_pos_err_dict is None:
            vertical_pos_err_dict = {}

        name = 'cse'
        cse = _cassettes.PMCassette(
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cse.shift([0, -self._gap/2, 0])
        cse.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cse

        name = 'csd'
        csd = _cassettes.PMCassette(
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        csd.shift([0, -self._gap/2, 0])
        csd.rotate([0, 0, 0], [0, 0, 1], -_np.pi/2)
        self._cassettes[name] = csd

        name = 'cie'
        cie = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cie.shift([0, -self._gap/2, 0])
        cie.rotate([0, 0, 0], [0, 0, 1], _np.pi/2)
        self._cassettes[name] = cie

        name = 'cid'
        cid = _cassettes.PMCassette(
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cid.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cid

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

    def get_fieldmap_header(
            self, kh, kv, field_phase, polarization_name):
        if polarization_name == '':
            polarization_name = '--'

        timestamp = _time.strftime('%Y-%m-%d_%H-%M-%S', _time.localtime())

        device_name = self.name
        if device_name == '':
            device_name = '--'

        pos_csd = 0
        pos_cse = self.dp + self.dcp
        pos_cie = 0
        pos_cid = self.dp - self.dcp

        k = (kh**2 + kv**2)**(1/2)

        header = []
        header.append('timestamp:\t{0:s}\n'.format(timestamp))
        header.append('magnet_name:\t{0:s}\n'.format(device_name))
        header.append('gap[mm]:\t{0:g}\n'.format(self.gap))
        header.append('period_length[mm]:\t{0:g}\n'.format(self.period_length))
        header.append('magnet_length[mm]:\t{0:g}\n'.format(self.device_length))
        header.append('dP[mm]:\t{0:g}\n'.format(self.dp))
        header.append('dCP[mm]:\t{0:g}\n'.format(self.dcp))
        header.append('dG[mm]:\t{0:g}\n'.format(self.dg))
        header.append('posCSD[mm]:\t{0:g}\n'.format(pos_csd))
        header.append('posCSE[mm]:\t{0:g}\n'.format(pos_cse))
        header.append('posCID[mm]:\t{0:g}\n'.format(pos_cid))
        header.append('posCIE[mm]:\t{0:g}\n'.format(pos_cie))
        header.append('polarization:\t{0:s}\n'.format(polarization_name))
        header.append('field_phase[deg]:\t{0:.0f}\n'.format(field_phase))
        header.append('K_Horizontal:\t{0:.1f}\n'.format(kh))
        header.append('K_Vertical:\t{0:.1f}\n'.format(kv))
        header.append('K:\t{0:.1f}\n'.format(k))
        header.append('\n')

        return header


class AppleII(_insertiondevice.InsertionDeviceModel):
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
            block_names_dict=None,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None, delete_all=True):
        if delete_all:
            _rad.UtiDelAll()

        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

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

        name = 'cse'
        cse = _cassettes.PMCassette(
            block_shape=mirror_block_shape,
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cse.shift([0, -self._gap/2, 0])
        cse.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cse

        name = 'csd'
        csd = _cassettes.PMCassette(
            block_shape=self._block_shape,
            upper_cassette=True, name=name,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        csd.shift([0, -self._gap/2, 0])
        csd.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = csd

        name = 'cie'
        cie = _cassettes.PMCassette(
            block_shape=self._block_shape,
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cie.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cie

        name = 'cid'
        cid = _cassettes.PMCassette(
            block_shape=mirror_block_shape,
            upper_cassette=False, name=name,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            horizontal_pos_err=horizontal_pos_err_dict.get(name),
            vertical_pos_err=vertical_pos_err_dict.get(name))
        cid.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cid

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


class APU(_insertiondevice.InsertionDeviceModel):
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
            block_names_dict=None,
            magnetization_dict=None,
            horizontal_pos_err_dict=None,
            vertical_pos_err_dict=None, delete_all=True):
        if delete_all:
            _rad.UtiDelAll()

        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

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
            block_names=block_names_dict.get(name),
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
            block_names=block_names_dict.get(name),
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
            period_length=52.5, gap=13.6, mr=1.39,
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
        distances = [8.4, 2, 3.3, 1, block_distance]

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


class DeltaCarnauba(Delta):
    """Delta Carnauba."""

    def __init__(
            self,
            block_shape='default', nr_periods=52,
            period_length=22, gap=7, mr=1.39,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.05,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='delta_carnauba', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'delta_carnauba')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'delta_carnauba')

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


class AppleXSabia(AppleX):
    """AppleX for Sirius Sabia beamline."""

    def __init__(
            self,
            block_shape='default', nr_periods=21,
            period_length=52.5, gap=13.6, mr=1.39,
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


class AppleXCarnauba(AppleX):
    """AppleX Carnauba."""

    def __init__(
            self,
            block_shape='default', nr_periods=53,
            period_length=22, gap=7, mr=1.39,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='applex_carnauba', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'delta_carnauba')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'delta_carnauba')

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
            nr_periods=21, period_length=52.5, gap=13.6, mr=1.39,
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


class AppleIICarnauba(AppleII):
    """AppleII with same parameters as DeltaCarnauba."""

    def __init__(
            self,
            block_shape='default', nr_periods=53,
            period_length=22, gap=7, mr=1.39,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='apple_carnauba', **kwargs):

        if block_shape == 'default':
            block_shape = _blocks.PMBlock.get_predefined_shape(
                'apple_carnauba')

        if block_subdivision == 'default':
            block_subdivision = _blocks.PMBlock.get_predefined_subdivision(
                'apple_carnauba')

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


class MiniPlanarSabia(APU):
    """APU with the same blocks as Delta Sabia."""

    def __init__(
            self,
            block_shape='default', nr_periods=3,
            period_length=52.5, gap=13.6, mr=1.39,
            block_subdivision='default',
            rectangular_shape=False, block_distance=0.125,
            start_blocks_length=None, start_blocks_distance=None,
            end_blocks_length=None, end_blocks_distance=None,
            name='mini_planar_sabia', **kwargs):

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
