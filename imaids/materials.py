
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad


mu0 = 4*_np.pi*1e-7


class Material():
    """Magnetic material."""

    def __init__(
            self, linear=True, mr=1.37,
            ksipar=0.06, ksiper=0.17,
            hlist=None, mlist=None,
            init_radia_object=True, name=''):

        self._linear = linear
        self._mr = mr
        self._ksipar = ksipar
        self._ksiper = ksiper
        self._hlist = list(hlist) if hlist is not None else None
        self._mlist = list(mlist) if mlist is not None else None
        self.name = name

        self._radia_object = None
        if init_radia_object:
            self.create_radia_object()

    def __str__(self):
        """Printable string representation of the object."""
        fmtstr = '{0:<18s} : {1}\n'
        r = ''
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                name = key[1:]
            else:
                name = key
            r += fmtstr.format(name, str(value))
        return r

    @property
    def linear(self):
        """True if the material is linear, False otherwise."""
        return self._linear

    @property
    def mr(self):
        """Block remanent magnetization [T]."""
        return self._mr

    @property
    def ksipar(self):
        """Parallel magnetic susceptibility."""
        return self._ksipar

    @property
    def ksiper(self):
        """Perpendicular magnetic susceptibility."""
        return self._ksiper

    @property
    def hlist(self):
        return _deepcopy(self._hlist)

    @property
    def mlist(self):
        return _deepcopy(self._mlist)

    @property
    def radia_object(self):
        return self._radia_object

    @property
    def state(self):
        data = {
            'linear': self.linear,
            'mr': self.mr,
            'ksipar': self.ksipar,
            'ksiper': self.ksiper,
            'hlist': self.hlist,
            'mlist': self.mlist,
            'name': self.name,
        }
        return data

    @classmethod
    def load_state(cls, filename):
        """Load state from file."""
        with open(filename) as f:
            kwargs = _json.load(f)
        return cls(init_radia_object=True, **kwargs)

    def create_radia_object(self):
        if self.linear:
            self._radia_object = _rad.MatLin(
                [self.ksipar, self.ksiper], self.mr)
        else:
            self._radia_object = _rad.MatSatIsoTab(
                _np.transpose([self.hlist, self.mlist]).tolist())

    def save_state(self, filename):
        """Save state to file."""
        with open(filename, 'w') as f:
            _json.dump(self.state, f)
        return True


class NdFeB(Material):

    def __init__(
            self, linear=True, mr=1.37,
            ksipar=0.06, ksiper=0.17,
            name='ndfeb', **kwargs):
        super().__init__(
            linear=linear, mr=mr,
            ksipar=ksipar, ksiper=ksiper,
            name=name, **kwargs)



class VanadiumPermendur(Material):

    def __init__(
            self, linear=False, hlist='default',
            mlist='default', name='iron', **kwargs):
        _h = [
            0.0,
            71.4,
            119.0,
            175.0,
            268.0,
            493.0,
            804.0,
            1910.0,
            4775.0,
            15120.0,
            42971.0,
            79577.0,
        ]
        _b = [
            0.00,
            0.60,
            1.00,
            1.60,
            1.80,
            2.00,
            2.10,
            2.20,
            2.26,
            2.30,
            2.34,
            2.39,
        ]

        if hlist == 'default':
            hlist = _np.array(_h)*mu0

        if mlist == 'default':
            mlist = _np.array(_b) - _np.array(_h)*mu0

        super().__init__(
            linear=linear, hlist=hlist, mlist=mlist,
            name=name, **kwargs)
