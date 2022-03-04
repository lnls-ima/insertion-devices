
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

    @staticmethod
    def find_peaks(data, prominence=0.05):
        return _utils.find_peaks(data, prominence=prominence)

    @staticmethod
    def find_valleys(data, prominence=0.05):
        return _utils.find_valleys(data, prominence=prominence)

    @staticmethod
    def find_peaks_and_valleys(data, prominence=0.05):
        return _utils.find_peaks_and_valleys(data, prominence=prominence)

    @staticmethod
    def find_zeros(pos, data):
        return _utils.find_zeros(pos, data)

    @staticmethod
    def delete_all():
        return _utils.delete_all()

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

    def mirror(self, point, normal):
        raise NotImplementedError


class SinusoidalFieldSource(FieldSource):
    """Sinusoidal field source."""

    def __init__(self, nr_periods=None, period_length=None):
        if nr_periods is not None and nr_periods <= 0:
            raise ValueError('nr_periods must be > 0.')

        if period_length is not None and period_length <= 0:
            raise ValueError('period_length must be > 0.')

        self._nr_periods = nr_periods
        self._period_length = period_length

    @property
    def nr_periods(self):
        """Number of complete periods."""
        return self._nr_periods

    @property
    def period_length(self):
        """Period length [mm]."""
        return self._period_length

    @staticmethod
    def calc_cosine_amplitude(z_list, field_list, freq_guess, maxfev=5000):
        return _utils.calc_cosine_amplitude(
            z_list, field_list, freq_guess, maxfev=maxfev)

    def calc_avg_period_length(
            self, z_list, field_list=None, x=0, y=0,
            period_length_guess=20, maxfev=5000, prominence=1):
        if field_list is None:
            field_list = self.get_field(x=x, y=y, z=z_list)

        freq_guess = 2*_np.pi/period_length_guess
        amp, _ = self.calc_cosine_amplitude(
            z_list, field_list, freq_guess, maxfev=maxfev)

        idx_max = _np.argmax(amp)
        idx_peaks_valleys = self.find_peaks_and_valleys(
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
        amp, phase = self.calc_cosine_amplitude(
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

    def calc_trajectory_avg_over_period(self, trajectory):
        trajz = [t for t in trajectory[:, 2]]
        step = trajz[1] - trajz[0]
        navg = int(self.period_length/step)

        avgtrajx = _np.convolve(
            trajectory[:, 0], _np.ones(navg)/navg, mode='same')
        avgtrajy = _np.convolve(
            trajectory[:, 1], _np.ones(navg)/navg, mode='same')

        trajz = trajz[navg:-navg]
        avgtrajx = avgtrajx[navg:-navg]
        avgtrajy = avgtrajy[navg:-navg]
        avgtraj = _np.transpose([avgtrajx, avgtrajy, trajz])
        return avgtraj

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
            z_list = self.find_zeros(trajectory[:, 2], trajectory[:, 3])
        else:
            z_list = self.find_zeros(trajectory[:, 2], trajectory[:, 4])

        if zmin is not None:
            z_list = z_list[z_list >= zmin]

        if zmax is not None:
            z_list = z_list[z_list <= zmax]

        if skip_poles != 0:
            z_list = z_list[skip_poles:-(skip_poles-1)]

        wavelength = self.calc_radiation_wavelength(
            energy, bx_amp, by_amp, harmonic=1)
        phase = self.calc_radiation_phase(energy, trajectory, wavelength)
        phase_poles = _np.interp(z_list, trajectory[:, 2], phase)

        coeffs = _np.polynomial.polynomial.polyfit(z_list, phase_poles, 1)
        phase_fit = _np.polynomial.polynomial.polyval(z_list, coeffs)
        phase_error = phase_poles - phase_fit

        phase_error_rms = _np.sqrt(_np.mean(phase_error**2))

        return z_list, phase_error, phase_error_rms

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


class FieldModel(FieldSource):

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

    def mirror(self, point, normal):
        if self._radia_object is not None:
            self._radia_object = _rad.TrfOrnt(
                self._radia_object, _rad.TrfPlSym(point, normal))
            return True
        else:
            return False


class FieldData(FieldSource):

    def __init__(self, filename=None, raw_data=None, selected_y=0):
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
        if filename is not None:
            self.read_file(filename, selected_y=selected_y)
        elif raw_data is not None:
            self.read_raw_data(raw_data, selected_y=selected_y)

    def __add__(self, other):
        px = [i for i in self._px]
        py = [i for i in self._py]
        pz = [i for i in self._pz]
        raw_data = []
        for z in pz:
            for y in py:
                for x in px:
                    b = self.get_field_at_point([x, y, z])
                    bo = other.get_field_at_point([x, y, z])
                    bs = _np.array(b) + _np.array(bo)
                    raw_data.append([x, y, z, bs[0], bs[1], bs[2]])
        raw_data = _np.array(raw_data)
        return self.__class__(raw_data=raw_data, selected_y=py[0])

    def __sub__(self, other):
        px = [i for i in self._px]
        py = [i for i in self._py]
        pz = [i for i in self._pz]
        raw_data = []
        for z in pz:
            for y in py:
                for x in px:
                    b = self.get_field_at_point([x, y, z])
                    bo = other.get_field_at_point([x, y, z])
                    bs = _np.array(b) - _np.array(bo)
                    raw_data.append([x, y, z, bs[0], bs[1], bs[2]])
        raw_data = _np.array(raw_data)
        return self.__class__(raw_data=raw_data, selected_y=py[0])

    @property
    def filename(self):
        return self._filename

    @property
    def px(self):
        return self._px

    @property
    def py(self):
        return self._py

    @property
    def pz(self):
        return self._pz

    @property
    def bx(self):
        return self._bx

    @property
    def by(self):
        return self._by

    @property
    def bz(self):
        return self._bz

    def _update_interpolation_functions(self):
        if self._nx == 1:
            self._bx_func = _interpolate.interp1d(
                self._pz, self._bx, bounds_error=False)
            self._by_func = _interpolate.interp1d(
                self._pz, self._by, bounds_error=False)
            self._bz_func = _interpolate.interp1d(
                self._pz, self._bz, bounds_error=False)
        elif self._nz == 1:
            self._bx_func = _interpolate.interp1d(
                self._px, self._bx, bounds_error=False)
            self._by_func = _interpolate.interp1d(
                self._px, self._by, bounds_error=False)
            self._bz_func = _interpolate.interp1d(
                self._px, self._bz, bounds_error=False)
        else:
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

    def correct_cross_talk(
            self, k0=7.56863157e-06, k1=-1.67524756e-02,
            k2=-6.78110439e-03):
        tmp_bx = _np.copy(self._bx)
        tmp_by = _np.copy(self._by)
        tmp_bz = _np.copy(self._bz)

        tmp_bx_corr = []

        for b in range(len(tmp_bx)):
            tmp_bx_corr.append((tmp_bx[b] + (((
                k0 + k1*tmp_by[b] + k2*tmp_by[b]**2) + (
                k0 + k1*tmp_bz[b] + k2*tmp_bz[b]**2)))/2))

        self._bx = _np.array(tmp_bx_corr)

        self._update_interpolation_functions()

    def get_field_at_point(self, point):
        if self._nx == 1:
            bx = self._bx_func(point[2])[0]
            by = self._by_func(point[2])[0]
            bz = self._bz_func(point[2])[0]
        elif self._nz == 1:
            bx = self._bx_func(point[0])[0]
            by = self._by_func(point[0])[0]
            bz = self._bz_func(point[0])[0]
        else:
            bx = self._bx_func(point[0], point[2])[0, 0]
            by = self._by_func(point[0], point[2])[0, 0]
            bz = self._bz_func(point[0], point[2])[0, 0]
        return [bx, by, bz]

    def shift(self, value):
        self._px += value[0]
        self._py += value[1]
        self._pz += value[2]
        self._update_interpolation_functions()

    def rotate(self, point, vector, angle):
        raise NotImplementedError

    def read_file(self, filename, selected_y=0):
        self._filename = filename

        header_size = 2000
        with open(self._filename, 'r') as f:
            data = f.read(header_size)

        idx = data.find('--------')
        skiprows = len(data[:idx].split('\n')) if idx != -1 else 0
        raw_data = _np.loadtxt(
            self._filename, skiprows=skiprows)
        self.read_raw_data(raw_data, selected_y=selected_y)

        return True

    def read_raw_data(self, raw_data, selected_y=0):
        self._raw_data = raw_data

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
            filt = (py == selected_y)
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
