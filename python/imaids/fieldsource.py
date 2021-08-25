
import radia as _rad

from . import functions as _functions


class FieldSource():
    """Field source class."""

    def __init__(self, radia_object=None):
        self._radia_object = radia_object

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
    def radia_object(self):
        """Number of the radia object."""
        return self._radia_object

    def calc_field_integrals(self, *args, **kwargs):
        return _functions.calc_field_integrals(
            self._radia_object, *args, **kwargs)

    def calc_trajectory(self, *args, **kwargs):
        return _functions.calc_trajectory(
            self._radia_object, *args, **kwargs)

    def draw(self):
        if self._radia_object is not None:
            return _functions.draw(self._radia_object)
        else:
            return False

    def get_field(self, *args, **kwargs):
        return _functions.get_field(self._radia_object, *args, **kwargs)

    def save_fieldmap(self, *args, **kwargs):
        return _functions.save_fieldmap(self._radia_object, *args, **kwargs)

    def save_fieldmap_spectra(self, *args, **kwargs):
        return _functions.save_fieldmap_spectra(
            self._radia_object, *args, **kwargs)

    def save_kickmap(self, *args, **kwargs):
        return _functions.save_kickmap(self._radia_object, *args, **kwargs)

    def solve(self, *args, **kwargs):
        return _functions.solve(self._radia_object, *args, **kwargs)

    def shift(self, value):
        if self._radia_object is not None:
            self._radia_object = _rad.TrfOrnt(
                self._radia_object, _rad.TrfTrsl(value))
            return True
        else:
            return False

    def rotate(self, point, vector, angle):
        if self._radia_object is not None:
            self._radia_object = _rad.TrfOrnt(
                self._radia_object, _rad.TrfRot(point, vector, angle))
            return True
        else:
            return False
