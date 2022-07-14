
from copy import deepcopy as _deepcopy
try:
    import importlib.resources as _resources
except ModuleNotFoundError:
    import importlib_resources as _resources
import pathlib as _pathlib
import json as _json
import numpy as _np
import radia as _rad


mu0 = 4*_np.pi*1e-7


class Material():
    """Magnetic materials base class."""

    def __init__(
            self, linear=True, mr=1.37,
            ksipar=0.06, ksiper=0.17,
            hlist=None, mlist=None, name=''):
        """Initializes attributes and executes Radia object creation method.        

        Args:
            linear (bool, optional): If True the object is create using the
                radia fuction MatLin. If False the object is create using
                the radia function MatSatIsoTab. Defaults to True.
            mr (float, optional): magnitude of the remanent magnetization
                vector in Tesla. Used for creating Radia Object when
                linear==True. Defaults to 1.37.
                    Direction of the remanent magnetization is not set for the
                    material, but defined by the initial magnetization vector
                    of the object to which the material is applyed
                    (if mr<0, remanent vector is antiparallel to the provided
                    magnetization for the object using the material).
            ksipar (float, optional): magnetic susceptibility value parallel 
                to easy magnetization axis. Used for creating Radia Object when
                linear==True. Defaults to 0.06.
            ksiper (float, optional): magnetic susceptibility value
                perpendicular to easy magnetization axis. Used for creating
                Radia Object when linear==True. Defaults to 0.17.
                    The easy magnetization axis is defined by the direction of
                    the remanent magnetization vector, explained above.
            hlist (list, optional): field strength H values in Tesla, of
                the M versus H curve for a nonlinear isotropic magnetic 
                material. Used for creating Radia Object when
                linear==False. Defaults to None.
            mlist (list, optional): magnetization M values in Tesla, of the 
                M versus H curve for a nonlinear isotropic magnetic material.
                Used for creating Radia Object when linear==False.
                Defaults to None.
            name (str, optional): Material name. Defaults to ''.
        """
        self._linear = linear
        self._mr = mr
        self._ksipar = ksipar
        self._ksiper = ksiper
        self._hlist = list(hlist) if hlist is not None else None
        self._mlist = list(mlist) if mlist is not None else None
        self.name = name

        self._radia_object = None
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
        """Remanent magnetization magnitude [T]."""
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
        """H values of MxH curve for nonlinear isotropic material [T]"""
        return _deepcopy(self._hlist)

    @property
    def mlist(self):
        """M values of MxH curve for nonlinear isotropic material [T]"""
        return _deepcopy(self._mlist)

    @property
    def radia_object(self):
        """int value referencing Radia object."""
        return self._radia_object

    @property
    def state(self):
        """Dictionary storing attribute values"""
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
    def load_state(cls, filename, **kwargs):
        """Create Material object from state file in .json format.

        Args:
            filename (str): Path to file.
            **kwargs: Keyword arguments passed to Material initialization,
                will override only correspondent values read from state file.
        
        Returns:
            Material: New object created with attribute
                values read from input file.   
        """
        with open(filename) as f:
            file_kwargs = _json.load(f)

        file_kwargs.update(kwargs)

        return cls(**file_kwargs)


    @classmethod
    def preset(cls, presetname, **kwargs):
        """Create Material object from preset.
        
        Presets are built-in .json state files.
        Available options may be consulted by the call:
            materials.Material.dir_presets()

        Args:
            presetname (str): Preset name.       
            **kwargs: Keyword arguments passed to Material initialization,
                will override only correspondent values read from preset state.
        
        Returns:
            Material: New object created with attribute
                values read from preset.        
        """

        with _resources.path(__package__, 'presets') as p:
            presetfile = p / (presetname + '.json')

        return cls.load_state(presetfile, **kwargs)

    
    @staticmethod
    def dir_presets():
        """List of available material presets.        
    
        Returns:
            list: Available .json material presets on repository. 
        """
        with _resources.path(__package__, 'presets') as p:
            presets = [f.stem for f in p.glob('*.json')]
        
        return presets


    def create_radia_object(self):
        """Creates the radia object."""
        if self.linear:
            self._radia_object = _rad.MatLin(
                [self.ksipar, self.ksiper], self.mr)
        else:
            self._radia_object = _rad.MatSatIsoTab(
                _np.transpose([self.hlist, self.mlist]).tolist())

    def save_state(self, filename):
        """Save state to file.

        Args:
            filename (str): path to file.

        Returns:
            bool: returns True if the state was save to file.
        """
        with open(filename, 'w') as f:
            _json.dump(self.state, f)
        return True


class NdFeB(Material):
    """Material class derivate with NdFeB values as default
    
       LEGACY FUNCTION - use Material.preset('NdFeB') instead
    """
    def __init__(
            self, linear=True, mr=1.37,
            ksipar=0.06, ksiper=0.17,
            name='ndfeb', **kwargs):
        """Initializes Material attributes.

        Args:
            linear (bool, optional): Defaults to True.
            mr (float, optional): Defaults to 1.37.
            ksipar (float, optional): Defaults to 0.06.
            ksiper (float, optional): Defaults to 0.17.
            name (str, optional): Defaults to 'ndfeb'.
            kwargs: Keyword arguments passed to Material initialization.
        """
        super().__init__(
            linear=linear, mr=mr,
            ksipar=ksipar, ksiper=ksiper,
            name=name, **kwargs)


class VanadiumPermendur(Material):
    """Material class derivate with VanadiumPermendur values as default
    
       LEGACY FUNCTION - use Material.preset('VanadiumPermendur') instead
    """
    def __init__(
            self, linear=False, hlist='default',
            mlist='default', name='iron', **kwargs):
        """Initializes Material attributes.      

        Args:
            linear (bool, optional): Defaults to False.
            hlist (str or list, optional): If hlist=='default', default list
            for VanadiumPermendur will be used. Otherwise, hlist must be
            list-like. Defaults to 'default'.
            mlist (list, optional):  If mlist=='default', default list
            for VanadiumPermendur will be used. Otherwise, hlist must be
            list-like. Defaults to 'default'.
            name (str, optional): Material name. Defaults to 'iron'.
            kwargs: Keyword arguments passed to Material initialization.
        """
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
