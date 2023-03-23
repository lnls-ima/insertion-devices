
import json as _json
import numpy as _np
import matplotlib.pyplot as _plt
import matplotlib.gridspec as _gridspec
import pandas as _pd

from . import utils as _utils
from . import fieldsource as _fieldsource
from . import insertiondevice as _insertiondevice


class UndulatorShimming():

    def __init__(
            self, zmin, zmax, znpts, cassettes,
            block_type='v', segments_type='half_period',
            energy=3.0, rkstep=0.5, xpos=0.0, ypos=0.0,
            zmin_pe=None, zmax_pe=None,
            include_pe=False, field_comp=None,
            solved_shim=True, solved_matrix=False):
        """Class used for calculating insertion devices shimming.

        Args:
            zmin (float): Initial/lower z longitudinal position (in mm) used
                in the calculation of:
                > trajectories.
                > field integrals.
                > field zeros at segment limits determination.
            zmax (float): Final/upper z longitudinal position (in mm) used
                in the calculation of:
                > trajectories.
                > field integrals.
                > field zeros at segment limits determination.
            znpts (int): Number of sampling points for field integrals.
            cassettes (list of str): Strings specifying which cassettes will
                be used in shimming. The strings must be keys at the cassettes
                dictionary of the considered insertion device model.
            block_type (str, optional): String specifying which types of blocks
                will be used for shimming. Available options are:
                'v'     : Vertical, blocks whose magnetization points mostly to
                          the y direction ("vertical" up or down transversal).
                'vpos'  : Vertical positive, blocks whose magnetization points
                          mostly to the positive y direction ("vertical" up
                          transversal)
                'vneg'  : Vertical negative, blocks whose magnetization points
                          mostly to the negative y direction ("vertical" down
                          transversal)
                'vlf'   : Vertical and longitudinal foward, the same as 'v'
                          plus the blocks whose magnetization points mostly
                          to the positive z direction ("foward" longitudinal).
                'all'   : All cassette blocks are use for shimming.
                'vlpair': Pairs of vertical ('v') and their next adjacent block
                          (longitudinal) used for shimming. Both blocks of a
                          pair are displaced together by the same shift during
                          the shimming procedure.
                Alternatively, this attribute may be passed as a dictionary,
                    specifying a block type per cassette:
                    e.g. {'cse':'v', 'cie':'vpos'}
                Defaults to 'v'.
            segments_type (str, optional): Defines how field zeros are used to
                obtain segments limits. Such zeros are the zeros z positions of
                a field component defined at the calc_segments method.
                If segments_type=='period', every other zero is used as segment
                    limit, starting from the first zero.
                If segments_type=='half_period' (default), all zeros are used
                    as segment limits.
                Defaults to 'half_period'.
            energy (float, optional): Electron energy at the beam, in KeV.
                Used for trajectory calculations. Defaults to 3.0.
            rkstep (float, optional): Step to solve the trajectories equations
                of motion. In mm. Defaults to 0.5.
            xpos (float, optional): Initial x transversal trajectory position.
                In mm. Defaults to 0.0.
            ypos (float, optional): Initial y transversal trajectory position.
                In mm. Defaults to 0.0.
            zmin_pe (float, optional): Lower z bound for list of poles in
                phase error calculations. If None, it is set equal to zmin.
                In mm. Defaults to None.
            zmax_pe (float, optional): upper z bound for list of poles in
                phase error calculations. If None, it is set equal to zmin.
                In mm. Defaults to None.
            include_pe (bool, optional): If True, the calculation for segment
                slopes for average trajectory also writes the phase errors
                defined by SinusoidalFieldSource.calc_phase_error method to
                output file. Defaults to False.
            field_comp (int, optional): This optional argument may be used to
                force the use of x or y field components for determining poles
                at phase error calculations (if performed), field zeros at
                segment limits determination and amplitudes for determining
                magnetization rescaling factor.
                    If field_comp==0 > y'==0 (related to Bx) defines poles.
                                     > Bx defines segment limits.
                                     > Bx field amplitude defines magnetization
                                       rescaling factor.
                    If field_comp==1 > x'==0 (related to By) defines poles.
                                     > By defines segment limits.
                                     > By field amplitude defines magnetization
                                       rescaling factor.
                    If None          > greater amplitude defines poles.
                                     > greater amplitude defines segments.
                                     > total amplitude, sqrt(Bx^2 + By^2)
                                       defines magnetization rescaling factor.
                Defaults to None.
            solved_shim (bool, optional): If True, magnetostatic problem is
                solved (Radia solve method is run) for the insertion device
                before calculating shimming signature field. Otherwise, solve
                method is not run. See help on calc_shim_signature method for
                details. Defaults to True.
            solved_matrix (bool, optional): If True, magnetostatic problem is
                solved (Radia solve method is run) for the insertion device
                before calculating each shim when determining the response
                matrix. Otherwise, solve method is not run. Defaults to False.

        Raises:
            ValueError: If block_type is not allowed.
            ValueError: If block_type dictionary keys do not match cassettes.
            ValueError: If segments_type is not "period" or "half_period".
        """
        if type(block_type) is str:
            block_type = {cassette:block_type for cassette in cassettes}
        for bt in block_type.values():
            if bt not in ('v', 'vpos', 'vneg', 'vlpair', 'vlf', 'all'):
                msg = 'Invalid block_type value. Valid options: '
                msg += '"v", "vpos", "vneg", "vlpair", "vlf", "all"'
                raise ValueError(msg)
        if set(block_type.keys()) != set(cassettes):
            raise ValueError('Block type dict does not match cassettes list')

        if segments_type not in ('period', 'half_period'):
            raise ValueError('Invalid segments_type value. Valid options: ' +
                                                '"period" or "half_period"')

        if zmin_pe is None:
            zmin_pe = zmin

        if zmax_pe is None:
            zmax_pe = zmax

        self._zmin = zmin
        self._zmax = zmax
        self._znpts = int(znpts)
        self._cassettes = cassettes
        self._block_type = block_type
        self._segments_type = segments_type
        self._energy = energy
        self._rkstep = rkstep
        self._xpos = xpos
        self._ypos = ypos
        self._zmin_pe = zmin_pe
        self._zmax_pe = zmax_pe
        self._include_pe = include_pe
        self._field_comp = field_comp
        self._solved_shim = solved_shim
        self._solved_matrix = solved_matrix

    @property
    def zmin(self):
        """Initial longitudinal position [mm]."""
        return self._zmin
    
    @property
    def zmax(self):
        """Final longitudinal position [mm]."""
        return self._zmax
    
    @property
    def znpts(self):
        """Number of sampling points for field integrals."""
        return self._znpts
    
    @property
    def cassettes(self):
        """List of strings specifying which cassettes will be used in shimming.
        """
        return self._cassettes
    
    @property
    def block_type(self):
        """String specifying which types of blocks will be used for shimming."""
        return self._block_type
    
    @property
    def segments_type(self):
        """Defines how field zeros are used to obtain segments limits."""
        return self._segments_type
    
    @property
    def energy(self):
        """Electron energy at the beam [KeV]."""
        return self._energy
    
    @property
    def rkstep(self):
        """Step to solve the trajectories equations of motion [mm]."""
        return self._rkstep
    
    @property
    def xpos(self):
        """Initial x transversal trajectory position [mm]."""
        return self._xpos
    
    @property
    def ypos(self):
        """Initial y transversal trajectory position [mm]."""
        return self._ypos
    
    @property
    def zmin_pe(self):
        """Lower z bound for list of poles in phase error calculations [mm]."""
        return self._zmin_pe
    
    @property
    def zmax_pe(self):
        """Upper z bound for list of poles in phase error calculations [mm]."""
        return self._zmax_pe
    
    @property
    def include_pe(self):
        """If True, the calculation for segment slopes also writes the phase
        errors to output file.
        """
        return self._include_pe
    
    @property
    def field_comp(self):
        """Force the use of x or y field components.
        > field_comp==0 -> Bx
        > field_comp==1 -> By
        """
        return self._field_comp
    
    @property
    def solved_shim(self):
        """Boolean. If True, magnetostatic problem is solved before calculating
        shimming signature field. Otherwise, solve method is not run.
        """
        return self._solved_shim
    
    @property
    def solved_matrix(self):
        """Boolean. If True, magnetostatic problem is solved before calculating
        each shim. Otherwise, solve method is not run.
        """
        return self._solved_matrix

    @staticmethod
    def get_rounded_shims(shims, possible_shims):
        """Returns list of feasible shims which best approximate input shims.

        Args:
            shims (list): List of ideal/desired shims.
            possible_shims (list): List of available shims.

        Returns:
            list: List of available shims which are the closest to input shims.
        """
        shims_round = []
        for shim in shims:
            shim_round = min(possible_shims, key=lambda x: abs(x-shim))
            shims_round.append(shim_round)
        return shims_round

    @staticmethod
    def calc_svd(response_matrix):
        """Singular value decomposition (SVD) of the input response_matrix:

        response_matrix = u @ s @ vt
            Where:
            > @ denotes matrix multiplication.
            > u and vt are unitary transformation matrices
            > s is a rectangular diagonal matrix, in which s[i,i]
              are the singular values and s[i,j] == 0 for i != j.

        Columns of u and vt are orthonormal basis vector for the spaces
        of the inputs and outputs of the response matrix.
        If M>N (M<N) the last column (line) of u (vt) is excluded in the
        output. Such column (line) is always multiplied by 0 values in s.

        Args:
            response_matrix (list, M x N): Input matrix
                for singular value decomposition.

        Returns:
            numpy.ndarray, M x min(M,N): Left matrix in decomposition, u.
            numpy.ndarray, min(M,N): 1d s[i,i] singular values list.
            numpy.ndarray, min(M,N) x N: Right matrix in decomposition, v.
        """
        u, sv, vt = _np.linalg.svd(response_matrix, full_matrices=False)
        return u, sv, vt

    @staticmethod
    def calc_inv_matrix(u, sv, vt, nsv=None):
        """Calculates the inverse of the matrix u @ s @ vt.

        Since u and vt are orthogonal matrices and s is diagonal with
        elements given by sv, the inverse is:
            u.T @ (1/sv) @ vt.T
        Where @ represents matrix multiplication, X.T is the transpose of
        X and (1/sv) is a rectangular diagonal matrix with elements 1/sv[i].
        (1/sv actually represents the transpose of the reciprocals matrix
        obtained from the original s SVD matrix)

        If an inverse does not exist (including the case of non-square SVD
        decomposed matrices), this procedure provides a pseudoinverse that
        approximates the inverse:
            (u.T @ (1/sv) @ vt.T)  @  (u @ sv @ vt)  ~  1 (identity matrix)

        Args:
            u (numpy.ndarray, M x min(M,N)): Left orthogonal matrix from SVD.
            sv (numpy.ndarray, min(M,N)): 1d singular values list from SVD.
            vt (numpy.ndarray, min(M,N) x N): Right orthogonal matrix from SVD.
            nsv (int, optional): Number of singular values to be considered,
                if nsv < len(sv), last (len(sv) - nsv) values are set to 0.
                if nsv >= len(sv), all singular values are considered.
                Defaults to None, in which case, nsv = len(sv).

        Returns:
           numpy.ndarray, N x M: Inverse (or pseudoinverse) matrix.
        """
        if nsv is None:
            nsv = len(sv)

        svinv = 1/sv
        svinv[nsv:] = 0
        minv = vt.T*svinv @ u.T
        return minv

    @staticmethod
    def get_weights_matrix(weights):
        """From a weights vector, get a diagonal matrix.

        After input vector is normalized, the square roots of its components
        are the diagonal elements of the returned matrix.

        This matrix is used for giving different weights to the different
        optimizable parameters (slopes and, possibly, phase errors).
        See help on calc_shims method for more details.

        Args:
            weights (list, N): Input weights vector.

        Returns:
            numpy.ndarray, N x N: Diagonal weights matrix.
        """
        weights_norm = _np.array(weights)/_np.linalg.norm(weights)
        weights_matrix = _np.diag(_np.sqrt(weights_norm))
        return weights_matrix

    @staticmethod
    def fit_trajectory_segments(trajectory, segs, max_size, full_output=False):
        """Performs linear fits on trajectory segments.

        Args:
            trajectory (list, Nx6): Nested list of vectors [x,y,z,x',y',z'],
                with positions x, y, z in mm and velocities x',y',z' in rad
                or dimensionless (trajectory parametrized by its length).
            segs (list, K): Longitudinal positions defining segment limits.
                Each segment starts at the first trajectory point with z
                coordinate greater than or equal to an element in segs
                (point immediately after or at segs value).
                Each segment ends in the trajectory point immediately before the
                first point of the next segment (except the last segment).
            max_size (float): Maximum longitudinal length of last segment.
                Such segment ends at the last trajectory point OR at the first
                trajectory point with z greater than (segs[-1] + max_size),
                whichever has smaller z.
            full_output (bool, optional): Determines wether segment limits are
                output (useful for debugging). Defaults to False.

        Returns:
            numpy.ndarray, Kx2: Nested array of pairs containing the linear
                and angular coefficients (respectively) of straight lines
                fitted to X trajectory coordinates of a trajectory segment.
            numpy.ndarray, Kx2: Nested array analogous to array above, for
                the Y trajectory coordinates.
            If full_output == True, additional outputs are given:
                numpy.ndarray, Kx3: Array containing [x,y,z] coordinates of
                    the trajectory points at the start of K segments.
                numpy.ndarray, Kx3: Array containing [x,y,z] coordinates of
                    the trajectory points at the end of K segments.
                list, (K+1): List of indices for trajectory points at the
                    start of K segments and at the end of the last segment.

        """
        trajx = trajectory[:, 0]
        trajy = trajectory[:, 1]
        trajz = trajectory[:, 2]

        seg_start = []
        seg_end = []
        poly_x = []
        poly_y = []

        nsegs = len(segs)

        # For each segs value, find lower i index for which trajz[i] >= value.
        index_list = []
        for pos in segs:
            idx = _np.where(trajz >= pos)[0]
            index_list.append(idx[0])

        # Index for ending last segment must be additionally defined.
        last_index = _np.where(trajz >= segs[-1] + max_size)[0]
        if len(last_index) == 0:
            index_list.append(len(trajz)-1)
        else:
            index_list.append(last_index[0])

        # Perform a linear fit at each trajectory segment defined between
        # consecutive indices in index_list.
        for i in range(nsegs):
            initial = index_list[i]
            final = index_list[i+1]

            tx = trajx[initial:final]
            ty = trajy[initial:final]
            tz = trajz[initial:final]

            if len(tx) == 0:
                break

            seg_start.append([tx[0], ty[0], tz[0]])
            seg_end.append([tx[-1], ty[-1], tz[-1]])

            xcoefs = _np.polynomial.polynomial.polyfit(tz, tx, 1)
            poly_x.append(xcoefs)

            ycoefs = _np.polynomial.polynomial.polyfit(tz, ty, 1)
            poly_y.append(ycoefs)

        seg_start = _np.array(seg_start)
        seg_end = _np.array(seg_end)
        poly_x = _np.array(poly_x)
        poly_y = _np.array(poly_y)

        if full_output:
            return poly_x, poly_y, seg_start, seg_end, index_list
        else:
            return poly_x, poly_y

    @staticmethod
    def read_response_matrix(filename):
        """Read response matrix from file.

        Args:
            filename (str): Name of file containing response matrix.
                File format:
                    Lines corresponding to optimizable parameters (slopes and,
                        possibly, phase errors) and columns corresponding to
                        individual shims (each one consisting in displacing
                        one block or a pair of blocks).
        Returns:
            numpy.ndarray: Response matrix (same format as the output
                from the calc_response_matrix method).
        """
        return _np.loadtxt(filename)

    @staticmethod
    def read_segs(filename):
        """Read list of segments (i.e. segment limits) from file.

        Args:
            filename (str): Name of file with segs list.
                File format:
                    One segment value per line.

        Returns:
            numpy.ndarray: Array of seg values (same format as the output
                from the calc_segments method).
        """
        return _np.loadtxt(filename)

    @staticmethod
    def read_shims(filename):
        """Read shims from file.

        Args:
            filename (str): Name of file with shims list.
                File format:
                            One line for each shim.

        Returns:
            numpy.ndarray: Array of shims (same format as the output from
                the calc_shims method).
        """
        return _np.loadtxt(filename)

    @staticmethod
    def read_error(filename):
        """Read errors from file (difference between optimizable parameters
        for model and measurement).

        Args:
            filename (str): Name of errors file.
                File format:
                    One line for each error, associated with a parameter.

        Returns:
            numpy.ndarray: Errors array (same format as the output from
                the calc_error method).
        """
        return _np.loadtxt(filename)

    @staticmethod
    def read_results(filename):
        """Read results file.

        Args:
            filename (str): Results file.
                File format:
                    JSON format containing dictionary of objects dictionaries
                    with keys given by labels. For a description of the data
                    in each object dictionary, see help on calc_results method.

        Returns:
            dict: Results dictionary (same format as the output from the
                calc_results method)
        """
        with open(filename, 'r') as f:
            results = _json.load(f)
        return results

    @staticmethod
    def read_fieldmap(filename, nr_periods, period, gap):
        """Read field map from file and returns an InsertionDeviceData object.

        Args:
            filename (str): Name of file containing field map.
                File format:
                    If present, header ends with a line containing the
                    string '--------'. After header each line corresponds
                    to a (x,y,z) point, and has the format "x y z bx by bz"
                    containing positions in mm and field components in T.
            nr_periods (int): Number of periods in the insertion device,
                stored as an attribute in the returned object.
            period (float): Period length, in mm, of the insertion device,
                stored as an attribute in the returned object.
            gap (float): Gap, in mm, of the insertion device, stored as an
                an attribute in the returned object.

        Returns:
            InsertionDeviceData: Data object with input containing the read
                field data as raw_data (list of x, y, z positions and mm and
                bx, by, bz fields in T).
        """
        data = _insertiondevice.InsertionDeviceData(
            nr_periods=nr_periods, period_length=period,
            gap=gap, filename=filename)
        return data

    @staticmethod
    def read_block_names(filename):
        """Read block names from file.

        Args:
            filename (str): Name of file with names.
                File format:
                    Each line contains the block names corresponding to
                    a single shim.

        Returns:
            numpy.ndarray: Array of block names.
        """
        return _np.loadtxt(filename, dtype=str)

    @staticmethod
    def read_rescale_factor(filename):
        """Read rescaling factor from a rescaling log file in JSON format.

        The returned float value for the rescaling factor should be keyed by
        'fres' (str) in the JSON file, and represents the factor by which the
        magnetization is multiplied for matching a given field measurement.

        Args:
            filename (str): Name of file with names.
                File format:
                    JSON file (log exported by get_rescale_factor) in which
                    the rescale factor is keyed by the string 'fres'.

        Returns:
            float: Rescaling factor.
        """
        with open(filename, 'r') as f:
            results = _json.load(f)
        return results['fres']

    def _calc_traj(self, obj, xl, yl):
        """Calculate trajectory of electron with initial transversal velocity
            (xl,yl) passing through a field source object.

        Source object may be an instance of FieldModel, FieldData, or of any
        class which is derived from them.

        The remaining necessary parameters for trajectory calculation are
        attributes of the self UndulatorShimming object (beam energy, initial
        positions, final z position and Runge-Kutta step).

        Args:
            obj (FieldModel or FieldData): Field source object for which the
                the trajectory is calculated.
            xl (float): Initial x transversal velocity, parametrized by
                trajectory length. In rad or dimensionless.
            yl (float): Initial y transversal velocity, parametrized by
                trajectory length. In rad or dimensionless.

        Returns:
            numpy.ndarray: Electron trajectory as [x, y, z, x', y', z'] nested
                list of x,y,z positions in mm and x',y',z' velocities in rad
                (dimensionless).
        """
        zl = _np.sqrt(1 - xl**2 - yl**2)
        traj = obj.calc_trajectory(
            self.energy,
            [self.xpos, self.ypos, self.zmin, xl, yl, zl],
            self.zmax, self.rkstep)
        return traj

    def _calc_phase_error(self, obj, traj):
        """Calculate the phase error of a trajectory in relation to a
            sinusoidal field object.

        Sinusoidal field object may be an instance of InsertionDeviceData,
        InsertionDeviceModel, Cassette, or any class which derived from them.

        The remaining necessary parameters for phase error calculation are
        attributes of the self UndulatorShimming object (beam energy, minimum
        and maximun z coordinates and field component switch).

        Args:
            obj (InsertionDeviceData, InsertionDeviceModel or Cassette): Object
                for calculating sinuosidal field. Phase error of the provided
                trajectory will be caluclated in relation to such field.
            traj (list): Electron trajectory as [x, y, z, x', y', z'] nested
                list of x,y,z positions in mm and x',y',z' velocieites in rad
                (dimensionless).
        Returns:
            list: List of poles z positons (in mm).
            numpy.ndarray: List of phase erros at poles (in rad).
            numpy.float64: Phase error rms (in rad).
        """
        bx_amp, by_amp, _, _ = obj.calc_field_amplitude()
        zpe, pe, pe_rms = obj.calc_phase_error(
            self.energy, traj, bx_amp, by_amp,
            zmin=self.zmin_pe, zmax=self.zmax_pe,
            field_comp=self.field_comp)
        return zpe, pe, pe_rms

    def _calc_field_integrals(self, obj):
        """Calculate magnetic field integrals from field source object.

        Source object may be an instance of FieldModel, FieldData, or of any
        class which is derived from them.

        The remaining necessary parameters for field integrals calculation are
        attributes of the self UndulatorShimming object (minimum and maximun z
        coordinates and number of z points for sampling).

        Args:
            obj (FieldModel or FieldData): Field source object for which the
                the field integrals are calculated.

        Returns:
            numpy.ndarray: Nested list of first integrals [ibx, iby, ibz],
                one for each longitudinal point (in G.cm).
            numpy.ndarray: Nested list of second integrals [iibx, iiby, iibz],
                one for each longitudinal point (in kG.cm2).
        """
        z = _np.linspace(self.zmin, self.zmax, self.znpts)
        ib, iib = obj.calc_field_integrals(z_list=z)
        return ib, iib

    def calc_rescale_factor(self, model, meas, filename=None,
                            solved=True, **kwargs):
        """Determine rescale factor by which magnetizations in input Radia model
            should be scaled so that its field profile matches the one in an input
            field data object.

        Args:
            model (Block, Cassette, Delta, AppleX, AppleII, APU or Planar):
                FieldModel object containing magnetized blocks with characteristic
                magnetization modulus (mr)
            meas (FieldSource): First object for calculating field profile,
                typically a FieldData object.
            filename (str, optional): If provided, a log file containing
                information on the rescaling procedure, including the
                resulting scaling factor, will be saved to this file in JSON
                format. Rescale factor is keyed by a 'fres' string.
                Defaults to None.
            **kwargs: additional keyword arguments optionally passed to
                calc_field_amplitude, which is called for finding the
                amplitudes used for scaling.
                By default, such method runs with its default values,
                which are ok for most use cases. Check the documentation
                on calc_field_amplitude for details.

        Returns:
            float: scaling factor. Ratio between field amplitude fitted to meas
                field profile and field amplitude fitted to model field profile.
                Fitted component for determining amplitudes is x, y or sqrt(x^2 +
                y^2), depending on the value of field_comp.
        """
        if solved:
            model.solve()
        bx_model, by_model, _, _ = model.calc_field_amplitude(**kwargs)
        bx_meas, by_meas, _, _ = meas.calc_field_amplitude(**kwargs)

        if self.field_comp == 0:
            fres = bx_meas/bx_model
        elif self.field_comp == 1:
            fres = by_meas/by_model
        else:
            b_model = _np.sqrt(bx_model**2 + by_model**2)
            b_meas = _np.sqrt(bx_meas**2 + by_meas**2)
            fres = b_meas/b_model

        if filename is not None:
            with open(filename, '+w') as f:
                rescale_log = {
                    'calc_field_amplitude_kwargs':kwargs,
                    'model_bx_amplitude':bx_model,
                    'model_by_amplitude':by_model,
                    'meas_bx_amplitude':bx_meas,
                    'meas_by_amplitude':by_meas,
                    'fres':fres
                }
                _json.dump(rescale_log, f, indent=2)

        return fres

    def calc_segments(self, obj, filename=None):
        """Generate longitudinal positions list for defining segment limits
            (see fit_trajectory_segments help for how such list might be used).

        The positions are based on the zeros of a field component, which is
        the one with greater amplitude produced by a given field source object
        (or determined by the field_comp object attribute, if it is not None).
        The segments_type object attribute is used as follows:
            If segments_type=='period', every other zero is used as segment
                limit, starting from the first zero.
            If segments_type=='half_period' (default), all zeros are used as
                segment limits.
        Regardless of segments_type value, additional limits are appended at
        the beginning and end of the limits list, separated by period_length
        (of object) from the previous first and last limits.

        Source objects may be an instance of FieldModel, FieldData, or of any
        class which is derived from them.

        This method uses the following UndulatorSHimming object attributes:
            > zmin, zmax, znpts, field_comp, segments_type.

        Args:
            obj (FieldModel or FieldData): Field source object whose zeros
                are used for determining base seg positions.
            filename (str, optional): If provided, this will be the name
                of a file in which the outputs of this function will also be
                written. Defaults to None.
                    File format:
                        One segment value per line.

        Returns:
            numpy.ndarray: Longitudinal positions list defining segment limits
                (see fit_trajectory_segments for how it might be used).
        """
        zpos = _np.linspace(self.zmin, self.zmax, self.znpts)
        field = obj.get_field(z=zpos)

        if self.field_comp:
            comp = self.field_comp
        else:
            freqs = _np.array([2*_np.pi/obj.period_length])
            amps, *_ = _utils.fit_fourier_components(field, freqs, zpos)
            comp = _np.argmax(amps)

        spos = obj.find_zeros(zpos, field[:, comp])

        if self.segments_type == 'period':
            segs = spos[::2]

        elif self.segments_type == 'half_period':
            segs = spos

        segs = _np.insert(
            segs, 0, segs[0] - obj.period_length)
        segs = _np.insert(
            segs, -1, segs[-1] + obj.period_length)

        segs = sorted(segs)

        if filename is not None:
            _np.savetxt(filename, segs)

        return segs

    def calc_slope_and_phase_error(self, obj, segs, xl, yl, filename=None):
        """Returns slopes of linear fits performed on segments of an averaged
        trajectory (1 period moving average).

        The trajectory is calculated for an electron with initial transversal
        velocity (xl,yl) passing through a sinusoidal field object. The object
        also provides the period used for trajectory averaging and for defining
        the maximum length of last segment.
        Sinusoidal field object may be an instance of InsertionDeviceData,
        InsertionDeviceModel, Cassette, or any class which derived from them.

        Args:
            obj (InsertionDeviceData, InsertionDeviceModel or Cassette): Object
                in which the trajectory is calculated and from which the period
                length is obtained.
            segs (list, K): Longitudinal positions defining segment limits
                (see help on fit_trajectory_segments for details on how this
                list is used to separate the trajectory into segments).
            xl (float): Initial x transversal velocity for trajectory,
                parametrized by trajectory length. In rad or dimensionless.
            yl (float): Initial y transversal velocity for trajectory,
                parametrized by trajectory length. In rad or dimensionless.
            filename (str, optional): If provided, this will be the name of
                a file in which outputs will be written. Defaults to None.
                If object attribute include_pe==False (default), only slopes
                will be written. If include_pe==True, phase errors will also
                be written.
                File format:
                        One x coordinate segment slope per line, folowed by
                        one y coordinate segment slope per line, followd by
                        (if include_pe==True) one phase error per line.

        Returns:
            numpy.ndarray, K: Slopes adjusted to the x position components
                of linear segments from averaged trajectory.
            numpy.ndarray, K: Slopes adjusted to the y position components
                of linear segments from averaged trajectory.
            numpy.ndarray: List of phase errors at poles defined by
                SinusoidalFieldSource.calc_phase_error method (in rad).
        """
        traj = self._calc_traj(obj, xl, yl)
        avgtraj = obj.calc_trajectory_avg_over_period(traj)

        px, py = self.fit_trajectory_segments(
            avgtraj, segs, obj.period_length)

        sx = px[:, 1]
        sy = py[:, 1]

        if self.include_pe:
            _, pe, _ = self._calc_phase_error(obj, traj)
            data = _np.concatenate([sx, sy, pe])
        else:
            pe = None
            data = _np.concatenate([sx, sy])

        if filename is not None:
            _np.savetxt(filename, data)

        return sx, sy, pe

    def get_block_names(self, model, filename=None, flatten=False):
        """Get list of names for the blocks used in shimming.

        The blocks are selected from the cassettes in the cassettes attribute
        and filtered and grouped according to block_type attribute (see help
        on get_shimming_blocks for details on the filtering and grouping).

        Model must be an instance of InsertionDeviceModel or of a derivate
        class AND must have non-empty cassettes dictionary (see help on
        get_shimming_blocks for details on the available built-in models).

        By default, the returned numpy array will have the same shame as the
        shimming elements array. But it may be flattened as an 1d array of
        blocks by the 'flatten' argument.

        Args:
            model (InsertionDeviceModel derivate, see above): Device model
                with the considered cassettes (cassettes attribute).
            filename (str, optional):  If provided, this will be the name of
                a file in which names will be written. Defaults to None.
                File format:
                    One name per line
            flatten (bool, optional): If True, names array will be flattened
                to a 1d array. Defaults to False.

        Returns:
            numpy.ndarray, NxM: array of names for blocks used in shimming
                (N sets/elements of M blocks).
        """
        access_names = _np.vectorize(lambda block: block.name)
        blocks = self.get_shimming_blocks(model, 'all')
        names = access_names(blocks)
        if flatten:
            names = names.flatten()
        if filename is not None:
            _np.savetxt(filename, names, fmt='%s')
        return names

    def get_shimming_blocks(self, model, cassette):
        """Get array of blocks from a particular cassete of a model based
            on a type defined by the type_block object attribute.

        Model must be an instance of InsertionDeviceModel or of a derivate
        class AND must have non-empty cassettes dictionary.
        Currently available built-in model classes are:
            Delta, AppleX, AppleII, APU, Planar, DeltaPrototype, DeltaSabia,
            DeltaCarnauba, AppleXSabia, AppleXCarnauba, AppleIISabia,
            AppleIICarnauba, Kyma22, Kyma58, HybridAPU, HybridPlanar,
            MiniPlanarSabia.

        Args:
            model (InsertionDeviceModel derivate, see list above): Device model
                with the cassette from which the blocks will be listed.
            cassette (str): Key specifying the cassette in the cassettes
                dictionary of the model.
                If cassette=='all', the function will be executed for all
                cassettes, in the order as they appear in the cassettes
                object attribute. A single NxM array of all the blocks
                will be returned.

        Returns:
            numpy.ndarray, NxM: Array containing blocks.Block objects.
                The blocks are filtered from the specified cassette and
                grouped according to the block_type. Only non-termination
                blocks are included.
                The array shape represents N shimming elements, each one
                conssisting of M blocks. In the 'v', 'vpos' and 'vneg' cases,
                each element is a single block (Nx1). For the 'vlpair' case,
                each element is an array of two blocks (Nx2), and each block
                is displaced as a single unit during the shimming procedure.
        """
        if cassette == 'all':

            shim_elements = [self.get_shimming_blocks(model, cas)
                             for cas in self.cassettes]
            shim_elements = _np.concatenate(shim_elements, axis=0)

        else:
            cas = model.cassettes[cassette]
            cas_block_type = self.block_type[cassette]
            mag = _np.array(cas.magnetization_list)
            blocks = _np.array(cas.blocks)

            # Eliminate termination blocks.
            nr_start = len(cas.start_blocks_length)
            nr_end = len(cas.end_blocks_length)
            if nr_end == 0:
                regular_mag = mag[nr_start:]
                regular_blocks = blocks[nr_start:]
            else:
                regular_mag = mag[nr_start:-nr_end]
                regular_blocks = blocks[nr_start:-nr_end]

            # Total magnetization outside y (tranversal 'vertical') direction:
            mres_zx = _np.sqrt(regular_mag[:, 0]**2 + regular_mag[:, 2]**2)
            mres_xy = _np.sqrt(regular_mag[:, 0]**2 + regular_mag[:, 1]**2)

            if cas_block_type == 'v':
                # absolute value of y component is predominant over mres_zx.
                filt = _np.abs(regular_mag[:, 1]) > mres_zx
            elif cas_block_type == 'vpos':
                # y component (with sign) is predominant over mres_zx.
                filt = regular_mag[:, 1] > mres_zx
            elif cas_block_type == 'vneg':
                # negative y component (with sing) is predominant over mres_zx.
                filt = regular_mag[:, 1]*(-1) > mres_zx
            elif cas_block_type == 'vlf':
                # absolute value of y component is predominant over mres.
                filt_v = _np.abs(regular_mag[:, 1]) > mres_zx
                # z component (with sign) is predominant over mres_xy.
                filt_vlf = regular_mag[:, 2] > mres_xy
                # Resulting filter.
                filt = _np.logical_or(filt_v, filt_vlf)
            elif cas_block_type == 'all':
                # all blocks
                filt = _np.array([True]*len(regular_mag[:, 1]))
            elif cas_block_type == 'vlpair':
                # This is a special option which groups the blocks in pairs
                # for shimming, the first block of the pair is a vertical
                # 'v' block. During the shimming, blocks in a pair are
                # displaced together.
                # First, the 'v' filter is defined.
                filt_single = _np.abs(regular_mag[:, 1]) > mres_zx
                # Then, the filter is expanded so that each True value
                # causes the next list element to also be True.
                filt = [filt_single[0]]
                for i in range(1, len(filt_single)):
                    filt.append((filt_single[i] or filt_single[i-1]))

            shim_regular_blocks = regular_blocks[filt]

            # Shim elements are the  items which are going to be moved.
            # They mey be a single block (array with one block) or more
            # than one block (array of blocks).
            if cas_block_type in ['v', 'vpos', 'vneg', 'vlf', 'all']:
                # In these cases, blocks are shimmed individually.
                shim_elements = [[x] for x in shim_regular_blocks]
            elif cas_block_type == 'vlpair':
                # In this case, blocks are grouped in pairs.
                if len(shim_regular_blocks)%2 == 1:
                    raise ValueError('Could not determine "vlpair" type ' + \
                                        'block pairs. Odd number of blocks')
                shim_elements = \
                    [[shim_regular_blocks[i], shim_regular_blocks[i+1]] \
                        for i in range(0, len(shim_regular_blocks), 2)]

        shim_elements = _np.array(shim_elements)

        return shim_elements

    def calc_response_matrix(
            self, model, model_segs, filename=None, shim=0.1):
        """Calculate response matrix associated to the effect of individual
        shims to a set of optimizable parameters, including segment slopes,
        and, possibly (if include_pe==True), phase errors.

        Each shim consists in displacing a single block by a small positive
        shift (local y+) or displacing a set of blocks together.
            Examples:
            'vneg'  : a shim, related a single row of the shimming matrix, is
                      the displacement of a single "vertical negative" block
                      (magnetization pointing to local y-).
            'vlpair': a shim, related a single row of the shimming matrix, is
                      the simultaneous displacement of a pair of blocks, a
                      vertical one and a longitudinal one (y+, z-) or (y-, z+).
        Thus, self.block_type specifies the blocks and their grouping, while
        self.cassettes specifies the cassettes from which blocks are selected.

        The slopes (optimizable parameters) are determined with respect to
        the given segment limits list. Phase errors are determined by the
        calc_phase_error method from the input model.

        The resulting matrix represents the linear operation:

            (optimizable parameters) = (response matrix) @ (shims)

        Model must be an instance of InsertionDeviceModel or of a derivate
        class AND must have non-empty cassettes dictionary.
        Currently available built-in model classes are:
            Delta, AppleX, AppleII, APU, Planar, DeltaPrototype, DeltaSabia,
            DeltaCarnauba, AppleXSabia, AppleXCarnauba, AppleIISabia,
            AppleIICarnauba, Kyma22, Kyma58, HybridAPU, HybridPlanar,
            MiniPlanarSabia.

        Args:
            model (InsertionDeviceModel derivate, see list above): Device model
                with the cassettes to be shimmed.
            model_segs (list, K): Longitudinal positions of segment limits
                (see help on fit_trajectory_segments for details on how this
                list is used to separate the trajectory into segments).
            filename (str, optional): File name of format name.extension for
                creating output files. If this argument is given, the following
                files are created:
                    name_mx.extension: in which each line contains the x slopes
                        derivatives with respect to a given shim.
                    name_my.extension: in which each line contains the y slopes
                        derivatives with respect to a given shim.
                    name_mpe.extension: in which each line contains the phase
                        error derivatives with respect to a given shim.
                    name.extension: response matrix, in which each line
                        corresponds to an optimizable parameter (slopes and,
                        possibly, phase errors) and each column corresponds
                        to a given shim.
                Defaults to None.
            shim (float, optional): Displacement (shim) value applied to blocks
                for determining the response matrix. In mm. Defaults to 0.1.

        Returns:
            numpy.ndarray: Response matrix, containing one line per optimized
                parameter (slopes and, possibly, phase errors) and one column
                per shim.
        """
        response_matrix = None

        sx0, sy0, pe0 = self.calc_slope_and_phase_error(
            model, model_segs, 0, 0)

        if filename is not None:
            ext = '.' + filename.split('.')[-1]
            filename_mx = filename.replace(ext, '_mx' + ext)
            filename_my = filename.replace(ext, '_my' + ext)
            filename_mpe = filename.replace(ext, '_mpe' + ext)
            open(filename_mx, 'w').close()
            open(filename_my, 'w').close()
            open(filename_mpe, 'w').close()

        mx = []
        my = []
        mpe = []
        blocks = self.get_shimming_blocks(model, 'all')

        for idx0 in range(len(blocks)):
            for idx1 in range(len(blocks[idx0])):
                blocks[idx0, idx1].shift([0, shim, 0])

            if self.solved_matrix:
                model.solve()
            sx, sy, pe = self.calc_slope_and_phase_error(
                model, model_segs, 0, 0)

            for idx1 in range(len(blocks[idx0])):
                blocks[idx0, idx1].shift([0, -shim, 0])

            dpx = (sx - sx0)/shim
            mx.append(dpx)

            dpy = (sy - sy0)/shim
            my.append(dpy)

            if self.include_pe:
                dpe = (pe - pe0)/shim
                mpe.append(dpe)

            if filename is not None:
                with open(filename_mx, 'a+') as fx:
                    strx = '\t'.join('{0:g}'.format(v) for v in dpx)
                    fx.write(strx + '\n')

                with open(filename_my, 'a+') as fy:
                    stry = '\t'.join('{0:g}'.format(v) for v in dpy)
                    fy.write(stry + '\n')

                if self.include_pe:
                    with open(filename_mpe, 'a+') as fpe:
                        strpe = '\t'.join('{0:g}'.format(v) for v in dpe)
                        fpe.write(strpe + '\n')

        mx = _np.array(mx)
        my = _np.array(my)
        mpe = _np.array(mpe)

        if self.include_pe:
            response_matrix = _np.transpose(_np.concatenate([mx, my, mpe], axis=1))
        else:
            response_matrix = _np.transpose(_np.concatenate([mx, my], axis=1))

        if filename is not None:
            _np.savetxt(filename, response_matrix)

        return response_matrix

    def calc_error(
            self, model, meas, model_segs, meas_segs, filename=None):
        """Calculate difference (errors) between optimizable parameters (slopes
        and, possibly, phase errors) calculated from a model source object and
        an experimental data source object.

        Field object containing radia model may be an instance of the classes
        InsertionDeviceModel, Cassette, or any class which derived from them.
        FIeld object containing measurements must be an instance of the
        InsertionDeviceData class.

        Individual segments lists may be used for the model and measurements
        objects. See help on fit_trajectory_segments for details on how such
        lists are used to separate calculated trajectories into segments.

        Args:
            model (InsertionDeviceModel or Cassette): Object associated to
                Radia model used for calculating optimizable parameters.
            meas (InsertionDeviceData): Object associated to experimental
                measurements used for calculating optimizable parameters.
            model_segs (list): Longitudinal positions defining segment limits.
            meas_segs (list): Longitudinal positions defining segment limits.
            filename (str, optional): If provided, this will be the name
                of a file in which the outputs of this function will also be
                written. Defaults to None.
                    File format:
                        One line for each error, associated to a parameter.

        Returns:
            numpy.ndarray: Array (1d) containing the errors, one for each
                optimizable parameter.
        """
        model_sx, model_sy, model_pe = self.calc_slope_and_phase_error(
            model, model_segs, 0, 0)

        meas_sx, meas_sy, meas_pe = self.calc_slope_and_phase_error(
            meas, meas_segs, 0, 0)

        sx_error = model_sx - meas_sx
        sy_error = model_sy - meas_sy

        if self.include_pe:
            dpe = model_pe - meas_pe
            error = _np.concatenate([sx_error, sy_error, dpe])
        else:
            error = _np.concatenate([sx_error, sy_error])

        if filename is not None:
            _np.savetxt(filename, error)

        return error

    def calc_shims(
            self, response_matrix, error, nsv=None, ws=None, filename=None):
        """From a response matrix, calculate shims that whould result in a
        given errors array.

        Args:
            response_matrix (numpy.ndarray, MxN): Response matrix for M
                optimizable parameters by N shims.
            error (numpy.ndarray, M): Error array associated to optimizable
                parameters for shimming.
            nsv (int, optional): Number of singular values to be considered.
             See help in calc_inv_matrix method for details. Defaults to None.
            ws (list, M, optional): Weights for optmizable parameters.
                If not None, each weight multiplies its corresponding error
                and corresponding line in the response matrix.
                Defaults to None.
            filename (str, optional): If provided, this will be the name
                of a file in which the outputs of this function will also be
                written. Defaults to None.
                    File format:
                        One line for each shim.

        Returns:
            numpy.ndarray, N: Resulting shims associated to input errors.
        """
        if ws is None:
            ws = [1.0]*response_matrix.shape[0]
        w = self.get_weights_matrix(ws)

        # SVD result used for calculating inverse matrix.
        u, sv, vt = self.calc_svd(w @ response_matrix)
        # Original matrix: MxN -> response matrix: NxM
        minv = self.calc_inv_matrix(u, sv, vt, nsv=nsv)
        # N shims = (NxM) @ M errors (parameters)
        shims = minv @ (w @ error)

        if filename is not None:
            _np.savetxt(filename, shims)

        return shims

    def save_shims_to_xls(self, model, shims, filename):
        """Export shim values to excel format.

        Args:
            model (InsertionDeviceModel): Model used from shimming from which
                blocks are taken.
            shims (numpy.ndarray): List of calcualted shims for being saved
                to file.
            filename (str, optional): File to which .xls data will be saved.
                    File format:
                        Two columns, representing block names and respective
                        shims as two columns.
        """
        names = self.get_block_names(model, flatten=True)
        df = _pd.DataFrame({'blocks':names, 'shims':shims})
        df.to_excel(filename)

    def calc_shim_signature(self, model, shims, filename=None):
        """Calculate the field difference between the non-shimmed and
        the shimmed insertion device (shimming signature).

        Model may be an instance of InsertionDeviceModel or any derivate class.

        Args:
            model (InsertionDeviceModel): Model used for calculating fields
                before and after shimming.
            shims (numpy.ndarray): List of shims for which signature is to
                be calculated. The block displacement represented by such
                list are determined by self.cassettes and self.block_type.
            filename (str, optional): If provided, resulting field map will
                be saved in a file with name filename.
                    File format:
                        If present, header ends with a line containing the
                        string '--------'. After header each line corresponds
                        to a (x,y,z) point, and has the format "x y z bx by bz"
                        containing positions in mm and field components in T.

        Returns:
            InsertionDeviceData: Data object with the same number of periods,
                period length and gap as the input model object.
                Contains the resulting signature field (difference between
                shimmemd and unshimmed fields) in the format of raw_data.
                (List of x, y, z positions and mm and bx, by, bz fields in T)
        """
        zpos = _np.linspace(self.zmin, self.zmax, self.znpts)
        field0 = model.get_field(z=zpos)

        count = 0
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(model, cassette)
            for idx0 in range(len(blocks)):
                for idx1 in range(len(blocks[idx0])):
                    blocks[idx0, idx1].shift([0, shims[count], 0])
                count += 1

        if self.solved_shim:
            model.solve()

        field = model.get_field(z=zpos)
        dfield = field - field0

        count = 0
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(model, cassette)
            for idx0 in range(len(blocks)):
                for idx1 in range(len(blocks[idx0])):
                    blocks[idx0, idx1].shift([0, (-1)*shims[count], 0])
                count += 1

        if self.solved_shim:
            model.solve()

        x = [self.xpos]*self.znpts
        y = [self.ypos]*self.znpts
        raw_data = _np.transpose(
            [x, y, zpos, dfield[:, 0], dfield[:, 1], dfield[:, 2]])

        shim_signature = _insertiondevice.InsertionDeviceData(
            nr_periods=model.nr_periods,
            period_length=model.period_length,
            gap=model.gap,
            raw_data=raw_data)

        if filename is not None:
            shim_signature.save_fieldmap(
                filename, self.xpos, self.ypos, zpos)

        return shim_signature

    def calc_shimmed_meas(self, meas, shim_signature, filename=None):
        """From a given shimming signature object (InsertionDeviceData) and an
        experimental field data object (also InsertionDeviceData), generate
        a third field data object in which the field is equal to the signature
        field added to the experimental field.

        Returned object represents the shimmed version of the experimental
        measurement. The field that would be observed if the shimming had
        been applied to the insertion device.

        Args:
            meas (InsertionDeviceData): Object containing experimental field
                data (as its raw_data attribute).
            shim_signature (InsertionDeviceData): Object containing field
                signature from shimming (such as an object returned by the
                calc_shim_signature method)
            filename (str, optional): If provided, resulting field map will
                be saved in a file with name filename.
                    File format:
                        If present, header ends with a line containing the
                        string '--------'. After header each line corresponds
                        to a (x,y,z) point, and has the format "x y z bx by bz"
                        containing positions in mm and field components in T.

        Returns:
            InsertionDeviceData: Data object with the same number of periods,
                period length and gap as the input MEASUREMENT object.
                Contains the resulting shimmed field as raw_data.
                (List of x, y, z positions and mm and bx, by, bz fields in T)
        """
        zpos = _np.linspace(self.zmin, self.zmax, self.znpts)
        field = meas.get_field(z=zpos)
        x = [self.xpos]*self.znpts
        y = [self.ypos]*self.znpts
        raw_data = _np.transpose(
            [x, y, zpos, field[:, 0], field[:, 1], field[:, 2]])
        shimmed_meas = _insertiondevice.InsertionDeviceData(
            nr_periods=meas.nr_periods,
            period_length=meas.period_length,
            gap=meas.gap,
            raw_data=raw_data)

        shimmed_meas.add_field(shim_signature)

        if filename is not None:
            shimmed_meas.save_fieldmap(
                filename, self.xpos, self.ypos, zpos)

        return shimmed_meas

    def calc_results(self, objs, labels, xls=None, yls=None, filename=None):
        """Receives a list of objects, calculates various for them (see Returns
            section), and compiles the results in a nested dictionary.
            Dictionary entries are keyed by the labels argument. Entries are
            dictionaries themselves, compiling the results for the objects.

        Objects may be of the types InsertionDeviceData, InsertionDeviceModel,
            Cassette, or any class which is derived from them.

        Args:
            objs (list): List of objects (see description above) for which
                data will be stored in the returned dicionary.
            labels (str): List of keys for the nested result dictionaries (one
                label for each object)
            xls (list of floats, optional): Transversal x positions for
                calculating trajectories for each object. If None, will be
                set to [0]*len(objs). Defaults to None.
            yls (list of floats, optional): Transversal y positions for
                calculating trajectories for each object. If None, will be
                set to [0]*len(objs). Defaults to None.
            filename (str, optional): If provided, results dictionary will
                be saved in a file with this name in json format.
                File format:
                    JSON format containing dictionary of object dictionaries
                    with keys given by labels. Data in each dictionary is
                    described in Returns section bellow.

        Returns:
            dict: Nested dictionary containing one dictionary per object,
                each object dictionary contains the following data:
                Trajectory:
                    'trajx' - x position (list, in micron)
                    'trajy' - y position (list, in micron)
                    'trajz' - z position (list, in mm)
                    'trajxl' - x velocity (list, in rad or dimensionless)
                    'trajyl' - y velocity (list, in rad or dimensionless)
                    'trajzl' - z velocity (list, in rad or dimensionless)
                Phase errors:
                    'zpe' - Pole z positions (list, in mm)
                    'pe' - Phase errors (list, in degrees)
                    'perms' - RMS of phase errors (float, in degrees)
                Field integrals of (bx,by,bz) field:
                    'ibx' - First bx integral (float, in G.cm)
                    'iby' - First by integral (float, in G.cm)
                    'ibz' - First bz integral (float, in G.cm)
                    'iibx' - Second bx integral (float, in  kG.cm²)
                    'iiby' - Second bx integral (float, in  kG.cm²)
                    'iibz' - Second bx integral (float, in  kG.cm²)
        """
        results = {}

        if xls is None:
            xls = [0]*len(objs)

        if yls is None:
            yls = [0]*len(objs)

        for obj, label, xl, yl in zip(objs, labels, xls, yls):
            traj = self._calc_traj(obj, xl, yl)
            zpe, pe, pe_rms = self._calc_phase_error(obj, traj)
            ib, iib = self._calc_field_integrals(obj)
            r = {}
            r['trajx'] = list(traj[:, 0]*1000)
            r['trajy'] = list(traj[:, 1]*1000)
            r['trajz'] = list(traj[:, 2])
            r['trajxl'] = list(traj[:, 3])
            r['trajyl'] = list(traj[:, 4])
            r['trajzl'] = list(traj[:, 5])
            r['zpe'] = list(zpe)
            r['pe'] = list(pe*180/_np.pi)
            r['perms'] = pe_rms*180/_np.pi
            r['ibx'] = list(ib[:, 0])
            r['iby'] = list(ib[:, 1])
            r['ibz'] = list(ib[:, 2])
            r['iibx'] = list(iib[:, 0])
            r['iiby'] = list(iib[:, 1])
            r['iibz'] = list(iib[:, 2])
            results[label] = r

        if filename is not None:
            with open(filename, '+w') as f:
                _json.dump(results, f)
        return results

    def plot_results(
            self, results, table_fontsize=12,
            table_decimals=1, filename=None, suptitle=None,
            trajx_lim=None, trajy_lim=None, pe_lim=None, figsize=(12,6)):
        """Generate figure from results dictionary.

        Args:
            results (dict): Results dictionary, in the format of the output
                from calc_results method.
            table_fontsize (int, optional): Table font size. Defaults to 12.
            table_decimals (int, optional): Number of decimals for rounding
                values displayed in table. Defaults to 1.
            filename (str, optional): If not None, represents file in which
                figure is saved. Defaults to None.
            suptitle (str, optional): Title for figure. Defaults to None.
            trajx_lim (list, 2, optional): Vertical axis lower and upper limits
                when plotting x component of trajectory. Defaults to None.
            trajy_lim (list, 2, optional): Vertical axis lower and upper limits
                when plotting y component of trajectory. Defaults to None.
            pe_lim (list, 2, optional): Vertical axis lower and upper limits
                when plotting phase errors. Defaults to None.
            figsize (tuple, 2, optional): Pair of floats specifying figure size
                Defaults to (12, 6).
        """
        labels = list(results.keys())

        spec = _gridspec.GridSpec(
            ncols=2, nrows=2,
            wspace=0.25, hspace=0.25,
            left=0.1, right=0.95, top=0.95, bottom=0.15)
        fig = _plt.figure(figsize=figsize)
        ax0 = fig.add_subplot(spec[0, 0])
        ax1 = fig.add_subplot(spec[0, 1])
        ax2 = fig.add_subplot(spec[1, 0])
        ax3 = fig.add_subplot(spec[1, 1])

        values = []
        for label in labels:
            data = results[label]

            if 'predicted' in label.lower():
                alpha = 0.5
            else:
                alpha = 1.0

            ax0.plot(data['trajz'], data['trajx'], label=label, alpha=alpha)
            ax1.plot(data['trajz'], data['trajy'], label=label, alpha=alpha)

            ax2.plot(data['zpe'], data['pe'], '-o', label=label, alpha=alpha)

            values.append(
                [data['ibx'][-1], data['iby'][-1],
                data['iibx'][-1], data['iiby'][-1],
                data['perms']])

        ax0.set_xlabel('Z [mm]')
        ax0.set_ylabel('TrajX [um]')
        ax0.grid(alpha=0.3)
        ax0.legend(loc='best')
        ax0.patch.set_edgecolor('black')
        ax0.patch.set_linewidth(2)
        if trajx_lim is not None:
            ax0.set_ylim(trajx_lim)

        ax1.set_xlabel('Z [mm]')
        ax1.set_ylabel('TrajY [um]')
        ax1.grid(alpha=0.3)
        ax1.patch.set_edgecolor('black')
        ax1.patch.set_linewidth(2)
        if trajy_lim is not None:
            ax1.set_ylim(trajy_lim)

        ax2.set_xlabel('Z [mm]')
        ax2.set_ylabel('Phase error [deg]')
        ax2.grid(alpha=0.3)
        ax2.patch.set_edgecolor('black')
        ax2.patch.set_linewidth(2)
        if pe_lim is not None:
            ax2.set_ylim(pe_lim)

        values = _np.round(
            _np.transpose(values), decimals=table_decimals)

        ax3.patch.set_visible(False)
        ax3.axis('off')
        table = ax3.table(
            cellText=values,
            colLabels=labels,
            rowLabels=[
                'IBx [G.cm]',
                'IBy [G.cm]',
                'IIBx [kG.cm2]',
                'IIBy [kG.cm2]',
                'PhaseErr [deg]',
                ],
            loc='center',
            colLoc='center',
            rowLoc='center',
            )
        table.auto_set_font_size(False)
        table.set_fontsize(table_fontsize)
        table.scale(0.7, 2)

        if suptitle is not None:
            _plt.suptitle(suptitle)

        if filename is not None:
            _plt.savefig(filename, dpi=400)

        return fig
