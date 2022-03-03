
import os as _os
import numpy as _np

from imaids import utils as _utils


class UndulatorShimming():

    def __init__(
            self, model, measurement, cassettes,
            zmin, zmax, znpts, main_comp=1,
            energy=3, rkstep=0.5, xpos=0, ypos=0):
        self.model = model
        self.measurement = measurement
        self.cassettes = cassettes
        self.zmin = zmin
        self.zmax = zmax
        self.znpts = znpts
        self.main_comp = main_comp
        self.energy = energy
        self.rkstep = rkstep
        self.xpos = xpos
        self.ypos = ypos

        self._segments = None
        self._response_matrix = None

    def calc_segments(self, prominence=0.05):
        self._segments = None
        
        zpos = _np.linspace(self.zmin, self.zmax, self.znpts)
        field = self.model.get_field(z=zpos)
        peaks = _utils.find_peaks_and_valleys(
            field[:, self.main_comp], prominence=prominence)
        
        block_pos = zpos[peaks] - self.model.period_length/4
        
        segs = list(block_pos[::2])
        segs.append(segs[-1] + self.model.period_length)
        segs.append(segs[0] - self.model.period_length)
        segs = sorted(segs)
        self._segments = segs
        
        return True

    def calc_slope(self, obj):       
        traj = obj.calc_trajectory(
            self.energy,
            [self.xpos, self.ypos, self.zmin, 0, 0, 1],
            self.zmax, self.rkstep)
        
        avgtraj = obj.calc_trajectory_avg_over_period(traj)

        _, _, poly_x, poly_y = obj.fit_trajectory_segments(
            avgtraj, self._segments, self.model.period_length)

        slope_x = poly_x[:, 1]
        slope_y = poly_y[:, 1]

        return slope_x, slope_y

    def get_shimming_blocks(self, cassette, tol=0.2):
        cas = self.model.cassettes[cassette]
        mag = _np.array(cas.magnetization_list)
        filt = mag[:, 1] > (cas.mr - tol)
        # filt = _np.abs(mag[:, 1]) > (cas.mr - tol)
        blocks = _np.array(cas.blocks)[filt]
        return blocks

    def load_response_matrix(self, filename):
        self._response_matrix = _np.loadtxt(filename)

    def calc_response_matrix(self, filename, shim=0.25):
        self._response_matrix = None

        if self._segments is None:
            self.calc_segments()

        self.model.solve()
        slope_x0, slope_y0 = self.calc_slope(self.model)

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
                
                self.model.solve()
                slope_x, slope_y = self.calc_slope(self.model)

                blocks[idx].shift([0, -shim, 0])

                dpx = (slope_x - slope_x0)/shim
                dpy = (slope_y - slope_y0)/shim

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

    def calc_shims(self):
        minv = _np.linalg.pinv(self._response_matrix)

        self.model.solve()
        slope_x0, slope_y0 = self.calc_slope(self.model)

        slope_x, slope_y = self.calc_slope(self.measurement)

        slope_error_x = slope_x0 - slope_x
        slope_error_y = slope_y0 - slope_y
        slope_error = _np.concatenate([slope_error_x, slope_error_y])

        shims = minv @ slope_error

        return shims

    def apply_shims(self, shims):
        count = 0
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(cassette)

            for idx in range(len(blocks)):
                blocks[idx].shift([0, shims[count], 0])
                count += 1

