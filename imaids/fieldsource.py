
import json as _json
from concurrent.futures import ProcessPoolExecutor as _ProcessPoolExecutor
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
        """Find the indices of peaks in data list.

        Args:
            data (list): Data with peaks.
            prominence (float or list, optional):
                Required width of peaks in samples. Defaults to 0.05.

        Returns:
            numpy.ndarray: Indices of peaks in data.
        """
        return _utils.find_peaks(data, prominence=prominence)

    @staticmethod
    def find_valleys(data, prominence=0.05):
        """Find the indices of valleys in data list.

        Args:
            data (list): Data with valleys.
            prominence (float or list, optional):
                Required width of valleys in samples. Defaults to 0.05.

        Returns:
            numpy.ndarray: Indices of valleys in data.
        """
        return _utils.find_valleys(data, prominence=prominence)

    @staticmethod
    def find_peaks_and_valleys(data, prominence=0.05):
        """Find the indices of peaks and valleys in data list.

        Args:
            data (list): Data with peaks and valleys.
            prominence (float or list, optional):
                Required width of peaks and valleys in samples.
                Defaults to 0.05.

        Returns:
            numpy.ndarray: Indices of peaks and valleys in data.
        """
        return _utils.find_peaks_and_valleys(data, prominence=prominence)

    @staticmethod
    def find_zeros(pos, data):
        """Find zeros positions on data.

        Args:
            pos (numpy.ndarray): Positions list.
            data (numpy.ndarray): Data list.

        Returns:
            numpy.ndarray: List of the zeros' positions.
        """
        return _utils.find_zeros(pos, data)

    @staticmethod
    def delete_all():
        """Delete all the previously created elements.

        Returns:
            int: 0.
        """
        return _utils.delete_all()

    def calc_field_integrals(self, z_list, x=0, y=0, field_list=None,
                                nproc=None, chunksize=100):
        """Calculate field integrals.

        Args:
            z_list (list): Longitudinal position list (in mm) to
                calculate field integrals.
            x (list or float or int, optional): x positions
                to calculate field integrals (in mm). Defaults to 0.
            y (list or float or int, optional): y positions
                to calculate field integrals (in mm). Defaults to 0.
            field_list (list, optional): Field data (in T).
                Defaults to None.
            nproc (int, optional): number of threads for parallel computation.
                of field. Ignored if field_list is given.
                Must be >=1. If None, serial case is performed (concurrent
                multiprocessing module will not be used). Defaults to None.
            chunksize (int, optional): multiprocessing parameter specifying
                size of list section sent to each process. Defaults to 100.

        Note:
            Python multiprocessing does not work interactively, it must be
            run in a __main__ module, inside the clause:
                if __name__ == '__main__':

        Raises:
            ValueError: Field data and longitudinal position must have
                the same length.

        Returns:
            numpy.ndarray: First integrals [ibx, iby, ibz] (in G.cm).
            numpy.ndarray: Second integrals [iibx, iiby, iibz] (in kG.cm²).
        """
        if field_list is not None:
            if len(field_list) != len(z_list):
                raise ValueError(
                    'Inconsistent length between field and position lists.')
        else:
            field_list = self.get_field(x=x, y=y, z=z_list, nproc=nproc,
                                        chunksize=chunksize)

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

    def calc_integral_multipole_coef(self, z, x):
        """Calculates skew and normal integrated multipole coefficients for the
        first field integrals. The integrals are calculated along z for the
        input list of x coordinates at y=0.

        Args:
            z (list, M): z values used for calculating first field integrals.
                (z is the integration variable) In mm.
            x (list, N): x values in which first field integrals along z are
                computed. In mm.

        Returns:
            numpy.ndarray, max_power: array containing skew components.
                Higher order first. In units of T.m^(1-N), ... , T.m.
                Maximum order is N = min(15, len(x)-1).
            numpy.ndarray, max_power: array containing normal components
                Higher order first. In units of T.m^(1-N), ... , T.m.
                Maximum order is N = min(15, len(x)-1).
        """

        integs = _np.array([self.calc_field_integrals(z, x=xp, y=0) for xp in x])
        # The array above has the shape: (len(x), 2, len(z), 3):
        #   len(x) x coordinates, 2 field integrals (first and second),
        #   len(z) z coordinates, 3 field components.

        ibx = integs[:, 0, -1, 0]*1e-6
        iby = integs[:, 0, -1, 1]*1e-6
        # Defining the first field integrals along x.
        # Indices correspond to all x points (:), the first integral (0),
        #   at the last z (-1) for the bx and by components (0 and 1)

        return _utils.fit_multipole_coef(x, ibx, x, iby)

    def calc_trajectory(
            self, energy, r0, zmax, rkstep, dz=0, on_axis_field=False):
        """Calculate electron trajectory.

        Args:
            energy (float): Electron energy at the beam (in KeV).
            r0 (list): Initial position to calculate trajectory
                [x,y,z,x',y',z'] x,y,z in mm and x',y',z' in rad or
                dimensionless.
            zmax (float): Final position to calculate trajectory (in mm).
            rkstep (float): Step to solve the equation of motion (in mm).
            dz (int or float, optional): Distance to add in z initial
                position. Defaults to 0.
            on_axis_field (bool, optional): If True, get field on axis,
                (B(x,y,z) = B(0,0,z)). Defaults to False.

        Returns:
            numpy.ndarray: Electron trajectory [x,y,z,x',y',z'],
                x,y,z in mm and x',y',z' in rad/dimensionless.
        """
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

        z0 = r[2]
        lz = _np.abs(zmax/1000 - z0)

        while _np.abs(r[2]- z0) < lz:
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

            r += (step/6)*(drds1 + 2*drds2 + 2*drds3 + drds4)

            trajectory.append([
                r[0]*1000, r[1]*1000, r[2]*1000, r[3], r[4], r[5]
            ])

        trajectory = _np.array(trajectory)

        return trajectory

    def get_field(self, x=0, y=0, z=0, nproc=None, chunksize=100):
        """Get field data.

        Args:
            x (list or float or int, optional): x positions
                to get field (in mm). Defaults to 0.
            y (list or float or int, optional): y positions
                to get field (in mm). Defaults to 0.
            z (list or float or int, optional): z positions
                to get field (in mm). Defaults to 0.
            nproc (int, optional): number of threads for parallel computation.
                Must be >=1. If None, serial case is performed (concurrent
                multiprocessing module will not be used). Defaults to None.
            chunksize (int, optional): multiprocessing parameter specifying
                size of list section sent to each process. Defaults to 100.

        Note:
            Python multiprocessing does not work interactively, it must be
            run in a __main__ module, inside the clause:
                if __name__ == '__main__':

        Raises:
            ValueError: Position arguments must be valid.
            ValueError: If provided, number of processes must be >=1.

        Returns:
            numpy.ndarray: Field data [bx, by, bz] (in T).
        """
        if int(_np.ndim(x)) == 0:
            x = [x]
        if int(_np.ndim(y)) == 0:
            y = [y]
        if int(_np.ndim(z)) == 0:
            z = [z]

        if sum([len(i) > 1 for i in [x, y, z]]) > 1:
            raise ValueError('Invalid position arguments.')

        pos_list = []
        for pos_z in z:
            for pos_x in x:
                for pos_y in y:
                    pos_list.append([pos_x, pos_y, pos_z])

        if nproc is not None:
            nproc = int(nproc)
            if nproc < 1:
                raise ValueError('Number or processes must be >=1.')
            with _ProcessPoolExecutor(max_workers=nproc) as executor:
                field_gen = executor.map(self.get_field_at_point, pos_list,
                                         chunksize=chunksize)
                return _np.array(list(field_gen))

        else:
            field = [self.get_field_at_point(pos) for pos in pos_list]
            return _np.array(field)

    def get_field_at_point(self, point):
        raise NotImplementedError

    def save_fieldmap(self, filename, x_list, y_list, z_list, header=None,
                        nproc=None, chunksize=100):
        """Save fieldmap file.

        Args:
            filename (str): Path to file.
            x_list (list or float or int): x positions
                to save in file (in mm).
            y_list (list or float or int): y positions
                to save in file (in mm).
            z_list (list or float or int): z positions
                to save in file (in mm).
            header (str, optional): File's header description.
                Defaults to None.
            nproc (int, optional): number of threads for parallel computation.
                Must be >=1. If None, serial case is performed (concurrent
                multiprocessing module will not be used). Defaults to None.
            chunksize (int, optional): multiprocessing parameter specifying
                size of list section sent to each process. Defaults to 100.

        Note:
            Python multiprocessing does not work interactively, it must be
            run in a __main__ module, inside the clause:
                if __name__ == '__main__':

        Raises:
            ValueError: If provided, number of processes must be >=1.

        Returns:
            bool: True.
        """
        if header is None:
            header = []

        if int(_np.ndim(x_list)) == 0:
            x_list = [x_list]

        if int(_np.ndim(y_list)) == 0:
            y_list = [y_list]

        if int(_np.ndim(z_list)) == 0:
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

            pos_list = []
            for z in z_list:
                for y in y_list:
                    for x in x_list:
                        pos_list.append([x,y,z])

            if nproc is not None:

                nproc = int(nproc)
                if nproc < 1:
                    raise ValueError('Number or processes must be >=1.')

                with _ProcessPoolExecutor(max_workers=nproc) as executor:
                    field_gen = executor.map(self.get_field_at_point, pos_list,
                                            chunksize=chunksize)
                    for field, pos in zip(field_gen, pos_list):
                        x, y, z = pos
                        bx, by, bz = field
                        line = line_fmt.format(x, y, z, bx, by, bz)
                        fieldmap.write(line)

            else:
                    for pos in pos_list:
                        x, y, z = pos
                        bx, by, bz = self.get_field_at_point(pos)
                        line = line_fmt.format(x, y, z, bx, by, bz)
                        fieldmap.write(line)

        return True

    def save_fieldmap_spectra(self, filename, x_list, y_list, z_list,
                                nproc=None, chunksize=100):
        """Save fieldmap file to use in spectra.

        Args:
            filename (str): Path to file.
            x_list (list or float or int): x positions
                to save in file (in mm).
            y_list (list or float or int): y positions
                to save in file (in mm).
            z_list (list or float or int): z positions
                to save in file (in mm).
            nproc (int, optional): number of threads for parallel computation.
                Must be >=1. If None, serial case is performed (concurrent
                multiprocessing module will not be used). Defaults to None.
            chunksize (int, optional): multiprocessing parameter specifying
                size of list section sent to each process. Defaults to 100.

        Note:
            Python multiprocessing does not work interactively, it must be
            run in a __main__ module, inside the clause:
                if __name__ == '__main__':

        Raises:
            ValueError: Number of points in the longitudinal direction
                must be >=4.
            ValueError: If provided, number of processes must be >=1.

        Returns:
            bool: True.
        """
        if int(_np.ndim(x_list)) == 0:
            x_list = [x_list]

        if int(_np.ndim(y_list)) == 0:
            y_list = [y_list]

        if int(_np.ndim(z_list)) == 0:
            z_list = [z_list]

        x_list = _np.round(x_list, decimals=8)
        y_list = _np.round(y_list, decimals=8)
        z_list = _np.round(z_list, decimals=8)

        nx = len(x_list)
        ny = len(y_list)
        nz = len(z_list)

        if len(x_list) == 1:
            nx = 2
            xstep = 1
            x_list = [x_list[0], x_list[0]]
        else:
            xstep = x_list[1] - x_list[0]

        if len(y_list) == 1:
            ny = 2
            ystep = 1
            y_list = [y_list[0], y_list[0]]
        else:
            ystep = y_list[1] - y_list[0]

        if len(z_list) < 4:
            raise ValueError('Number of points in the longitudinal direction ' +
                                'must be >=4.')
        else:
            zstep = z_list[1] - z_list[0]

        header_data = [xstep, ystep, zstep, nx, ny, nz]
        header = '{0:g}\t{1:g}\t{2:g}\t{3:d}\t{4:d}\t{5:d}\n'.format(*header_data)

        with open(filename, 'w') as fieldmap:
            fieldmap.write(header)

            line_fmt = '{0:g}\t{1:g}\t{2:g}\n'

            pos_list = []
            for x in x_list:
                for y in y_list:
                    for z in z_list:
                        pos_list.append([x,y,z])

            if nproc is not None:

                nproc = int(nproc)
                if nproc < 1:
                    raise ValueError('Number or processes must be >=1.')

                with _ProcessPoolExecutor(max_workers=nproc) as executor:
                    field_gen = executor.map(self.get_field_at_point, pos_list,
                                            chunksize=chunksize)
                    for field in field_gen:
                        bx, by, bz = field
                        line = line_fmt.format(bx, by, bz)
                        fieldmap.write(line)
            else:
                for pos in pos_list:
                    bx, by, bz = self.get_field_at_point(pos)
                    line = line_fmt.format(bx, by, bz)
                    fieldmap.write(line)

        return True

    def save_kickmap(
            self, filename, energy, x_list, y_list, zmin, zmax, rkstep):
        """Save kickmap file.

        Args:
            filename (str): Path to file.
            energy (float): Electron energy at the beam (in KeV).
            x_list (list or float or int): x positions to save in file (in mm).
            y_list (list or float or int): y positions to save in file (in mm).
            zmin (float): z minimum position to save in file (in mm).
            zmax (float): z maximum position to save in file (in mm).
            rkstep (float): Step to solve the equation of motion (in mm).

        Returns:
            numpy.ndarray: Total Horizontal 2nd Order Kick (in T2m2).
            numpy.ndarray: Total Vertical 2nd Order Kick (in T2m2).
            numpy.ndarray: Horizontal Final Position (in m).
            numpy.ndarray: Vertical Final Position (in m).
        """
        _, light_speed = _utils.get_constants()
        brho = energy*1e9/light_speed

        if int(_np.ndim(x_list)) == 0:
            x_list = [x_list]

        if int(_np.ndim(y_list)) == 0:
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
        """Sinusoidal field source class.

        Args:
            nr_periods (int, optional): Number of complete periods.
                Defaults to None.
            period_length (float, optional): Period length (in mm).
                Defaults to None.

        Raises:
            ValueError: Number of complete periods must be bigger than zero.
            ValueError: Period length must be bigger than zero.
        """
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
        """Calculate cosine amplitude.

        Args:
            z_list (list): List of positions (in mm).
            field_list (list): List of fields (in T).
            freq_guess (float): Initial guess for the spacial frequencies
                of the fitting cosines. (in 1/mm).
            maxfev (int, optional): Maximum number of calls to the least
                squares scipy function during fitting. Defaults to 5000.

        Returns:
            list: Amplitudes fitted to the components' oscillations (in T).
            list: Phases fitted to the components' oscillations
                (dimensionless).
        """
        return _utils.calc_cosine_amplitude(
            z_list, field_list, freq_guess, maxfev=maxfev)

    def calc_avg_period_length(
            self, z_list, field_list=None, x=0, y=0,
            period_length_guess=20, maxfev=5000, prominence=1):
        """Calculate average period length.

        Args:
            z_list (list): List of z positions to get field data (in mm).
            field_list (list, optional): List of fields (in T).
                Defaults to None.
            x (int, optional): x position to get field data (in mm).
                Defaults to 0.
            y (int, optional): y position to get field data (in mm).
                Defaults to 0.
            period_length_guess (float, optional): Initial guess for the
                period length. Defaults to 20.
            maxfev (int, optional): Maximum number of calls to the least
                squares scipy function during fitting. Defaults to 5000.
            prominence (int or float optional): Required width of peaks
                and valleys in samples. Defaults to 1.

        Returns:
            numpy.float64: Average period length (in mm).
            int: Number of complete periods.
        """
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

    def get_effective_field(self, polarization, hmax, x):
        """Calculate effective field amplitude from model.

        Args:
            polarization (string): String specifying the polarization of radiation.
                Available options are:
                'hp': Horizontal polarization
                'vp': Vertical polarization
                'cp': Circular polarization
            hmax (int): max field harmonic to be considered.
            x (float): horizontal position to calc field [mm]

        Returns:
            float : effective field amplitude [T]
            float: first harmonic field amplitude [T]
            numpy.ndarray: field along longitudinal positions [T]
        """
        zmin = -2*self.period_length
        zmax = 2*self.period_length
        npts = 201
        z = _np.linspace(zmin, zmax, npts)
        bvec = self.get_field(x=x,z=z)
        if polarization == 'vp':
            b = bvec[:, 0]
        elif polarization in ('hp', 'cp'):
            b = bvec[:, 1]
        else:
            raise ValueError("invalid polarization argument")

        freq0 = 2*_np.pi/self.period_length
        hs = _np.arange(1, hmax+1, 2)
        freqs = hs*freq0
        amps, *_ = _utils.fit_fourier_components(b, freqs, z)
        amps /= hs
        beff = _np.sqrt(_np.sum(_np.dot(amps, amps)))
        return beff, amps[0], b

    def calc_field_amplitude(
            self, z_list=None, field_list=None,
            x=0, y=0, npts_per_period=101, maxfev=10000):
        """Calculate field amplitude.

        Args:
            z_list (list, optional): List of z positions (in mm).
                Defaults to None.
            field_list (list, optional): List of fields (in T).
                Defaults to None.
            x (int, optional):  x position to get field data (in mm).
                Defaults to 0.
            y (int, optional):  y position to get field data (in mm).
                Defaults to 0.
            npts_per_period (int, optional): Number of points per period.
                Defaults to 101.
            maxfev (int, optional): Maximum number of calls to the least
                squares scipy function during fitting. Defaults to 10000.

        Returns:
            numpy.float64: Bx field amplitude (in T).
            numpy.float64: By field amplitude (in T).
            numpy.float64: Bz field amplitude (in T).
            numpy.float64: Bxy phase (dimensionless).
        """
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

    def calc_roll_off_peaks(self, z, x, y=0, field_comp=None):
        """Calculate roll-off of peak fields at x=0 along x lines.

        The roll-off at x=xp is defined as:

            1 - bi(x=xp,z=z_peak_j) / bi(x=0, z=z_peak_j)

        The i-th component of the field b is calculated in two points, in which
            z_peak_j is the position of the j-th field peak along x=0.
        The y position is fixed throughout all the calculations,
            defaulting to 0.

        Args:
            z (list): z positions along which the peak positions will be
                determined at x=0 and y=y.
            x (list): x positions for which peaks roll-off will be determined.
            y (float, optional): y position for calculations. Defaults to 0.
            field_comp (int, optional): Parameter used to force one of the
                components to be used for determining peak positions.
                    If field_comp==0, peaks z position are Bx maxima.
                    If field_comp==1, peaks z position are By maxima.
                    If None, the component with greater amplitude will be used.
                Defaults to None.

        Returns:
            numpy.ndarray 3 x N x len(x): Array of roll-off values for the
                3 field components, N found peaks and len(x) points in x.
                Ex: [1, 3, 10] will be the By roll-ff of the 3rd peak
                    at the 10th x value.
        """
        if field_comp is None:
            field0 = self.get_field(x=0, y=y, z=z)
            ampl0 = self.calc_field_amplitude(z_list=z, field_list=field0)
            field_comp = int(ampl0[1] >= ampl0[0])

        field0 = self.get_field(x=0, y=y, z=z)
        peaks = self.find_peaks(field0[:,field_comp]) # These are peak indices
                                                      # in field0, and thus
                                                      # in the z list as well.

        rolloff_array = _np.zeros((3, len(peaks), len(x)))
        for i in range(3): # Field components.
            for peak_idx, peak in enumerate(peaks): # Peak indices (indexed).
                b0 = field0[peak]
                for x_idx, xp in enumerate(x): # x values (indexed).
                    b = self.get_field(x=xp, y=y, z=z[peak])[0]
                    rolloff_array[i, peak_idx, x_idx] = 1 - b[i]/b0[i]

        return rolloff_array

    def calc_roll_off_amplitude(self, z, x, y=0):
        """Calculate roll-off of field amplitudes along x.

        The roll-off at x=xp is defined as:

            1 - Ampl_i(x=xp) / Ampl_i(x=0)

        Where Ampl_i is the amplitude of the i-th field component, which is
            calculated for field profiles along z in x=xp and x=0.
        The y position is fixed throughout all the calculations,
            defaulting to 0.

        Args:
            z (list): z positions for calculating field profiles when
                determining field amplitudes.
            x (list): x positions for which peaks roll-off will be determined.
            y (float, optional): y position for calculations. Defaults to 0.

        Returns:
            numpy.ndarray 3 x len(x): Array of roll-ff values for the
                3 field components and len(x) points in x.
                Ex: [1, 5] will be the By amplitude roll-off
                    at the 5th x value.
        """
        field0 = self.get_field(x=0, y=y, z=z)
        ampl0 = self.calc_field_amplitude(z_list=z, field_list=field0)
        ampl0 = _np.array(ampl0)

        rolloff_array = _np.zeros((3, len(x)))

        for xp_idx, xp in enumerate(x):
            field = self.get_field(x=xp, y=y, z=z)
            ampl = self.calc_field_amplitude(z_list=z, field_list=field)
            ampl = _np.array(ampl)
            rolloff_array[:, xp_idx] = 1 - ampl[:3]/ampl0[:3]

        return rolloff_array

    def calc_multipoles_peaks(self, z, x, field_comp=None):
        """Calculates skew and normal multipole coefficients for the peaks
        of the field. The peaks are found for for x=y=0 along z.

        Args:
            z (list, M): z values used for calculating first field integrals.
                (z is the integration variable) In mm.
            x (list, N): x values in which first field integrals along z are
                computed. In mm.
            field_comp (int, optional): Parameter used to force one of the
                components to be used for determining peak positions.
                    If field_comp==0, peaks z position are Bx maxima.
                    If field_comp==1, peaks z position are By maxima.
                    If None, the component with greater amplitude will be used.
                Defaults to None.

        Returns:
            numpy.ndarray 2 x max_power x N: Array of multipole
                coefficients (up to max_power) for the N found peaks.
                Ex 1: [1, 0, 3] will be the dipole normal component of the 3rd 
                    peak.
                Ex 2: [0, 0, 3] will be the dipole skew component of the 3rd 
                    peak.
        """
        if field_comp is None:
            field0 = self.get_field(x=0, y=0, z=z)
            ampl0 = self.calc_field_amplitude(z_list=z, field_list=field0)
            field_comp = int(ampl0[1] >= ampl0[0])

        field0 = self.get_field(x=0, y=0, z=z)
        peaks = self.find_peaks(field0[:,field_comp]) # These are peak indices
                                                      # in field0, and thus
                                                      # in the z list as well.

        max_power = min([15, len(x)-1])

        multipole_array = _np.zeros((2, max_power, len(peaks)))
        for peak_idx, peak in enumerate(peaks): # Peak indices (indexed).
            b_peak = self.get_field(x=x, y=0, z=z[peak])
            bx_peak = b_peak[:, 0]
            by_peak = b_peak[:, 1]
            multipoles = _utils.fit_multipole_coef(x, bx_peak, x, by_peak)
            multipole_array[0, :, peak_idx] = multipoles[0]
            multipole_array[1, :, peak_idx] = multipoles[1]

        return multipole_array

    def calc_deflection_parameter(self, bx_amp=None, by_amp=None):
        """Calculate deflection parameter.

        Args:
            bx_amp (float, optional): Bx field amplitude (in T).
                Defaults to None.
            by_amp (float, optional): By field amplitude (in T).
                Defaults to None.

        Returns:
            numpy.float64: Horizontal deflection parameter (in T.mm).
            numpy.float64: Vertical deflection parameter (in T.mm).
        """
        if bx_amp is None or by_amp is None:
            bx_amp, by_amp, _, _ = self.calc_field_amplitude()
        period = self.period_length*1e-3
        kh = _utils.calc_deflection_parameter(b_amp=by_amp, period_length=period)
        kv = _utils.calc_deflection_parameter(b_amp=bx_amp, period_length=period)
        return kh, kv

    def calc_trajectory_avg_over_period(self, trajectory):
        """Calculate the average electron trajectory over period.

        Args:
            trajectory (list): Electron trajectory [x,y,z,x',y',z'],
                x,y,z in mm and x',y',z' in rad/dimensionless.

        Returns:
            numpy.ndarray: Average electron trajectory over period.
        """
        trajz = [t for t in trajectory[:, 2]]
        step = _np.abs(trajz[1] - trajz[0])
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
        """Calculate trajectory length in mm.

        Args:
            trajectory (list): Electron trajectory [x,y,z,x',y',z'],
                x,y,z in mm and x',y',z' in rad/dimensionless.

        Returns:
            numpy.ndarray: Electron trajectory length.
        """
        traj_pos = trajectory[:, 0:3]
        traj_diff = _np.diff(traj_pos, axis=0)
        traj_len = _np.append(
            0, _np.cumsum(_np.sqrt(_np.sum(traj_diff**2, axis=1))))
        return traj_len

    def calc_radiation_phase(self, energy, trajectory, wavelength):
        """Calculate radiation phase in rad.

        Args:
            energy (float): Electron energy at the beam (in KeV).
            trajectory (list): Electron trajectory [x,y,z,x',y',z'],
                x,y,z in mm and x',y',z' in rad/dimensionless.
            wavelength (float): Radiation wavelength.

        Returns:
            numpy.ndarray: Radiation phase.
        """
        beta, *_ = _utils.calc_beam_parameters(energy)
        traj_z = trajectory[:, 2]
        traj_len = self.calc_trajectory_length(trajectory)
        return (2*_np.pi/(wavelength))*(traj_len/beta - (traj_z - traj_z[0]))

    def calc_radiation_wavelength(
            self, energy, bx_amp, by_amp, harmonic=1):
        """Calculate radiation wavelength in mm.

        Args:
            energy (float): Electron energy at the beam (in KeV).
            bx_amp (float): Bx field amplitude (in T).
            by_amp (float): By field amplitude (in T).
            harmonic (int, optional): Harmonic to calculate radiation
                wavelegth. Defaults to 1.

        Returns:
            numpy.float64: Radiation wavelength.
        """
        _, gamma, _ = _utils.calc_beam_parameters(energy)
        kh, kv = self.calc_deflection_parameter(bx_amp, by_amp)
        wl = (self.period_length/(2*harmonic*(gamma**2)))*(
            1 + (kh**2 + kv**2)/2)
        return wl

    def calc_phase_error(
            self, energy, trajectory, bx_amp, by_amp,
            skip_poles=0, zmin=None, zmax=None, field_comp=None):
        """Calculate phase error.

        Args:
            energy (float): Electron energy at the beam (in KeV).
            trajectory (list): Electron trajectory [x,y,z,x',y',z'],
                x,y,z in mm and x',y',z' in rad/dimensionless.
            bx_amp (float): Bx field amplitude (in T).
            by_amp (float): By field amplitude (in T).
            skip_poles (int, optional): Number of poles to skip in start
                and end of trajectory. Defaults to 0.
            zmin (float, optional): z minimum position (in mm).
                Defaults to None.
            zmax (float, optional): z maximum position (in mm).
                Defaults to None.
            field_comp (int, optional): Parameter used to force one of the
                components (x or y) to be used to determine the poles.
                Defaults to None.

        Returns:
            list: z positon list (in mm).
            numpy.ndarray: Phase error list (in rad).
            numpy.float64: Phase error rms (in rad).
        """
        if field_comp is None:
            z_from_by = by_amp >= bx_amp
        elif field_comp == 0:
            z_from_by = False
        elif field_comp == 1:
            z_from_by = True

        if z_from_by:
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
        """Get filename.

        Args:
            date (str): String on date format, YYYY-MM-DD.
            x_list (list or float or int): x positions to save in file.
            y_list (list or float or int): y positions to save in file.
            z_list (list or float or int): z positions to save in file.
            kh (float): Horizontal deflection parameter (in T.mm).
            kv (float): Vertical deflection parameter (in T.mm).
            polarization_name (str, optional): Name of the polarization to
                save in file. Defaults to None.
            add_label (str, optional): Label to add in filename.
                Defaults to None.
            file_extension (str, optional): File extension to save.
                Defaults to '.fld'.

        Returns:
            str: Filename.
        """
        filename = '{0:s}'.format(date)

        if int(_np.ndim(x_list)) == 0:
            x_list = [x_list]

        if int(_np.ndim(y_list)) == 0:
            y_list = [y_list]

        if int(_np.ndim(z_list)) == 0:
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
        """Field model class.

        Args:
            radia_object (int, optional): Number of the radia object.
                Defaults to None.
        """
        self._radia_object = radia_object

    @property
    def radia_object(self):
        """Number of the radia object."""
        return self._radia_object

    @property
    def center_point(self):
        """Vector coordinates ([x,y,z]) of radia object geometrical center."""

        if self.radia_object is None:
            raise None

        centers = _np.array(_rad.ObjM(self.radia_object))[:,0]
        center = centers.mean(axis=0)
        return list(center)

    @property
    def state(self):
        return {}

    @classmethod
    def load_state(cls, filename):
        """Load state from file.

        Args:
            filename (str): Path to file.
        """
        with open(filename) as f:
            kwargs = _json.load(f)
        return cls(**kwargs)

    def draw(self):
        """Draw radia object.

        Returns:
            bool: If radia object is not None, return True.
        """
        if self._radia_object is None:
            return False

        #_rad.ObjDrwAtr(self._radia_object, [0, 0.5, 1], 0.001)
        _rad.ObjDrwOpenGL(self._radia_object)
        return True

    def get_field_at_point(self, point):
        """Get field data at point.

        Computes magnetic field created by the object in the point
        with Cartesian coordinates {x,y,z}.

        Args:
            point (list): List of x,y,z positions to get field (in mm).

        Returns:
            list: Field data list (in T).
        """
        return _rad.Fld(self._radia_object, "b", point)

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

    def solve(self, prec=0.00001, max_iter=1000):
        """Executes an automatic relaxation procedure.

        Args:
            prec (float, optional): Absolute precision value
                for magnetization, to be reached by the end of the
                relaxation (in T). Defaults to 0.00001.
            max_iter (int, optional): Maximum number of iterations
                permitted to reach the specified precision.
                Defaults to 1000.

        Returns:
            list: A list of four numbers specifying (1) average absolute
                change in magnetization after previous iteration over all
                the objects participating in the relaxation, (2) maximum
                absolute value of magnetization over all the objects
                participating in the relaxation, (3) maximum absolute
                value of magnetic field strength over central points of
                all the objects participating in the relaxation, and (4)
                actual number of iterations done. The values (1)-(3) given,
                are those of last iteration.
        """
        return _rad.Solve(self._radia_object, prec, max_iter)

    def shift(self, value):
        """Shift radia object.

        Args:
            value (list): List of three real numbers specifying
                the translation vector.

        Returns:
            bool: If radia object is not None, return True.
                Else, return False.
        """
        if self._radia_object is not None:
            self._radia_object = _rad.TrfOrnt(
                self._radia_object, _rad.TrfTrsl(value))
            return True
        else:
            return False

    def rotate(self, point, vector, angle):
        """Rotate radia object.

        Args:
            point (list): List of three real numbers specifying
                Cartesian coordinates of a point on the rotation axis.
            vector (list): List of three real numbers specifying
                components of the rotation axis vector.
            angle (float): Rotation angle, in radians.

        Returns:
            bool: If radia object is not None, return True.
                Else, return False.
        """
        if self._radia_object is not None:
            self._radia_object = _rad.TrfOrnt(
                self._radia_object, _rad.TrfRot(point, vector, angle))
            return True
        else:
            return False

    def mirror(self, point, normal):
        """Mirror radia object.

        Args:
            point (list): List of three real numbers specifying
                Cartesian coordinates of a point on the symmetry plane.
            normal (list): List of three real numbers specifying
                components of the vector normal to the plane.

        Returns:
            bool: If radia object is not None, return True.
                Else, return False.
        """
        if self._radia_object is not None:
            self._radia_object = _rad.TrfOrnt(
                self._radia_object, _rad.TrfPlSym(point, normal))
            return True
        else:
            return False


class FieldData(FieldSource):

    def __init__(self, filename=None, raw_data=None, selected_y=0):
        """Field data class.

        Args:
            filename (str, optional): Path to file. Defaults to None.
            raw_data (list, optional): List of x, y, z positions and
                bx, by, bz fields to read and save. Defaults to None.
            selected_y (int, optional): y position to get field data
                (in mm). Defaults to 0.
        """
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

    @property
    def raw_data(self):
        return self._raw_data

    def _update_interpolation_functions(self):
        """Update field data using scipy interpolation functions.
            Interpolations 1D or 2D only.

        Returns:
            bool: True.
        """
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

    def add_field(self, other):
        """Add field from another radia object.

        Args:
            other (imaids.fieldsource.FieldModel): Other radia object
                to get the field to add to the radia object field.
        """
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
        self.read_raw_data(raw_data=raw_data)

    def sub_field(self, other):
        """Subtract field from another radia object.

        Args:
            other (imaids.fieldsource.FieldModel): Other radia object
                to get the field to subtract to the radia object field.
        """
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
        self.read_raw_data(raw_data=raw_data)

    def clear(self):
        """Clear all field data.
        """
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
        """Correct hall probe 03121 angles.
            Default values were measured in CNPEM.

        Args:
            angxy (float, optional): Angle X pitch. Defaults to 0.15.
            angxz (float, optional): Angle X tilt. Defaults to -0.21.
            angyx (float, optional): Angle Y pitch. Defaults to -0.01.
            angyz (float, optional): Angle Y roll. Defaults to -0.02.
            angzx (float, optional): Angle Z tilt. Defaults to 0.01.
            angzy (float, optional): Angle Z roll. Defaults to -0.74.
        """
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

    def correct_cross_talk(self, kx=None,
                                 ky=[-0.006781104386361973,
                                     -0.01675247563602003,
                                     7.568631573320983e-06],
                                 kz=[-0.006170829583118335,
                                     -0.016051627320478382,
                                     7.886674928668737e-06]):
        """Correct hall probe 03121 Bx crosstalk.
            Default values were measured in CNPEM.

        The measured correction (2021) corresponds to the default values:
            kx=None,
            ky=[-0.006781104386361973,
                -0.01675247563602003,
                 7.568631573320983e-06],
            kz=[-0.006170829583118335,
                -0.016051627320478382,
                 7.886674928668737e-06]
        In which case:
            ky are the polynomial coefficients from By x Bx curve.
            kz are the polynomial coefficients from Bz x Bx curve.

        A 2023 refinement utilizes the following coefficients:
            kx=[1.1968435541606862e-05, 1.0000903755342276,
                0.003902372429973103, 0.0015876826767971318,
                -0.00011855122769391756, 0.00018042854166951708,
                3.232522985657504e-05, -8.863091992783466e-05,
                0.006797031584016086, -1.7400091098968548e-05],
            ky=[2.460277578039647e-06, -0.0017171247799396315,
                0.9997387421292917, -0.003778756411580486,
                -9.401652170475417e-06, 0.0002770803364512977,
                -0.00015972968246003868, -0.00010092368327927533,
                -1.950583361213016e-05, -8.581623793815916e-06],
            kz=[1.3856739048740362e-05, -0.012441651511780439,
                -0.010944669938681267, 0.9950329773452086,
                -0.00010605233698879774, -0.006723163190553383,
                0.00010206404253645934, -3.1071386016166515e-05,
                -3.5047938517653965e-06, -0.0005648410511115029])
        In which case the correction is based on quadratic functions:
            bx_corrected = func([bx, by, bz], kx)
            by_corrected = func([by, by, bz], ky)
            bz_corrected = func([bz, by, bz], kz)
        In which the func returns a corrected field component:
            k[0]                                    # constant terms
          + k[1]*bx + k[2]*by + k[3]*bz             # linear terms
          + k[4]*bx*bx + k[5]*bx*by + k[6]*bx*bz    #
          + k[7]*by*by + k[8]*by*bz + k[9]*bz*bz    # quadratic terms

        Args:
            kx (None or list, 3): Polynomial coefficients for bx.
            ky (list, 3 or list, 6): Polynomial coefficients for by.
            kz (list, 3 or list, 6): Polynomial coefficients for bz.
        """

        if (len(ky)==3) and (len(kz)==3):
            tmpBx = _np.copy(self._bx)
            tmpBy = _np.copy(self._by)
            tmpBz = _np.copy(self._bz)

            tmpBxCorr = []

            for x in range(len(tmpBx)):
                tmpBxCorr.append([])
                for z in range(len(tmpBx[x])):
                    if (abs(tmpBz[x][z]/tmpBy[x][z]) > 10 or
                        abs(tmpBy[x][z]/tmpBz[x][z]) > 10):
                        tmpBxCorr[x].append(tmpBx[x][z])
                    else:
                        tmpBxCorr[x].append(tmpBx[x][z] - (
                            (
                                ky[2] + ky[1]*tmpBy[x][z] +
                                ky[0]*tmpBy[x][z]**2)
                            *0.3825*tmpBz[x][z]/tmpBy[x][z] +
                            (
                                kz[2] + kz[1]*tmpBz[x][z] +
                                kz[0]*tmpBz[x][z]**2)
                            *0.6175*tmpBy[x][z]/tmpBz[x][z]
                            )
                                            )

            self._bx = _np.array(tmpBxCorr)

        elif (kx is not None) and (len(kx) == len(ky) == len(kz) == 10):

            def func(b, a, nx, ny, nz, kxx, kxy, kxz, kyy, kyz, kzz):
                bx, by, bz = b
                return a + nx*bx + ny*by + nz*bz \
                         + kxx*bx*bx + kxy*bx*by + kxz*bx*bz \
                         + kyy*by*by + kyz*by*bz + kzz*bz*bz

            func_x = lambda bx, by, bz: func([bx, by, bz], *kx)
            func_y = lambda bx, by, bz: func([bx, by, bz], *ky)
            func_z = lambda bx, by, bz: func([bx, by, bz], *kz)

            vectorized_func_x = _np.vectorize(func_x)
            vectorized_func_y = _np.vectorize(func_y)
            vectorized_func_z = _np.vectorize(func_z)

            corrected_bx = vectorized_func_x(self._bx, self._by, self._bz)
            corrected_by = vectorized_func_y(self._bx, self._by, self._bz)
            corrected_bz = vectorized_func_z(self._bx, self._by, self._bz)

            self._bx = corrected_bx
            self._by = corrected_by
            self._bz = corrected_bz

        self._update_interpolation_functions()

    def get_field_at_point(self, point):
        """Get field at point.

        Args:
            point (list): List of x,y,z positions to get field (in mm).

        Returns:
            list: Field data list [bx, by, bz] (in T).
        """
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
        """Shift field data.

        Args:
            value (list): List of x,y,z distances to shift field data (in mm).
        """
        self._px += value[0]
        self._py += value[1]
        self._pz += value[2]
        self._update_interpolation_functions()

    def rotate(self, point, vector, angle):
        raise NotImplementedError

    def read_file(self, filename, selected_y=0):
        """Read and load field data from file.

        Args:
            filename (str): Path to file.
            selected_y (int, optional): y position to get field data
                (in mm). Defaults to 0.

        Returns:
            bool: True.
        """
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
        """Read and load field data from raw data.

        Args:
            raw_data (list): List of x, y, z positions and bx, by, bz
                fields to read and load.
            selected_y (int, optional): y position to get field data
                (in mm). Defaults to 0.

        Returns:
            bool: True.
        """
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
