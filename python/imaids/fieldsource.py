
import numpy as _np
from scipy import integrate as _integrate
from scipy import interpolate as _interpolate
import radia as _rad

from . import utils as _utils


class FieldSource():
    """Field source class."""

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

    def calc_field_integrals(self, z_list, x=0, y=0, field_list=None):
        if field_list is not None:
            if len(field_list) != len(z_list):
                raise ValueError(
                    'Inconsistent length between field and position lists.')
        else:
            field_list = self.get_field(x=x, y=y, z=z_list)

        bx, by, bz = _np.transpose(field_list)

        z_list_m = _np.array(z_list)/1000
        ibx = _integrate.cumtrapz(bx, z_list_m, initial=0)
        iby = _integrate.cumtrapz(by, z_list_m, initial=0)
        ibz = _integrate.cumtrapz(bz, z_list_m, initial=0)
        iibx = _integrate.cumtrapz(ibx, z_list_m, initial=0)
        iiby = _integrate.cumtrapz(iby, z_list_m, initial=0)
        iibz = _integrate.cumtrapz(ibz, z_list_m, initial=0)

        ib = _np.transpose([ibx, iby, ibz])*1e6
        iib = _np.transpose([iibx, iiby, iibz])*1e5

        return ib, iib

    def calc_trajectory(
            self, energy, r0, zmax, rkstep, dz=0, on_axis_field=False):
        r1 = _np.zeros(6, dtype=float)
        r2 = _np.zeros(6, dtype=float)
        r3 = _np.zeros(6, dtype=float)

        beta, _, brho = _utils.calc_beam_parameters(energy)
        a = 1/brho/beta

        # from mm to m
        r = _np.array(r0, dtype=float)
        r[0] = r[0]/1000
        r[1] = r[1]/1000
        r[2] = (r[2] + dz)/1000
        step = rkstep/1000

        trajectory = []
        trajectory.append([
            r[0]*1000, r[1]*1000, r[2]*1000, r[3], r[4], r[5]
        ])

        while r[2] < zmax/1000:
            pos = [p*1000 for p in r[:3]]
            if on_axis_field:
                pos[0], pos[1] = 0, 0
            b = self.get_field_at_point(pos)
            drds1 = _utils.newton_lorentz_equation(a, r, b)
            r1 = r + (step/2)*drds1

            pos1 = [p*1000 for p in r1[:3]]
            if on_axis_field:
                pos1[0], pos1[1] = 0, 0
            b1 = self.get_field_at_point(pos1)
            drds2 = _utils.newton_lorentz_equation(a, r1, b1)
            r2 = r + (step/2)*drds2

            pos2 = [p*1000 for p in r2[:3]]
            if on_axis_field:
                pos2[0], pos2[1] = 0, 0
            b2 = self.get_field_at_point(pos2)
            drds3 = _utils.newton_lorentz_equation(a, r2, b2)
            r3 = r + step*drds3

            pos3 = [p*1000 for p in r3[:3]]
            if on_axis_field:
                pos3[0], pos3[1] = 0, 0
            b3 = self.get_field_at_point(pos3)
            drds4 = _utils.newton_lorentz_equation(a, r3, b3)

            r = r + (step/6)*(drds1 + 2*drds2 + 2*drds3 + drds4)

            trajectory.append([
                r[0]*1000, r[1]*1000, r[2]*1000, r[3], r[4], r[5]
            ])

        trajectory = _np.array(trajectory)

        return trajectory

    def get_field(self, x=0, y=0, z=0):
        if isinstance(x, (float, int)):
            x = [x]
        if isinstance(y, (float, int)):
            y = [y]
        if isinstance(z, (float, int)):
            z = [z]

        if sum([len(i) > 1 for i in [x, y, z]]) > 1:
            raise ValueError('Invalid position arguments.')

        if len(x) > 1:
            field = [self.get_field_at_point([xi, y, z]) for xi in x]
        elif len(y) > 1:
            field = [self.get_field_at_point([x, yi, z]) for yi in y]
        elif len(z) > 1:
            field = [self.get_field_at_point([x, y, zi]) for zi in z]
        else:
            field = [self.get_field_at_point([x, y, z])]

        return _np.array(field)

    def get_field_at_point(self, point):
        raise NotImplementedError

    def save_fieldmap(self, filename, x_list, y_list, z_list, header=None):
        if header is None:
            header = []

        if isinstance(x_list, (float, int)):
            x_list = [x_list]

        if isinstance(y_list, (float, int)):
            y_list = [y_list]

        if isinstance(z_list, (float, int)):
            z_list = [z_list]

        x_list = _np.round(x_list, decimals=8)
        y_list = _np.round(y_list, decimals=8)
        z_list = _np.round(z_list, decimals=8)

        with open(filename, 'w') as fieldmap:
            for line in header:
                fieldmap.write(line)

            fieldmap.write('X[mm]\tY[mm]\tZ[mm]\tBx[T]\tBy[T]\tBz[T]\n')
            fieldmap.write(
                '----------------------------------------' +
                '----------------------------------------' +
                '----------------------------------------' +
                '----------------------------------------\n')

            line_fmt = '{0:g}\t{1:g}\t{2:g}\t{3:g}\t{4:g}\t{5:g}\n'

            for z in z_list:
                for y in y_list:
                    for x in x_list:
                        bx, by, bz = self.get_field_at_point([x, y, z])
                        line = line_fmt.format(x, y, z, bx, by, bz)
                        fieldmap.write(line)

        return True

    def save_fieldmap_spectra(self, filename, x_list, y_list, z_list):
        if isinstance(x_list, (float, int)):
            x_list = [x_list]

        if isinstance(y_list, (float, int)):
            y_list = [y_list]

        if isinstance(z_list, (float, int)):
            z_list = [z_list]

        x_list = _np.round(x_list, decimals=8)
        y_list = _np.round(y_list, decimals=8)
        z_list = _np.round(z_list, decimals=8)

        nx = len(x_list)
        ny = len(y_list)
        nz = len(z_list)

        if len(x_list) == 1:
            xstep = 0
        else:
            xstep = x_list[1] - x_list[0]

        if len(y_list) == 1:
            ystep = 0
        else:
            ystep = y_list[1] - y_list[0]

        if len(z_list) == 1:
            zstep = 0
        else:
            zstep = z_list[1] - z_list[0]

        header_data = [xstep, ystep, zstep, nx, ny, nz]
        header = '{0:g} {1:g} {2:g} {3:d} {4:d} {5:d}\n'.format(*header_data)

        with open(filename, 'w') as fieldmap:
            fieldmap.write(header)

            line_fmt = '{0:g}\t{1:g}\t{2:g}\n'

            for x in x_list:
                for y in y_list:
                    for z in z_list:
                        bx, by, bz = self.get_field_at_point([x, y, z])
                        line = line_fmt.format(bx, by, bz)
                        fieldmap.write(line)

        return True

    def save_kickmap(
            self, filename, energy, x_list, y_list, zmin, zmax, rkstep):
        _, light_speed = _utils.get_constants()
        brho = energy*1e9/light_speed

        if isinstance(x_list, (float, int)):
            x_list = [x_list]

        if isinstance(y_list, (float, int)):
            y_list = [y_list]

        x_list = _np.round(x_list, decimals=8)
        y_list = _np.round(y_list, decimals=8)

        nx = len(x_list)
        ny = len(y_list)

        y_list_rev = y_list[::-1]

        extension = filename.split('.')[-1]
        filename_tmp = filename.replace(extension, 'tmp')
        with open(filename_tmp, '+a') as tmp:
            line = '\t'.join(['x', 'y', 'kx', 'ky', 'xf', 'yf'])
            tmp.write(line + '\n')

        kickx_map = _np.zeros([ny, nx])
        kicky_map = _np.zeros([ny, nx])
        finalx_map = _np.zeros([ny, nx])
        finaly_map = _np.zeros([ny, nx])

        for j in range(ny):
            yi = y_list_rev[j]
            for i in range(nx):
                xi = x_list[i]
                traj = self.calc_trajectory(
                    energy, [xi, yi, zmin, 0, 0, 1], zmax, rkstep)
                xf = traj[-1, 0]
                yf = traj[-1, 1]
                xl = traj[-1, 3]
                yl = traj[-1, 4]
                zl = traj[-1, 5]
                kickx = (xl/zl)*(brho**2)
                kicky = (yl/zl)*(brho**2)
                kickx_map[j, i] = kickx
                kicky_map[j, i] = kicky
                finalx_map[j, i] = xf/1000
                finaly_map[j, i] = yf/1000
                with open(filename_tmp, '+a') as tmp:
                    data = [xi, yi, kickx, kicky, xf/1000, yf/1000]
                    line = '\t'.join('{0:g}'.format(v) for v in data)
                    tmp.write(line + '\n')

        with open(filename, 'w') as kickmap:
            kickmap.write('# Author:Radia for Python User\n#\n')
            kickmap.write(
                '# Total Length of Longitudinal Interval [m]\n{0:g}\n'.format(
                    (zmax - zmin)/1000))
            kickmap.write('# Number of Horizontal Points \n{0:d}\n'.format(nx))
            kickmap.write('# Number of Vertical Points \n{0:d}\n'.format(ny))

            posx_str = '\t\t'
            posx_str += '\t'.join('{0:g}'.format(x/1000) for x in x_list)
            posx_str += '\n'

            kickmap.write('# Total Horizontal 2nd Order Kick [T2m2]\nSTART\n')
            kickmap.write(posx_str)
            for j in range(ny):
                line = '{0:g}\t'.format(y_list_rev[j]/1000)
                line += '\t'.join('{0:g}'.format(k) for k in kickx_map[j, :])
                line += '\n'
                kickmap.write(line)

            kickmap.write('# Total Vertical 2nd Order Kick [T2m2]\nSTART\n')
            kickmap.write(posx_str)
            for j in range(ny):
                line = '{0:g}\t'.format(y_list_rev[j]/1000)
                line += '\t'.join('{0:g}'.format(k) for k in kicky_map[j, :])
                line += '\n'
                kickmap.write(line)

            kickmap.write('# Horizontal Final Position [m]\nSTART\n')
            kickmap.write(posx_str)
            for j in range(ny):
                line = '{0:g}\t'.format(y_list_rev[j]/1000)
                line += '\t'.join('{0:g}'.format(k) for k in finalx_map[j, :])
                line += '\n'
                kickmap.write(line)

            kickmap.write('# Vertical Final Position [m]\nSTART\n')
            kickmap.write(posx_str)
            for j in range(ny):
                line = '{0:g}\t'.format(y_list_rev[j]/1000)
                line += '\t'.join('{0:g}'.format(k) for k in finaly_map[j, :])
                line += '\n'
                kickmap.write(line)

        return kickx_map, kicky_map, finalx_map, finaly_map

    def shift(self, value):
        raise NotImplementedError

    def rotate(self, point, vector, angle):
        raise NotImplementedError


class RadiaModel(FieldSource):

    def __init__(self, radia_object=None):
        self._radia_object = radia_object

    @property
    def radia_object(self):
        """Number of the radia object."""
        return self._radia_object

    def draw(self):
        if self._radia_object is None:
            return False

        _rad.ObjDrwAtr(self._radia_object, [0, 0.5, 1], 0.001)
        _rad.ObjDrwOpenGL(self._radia_object)
        return True

    def get_field_at_point(self, point):
        return _rad.Fld(self._radia_object, "b", point)

    def solve(self, prec=0.00001, max_iter=1000):
        return _rad.Solve(self._radia_object, prec, max_iter)

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


class FieldData(FieldSource):

    def __init__(self):
        self._filename = None
        self._raw_data = None
        self._nx = None
        self._ny = None
        self._nz = None
        self._px = None
        self._py = None
        self._pz = None
        self._bx = None
        self._by = None
        self._bz = None
        self._bx_func = None
        self._by_func = None
        self._bz_func = None

    @property
    def filename(self):
        return self._filename

    def _update_interpolation_functions(self):
        self._bx_func = _interpolate.RectBivariateSpline(
            self._px, self._pz, self._bx)
        self._by_func = _interpolate.RectBivariateSpline(
            self._px, self._pz, self._by)
        self._bz_func = _interpolate.RectBivariateSpline(
            self._px, self._pz, self._bz)
        return True

    def clear(self):
        self._filename = None
        self._raw_data = None
        self._nx = None
        self._ny = None
        self._nz = None
        self._px = None
        self._py = None
        self._pz = None
        self._bx = None
        self._by = None
        self._bz = None
        self._bx_func = None
        self._by_func = None
        self._bz_func = None

    def correct_angles(
            self, angxy=0.15, angxz=-0.21, angyx=-0.01,
            angyz=-0.02, angzx=0.01, angzy=-0.74):
        tmp_bx = _np.copy(self._bx)
        tmp_by = _np.copy(self._by)
        tmp_bz = _np.copy(self._bz)

        bxy = tmp_by*_np.sin(angxy*_np.pi/180)
        bxz = tmp_bz*_np.sin(angxz*_np.pi/180)
        self._bx = tmp_bx - bxy - bxz

        byx = tmp_bx*_np.sin(angyx*_np.pi/180)
        byz = tmp_bz*_np.sin(angyz*_np.pi/180)
        self._by = tmp_by - byx - byz

        bzx = tmp_bx*_np.sin(angzx*_np.pi/180)
        bzy = tmp_by*_np.sin(angzy*_np.pi/180)
        self._bz = tmp_bz - bzx - bzy

        self._update_interpolation_functions()

    def get_field_at_point(self, point):
        bx = self._bx_func(point[0], point[2])[0, 0]
        by = self._by_func(point[0], point[2])[0, 0]
        bz = self._bz_func(point[0], point[2])[0, 0]
        return [bx, by, bz]

    def shift(self, value):
        self._px += value[0]
        self._pz += value[2]
        self._update_interpolation_functions()

    def rotate(self, point, vector, angle):
        raise NotImplementedError

    def read_file(
            self, filename, header_size=2000, y=0, interpolation='linear'):
        self._filename = filename

        with open(self._filename, 'r') as f:
            data = f.read(header_size)

        idx = data.find('--------')
        skiprows = len(data[:idx].split('\n')) if idx != -1 else 0
        self._raw_data = _np.loadtxt(
            self._filename, skiprows=skiprows)

        px = self._raw_data[:, 0]
        py = self._raw_data[:, 1]
        pz = self._raw_data[:, 2]
        bx = self._raw_data[:, 3]
        by = self._raw_data[:, 4]
        bz = self._raw_data[:, 5]

        self._nx = len(_np.unique(px))
        self._ny = len(_np.unique(py))
        self._nz = len(_np.unique(pz))

        if self._ny > 1:
            filt = (py == y)
            bx = bx[filt]
            by = by[filt]
            bz = bz[filt]

        self._px = _np.unique(px)
        self._py = _np.unique(py)
        self._pz = _np.unique(pz)

        self._bx = _np.transpose(bx.reshape(self._nz, -1))
        self._by = _np.transpose(by.reshape(self._nz, -1))
        self._bz = _np.transpose(bz.reshape(self._nz, -1))

        self._update_interpolation_functions()

        return True
