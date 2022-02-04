
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
            klist=None, mlist=None,
            init_radia_object=True, name=''):

        self._linear = linear
        self._mr = mr
        self._ksipar = ksipar
        self._ksiper = ksiper
        self._klist = list(klist) if klist is not None else None
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
    def klist(self):
        return _deepcopy(self._klist)

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
            'klist': self.klist,
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
                _np.transpose([self.klist, self.mlist]).tolist())

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


class Iron(Material):

    def __init__(
            self, linear=False, klist='default',
            mlist='default', name='iron', **kwargs):
        iron_h = [
            0.8, 1.5, 2.2, 3.6, 5, 6.8, 9.8, 18, 28,
            37.5, 42, 55, 71.5, 80, 85, 88, 92, 100,
            120, 150, 200, 300, 400, 600, 800, 1000,
            2000, 4000, 6000, 10000, 25000, 40000]
        iron_m = [
            0.000998995, 0.00199812, 0.00299724,
            0.00499548, 0.00699372, 0.00999145,
            0.0149877, 0.0299774, 0.0499648, 0.0799529,
            0.0999472, 0.199931, 0.49991, 0.799899, 0.999893,
            1.09989, 1.19988, 1.29987, 1.41985, 1.49981,
            1.59975, 1.72962, 1.7995, 1.89925, 1.96899,
            1.99874,  2.09749, 2.19497, 2.24246, 2.27743,
            2.28958, 2.28973]

        if klist == 'default':
            klist = _np.array(iron_h)*mu0

        if mlist == 'default':
            mlist = iron_m

        super().__init__(
            linear=linear, klist=klist, mlist=mlist,
            name=name, **kwargs)


class Permendur(Material):

    def __init__(
            self, linear=False, klist='default',
            mlist='default', name='permendur', **kwargs):
        permendur_h = [
            1.01040000e+00,
            2.03005312e+02,
            2.22913049e+02,
            2.43491638e+02,
            2.72807126e+02,
            3.19224408e+02,
            3.91729364e+02,
            4.95351181e+02,
            6.34832700e+02,
            8.22597280e+02,
            1.08094594e+03,
            1.43885757e+03,
            1.92626020e+03,
            2.57757203e+03,
            3.45515665e+03,
            4.69605131e+03,
            6.61839266e+03,
            1.00456446e+04,
            1.73835508e+04,
            3.42331679e+04]
        permendur_m = [
            0,
            0.585315598,
            0.865625605,
            1.033316775,
            1.165471494,
            1.278133069,
            1.378005711,
            1.468654074,
            1.552242092,
            1.630200393,
            1.703533209,
            1.772977569,
            1.839093362,
            1.902317766,
            1.962999893,
            2.021423791,
            2.077824248,
            2.132397988,
            2.185311783,
            2.236708474]

        if klist == 'default':
            klist = _np.array(permendur_h)*mu0

        if mlist == 'default':
            mlist = permendur_m

        super().__init__(
            linear=linear, klist=klist, mlist=mlist,
            name=name, **kwargs)
