
import numpy as _np

from . import utils as _utils
from . import fieldsource as _fieldsource


class UndulatorShimming():

    def __init__(
            self, model, meas, zmin, zmax, znpts,
            cassettes=None, block_type='v', segments_type='half_period', 
            traj_type='pos', energy=3.0, rkstep=0.5, xpos=0.0, ypos=0.0):
        if cassettes is None:
            cassettes = list(model.cassettes.keys())
        for cassette in cassettes:
            if cassette not in model.cassettes:
                raise ValueError(
                    'Invalid cassette name: {0:s}'.format(cassette))

        if block_type not in ('v', 'vpos', 'vneg'):
            raise ValueError(
                'Invalid block_type value. Valid options: "v", "vpos", "vneg"')

        if segments_type not in ('period', 'half_period'):
            raise ValueError(
                'Invalid segments_type value. Valid options: "period" or "half_period"')

        if traj_type not in ('pos', 'neg', 'both'):
            raise ValueError(
                'Invalid segments_type value. Valid options: "pos", "neg", "both"')

        self.model = model
        self.meas = meas
        self.cassettes = cassettes
        self.block_type = block_type
        self.segments_type = segments_type
        self.traj_type = traj_type
        self.zmin = zmin
        self.zmax = zmax
        self.znpts = int(znpts)
        self.energy = energy
        self.rkstep = rkstep
        self.xpos = xpos
        self.ypos = ypos

        self._model_segments = None
        self._meas_segments = None
        self._response_matrix = None
        self._model_slope_x = None
        self._model_slope_y = None
        self._model_slope_solved = None

    @property
    def response_matrix(self):
        return self._response_matrix

    @property
    def model_segments(self):
        return self._model_segments
    
    @property
    def meas_segments(self):
        return self._meas_segments

    def calc_model_segments(self):
        self._model_segments = self.calc_segments(self.model)

    def calc_meas_segments(self):
        self._meas_segments = self._model_segments

    def calc_segments(self, obj):
        zpos = _np.linspace(self.zmin, self.zmax, self.znpts)
        field = obj.get_field(z=zpos)

        freqs = _np.array([2*_np.pi/self.model.period_length])
        amps, *_ = _utils.fit_fourier_components(field, freqs, zpos)
        comp = _np.argmax(amps)
        spos = obj.find_zeros(zpos, field[:, comp])

        if self.segments_type == 'period':
            segs = spos[::2]
        
        elif self.segments_type == 'half_period':
            segs = spos

        segs = _np.insert(
            segs, 0, segs[0] - self.model.period_length)
        segs = _np.insert(
            segs, -1, segs[-1] + self.model.period_length)
        
        return sorted(segs)

    def fit_trajectory_segments(self, trajectory, segs, max_size):
        trajx = trajectory[:, 0]
        trajy = trajectory[:, 1]
        trajz = trajectory[:, 2]

        seg_start = []
        seg_end = []
        poly_x = []
        poly_y = []

        nsegs = len(segs)

        index_list = []
        for pos in segs:
            index_list.append(_np.where(trajz >= pos)[0][0])
        
        last_index = _np.where(trajz >= segs[-1] + max_size)[0]
        if len(last_index) == 0:
            index_list.append(len(trajz)-1)
        else:
            index_list.append(last_index[0])

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

        return poly_x, poly_y

    def _calc_traj_slope(self, obj, segs, traj):
        avgtraj = obj.calc_trajectory_avg_over_period(traj)

        poly_x, poly_y = self.fit_trajectory_segments(
            avgtraj, segs, self.model.period_length)

        slope_x = poly_x[:, 1]
        slope_y = poly_y[:, 1]

        return slope_x, slope_y

    def calc_slope(self, obj, segs):
        slope_x = []
        slope_y = []

        if self.traj_type in ('pos', 'both'):
            traj_pos = obj.calc_trajectory(
                self.energy,
                [self.xpos, self.ypos, self.zmin, 0, 0, 1],
                self.zmax, self.rkstep)
            slope_x_pos, slope_y_pos = self._calc_traj_slope(
                obj, segs, traj_pos)
            
            slope_x = _np.append(slope_x, slope_x_pos)
            slope_y = _np.append(slope_y, slope_y_pos)
        
        if self.traj_type in ('neg', 'both'):
            traj_neg = obj.calc_trajectory(
                self.energy,
                [self.xpos, self.ypos, self.zmax, 0, 0, 1],
                self.zmin, (-1)*self.rkstep)
            traj_neg = _np.flip(traj_neg, axis=0)
            slope_x_neg, slope_y_neg = self._calc_traj_slope(
                obj, segs, traj_neg)
            
            slope_x = _np.append(slope_x, slope_x_neg)
            slope_y = _np.append(slope_y, slope_y_neg)

        return slope_x, slope_y

    def get_block_names(self):
        names = []
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(cassette)
            names.extend([b.name for b in blocks])
        return names

    def get_shimming_blocks(self, cassette):
        cas = self.model.cassettes[cassette]
        mag = _np.array(cas.magnetization_list)
        mres = _np.sqrt(mag[:, 0]**2 + mag[:, 2]**2)
        
        if self.block_type == 'v':
            filt = _np.abs(mag[:, 1]) > mres
        elif self.block_type == 'vpos':
            filt = mag[:, 1] > mres
        elif self.block_type == 'vneg':
            filt = mag[:, 1]*(-1) > mres
        
        blocks = _np.array(cas.blocks)[filt]

        tol = 0.1
        regular_blocks = []
        for block in blocks:
            if block.length > (1 - tol)*self.model.period_length/4:
                regular_blocks.append(block)
        
        return regular_blocks

    def load_response_matrix(self, filename):
        self._response_matrix = _np.loadtxt(filename)

    def calc_model_slope(self, solved=True):
        if self.model_segments is None:
            self.calc_model_segments()

        if solved:
            self.model.solve()
        
        self._model_slope_solved = solved

        self._model_slope_x, self._model_slope_y = self.calc_slope(
            self.model, self.model_segments)
        
        return True

    def calc_response_matrix(
            self, filename, shim=0.1, solved=True):
        self._response_matrix = None

        if self.model_segments is None:
            self.calc_model_segments()

        if (self._model_slope_solved != solved or 
                self._model_slope_x is None or self._model_slope_y is None):
            self.calc_model_slope(solved=solved)

        ext = '.' + filename.split('.')[-1]
        filename_mx = filename.replace(ext, '_mx' + ext)
        filename_my = filename.replace(ext, '_my' + ext)
        open(filename_mx, 'w').close()
        open(filename_my, 'w').close()

        mx = []
        my = []
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(cassette)
            
            for idx in range(len(blocks)):
                blocks[idx].shift([0, shim, 0])
                
                if solved:
                    self.model.solve()
                slope_x, slope_y = self.calc_slope(
                    self.model, self.model_segments)

                blocks[idx].shift([0, -shim, 0])

                dpx = (slope_x - self._model_slope_x)/shim
                dpy = (slope_y - self._model_slope_y)/shim

                with open(filename_mx, 'a+') as fx:
                    strx = '\t'.join('{0:g}'.format(v) for v in dpx)
                    fx.write(strx + '\n')

                with open(filename_my, 'a+') as fy:
                    stry = '\t'.join('{0:g}'.format(v) for v in dpy)
                    fy.write(stry + '\n')

                mx.append(dpx)
                my.append(dpy)

        mx = _np.array(mx)
        my = _np.array(my)
        m = _np.transpose(_np.concatenate([mx, my], axis=1))
        _np.savetxt(filename, m)

        self._response_matrix = m

        return True

    def calc_shims(self, nsv=None, solved=True):
        if self.model_segments is None:
            self.calc_model_segments()

        if self.meas_segments is None:
            self.calc_meas_segments()

        if (self._model_slope_solved != solved or 
                self._model_slope_x is None or self._model_slope_y is None):
            self.calc_model_slope(solved=solved)

        u, sv, vt = _np.linalg.svd(self.response_matrix, full_matrices=False)
        
        if nsv is None:
            nsv = len(sv)

        svinv = 1/sv
        svinv[nsv:] = 0
        minv = vt.T*svinv @ u.T

        slope_x, slope_y = self.calc_slope(
            self.meas, self.meas_segments)

        slope_error_x = self._model_slope_x - slope_x
        slope_error_y = self._model_slope_y - slope_y
        slope_error = _np.concatenate([slope_error_x, slope_error_y])

        shims = minv @ slope_error

        return shims, sv

    def get_rounded_shims(self, shims, possible_shims):
        shims_round = []
        for shim in shims:
            shim_round = min(possible_shims, key=lambda x: abs(x-shim))
            shims_round.append(shim_round)
        return shims_round

    def get_shims_signature(self, shims):
        zpos = _np.linspace(self.zmin, self.zmax, self.znpts)
        field0 = self.model.get_field(z=zpos)
        
        count = 0
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(cassette)

            for idx in range(len(blocks)):
                blocks[idx].shift([0, shims[count], 0])
                count += 1
        self.model.solve()

        field = self.model.get_field(z=zpos)
        dfield = field - field0

        count = 0
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(cassette)

            for idx in range(len(blocks)):
                blocks[idx].shift([0, (-1)*shims[count], 0])
                count += 1

        x = [self.xpos]*self.znpts
        y = [self.ypos]*self.znpts
        raw_data = _np.transpose(
            [x, y, zpos, dfield[:, 0], dfield[:, 1], dfield[:, 2]])

        return _fieldsource.FieldData(raw_data=raw_data)

