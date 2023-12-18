
import time as _time
import numpy as _np
import radia as _rad

from . import insertiondevice as _insertiondevice
from . import blocks as _blocks
from . import cassettes as _cassettes
from . import materials as _materials
from . import utils as _utils


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

    def create_radia_object(
            self,
            block_names_dict=None,
            magnetization_dict=None,
            position_err_dict=None):
        """Create Delta model radia object.

        Args:
            block_names_dict (dict, optional): Blocks names dictionary.
                Defaults to None.
            magnetization_dict (dict, optional): Blocks magnetization
                dictionary (in T). Defaults to None.
            position_err_dict (dict, optional): Blocks position errors
                dictionary (in mm). Defaults to None.
        """
        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if position_err_dict is None:
            position_err_dict = {}

        name = 'cse'
        cse = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cse.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        else:
            cse.shift([0, -self._gap/2, 0])
            cse.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cse

        name = 'csd'
        csd = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in csd.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], -_np.pi/2)
        else:
            csd.shift([0, -self._gap/2, 0])
            csd.rotate([0, 0, 0], [0, 0, 1], -_np.pi/2)
        self._cassettes[name] = csd

        name = 'cie'
        cie = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cie.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], _np.pi/2)
        else:
            cie.shift([0, -self._gap/2, 0])
            cie.rotate([0, 0, 0], [0, 0, 1], _np.pi/2)
        self._cassettes[name] = cie

        name = 'cid'
        cid = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cid.blocks:
                block.shift([0, -self._gap/2, 0])
        else:
            cid.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cid

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [csd, cse, cid, cie]])
        self.rotate([0, 0, 0], [0, 0, 1], -_np.pi/4)

    def set_cassete_positions(self, dp=None, dcp=None, dgv=None, dgh=None):
        """Change longitudinal cassette positions to adjust
        polarization and energy.

        Args:
            dp (float, optional): Phase displacement (in mm).
                Defaults to None.
            dcp (float, optional): Opposite phase displacement (in mm).
                Defaults to None.
            dgv (float, optional): Energy adjust (GV) (in mm).
                Defaults to None.
            dgh (float, optional): Energy adjust (GH) (in mm).
                Defaults to None.

        Returns:
            bool: True.
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
        """Get fieldmap header to save in file.

        Args:
            kh (float): Horizontal deflection parameter (in T.mm).
            kv (float): Vertical deflection parameter (in T.mm).
            field_phase (float): Field phase (in deg).
            polarization_name (str): Name of the polarization
                to save in file.

        Returns:
            list: List of strings containing the main parameters of the
                insertion device to use as a file's header.
        """
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

    def create_radia_object(
            self,
            block_names_dict=None,
            magnetization_dict=None,
            position_err_dict=None):
        """Create AppleX radia object.

        Args:
            block_names_dict (dict, optional): Blocks names dictionary.
                Defaults to None.
            magnetization_dict (dict, optional): Blocks magnetization
                dictionary (in T). Defaults to None.
            position_err_dict (dict, optional): Blocks position errors
                dictionary (in mm). Defaults to None.
        """
        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if position_err_dict is None:
            position_err_dict = {}

        name = 'cse'
        cse = _cassettes.Cassette(
            upper_cassette=True, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cse.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        else:
            cse.shift([0, -self._gap/2, 0])
            cse.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cse

        name = 'csd'
        csd = _cassettes.Cassette(
            upper_cassette=True, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in csd.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], -_np.pi/2)
        else:
            csd.shift([0, -self._gap/2, 0])
            csd.rotate([0, 0, 0], [0, 0, 1], -_np.pi/2)
        self._cassettes[name] = csd

        name = 'cie'
        cie = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cie.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], _np.pi/2)
        else:
            cie.shift([0, -self._gap/2, 0])
            cie.rotate([0, 0, 0], [0, 0, 1], _np.pi/2)
        self._cassettes[name] = cie

        name = 'cid'
        cid = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cid.blocks:
                block.shift([0, -self._gap/2, 0])
        else:
            cid.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cid

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [csd, cse, cid, cie]])
        self.rotate([0, 0, 0], [0, 0, 1], -_np.pi/4)

    def set_cassete_positions(self, dp=None, dcp=None, dg=None):
        """Change longitudinal cassette positions to adjust
        polarization and energy.

        Args:
            dp (float, optional): Phase displacement (in mm).
                Defaults to None.
            dcp (float, optional): Opposite phase displacement (in mm).
                Defaults to None.
            dg (float, optional): Energy adjust (in mm).
                Defaults to None.

        Returns:
            bool: True.
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
        """Get fieldmap header to save in file.

        Args:
            kh (float): Horizontal deflection parameter (in T.mm).
            kv (float): Vertical deflection parameter (in T.mm).
            field_phase (float): Field phase (in deg).
            polarization_name (str): Name of the polarization
                to save in file.

        Returns:
            list: List of strings containing the main parameters of the
                insertion device to use as a file's header.
        """
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
            position_err_dict=None):
        """Create AppleII radia object.

        Args:
            block_names_dict (dict, optional): Blocks names dictionary.
                Defaults to None.
            magnetization_dict (dict, optional): Blocks magnetization
                dictionary (in T). Defaults to None.
            position_err_dict (dict, optional): Blocks position errors
                dictionary (in mm). Defaults to None.
        """
        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if position_err_dict is None:
            position_err_dict = {}

        name = 'cse'
        cse = _cassettes.Cassette(
            upper_cassette=True, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cse.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cse.blocks:
                block.shift([0, -self._gap/2, self.dp + self.dcp])
                block.mirror([0, 0, 0], [1, 0, 0])
                block.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        else:
            cse.shift([0, -self._gap/2, self.dp + self.dcp])
            cse.mirror([0, 0, 0], [1, 0, 0])
            cse.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cse

        name = 'csd'
        csd = _cassettes.Cassette(
            upper_cassette=True, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        csd.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in csd.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        else:
            csd.shift([0, -self._gap/2, 0])
            csd.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = csd

        name = 'cie'
        cie = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cie.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cie.blocks:
                block.shift([0, -self._gap/2, 0])
        else:
            cie.shift([0, -self._gap/2, 0])
        self._cassettes[name] = cie

        name = 'cid'
        cid = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cid.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cid.blocks:
                block.shift([0, -self._gap/2, self.dp - self.dcp])
                block.mirror([0, 0, 0], [1, 0, 0])
        else:
            cid.shift([0, -self._gap/2, self.dp - self.dcp])
            cid.mirror([0, 0, 0], [1, 0, 0])
        self._cassettes[name] = cid

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [csd, cse, cid, cie]])

    def set_cassete_positions(self, dp=None, dcp=None, dg=None):
        """Change longitudinal cassette positions and gap.

        Args:
            dp (float, optional): Phase displacement (in mm).
                Defaults to None.
            dcp (float, optional): Opposite phase displacement (in mm).
                Defaults to None.
            dg (float, optional): Energy adjust (in mm).
                Defaults to None.

        Returns:
            bool: True.
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
        cse.shift([0, diff_dg/2, cse_shift])
        cid.shift([0, -diff_dg/2, cid_shift])
        cie.shift([0, -diff_dg/2, cie_shift])

        self._dp = dp
        self._dcp = dcp
        self._dg = dg
        return True


class APU(_insertiondevice.InsertionDeviceModel):
    """Adjustable phase undulador model."""

    def __init__(self, cs_block_shape=None,
                       ci_block_shape=None, *args, **kwargs):
        """Create radia model."""
        self._dg = 0
        self._cs_block_shape = cs_block_shape
        self._ci_block_shape = ci_block_shape
        super().__init__(*args, **kwargs)

    @property
    def dg(self):
        """Longitudinal cassette displacement in mm."""
        return self._dg

    @property
    def cs_block_shape(self):
        """Superior cassette block shape."""
        return self._cs_block_shape

    @property
    def ci_block_shape(self):
        """Inferior cassette block shape."""
        return self._ci_block_shape

    @dg.setter
    def dg(self, value):
        self.set_cassete_positions(dg=value)

    def create_radia_object(
            self,
            block_names_dict=None,
            magnetization_dict=None,
            position_err_dict=None):
        """Create APU radia model.

        Args:
            block_names_dict (dict, optional): Blocks names dictionary.
                Defaults to None.
            magnetization_dict (dict, optional): Blocks magnetization
                dictionary (in T). Defaults to None.
            position_err_dict (dict, optional): Blocks position errors
                dictionary (in mm). Defaults to None.
        """
        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if position_err_dict is None:
            position_err_dict = {}

        name = 'cs'
        if self.cs_block_shape is not None:
            self.cs_cassette_properties = self.cassette_properties.copy()
            self.cs_cassette_properties['block_shape'] = self.cs_block_shape
        else:
            self.cs_cassette_properties = self.cassette_properties
        cs = _cassettes.Cassette(
            upper_cassette=True, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cs_cassette_properties)
        cs.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cs.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        else:
            cs.shift([0, -self._gap/2, 0])
            cs.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cs

        name = 'ci'
        if self.ci_block_shape is not None:
            self.ci_cassette_properties = self.cassette_properties.copy()
            self.ci_cassette_properties['block_shape'] = self.ci_block_shape
        else:
            self.ci_cassette_properties = self.cassette_properties
        ci = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.ci_cassette_properties)
        ci.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in ci.blocks:
                block.shift([0, -self._gap/2, 0])
        else:
            ci.shift([0, -self._gap/2, 0])
        self._cassettes[name] = ci

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [cs, ci]])

    def set_cassete_positions(self, dg=None):
        """Change longitudinal cassette position.

        Args:
            dg (float, optional): Energy adjust (in mm).
                Defaults to None.

        Returns:
            bool: True.
        """
        if dg is None:
            dg = self._dg

        diff_dg = dg - self._dg

        cs = self._cassettes['cs']
        cs.shift([0, 0, diff_dg])

        self._dg = dg
        return True


class Planar(_insertiondevice.InsertionDeviceModel):
    """Planar undulador model."""

    def __init__(self, *args, **kwargs):
        """Create radia model."""
        self._dg = 0
        super().__init__(*args, **kwargs)

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
            position_err_dict=None):
        """Create Planar radia model.

        Args:
            block_names_dict (dict, optional): Blocks names dictionary.
                Defaults to None.
            magnetization_dict (dict, optional): Blocks magnetization
                dictionary (in T). Defaults to None.
            position_err_dict (dict, optional): Blocks position errors
                dictionary (in mm). Defaults to None.
        """
        self._cassettes = {}

        if block_names_dict is None:
            block_names_dict = {}

        if magnetization_dict is None:
            magnetization_dict = {}

        if position_err_dict is None:
            position_err_dict = {}

        name = 'cs'
        cs = _cassettes.Cassette(
            upper_cassette=True, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        cs.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in cs.blocks:
                block.shift([0, -self._gap/2, 0])
                block.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        else:
            cs.shift([0, -self._gap/2, 0])
            cs.rotate([0, 0, 0], [0, 0, 1], _np.pi)
        self._cassettes[name] = cs

        name = 'ci'
        ci = _cassettes.Cassette(
            upper_cassette=False, name=name,
            nr_periods=self.nr_periods, period_length=self.period_length,
            init_radia_object=False, **self.cassette_properties)
        ci.create_radia_object(
            block_names=block_names_dict.get(name),
            magnetization_list=magnetization_dict.get(name),
            position_err=position_err_dict.get(name))
        if self.trf_on_blocks:
            for block in ci.blocks:
                block.shift([0, -self._gap/2, 0])
        else:
            ci.shift([0, -self._gap/2, 0])
        self._cassettes[name] = ci

        self._radia_object = _rad.ObjCnt(
            [c.radia_object for c in [cs, ci]])

    def set_cassete_positions(self, dg=None):
        """Change longitudinal cassette position.

        Args:
            dg (float, optional): Energy adjust (in mm).
                Defaults to None.

        Returns:
            bool: True.
        """
        if dg is None:
            dg = self._dg

        diff_dg = dg - self._dg

        cs = self._cassettes['cs']
        cs.shift([0, diff_dg/2, 0])

        ci = self._cassettes['ci']
        ci.shift([0, -diff_dg/2, 0])

        self._dg = dg
        return True


class DeltaPrototype(Delta):
    """Delta Prototype model."""

    def __init__(
            self, block_shape='default',
            nr_periods=60, period_length=20, gap=7, mr=1.36,
            block_subdivision='default',
            rectangular=False, longitudinal_distance=0,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='delta_prototype', **kwargs):
        """Create Delta Prototype model.

        Args:
            block_shape (str or list, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 60.
            period_length (int or float, optional): Period length (in mm).
                Defaults to 20.
            gap (int or float, optional): Insertion device magnetic gap
                (in mm). Defaults to 7.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.36.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (int or float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'delta_prototype'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'delta_prototype')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
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
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
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
            rectangular=False, longitudinal_distance=0.125,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='delta_sabia', **kwargs):
        """Create Delta Sabia beamline model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 21.
            period_length (float, optional): Period length (in mm).
                Defaults to 52.5.
            gap (float, optional): Insertion device magnetic gap
                (in mm). Defaults to 13.6.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.39.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.125.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'delta_sabia'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'delta_sabia')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'delta_sabia')

        block_len = period_length/4 - longitudinal_distance
        lenghts = [
            block_len/4, block_len/4, 3*block_len/4, 3*block_len/4, block_len]
        distances = [8.4, 2, 3.3, 1, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
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
            period_length=22, gap=7, mr=1.37,
            block_subdivision='default',
            rectangular=False, longitudinal_distance=0.05,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='delta_carnauba', **kwargs):
        """Create Delta Carnauba beamline model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 52.
            period_length (int or float, optional): Period length (in mm).
                Defaults to 22.
            gap (int or float, optional): Insertion device magnetic gap
                (in mm). Defaults to 7.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.37.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.05.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'delta_carnauba'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'delta_carnauba')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'delta_carnauba')

        block_len = period_length/4 - longitudinal_distance
        tlen = _np.round(block_len/4, decimals=2)
        lenghts = _np.round(
            [tlen, tlen, 3*tlen, 3*tlen, block_len], decimals=2).tolist()
        distances = [2.9, 1.5, 1.8, 0.4, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
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
            rectangular=False, longitudinal_distance=0.125,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='applex_sabia', **kwargs):
        """Create AppleX Sabia beamline model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 21.
            period_length (float, optional): Period length (in mm).
                Defaults to 52.5.
            gap (float, optional): Insertion device magnetic gap
                (in mm). Defaults to 13.6.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.39.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.125.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'applex_sabia'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'delta_sabia')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'delta_sabia')

        block_len = period_length/4 - longitudinal_distance
        lenghts = [
            block_len/4, block_len/4, 3*block_len/4, 3*block_len/4, block_len]
        distances = [8.7, 2, 3.3, 1, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
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
            rectangular=False, longitudinal_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='applex_carnauba', **kwargs):
        """Create AppleX Carnauba beamline model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 53.
            period_length (int or float, optional): Period length (in mm).
                Defaults to 22.
            gap (int or float, optional): Insertion device magnetic gap
                (in mm). Defaults to 7.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.39.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.1.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'applex_carnauba'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'delta_carnauba')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'delta_carnauba')

        block_len = period_length/4 - longitudinal_distance
        lenghts = [
            block_len/4, block_len/4, 3*block_len/4, 3*block_len/4, block_len]
        distances = [3.64, 0.84, 1.38, 0.42, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class AppleIISabia(AppleII):
    """AppleII with same parameters as DeltaSabia."""

    def __init__(
            self, block_shape='default',
            nr_periods=21, period_length=52.5, gap=8, mr=1.32,
            block_subdivision='default',
            rectangular=True, longitudinal_distance=0.125,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='apple_sabia', **kwargs):
        """Create AppleII with same parameters as DeltaSabia model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 21.
            period_length (float, optional): Period length (in mm).
                Defaults to 52.5.
            gap (float, optional): Insertion device magnetic gap
                (in mm). Defaults to 13.6.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.39.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to True.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.125.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'apple_sabia'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'apple_sabia')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'apple_sabia')

        block_len = period_length/4 - longitudinal_distance
        lenghts = [block_len/4, block_len/2, 3*block_len/4, block_len]
        distances = [block_len/2, block_len/4, 0, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
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
            rectangular=False, longitudinal_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='apple_carnauba', **kwargs):
        """Create AppleII with same parameters as DeltaCarnauba.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 53.
            period_length (int or float, optional): Period length (in mm).
                Defaults to 22.
            gap (int or float, optional): Insertion device magnetic gap
                (in mm). Defaults to 7.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.39.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.1.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'apple_carnauba'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'apple_carnauba')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'apple_carnauba')

        block_len = period_length/4 - longitudinal_distance
        lenghts = [block_len/4, block_len/2, 3*block_len/4, block_len]
        distances = [block_len/2, block_len/4, 0, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
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
            rectangular=False, longitudinal_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='kyma_22', **kwargs):
        """Create Kyma22 model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 51.
            period_length (int or float, optional): Period length (in mm).
                Defaults to 22.
            gap (int or float, optional): Insertion device magnetic gap
                (in mm). Defaults to 8.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.32.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.1.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'kyma_22'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'kyma_22')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'kyma_22')

        block_len = period_length/4 - longitudinal_distance
        lenghts = [
            block_len/2, block_len, block_len/2,
            block_len, block_len]
        distances = [
            block_len/4, block_len/4, block_len/4,
            longitudinal_distance, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class Kyma58(APU):
    """Kyma commissioning undulador."""

    def __init__(
            self, block_shape='default',
            nr_periods=18, period_length=58, gap=15.8, mr=1.32,
            block_subdivision='default',
            rectangular=False, longitudinal_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='kyma_58', **kwargs):
        """Create Kyma58 model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 18.
            period_length (int or float, optional): Period length (in mm).
                Defaults to 58.
            gap (float, optional): Insertion device magnetic gap
                (in mm). Defaults to 15.8.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.32.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.1.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'kyma_58'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'kyma_58')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'kyma_58')

        block_len = period_length/4 - longitudinal_distance
        lenghts = [
            block_len/2, block_len, block_len/2,
            block_len, block_len]
        distances = [
            block_len/4, block_len/4, block_len/4,
            longitudinal_distance, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class PAPU(APU):
    """Prototype Adjustable Phase Undulador model."""

    def __init__(
            self, block_shape='default',
            nr_periods=18, period_length=50.0, gap=24.0, mr=1.22,
            block_subdivision='default',
            rectangular=False, longitudinal_distance=0.2,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='PAPU', **kwargs):

        """Create PAPU model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 50.
            period_length (int or float, optional): Period length (in mm).
                Defaults to 50.0.
            gap (float, optional): Insertion device magnetic gap
                (in mm). Defaults to 8.0.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.25.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.2.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'PAPU'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape('papu')
            block_shape_flip = _blocks.Block.get_predefined_shape('papu_flip')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                                                                        'papu')

        block_len = period_length/4 - longitudinal_distance
        lenghts = [block_len/4, block_len/4, block_len/4,
                   block_len/4, block_len/4, block_len/4, block_len]
        distances = [6, 0, 2.4, 1, 0, 0.2, 0.2]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            cs_block_shape=block_shape_flip, ci_block_shape=block_shape,
            mr=mr, gap=gap, nr_periods=nr_periods,
            period_length=period_length,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)

        magnetizations = _np.array(
              [[0,mr,0],
               [0,0,-mr], [0,0,-mr],
               [0,-mr,0], [0,-mr,0], [0,-mr,0],
               [0,0,mr]]
            + nr_periods*[[0,mr,0], [0,0,-mr],
                          [0,-mr,0], [0,0,mr]]
            + [[0,mr,0], [0,mr,0], [0,mr,0],
               [0,0,-mr], [0,0,-mr],
               [0,-mr,0]])
        # In the APU implementation, the superior cassette is the one
        # created by rotation of the inferior cassette around (0,0,1).
        magnetization_dict = {'cs': -1*magnetizations, 'ci': magnetizations}

        block_names = {'cs':[f'block_{n:02d}' for n in range(4*nr_periods+13)],
                       'ci':[f'block_{n:02d}' for n in range(4*nr_periods+13)]}

        self.create_radia_object(
                    magnetization_dict=magnetization_dict,
                    block_names_dict=block_names)

        self.shift([-1.7, 0, 0])


class HybridAPU(APU):
    """Hybrid APU undulador."""

    def __init__(
            self, block_shape='default',
            nr_periods=10, period_length=19.9, gap=5.2, mr=1.34,
            block_subdivision='default', hybrid=True,
            pole_shape='default', pole_length='default',
            pole_material='default', pole_subdivision='default',
            rectangular=False, longitudinal_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='hybrid_planar', **kwargs):
        """Create Hybrid APU model.

        Args:
            block_shape (str or list, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 10.
            period_length (float, optional): Period length (in mm).
                Defaults to 19.9.
            gap (float, optional): Insertion device magnetic gap
                (in mm). Defaults to 5.2.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.34.
           block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            hybrid (bool, optional): If True, creates a hybrid device.
                Defaults to True.
            pole_shape (str or list, optional): List of points [x, y] to
                create poles shape (in mm). Defaults to 'default'.
            pole_length (str or float, optional): Pole longitudinal length
                (in mm). Defaults to 'default'.
            pole_material (str or imaids.materials, optional): Material object
                to apply to pole. Defaults to 'default'.
            pole_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subpole in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.1.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'hybrid_planar'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'hybrid_block')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'hybrid_block')

        if pole_shape == 'default':
            pole_shape = _blocks.Block.get_predefined_shape(
                'hybrid_pole')

        if pole_subdivision == 'default':
            pole_subdivision = _blocks.Block.get_predefined_subdivision(
                'hybrid_pole')

        if pole_material == 'default':
            pole_material = _materials.VanadiumPermendur()

        if pole_length == 'default':
            pole_length = _utils.hybrid_undulator_pole_length(
                gap, period_length)

        block_len = (
            period_length/2 - pole_length - 2*longitudinal_distance)

        lenghts = [block_len/2, pole_length/2, block_len]
        distances = [pole_length, pole_length, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
            hybrid=hybrid,
            pole_shape=pole_shape,
            pole_length=pole_length,
            pole_material=pole_material,
            pole_subdivision=pole_subdivision,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class HybridPlanar(Planar):
    """Hybrid planar undulador."""

    def __init__(
            self, block_shape='default',
            nr_periods=10, period_length=19.9, gap=5.2, mr=1.34,
            block_subdivision='default', hybrid=True,
            pole_shape='default', pole_length='default',
            pole_material='default', pole_subdivision='default',
            rectangular=False, longitudinal_distance=0.1,
            start_blocks_length='default', start_blocks_distance='default',
            end_blocks_length='default', end_blocks_distance='default',
            name='hybrid_planar', **kwargs):
        """Create Hybrid planar model.

        Args:
            block_shape (str or list, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 10.
            period_length (float, optional): Period length (in mm).
                Defaults to 19.9.
            gap (float, optional): Insertion device magnetic gap
                (in mm). Defaults to 5.2.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.34.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            hybrid (bool, optional): If True, creates a hybrid device.
                Defaults to True.
            pole_shape (str or list, optional): List of points [x, y] to
                create poles shape (in mm). Defaults to 'default'.
            pole_length (str or float, optional): Pole longitudinal length
                (in mm). Defaults to 'default'.
            pole_material (str or imaids.materials, optional): Material object
                to apply to pole. Defaults to 'default'.
            pole_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subpole in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.1.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to 'default'.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to 'default'.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to 'default'.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to 'default'.
            name (str, optional): Insertion device name.
                Defaults to 'hybrid_planar'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'hybrid_block')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'hybrid_block')

        if pole_shape == 'default':
            pole_shape = _blocks.Block.get_predefined_shape(
                'hybrid_pole')

        if pole_subdivision == 'default':
            pole_subdivision = _blocks.Block.get_predefined_subdivision(
                'hybrid_pole')

        if pole_material == 'default':
            pole_material = _materials.VanadiumPermendur()

        if pole_length == 'default':
            pole_length = _utils.hybrid_undulator_pole_length(
                gap, period_length)

        block_len = (
            period_length/2 - pole_length - 2*longitudinal_distance)

        lenghts = [block_len/2, pole_length/2, block_len]
        distances = [pole_length, pole_length, longitudinal_distance]

        if start_blocks_length == 'default':
            start_blocks_length = lenghts

        if start_blocks_distance == 'default':
            start_blocks_distance = distances

        if end_blocks_length == 'default':
            end_blocks_length = lenghts[0:-1][::-1]

        if end_blocks_distance == 'default':
            end_blocks_distance = distances[0:-1][::-1]

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
            hybrid=hybrid,
            pole_shape=pole_shape,
            pole_length=pole_length,
            pole_material=pole_material,
            pole_subdivision=pole_subdivision,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)


class MiniPlanarSabia(Planar):
    """Planar undulator with the same blocks as Delta Sabia."""

    def __init__(
            self,
            block_shape='default', nr_periods=3,
            period_length=52.5, gap=13.6, mr=1.39,
            block_subdivision='default',
            rectangular=False, longitudinal_distance=0.125,
            start_blocks_length=None, start_blocks_distance=None,
            end_blocks_length=None, end_blocks_distance=None,
            name='mini_planar_sabia', **kwargs):
        """Create Mini planar with the same blocks as Delta Sabia model.

        Args:
            block_shape (str, optional): List of points [x, y] to
                create blocks shape (in mm). Defaults to 'default'.
            nr_periods (int, optional): Number of complete periods.
                Defaults to 3.
            period_length (float, optional): Period length (in mm).
                Defaults to 52.5.
            gap (float, optional): Insertion device magnetic gap
                (in mm). Defaults to 13.6.
            mr (float, optional): Remanent magnetization (in T).
                Defaults to 1.39.
            block_subdivision (str or list, optional): List specifying
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z]. Defaults to 'default'.
            rectangular (bool, optional): If True, create model with
                rectangular blocks. Defaults to False.
            longitudinal_distance (float, optional): Longitunal
                distance between blocks (in mm). Defaults to 0.125.
            start_blocks_length (str or list, optional): List of block lengths
                in the start of the cassette (in mm). Defaults to None.
            start_blocks_distance (str or list, optional): List of distance
                between blocks in the start of the cassette (in mm).
                Defaults to None.
            end_blocks_length (str or list, optional): List of block lengths
                in the end of the cassette (in mm). Defaults to None.
            end_blocks_distance (str or list, optional): List of distance
                between blocks in the end of the cassette (in mm).
                Defaults to None.
            name (str, optional): Insertion device name.
                Defaults to 'mini_planar_sabia'.
        """

        if block_shape == 'default':
            block_shape = _blocks.Block.get_predefined_shape(
                'delta_sabia')

        if block_subdivision == 'default':
            block_subdivision = _blocks.Block.get_predefined_subdivision(
                'delta_sabia')

        super().__init__(
            nr_periods=nr_periods, period_length=period_length,
            gap=gap, mr=mr, block_shape=block_shape,
            block_subdivision=block_subdivision,
            rectangular=rectangular,
            longitudinal_distance=longitudinal_distance,
            start_blocks_length=start_blocks_length,
            start_blocks_distance=start_blocks_distance,
            end_blocks_length=end_blocks_length,
            end_blocks_distance=end_blocks_distance,
            name=name, **kwargs)
