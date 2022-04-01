
import json as _json
import numpy as _np
import matplotlib.pyplot as _plt
import matplotlib.gridspec as _gridspec

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
        if block_type not in ('v', 'vpos', 'vneg'):
            raise ValueError(
                'Invalid block_type value. Valid options: "v", "vpos", "vneg"')

        if segments_type not in ('period', 'half_period'):
            raise ValueError(
                'Invalid segments_type value. Valid options: "period" or "half_period"')

        if zmin_pe is None:
            zmin_pe = zmin

        if zmax_pe is None:
            zmax_pe = zmax

        self.cassettes = cassettes
        self.block_type = block_type
        self.segments_type = segments_type
        self.zmin = zmin
        self.zmax = zmax
        self.znpts = int(znpts)
        self.energy = energy
        self.rkstep = rkstep
        self.xpos = xpos
        self.ypos = ypos
        self.zmin_pe = zmin_pe
        self.zmax_pe = zmax_pe
        self.include_pe = include_pe
        self.field_comp = field_comp
        self.solved_shim = solved_shim
        self.solved_matrix = solved_matrix

    @staticmethod
    def get_rounded_shims(shims, possible_shims):
        shims_round = []
        for shim in shims:
            shim_round = min(possible_shims, key=lambda x: abs(x-shim))
            shims_round.append(shim_round)
        return shims_round

    @staticmethod
    def calc_svd(response_matrix):
        u, sv, vt = _np.linalg.svd(response_matrix, full_matrices=False)
        return u, sv, vt

    @staticmethod
    def fit_trajectory_segments(trajectory, segs, max_size):
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
            idx = _np.where(trajz >= pos)[0]
            index_list.append(idx[0])
        
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

    @staticmethod
    def read_response_matrix(filename):
        return _np.loadtxt(filename)

    @staticmethod
    def read_segs(filename):
        return _np.loadtxt(filename)

    @staticmethod
    def read_shims(filename):
        return _np.loadtxt(filename)

    @staticmethod
    def read_error(filename):
        return _np.loadtxt(filename)

    @staticmethod
    def read_results(filename):
        with open(filename, 'r') as f:
            results = _json.load(f)
        return results

    @staticmethod
    def read_fieldmap(filename, nr_periods, period, gap):
        data = _insertiondevice.InsertionDeviceData(
            nr_periods=nr_periods, period_length=period,
            gap=gap, filename=filename)
        return data

    def _calc_traj(self, obj, xl, yl):
        zl = _np.sqrt(1 - xl**2 - yl**2)
        traj = obj.calc_trajectory(
            self.energy,
            [self.xpos, self.ypos, self.zmin, xl, yl, zl],
            self.zmax, self.rkstep)
        return traj

    def _calc_phase_error(self, obj, traj):
        bx_amp, by_amp, _, _ = obj.calc_field_amplitude()
        zpe, pe, pe_rms = obj.calc_phase_error(
            self.energy, traj, bx_amp, by_amp,
            zmin=self.zmin_pe, zmax=self.zmax_pe,
            field_comp=self.field_comp)
        return zpe, pe, pe_rms

    def _calc_field_integrals(self, obj):
        z = _np.linspace(self.zmin, self.zmax, self.znpts)
        ib, iib = obj.calc_field_integrals(z_list=z)
        return ib, iib

    def calc_segments(self, obj, filename=None):
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

    def get_block_names(self, model):
        names = []
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(model, cassette)
            names.extend([b.name for b in blocks])
        return names

    def get_shimming_blocks(self, model, cassette):
        cas = model.cassettes[cassette]
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
            if block.length > (1 - tol)*model.period_length/4:
                regular_blocks.append(block)
        
        return regular_blocks

    def calc_response_matrix(
            self, model, model_segs, filename=None, shim=0.1):
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
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(model, cassette)

            for idx in range(len(blocks)):
                blocks[idx].shift([0, shim, 0])
                
                if self.solved_matrix:
                    model.solve()
                sx, sy, pe = self.calc_slope_and_phase_error(
                    model, model_segs, 0, 0)

                blocks[idx].shift([0, -shim, 0])

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
        if ws is None:
            ws = [1.0]*response_matrix.shape[0]
        ws = _np.array(ws)/_np.linalg.norm(ws)
        w = _np.diag(_np.sqrt(ws))

        m = response_matrix
        m = w @ m
        u, sv, vt = self.calc_svd(m)
        
        if nsv is None:
            nsv = len(sv)
        
        svinv = 1/sv
        svinv[nsv:] = 0
        minv = vt.T*svinv @ u.T

        ws_error = w @ error

        shims = minv @ ws_error

        if filename is not None:
            _np.savetxt(filename, shims)

        return shims

    def calc_shim_signature(self, model, shims, filename=None):
        zpos = _np.linspace(self.zmin, self.zmax, self.znpts)
        field0 = model.get_field(z=zpos)
        
        count = 0
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(model, cassette)
            for idx in range(len(blocks)):
                blocks[idx].shift([0, shims[count], 0])
                count += 1

        if self.solved_shim:
            model.solve()

        field = model.get_field(z=zpos)
        dfield = field - field0

        count = 0
        for cassette in self.cassettes:
            blocks = self.get_shimming_blocks(model, cassette)

            for idx in range(len(blocks)):
                blocks[idx].shift([0, (-1)*shims[count], 0])
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
            trajx_lim=None, trajy_lim=None, pe_lim=None):
        labels = list(results.keys())

        spec = _gridspec.GridSpec(
            ncols=2, nrows=2,
            wspace=0.25, hspace=0.25,
            left=0.1, right=0.95, top=0.95, bottom=0.15)
        fig = _plt.figure()
        ax0 = fig.add_subplot(spec[0, 0])
        ax1 = fig.add_subplot(spec[0, 1])
        ax2 = fig.add_subplot(spec[1, 0])
        ax3 = fig.add_subplot(spec[1, 1])

        values = []
        for label in labels:
            data = results[label]
            ax0.plot(data['trajz'], data['trajx'], label=label)
            ax1.plot(data['trajz'], data['trajy'], label=label)

            ax2.plot(data['zpe'], data['pe'], '-o', label=label)

            values.append(
                [data['ibx'][-1], data['iby'][-1],
                data['iibx'][-1], data['iibx'][-1],
                data['perms']])

        ax0.set_xlabel('Z [mm]')
        ax0.set_ylabel('TrajX [um]')
        ax0.grid(alpha=0.3)
        ax0.legend(loc='best')
        ax0.patch.set_edgecolor('black')
        ax0.patch.set_linewidth('2')
        if trajx_lim is not None:
            ax0.set_ylim(trajx_lim)

        ax1.set_xlabel('Z [mm]')
        ax1.set_ylabel('TrajY [um]')
        ax1.grid(alpha=0.3)
        ax1.patch.set_edgecolor('black')
        ax1.patch.set_linewidth('2')
        if trajy_lim is not None:
            ax1.set_ylim(trajy_lim)

        ax2.set_xlabel('Z [mm]')
        ax2.set_ylabel('Phase error [deg]')
        ax2.grid(alpha=0.3)
        ax2.patch.set_edgecolor('black')
        ax2.patch.set_linewidth('2')
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


    