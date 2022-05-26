
import numpy as _np
from scipy import signal as _signal
from scipy import optimize as _optimize
import radia as _rad


def set_len_tol(absolute=1e-12, relative=1e-12):
    """Set absolute and relative randomization for Radia lengths.

    This is a wrapper function for the radia.FldLenTol function.

    The randomizaton values are internal parameters of Radia calculations
    for which the default values are tipically optmial. Too small values
    may lead to errors.    

    Args:
        absolute (float, optional): Absolute randomization magnitude.
            Defaults to 1e-12.
        relative (float, optional): Relative randomization magnitude.
            Defaults to 1e-12.

    Returns:
        int: 1
    """
    return _rad.FldLenTol(absolute, relative)


def delete_all():
    """Deletes all Radia objects.

    This is a wrapper function for the radia.UtiDelAll function.

    Deletes all Radia elements, including field sources, materials,
    transformations and interaction matrices.

    Returns:
        int: 0
    """
    return _rad.UtiDelAll()


def cosine_function(z, bamp, freq, phase):
    """Cosine function with specified amplitude, frequency and phase.

    Args:
        z (float or numpy.ndarray): Cosine argument parameter.
        bamp (float): Amplitude multiplying cosine.
        freq (float): Cosine frequency multiplying z parameter.
        phase (float): Phase added to the cosine argument.

    Returns:
        float or numpy.ndarray: Cosine function, bamp*cos(freq*z + phase)
    """
    return bamp*_np.cos(freq*z + phase)


def hybrid_undulator_pole_length(gap, period_length):
    """Hybrid undulator optmized pole thickness.

    Equation and coefficients as described in:
        J. Bahrdt, E. Gluskin, Nuclear Instruments and Methods
        in Physics Research Section A 907, 149–168 (2018).
        doi: 10.1016/j.nima.2018.03.069

    Args:
        gap (float): Magnetic gap
            (lenght units, same as used for period_length, ex: mm).
        period_length (float): Period length
            (lenght units, same as used for gap, ex: mm).

    Returns:
        float: Optmized pole thickness resulting from the applyed model
            (lenght units, same as used for inputs, ex: mm).
    """
    a = 5.939
    b = -11.883
    c = 16.354
    d = -8.55
    gp = gap/period_length
    pole_length = gap*a*_np.exp(b*gp + c*(gp**2) + d*(gp**3))
    return pole_length


def fitting_matrix(tim, freqs):
    """Create the matrix used for fitting of Fourier components.

    The ordering of the matrix is the following:
        mat[i, 2*j] = cos(freqs[j]*tim[i])
        mat[i, 2*j+1] = sin(freqs[j]*tim[i])

    Args:
        tim (numpy.ndarray): Array of times, or other quantity parameterizing
            the fitted data, such as position. Defines frequency units.
        freqs (numpy.ndarray): Array with frequencies to fit (in units of
            the reciprocal of tim units).

    Returns:
        numpy.ndarray: Fitting matrix of shape (len(tim), 2*len(freqs))
    """
    mat = _np.zeros((tim.size, 2*freqs.size))
    arg = freqs[None, :]*tim[:, None]
    cos = _np.cos(arg)
    sin = _np.sin(arg)
    mat[:, ::2] = cos
    mat[:, 1::2] = sin
    return mat


def fit_fourier_components(data, freqs, tim):
    """Fit Fourier components in signal for the given frequencies.

    Args:
        data (numpy.ndarray, NxM): Signal to be fitted consisting of M
            columns of data. Each element or line of data is related to
            an element of tim.
        freqs (numpy.ndarray, K): K frequencies to fit Fourier components
            (in units of the reciprocal of tim units)
        tim (numpy.ndarray, N): Time vector for data columns, or vector of
            other quantity parameterizing the data, such as position. Defines
            frequency units. 

    Returns:
        numpy.ndarray, KxM: Fourier amplitudes, modulus of a [C_sin, C_cos]
            vector of the cosine and sine coefficients at a given frequency.
        numpy.ndarray, KxM: Fourier phase, argument of the same [C_sin, C_cos]
            vector (phase==0 means pure sine).
        numpy.ndarray, KxM: Fourier cosine coefficients.
        numpy.ndarray, KxM: Fourier sine coefficients.
        numpy.ndarray, Nx2K: Fourier matrix of sines and cosines, returned
            by the fitting_matrix method.
    """
    mat = fitting_matrix(tim, freqs)
    coeffs, *_ = _np.linalg.lstsq(mat, data, rcond=None)
    cos = coeffs[::2]
    sin = coeffs[1::2]
    amps = _np.sqrt(cos**2 + sin**2)
    phases = _np.arctan2(cos, sin)
    return amps, phases, cos, sin, mat


def calc_cosine_amplitude(pos_list, values_list, freq_guess, maxfev=5000):
    """Fit 3D vector components dependency on 1D positions
         using cosine functions.

    This function may be used for any 1D oscilatory dependency of 3D vector.
    As an example (and typical use) the units described bellow assume the fit
    of a magnetic field 1D position profile, in T and mm.

    Args:
        pos_list (list, N): List of positions (in mm)
        values_list (list, Nx3): List of 3D field vectors associated with the
            positions list. Elements are lists of the three vector components.
            (in T)
        freq_guess (float): Initial guess for the spacial frequencies of the
            fitting cosines. (in 1/mm)
        maxfev (int, optional): maximun number of calls to the least squares
            scipy function during fitting. Default value typically enough.
            Defaults to 5000.

    Raises:
        ValueError: Raised if list of values and list of positions
            are not of same length.

    Returns:
        list, 3: Amplitudes fitted to the components' oscilathions (in T).
        list, 3: Phases fitted to the components' osiclations (dimensionless).
    """
    if len(pos_list) != len(values_list):
        raise ValueError(
            'Inconsistent length between values and position lists.')

    pos_list = _np.array(pos_list)
    values_list = _np.array(values_list)

    vx, vy, vz = _np.transpose(values_list)
    vx_amp_init = _np.max(_np.abs(vx))
    vy_amp_init = _np.max(_np.abs(vy))
    vz_amp_init = _np.max(_np.abs(vz))

    try:
        px = _optimize.curve_fit(
            cosine_function, pos_list, vx,
            p0=[vx_amp_init, freq_guess, 0],
            maxfev=maxfev)[0]
        vx_amp = _np.abs(px[0])
        vx_phase = px[2]
    except Exception:
        vx_amp = 0
        vx_phase = 0

    try:
        py = _optimize.curve_fit(
            cosine_function, pos_list, vy,
            p0=[vy_amp_init, freq_guess, 0],
            maxfev=maxfev)[0]
        vy_amp = _np.abs(py[0])
        vy_phase = py[2]
    except Exception:
        vy_amp = 0
        vy_phase = 0

    try:
        pz = _optimize.curve_fit(
            cosine_function, pos_list, vz,
            p0=[vz_amp_init, freq_guess, 0],
            maxfev=maxfev)[0]
        vz_amp = _np.abs(pz[0])
        vz_phase = pz[2]
    except Exception:
        vz_amp = 0
        vz_phase = 0

    amp = [vx_amp, vy_amp, vz_amp]
    phase = [vx_phase, vy_phase, vz_phase]

    return amp, phase


def depth(lst):
    """Returns list depth.

    Args:
        lst (list): List for which depth is to be determined.

    Returns:
        int: Depth of input list.
    
    Examples:
        >>> depth([1,2,3])
        1
        >>> depth([[1,2,3]])
        2
        >>> depth([[[1,2],[3,4]]])
        3
    """
    return isinstance(lst, list) and max(map(depth, lst)) + 1


def flatten(lst):
    """Converts 2D matrix into a 1D list.

    Args:
        lst (list): 2D matrix (list with depth=2).

    Returns:
        list: 1D list of the input matrix elements.
    """
    return [item for sublist in lst for item in sublist]


def get_constants():
    """Basic physical constants for calculations on insertion devices.

    Returns:
        float: Electron rest energy (in eV)
        float: Speed of light (in m/s)
    """
    electron_rest_energy = 510998.92811  # [eV]
    light_speed = 299792458  # [m/s]
    return electron_rest_energy, light_speed


def calc_beam_parameters(energy):
    """Calculates electron beam parameters from its energy.

    Args:
        energy (float): Electron energy at the beam (in KeV)

    Returns:
        float: Beta v/c lightspeed fraction (dimensionless).
        float: Lorentz gamma factor (dimensionless).
        float: Electron (q=-1) magnetic rigidity (in eV.s/m).
    """
    electron_rest_energy, light_speed = get_constants()
    gamma = energy*1e9/electron_rest_energy
    beta = _np.sqrt(1 - 1/((energy*1e9/electron_rest_energy)**2))
    brho = energy*1e9/light_speed
    return beta, gamma, brho


def newton_lorentz_equation(a, r, b):
    """Equation of motion for a charged particle in a magnetic.

    Implementarion allows for both time (t) and lenght (s) parametrization.
    Trajectory is described by 6 components vectors, labeled "r", in which:
        (r[0], r[1], r[2]) are the (x,y,z) cartesian coordinates
        (r[3], r[4], r[5]) are, respectively, the derivatives of x, y and z
            coordenates with respect to the trajectory parameter (t or s).
    
    The equation of motion defines the derivatative (r') of such vector:
        r'[0], r'[1] and r'[2] are r[3], r[4], and r[5], respectively.
        r'[3], r'[4] and r'[5] derivatives are defined by the Lorentz force:
            (r'[3], r'[4], r'[5]) = -a (r[3], r[4], r[5]) x (b[0], b[1], b[2])            
            where "b" is the magnetic field and "x" is the vector product
    The negative sign at the equation makes it more convenient in calculations
    for negatively charged electrons, avoiding negative "a" values.
    
    Args:
        a (float): Lorentz force pre-factor
            For Lorentz magnetic force at each parametrizaton (with [units]):
                Time parameter (t):     a = -q[C]/(gamma*m[Kg])
                Lenght parameter (s):   a = -q[C]*c[m/s]/(beta*E[J])
                                        a = -q[e]*c[m/s]/(beta*E[eV])
                            for q=-1e:  a = c[m/s]/(beta*E[eV])
                m: particle mass      
                q: particle electric charge
                e: elementary carge
                c: speed of light
                beta: lightspeed fraction, v/c
                gamma: lorentz vactor, (1-beta^2)^(-1/2)        
        r (list, 6): Vector containing the cartesian and their derivatives.
            (coordinates in mm).
            (derivatives in mm/s or dimensionless, for t or s parameters).        
        b (list, 3): Magnetic field 3D vector (in T)
    
    Returns:
        list, 6: Derivative of the input trajectory vector, contains
            3 cartesian first derivatives (velocities) and 3 cartesian second
            derivatives (acceleracionts)
                (first derivatives in mm/s or dimensionless, for t or s).
                (second derivatives in mm/(s^2) or 1/mm, for t or s).
    """
    drds = _np.zeros(6)
    drds[0] = r[3]
    drds[1] = r[4]
    drds[2] = r[5]
    drds[3] = -a*(r[4]*b[2] - r[5]*b[1])
    drds[4] = -a*(r[5]*b[0] - r[3]*b[2])
    drds[5] = -a*(r[3]*b[1] - r[4]*b[0])
    return drds


def rotation_matrix(axis, theta):
    """Returns rotation matrix for rotation by an angle around an axis

    Args:
        axis (list, 3): Vector representing rotation axis.
        theta (float): Rotation angle (in radians).

    Returns:
        numpy.ndarray, 3x3: Rotation matrix.
    """
    axis = _np.asarray(axis)
    axis = axis / _np.sqrt(_np.dot(axis, axis))
    a = _np.cos(theta / 2.0)
    b, c, d = -axis * _np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    matrix = _np.array([
        [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
        [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
        [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc],
        ])
    return matrix


def find_peaks(data, prominence=0.05):
    """Find the indices of peaks in data list.

    Peaks are found by the function scipy.signal.find_peaks.

    Args:
        data (list): Data list for determining peak indices.
        prominence (float or list, 2; optional): Minimum peak prominence,
            or, if list, minimum and maximun prominence. Defaults to 0.05.

    Returns:
        numpy.ndarray: Indices of found data peaks. 
    """
    peaks, _ = _signal.find_peaks(data, prominence=prominence)
    return peaks


def find_valleys(data, prominence=0.05):
    """Find the indices of valleys in data list.

    Valleys are found by the function scipy.signal.find_peaks,
        which recieves the original data multiplied by -1.

    Args:
        data (list): Data list for determining valley indices.
        prominence (float or list, 2; optional): Minimum valley prominence,
            or, if list, minimum and maximun prominence. Defaults to 0.05.

    Returns:
        numpy.ndarray: Indices of found data valleys. 
    """
    valleys, _ = _signal.find_peaks(data*(-1), prominence=prominence)
    return valleys


def find_peaks_and_valleys(data, prominence=0.05):
    """Find indices of peaks and valleys in data list.

    This method combines the methods find_peaks and find_valleys,
        which are both executed with the same arguments. 

    Args:
        data (list): Data list for determining peak and valley indices.
        prominence (float or list, 2; optional): Minium prominence,
            or, if list, minimum and maximun prominence. Defaults to 0.05.

    Returns:
        numpy.ndarray: Indices of found data peaks and data valleys.
    """
    peaks = find_peaks(data, prominence=prominence)
    valleys = find_valleys(data, prominence=prominence)
    return sorted(_np.append(peaks, valleys))


def find_zeros(pos, data):
    """Find zero positions on data.

    Consecutie data pairs with changing sign data are first determined:
        Pair:       (pos[i], data[i]) and (pos[i+1], data[i+1])
        In which:   data[i] x data[i+1] = -1
    Each data pair results in a zero position between pos[i] and pos[i+1]:
        (data[i+1]*pos[i] - data[i]*pos[i+1]) / (data[i+1] - data[i])
    Which is the position in which the linear interpolation between the
    points crosses the data==0 axis.

    Args:
        pos (numpy.ndarray): Positions list.
        data (numpy.ndarray): Data list.

    Returns:
        numpy.ndarray: List of the zeros' positions.
    """
    s = _np.sign(data)
    idxb = (s[0:-1] + s[1:] == 0).nonzero()[0]
    idxa = idxb + 1
    posb = pos[idxb]
    posa = pos[idxa]
    datab = data[idxb]
    dataa = data[idxa]
    pos_zeros = (dataa*posb - datab*posa)/(dataa - datab)
    return pos_zeros
