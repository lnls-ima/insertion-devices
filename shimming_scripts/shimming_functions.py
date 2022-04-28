
import os
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from shimming_files import ShimmingFiles
from imaids import utils, models, shimming, insertiondevice


FILES = ShimmingFiles(label='21periods_shimmingB')


def configure_plot():
    plt.rcParams['figure.figsize'] = [18, 8]
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['lines.markersize'] = 6
    plt.rcParams['lines.linewidth'] = 3


def group_block_names(names, subcassettes):
    group_names = []
    prev_btype = None
    
    for nm, sc in zip(names, subcassettes):
        btype = nm[:2]
                
        if prev_btype is not None and btype == prev_btype:
            group_names[-1] += '-' + nm
        else:
            group_names.append(sc + '_' + nm)
        
        prev_btype = btype

    return group_names


def get_block_names_and_shims(filename):
    cid_df = pd.read_excel(filename, sheet_name='CID', header=0)
    cie_df = pd.read_excel(filename, sheet_name='CIE', header=0)
    csd_df = pd.read_excel(filename, sheet_name='CSD', header=0)
    cse_df = pd.read_excel(filename, sheet_name='CSE', header=0)

    idx = 0
    cid_ns = np.array(cid_df.iloc[:, idx]).tolist()
    cie_ns = np.array(cie_df.iloc[:, idx]).tolist()
    csd_ns = np.array(csd_df.iloc[:, idx]).tolist()
    cse_ns = np.array(cse_df.iloc[:, idx]).tolist()

    idx = 4
    cid_sc = np.array(cid_df.iloc[:, idx]).tolist()
    cie_sc = np.array(cie_df.iloc[:, idx]).tolist()
    csd_sc = np.array(csd_df.iloc[:, idx]).tolist()
    cse_sc = np.array(cse_df.iloc[:, idx]).tolist()

    idx = 8
    cid_shims = np.array(cid_df.iloc[:, idx]).astype(float)
    cie_shims = np.array(cie_df.iloc[:, idx]).astype(float)
    csd_shims = np.array(csd_df.iloc[:, idx]).astype(float)
    cse_shims = np.array(cse_df.iloc[:, idx]).astype(float)

    block_names_dict = {
        'cid': group_block_names(cid_ns, cid_sc),
        'cie': group_block_names(cie_ns, cie_sc),
        'csd': group_block_names(csd_ns, csd_sc),
        'cse': group_block_names(cse_ns, cse_sc),
    }

    block_shims_dict = {
        'cid': cid_shims,
        'cie': cie_shims,
        'csd': csd_shims,
        'cse': cse_shims,
    }
    
    return block_names_dict, block_shims_dict


def configure_model(model, polarization, kstr, solve=True):
    if polarization == 'hp':
        dp = 0
    elif polarization == 'cp':
        dp = -model.period_length/4
    elif polarization == 'vp':
        dp = -model.period_length/2

    if kstr == 'kmax':
        dgv = model.period_length/2
    elif kstr == 'kmed':
        dgv = model.period_length/4
    elif kstr == 'k0':
        dgv = 0

    model.dgv = dgv
    model.dp = dp
    if solve:
        model.solve()

    return True


def create_model(
        nr_periods, add_errors=False, remove_subdivision=False):
    block_names_dict, _ = get_block_names_and_shims(
        FILES.get_filename_undulator_data())

    if add_errors:
        period = 52.5
        period_err = 0.2
        mag_amp = 2/100  # [%]
        mag_ang = 2*np.pi/180  # [rad]
        herr = 0.1  # [mm]
        verr = 0.1  # [mm]
        lerr = 0.05  # [mm]
        term_err = True
        core_err = True
    else:
        period = 52.5
        period_err = 0
        mag_amp = 0
        mag_ang = 0
        herr = 0
        verr = 0
        lerr = 0
        term_err = False
        core_err = False 

    if remove_subdivision:
        model = models.DeltaSabia(
            nr_periods=nr_periods,
            period_length=period + period_err,
            block_subdivision=None)
    else:
        model = models.DeltaSabia(
            nr_periods=nr_periods, period_length=period + period_err)

    mag_dict = {}
    perr_dict = {}
    for name, cassette in model.cassettes.items():
        mag = cassette.get_random_errors_magnetization_list(
            max_amplitude_error=mag_amp,
            max_angular_error=mag_ang,
            termination_errors=term_err,
            core_errors=core_err)
        perr = cassette.get_random_errors_position(
            max_horizontal_error=herr,
            max_vertical_error=verr,
            max_longitudinal_error=lerr,
            termination_errors=term_err,
            core_errors=core_err)
        mag_dict[name] = mag
        perr_dict[name] = perr

    model.create_radia_object(
        magnetization_dict=mag_dict,
        position_err_dict=perr_dict,
        block_names_dict=block_names_dict)

    model.save_state(
        FILES.get_filename_model(
            with_errors=add_errors,
            remove_subdivision=remove_subdivision))

    return model


def get_trajectory_params(nr_periods):
    params = {}
    params['energy'] = 3
    params['rkstep'] = 1
    if nr_periods == 3:
        params['zmin'] = -300
        params['zmax'] = 300
        params['znpts'] = 301
        params['x'] = 0
        params['y'] = 0
    elif nr_periods == 9:
        params['zmin'] = -500
        params['zmax'] = 500
        params['znpts'] = 501
        params['x'] = 0
        params['y'] = 0
    elif nr_periods == 21:
        params['zmin'] = -900
        params['zmax'] = 900
        params['znpts'] = 901
        params['x'] = 0
        params['y'] = 0
    return params


def get_phase_error_params(nr_periods):
    params = {}
    if nr_periods == 3:
        params['zmin'] = -50
        params['zmax'] = 80
    elif nr_periods == 9:
        params['zmin'] = -200
        params['zmax'] = 230
    elif nr_periods == 21:
        params['zmin'] = -530
        params['zmax'] = 550
    return params


def load_measurement(nr_periods, polarization, kstr, zshift=0, add_label=None):
    period = 52.5
    gap = 13.6
    filename_meas = FILES.get_filename_measurement(
        polarization=polarization, kstr=kstr, add_label=add_label)
    meas = insertiondevice.InsertionDeviceData(
        nr_periods=nr_periods, period_length=period,
        gap=gap, filename=filename_meas)
    meas.shift([0, 0, zshift])
    return meas


def load_model(
        nr_periods, polarization, kstr,
        solve=True, with_errors=False,
        remove_subdivision=False):
    filename_model = FILES.get_filename_model(
        with_errors=with_errors,
        remove_subdivision=remove_subdivision,
    )
    if not os.path.isfile(filename_model):
        return None
 
    model = models.DeltaSabia.load_state(filename_model)
    configure_model(model, polarization, kstr, solve=solve)
    return model


def plot_traj(obj, xl=0, yl=0):
    params = get_trajectory_params(obj.nr_periods)

    zl = np.sqrt(1 - xl**2 - yl**2)
    traj = obj.calc_trajectory(
        params['energy'],
        [params['x'], params['y'], params['zmin'], xl, yl, zl],
        params['zmax'],
        params['rkstep'],
    )

    fig, axs = plt.subplots(2)
    axs[0].plot(traj[:, 2], traj[:, 0]*1000)
    axs[0].grid(alpha=0.3)
    axs[0].set_ylabel('x [um]')

    axs[1].plot(traj[:, 2], traj[:, 1]*1000)
    axs[1].grid(alpha=0.3)
    axs[1].set_xlabel('z [mm]')
    axs[1].set_ylabel('y [um]')

    return True


def plot_compare_field(model, meas):
    params = get_trajectory_params(model.nr_periods)

    z = np.linspace(
        params['zmin'], params['zmax'], params['znpts'])
    bmodel = model.get_field(z=z)
    bmeas = meas.get_field(z=z)

    fig, axs = plt.subplots(2)
    axs[0].plot(z, bmodel[:, 0], label='Model')
    axs[0].plot(z, bmeas[:, 0], label='Meas')
    axs[0].grid(alpha=0.3)
    axs[0].set_ylabel('Bx [T]')

    axs[1].plot(z, bmodel[:, 1], label='Model')
    axs[1].plot(z, bmeas[:, 1], label='Meas')
    axs[1].grid(alpha=0.3)
    axs[1].set_xlabel('z [mm]')
    axs[1].set_ylabel('By [T]')

    return True


def get_rescale_factor(model, meas, field_comp=None):
    bx_model, by_model, _, _ = model.calc_field_amplitude()
    bx_meas, by_meas, _, _ = meas.calc_field_amplitude()

    if field_comp == 0:
        fres = bx_meas/bx_model
    elif field_comp == 1:
        fres = by_meas/by_model
    else:
        b_model = np.sqrt(bx_model**2 + by_model**2)
        b_meas = np.sqrt(bx_meas**2 + by_meas**2)
        fres = b_meas/b_model
    
    return fres


def rescale_model(model, fres):
    mr = model.cassette_properties['mr']
    dgv = model.dgv
    dp = model.dp
    nr_periods = model.nr_periods
    period_length = model.period_length
    bn_dict = model.block_names_dict
    mag_dict = model.magnetization_dict
    pos_dict = model.position_err_dict

    model_res = models.DeltaSabia(
        nr_periods=nr_periods, mr=mr*fres, period_length=period_length)
    model_res.create_radia_object(
        block_names_dict=bn_dict,
        magnetization_dict=mag_dict,
        position_err_dict=pos_dict,
    )
    model_res.dgv = dgv
    model_res.dp = dp
    model_res.solve()

    return model_res


def calc_kicks(nr_periods, obj, dz=0):
    filename_matrix = FILES.get_filename_ffmatrix()
    matrix = np.loadtxt(filename_matrix)

    u, sv, vt = shimming.UndulatorShimming.calc_svd(matrix)
    svinv = 1/sv
    minv = vt.T*svinv @ u.T

    params = get_trajectory_params(nr_periods)

    xl = 0
    yl = 0
    zl = np.sqrt(1 - xl**2 - yl**2)
    traj = obj.calc_trajectory(
        params['energy'],
        [params['x'], params['y'], params['zmin'], xl, yl, zl],
        params['zmax']-1-dz,
        params['rkstep'],
    )

    dx = traj[-1, 0]
    dy = traj[-1, 1]
    dxl = traj[-1, 3]
    dyl = traj[-1, 4]
    d = np.array([dx, dy, dxl, dyl])*(-1)

    kicks = minv @ d
    return kicks


def round_shims(shims):
    available_shims = [
            0.00,
            0.05,
            0.10,
            0.15,
            0.20,
            0.25,
            0.30,
            0.35,
            0.40,
            0.45,
            0.50,
        ]
    initial_shim = 0.25
    possible_shims = np.array(available_shims) - initial_shim

    shims_round = []
    for shim in shims:
        shim_round = min(possible_shims, key=lambda x: abs(x-shim))
        shims_round.append(shim_round)
    shims_round = np.round(shims_round, decimals=2)
    return shims_round


def run_create_model():
    nr_periods = 21
    polarization = 'hp'
    kstr = 'kmax'
    add_errors = False
    remove_subdivision = True

    configure_plot()

    model = create_model(
        nr_periods, add_errors, remove_subdivision)
    configure_model(model, polarization, kstr)
    plot_traj(model)
    
    plt.suptitle(polarization.upper() + ' ' + kstr.capitalize())
    plt.show()

    return True


def run_plot_field_integrals():
    nr_periods = 21

    k = {}
    ibx = {}
    iby = {}
    iibx = {}
    iiby = {}

    params = get_trajectory_params(nr_periods)
    z = np.linspace(params['zmin'], params['zmax'], params['znpts'])

    polarizations = ['hp', 'vp', 'cp']
    kstrs = ['k0', 'kmed', 'kmax']

    for polarization in polarizations:
        for kstr in kstrs:
            if kstr == 'k0' and polarization != 'hp':
                continue
            meas = load_measurement(nr_periods, polarization, kstr)
            bx_amp, by_amp, _, _ = meas.calc_field_amplitude()
            kh, kv = meas.calc_deflection_parameter(bx_amp, by_amp)
            ib, iib = meas.calc_field_integrals(z_list=z)

            if polarization not in ibx:
                k[polarization] = []
                ibx[polarization] = [] 
                iby[polarization] = [] 
                iibx[polarization] = [] 
                iiby[polarization] = [] 

            if polarization == 'vp':
                k[polarization].append(kv)
            else:
                k[polarization].append(kh)

            ibx[polarization].append(ib[-1, 0])
            iby[polarization].append(ib[-1, 1])
            iibx[polarization].append(iib[-1, 0])
            iiby[polarization].append(iib[-1, 1])

    fig, axs = plt.subplots(2)
    axs[0].plot(k['hp'], ibx['hp'], '-o', label='HP')
    axs[0].plot(k['vp'], ibx['vp'], '-o', label='VP')
    axs[0].plot(k['cp'], ibx['cp'], '-o', label='CP')
    axs[0].grid(alpha=0.3)
    axs[0].set_xlabel('K')
    axs[0].set_ylabel('IBx [G.cm]')

    axs[1].plot(k['hp'], iby['hp'], '-o', label='HP')
    axs[1].plot(k['vp'], iby['vp'], '-o', label='VP')
    axs[1].plot(k['cp'], iby['cp'], '-o', label='CP')
    axs[1].grid(alpha=0.3)
    axs[1].set_xlabel('K')
    axs[1].set_ylabel('IBy [G.cm]')

    fig, axs = plt.subplots(2)
    axs[0].plot(k['hp'], iibx['hp'], '-o', label='HP')
    axs[0].plot(k['vp'], iibx['vp'], '-o', label='VP')
    axs[0].plot(k['cp'], iibx['cp'], '-o', label='CP')
    axs[0].grid(alpha=0.3)
    axs[0].set_xlabel('K')
    axs[0].set_ylabel('IIBx [kG.cm2]')

    axs[1].plot(k['hp'], iiby['hp'], '-o', label='HP')
    axs[1].plot(k['vp'], iiby['vp'], '-o', label='VP')
    axs[1].plot(k['cp'], iiby['cp'], '-o', label='CP')
    axs[1].grid(alpha=0.3)
    axs[1].set_xlabel('K')
    axs[1].set_ylabel('IIBy [kG.cm2]')

    plt.show()


def run_plot_field_integrals_profile():
    nr_periods = 21
    xs = np.linspace(-5.0, 5.0, 11)

    configs = [
        'hp_kmax',
        'hp_kmed',
        'hp_k0',
        'vp_kmax',
        'vp_kmed',
        'cp_kmax',
        'cp_kmed',
    ]

    ibx = {}
    iby = {}
    iibx = {}
    iiby = {}

    params = get_trajectory_params(nr_periods)
    z = np.linspace(params['zmin'], params['zmax'], params['znpts'])

    for config in configs:
        polarization = config.split('_')[0]
        kstr = config.split('_')[1]
        meas = load_measurement(nr_periods, polarization, kstr)

        ibx[config] = [] 
        iby[config] = [] 
        iibx[config] = [] 
        iiby[config] = [] 

        for x in xs: 
            ib, iib = meas.calc_field_integrals(z_list=z, x=x)
            ibx[config].append(ib[-1, 0])
            iby[config].append(ib[-1, 1])
            iibx[config].append(iib[-1, 0])
            iiby[config].append(iib[-1, 1])

    fig, axs = plt.subplots(2)
    for config in configs:
        axs[0].plot(xs, ibx[config], label=config)
        axs[0].grid(alpha=0.3)
        axs[0].set_ylabel('IBx [G.cm]')

        axs[1].plot(xs, iby[config], label=config)
        axs[1].grid(alpha=0.3)
        axs[1].set_xlabel('x [mm]')
        axs[1].set_ylabel('IBy [G.cm]')
        axs[1].legend(loc='best')

    fig, axs = plt.subplots(2)
    for config in configs:
        axs[0].plot(xs, iibx[config], label=config)
        axs[0].grid(alpha=0.3)
        axs[0].set_ylabel('IIBx [kG.cm2]')

        axs[1].plot(xs, iiby[config], label=config)
        axs[1].grid(alpha=0.3)
        axs[1].set_xlabel('x [mm]')
        axs[1].set_ylabel('IIBy [kG.cm2]')
        axs[1].legend(loc='best')

    plt.show()


def run_save_model_fieldmap():
    nr_periods = 21
    polarization = 'cp'
    kstr = 'kmed'
    solved = True
    with_errors = False
    remove_subdivision = False
    
    model = load_model(
        nr_periods, polarization, kstr,
        solve=solved,
        with_errors=with_errors,
        remove_subdivision=remove_subdivision)
    
    filename = FILES.get_filename_fieldmap(
        polarization=polarization,
        kstr=kstr,
        with_errors=with_errors,
        remove_subdivision=remove_subdivision)
    params = get_trajectory_params(model.nr_periods)
    z = np.linspace(params['zmin'], params['zmax'], params['znpts'])
    # x = np.linspace(-0.5, 0.5, 3)
    # y = np.linspace(-0.5, 0.5, 3)
    x = 0
    y = 0
    model.save_fieldmap(filename, x, y, z)


def run_calc_response_matrix():
    nr_periods = 21
    polarization = 'hp'
    kstr = 'kmax'
    field_comp = 1
    
    cassettes = ['csd', 'cse']
    block_type = 'v'
    segments_type = 'half_period'
    include_pe = True
    solved_matrix = False

    if solved_matrix:
        remove_subdivision = False
    else:
        remove_subdivision = True

    with_errors = False

    model = load_model(
        nr_periods, polarization, kstr,
        solve=solved_matrix, with_errors=with_errors,
        remove_subdivision=remove_subdivision)
    
    if model is None:
        model = create_model(
            nr_periods,
            add_errors=with_errors,
            remove_subdivision=remove_subdivision)
        configure_model(model, polarization, kstr)
   
    traj_params = get_trajectory_params(model.nr_periods)
    pe_params = get_phase_error_params(model.nr_periods)
    sh = shimming.UndulatorShimming(
        traj_params['zmin'],
        traj_params['zmax'],
        traj_params['znpts'],
        cassettes=cassettes,
        block_type=block_type,
        segments_type=segments_type,
        include_pe=include_pe,
        zmin_pe=pe_params['zmin'],
        zmax_pe=pe_params['zmax'],
        field_comp=field_comp,
        solved_matrix=solved_matrix,
        )
    
    filename_segs = FILES.get_filename_segs(
        block_type=block_type,
        segments_type=segments_type,
        polarization=polarization,
        kstr=kstr)
    model_segs = sh.calc_segments(
        model, filename=filename_segs)
    
    filename_matrix = FILES.get_filename_matrix(
        cassettes=cassettes,
        block_type=block_type,
        segments_type=segments_type,
        solved_matrix=solved_matrix,
        include_pe= include_pe,
        polarization=polarization,
        kstr=kstr)

    if os.path.isfile(filename_matrix):
        raise Exception(
            'File: {0:s} already exists!'.format(filename_matrix))  

    response_matrix = sh.calc_response_matrix(
        model, model_segs, filename=filename_matrix)

    return response_matrix


def run_apply_shimming():
    dirname = 'delta_sabia_shimming_b_add_cte'
    plot_field = True
    plot_rescale_field = False
    plot_sv = False

    nr_periods = 21
    polarization = 'cp'
    kstr = 'kmed'
    nsv = 40

    if polarization == 'vp':
        field_comp = 0
    else:
        field_comp = 1

    cassettes = ['csd', 'cse']
    block_type = 'v'
    segments_type = 'half_period'
    include_pe = True
    solved_matrix = False
    solved_shim = True

    phase_error_w = 2e-8

    configure_plot()
    FILES.mkdir_results(dirname)

    model = load_model(
        nr_periods, polarization, kstr,
        solve=solved_shim,
        with_errors=False,
        remove_subdivision=False)
    print('model loaded')

    meas = load_measurement(nr_periods, polarization, kstr)
    print('meas loaded')

    cte = -0.00012
    raw_data = np.transpose([
        meas._raw_data[:, 0],
        meas._raw_data[:, 1],
        meas._raw_data[:, 2],
        meas._raw_data[:, 3]*0,
        meas._raw_data[:, 4]*0 + cte,
        meas._raw_data[:, 5]*0,
    ])
    cte_field = insertiondevice.InsertionDeviceData(
        nr_periods=nr_periods, gap=model.gap,
        period_length=model.period_length, raw_data=raw_data)
    meas.add_field(cte_field)
    print('adding cte to measure: ', cte)

    # meas = load_model(
    #     nr_periods, polarization, kstr,
    #     solve=solved_shim,
    #     with_errors=True,
    #     remove_subdivision=False)
    # print('model with errors loaded')

    if plot_field:
        plot_compare_field(model, meas)
        plt.show()

    filename_error = FILES.get_filename_error(
        dirname, polarization=polarization, kstr=kstr)

    if not os.path.isfile(filename_error):
        fres = get_rescale_factor(model, meas, field_comp=field_comp)
        print('rescale factor: ', fres)

        model = rescale_model(model, fres)
        print('model rescaled')

        if plot_rescale_field:
            plot_compare_field(model, meas)
            plt.show()

    traj_params = get_trajectory_params(model.nr_periods)
    pe_params = get_phase_error_params(model.nr_periods)
    sh = shimming.UndulatorShimming(
        traj_params['zmin'],
        traj_params['zmax'],
        traj_params['znpts'],
        cassettes=cassettes,
        block_type=block_type,
        segments_type=segments_type,
        include_pe=include_pe,
        zmin_pe=pe_params['zmin'],
        zmax_pe=pe_params['zmax'],
        field_comp=field_comp,
        solved_matrix=solved_matrix,
        solved_shim=solved_shim,
        )

    filename_matrix = FILES.get_filename_matrix(
        cassettes=cassettes,
        block_type=block_type,
        segments_type=segments_type,
        solved_matrix=solved_matrix,
        include_pe= include_pe,
        polarization=polarization,
        kstr=kstr)
    response_matrix = sh.read_response_matrix(filename_matrix)    
    print('response matrix loaded')

    filename_segs = FILES.get_filename_segs(
        block_type=block_type,
        segments_type=segments_type,
        polarization=polarization,
        kstr=kstr)
    model_segs = sh.read_segs(filename_segs)
    print('loaded model segs')

    if os.path.isfile(filename_error):
        error = sh.read_error(filename_error)
        print('load error')
    else:
        error = sh.calc_error(
            model, meas, model_segs, model_segs, filename=filename_error)
        print('calc error')

    ws = np.array([1.0]*int(response_matrix.shape[0]))
    ws[2*len(model_segs-1):] = phase_error_w

    if plot_sv:
        _, sv, _ = sh.calc_svd(response_matrix)
        plt.plot(sv, '-o')
        plt.grid(True)
        plt.show()

    filename_block_names = FILES.get_filename_block_names(dirname)
    sh.get_block_names(model, filename=filename_block_names)

    filename_shims = FILES.get_filename_shims(
        dirname, polarization=polarization, kstr=kstr)
    if os.path.isfile(filename_shims):   
        shims = sh.read_shims(filename_shims)
        print('load shims')
    else:
        shims = sh.calc_shims(
            response_matrix, error, nsv=nsv, ws=ws, filename=filename_shims)
        print('shims [mm]: ', np.round(shims, decimals=2))

    filename_sig = FILES.get_filename_sig(
        dirname, polarization=polarization, kstr=kstr)
    if os.path.isfile(filename_sig):
        period = model.period_length
        gap = model.gap
        shim_signature = sh.read_fieldmap(
            filename_sig, nr_periods, period, gap)
        print('load shim signature')
    else:
        shim_signature = sh.calc_shim_signature(
            model, shims, filename=filename_sig)
        print('calc shim signature')
    
    filename_shimmed = FILES.get_filename_shimmed(
        dirname, polarization=polarization, kstr=kstr)
    if os.path.isfile(filename_shimmed):
        period = model.period_length
        gap = model.gap
        shimmed_meas = sh.read_fieldmap(
            filename_shimmed, nr_periods, period, gap)
        print('load shimmed meas')
    else:
        shimmed_meas = sh.calc_shimmed_meas(
            meas, shim_signature, filename=filename_shimmed)
        print('calc shimmed meas')

    filename_results = FILES.get_filename_results(
        dirname, polarization=polarization, kstr=kstr)
    if os.path.isfile(filename_results):
        results = sh.read_results(filename_results)
        print('load results')
    else:
        objs = [model, meas, shimmed_meas]
        labels = ['Model', 'Meas', 'Shimmed']
        xls = [0, 0, 0]
        yls = [0, 0, 0]
        results = sh.calc_results(objs, labels, xls, yls, filename=filename_results)
        print('calc results')
    
    suptitle = polarization.upper() + ' ' + kstr.capitalize()
    filename_fig = FILES.get_filename_fig(
        dirname, polarization=polarization, kstr=kstr)
    sh.plot_results(
        results, suptitle=suptitle, filename=filename_fig)

    plt.show()


def run_plot_shims():
    dirname = 'delta_sabia_shimming_b'
    avg = True

    names = [
        'hp_kmax',
        'hp_kmed',
        'vp_kmax',
        'vp_kmed',
        'cp_kmax',
        'cp_kmed',
    ]

    shims_all = []
    fmt = '-'

    fig, ax = plt.subplots(1)
    for name in names:
        polarization = name.split('_')[0]
        kstr = name.split('_')[1]
        filename = FILES.get_filename_shims(
            dirname, polarization=polarization, kstr=kstr)
        shims = np.loadtxt(filename)
        ax.plot(shims, fmt, label=name) 

        shims_all.append(shims)

    shims_all = np.array(shims_all)

    shims_avg = np.mean(shims_all, axis=0)
    print('avg')
    print(shims_avg)
    avg = True
    rounded = False
    filename_avg = FILES.get_filename_shims(
        dirname, avg=avg, rounded=rounded)
    np.savetxt(filename_avg, shims_avg)

    available_shims = [
            0.00,
            0.05,
            0.10,
            0.15,
            0.20,
            0.25,
            0.30,
            0.35,
            0.40,
            0.45,
            0.50,
        ]
    initial_shim = 0.25
    possible_shims = np.array(available_shims) - initial_shim
    
    # tol = 0.01
    # val = 0.05
    # filt = ((possible_shims < val - tol) | (possible_shims > val + tol))
    # possible_shims = possible_shims[filt]

    # tol = 0.01
    # val = -0.05
    # filt = ((possible_shims < val - tol) | (possible_shims > val + tol))
    # possible_shims = possible_shims[filt]

    shims_round = []
    for shim in shims_avg:
        shim_round = min(possible_shims, key=lambda x: abs(x-shim))
        shims_round.append(shim_round)
    shims_round = np.round(shims_round, decimals=2)

    print('rounded')
    print(shims_round)
    ax.plot(shims_round, 'k--', label='Avg', linewidth=3)

    avg = True
    rounded = True
    filename_avg_rounded = FILES.get_filename_shims(
        dirname, avg=avg, rounded=rounded)
    np.savetxt(filename_avg_rounded, shims_round)

    ax.grid(alpha=0.3)
    ax.set_ylabel('Shims [mm]')
    ax.legend(loc='best')
    plt.show()


def run_calc_joined_shims():
    dirname = 'delta_sabia_shimming_b'
    nr_periods = 21
    nsv = 40

    phase_error_w = 2e-8

    configs = [
        'hp_kmax',
        'hp_kmed',
        'vp_kmax',
        'vp_kmed',
        'cp_kmax',
        'cp_kmed',
    ]

    cassettes = ['csd', 'cse']
    block_type = 'v'
    segments_type = 'half_period'
    include_pe = True
    solved_matrix = False
    
    m_list = []
    err_list = []
    ws_list = []
    for config in configs:
        polarization = config.split('_')[0]
        kstr = config.split('_')[1]
        filename_matrix = FILES.get_filename_matrix(
            cassettes=cassettes,
            block_type=block_type,
            segments_type=segments_type,
            solved_matrix=solved_matrix,
            include_pe= include_pe,
            polarization=polarization,
            kstr=kstr)
        m = np.loadtxt(filename_matrix)
        m_list.append(m)

        filename_error = FILES.get_filename_error(
            dirname, polarization=polarization, kstr=kstr)
        err = np.loadtxt(filename_error)
        [err_list.append(x) for x in err]

        slope_size = len(err) - 82
        ws = np.array([1.0]*len(err))
        if polarization == 'hp':
            ws[slope_size:] = phase_error_w*3
        else:
            ws[slope_size:] = phase_error_w
        [ws_list.append(x) for x in ws]

    model = load_model(
        nr_periods, 'hp', 'kmax',
        solve=False, with_errors=False,
        remove_subdivision=True)

    response_matrix = np.concatenate(m_list, axis=0)

    traj_params = get_trajectory_params(nr_periods)
    pe_params = get_phase_error_params(nr_periods)
    sh = shimming.UndulatorShimming(
        traj_params['zmin'],
        traj_params['zmax'],
        traj_params['znpts'],
        cassettes=cassettes,
        block_type=block_type,
        segments_type=segments_type,
        include_pe=include_pe,
        zmin_pe=pe_params['zmin'],
        zmax_pe=pe_params['zmax'],
        solved_matrix=solved_matrix,
        )

    rounded = False
    filename_join = FILES.get_filename_shims(
        dirname, rounded=rounded)
    shims = sh.calc_shims(
        response_matrix, err_list, nsv=nsv,
        ws=ws_list, filename=filename_join)
    print('shims [mm]: ', np.round(shims, decimals=2))

    available_shims = [
            0.00,
            0.05,
            0.10,
            0.15,
            0.20,
            0.25,
            0.30,
            0.35,
            0.40,
            0.45,
            0.50,
        ]
    initial_shim = 0.25
    possible_shims = np.array(available_shims) - initial_shim

    shims_round = []
    for shim in shims:
        shim_round = min(possible_shims, key=lambda x: abs(x-shim))
        shims_round.append(shim_round)
    shims_round = np.round(shims_round, decimals=2)
    print('rounded')
    print(shims_round)

    rounded = True
    filename_join_rounded = FILES.get_filename_shims(
        dirname, rounded=rounded)
    np.savetxt(filename_join_rounded, shims_round)


def run_compare_join_avg_shims():
    dirname = 'delta_sabia_shimming_b'
    rounded = False

    avg = True
    filename_avg = FILES.get_filename_shims(
        dirname, avg=avg, rounded=rounded)
    shims_avg = np.loadtxt(filename_avg)

    filename_join = FILES.get_filename_shims(
        dirname, rounded=rounded)
    shims_join = np.loadtxt(filename_join)

    fig, ax = plt.subplots()
    ax.plot(shims_avg, '-o', label='Avg')
    ax.plot(shims_join, '-o', label='Joined')
    ax.grid(alpha=0.3)
    ax.legend(loc='best')
    ax.set_ylabel('Shims [mm]')

    plt.show()


def run_plot_shims_results():
    fast = True
    dirname_shim = 'delta_sabia_shimming_b'
    dirname = dirname_shim + '_shims_avg'
    nr_periods = 21
    avg = True
    rounded = False
    add_label = None
    # fname = 'test8_checked.txt'

    configs = [
        'hp_kmax',
        'hp_kmed',
        'vp_kmax',
        'vp_kmed',
        'cp_kmax',
        'cp_kmed',
    ]

    cassettes = ['csd', 'cse']
    block_type = 'v'
    segments_type = 'half_period'
    include_pe = True

    if fast:
        solved_shim = False
        remove_subdivision = True
    else:
        solved_shim = True
        remove_subdivision = False

    configure_plot()
    FILES.mkdir_results(dirname)

    filename_shim = FILES.get_filename_shims(
        dirname_shim, avg=avg, rounded=rounded, add_label=add_label)
    # filename_shim = os.path.join(
    #     FILES.get_dir_results(dirname_shim), fname)
    shims = np.loadtxt(filename_shim)
    print('Shims[mm]: ', shims)
    print('Nr shims: ', len(shims.nonzero()[0]))

    filename_shim_nd = FILES.get_filename_shims(
        dirname, avg=avg, rounded=rounded, add_label=add_label)
    np.savetxt(filename_shim_nd, shims)

    filename_bn = FILES.get_filename_block_names(dirname_shim)
    names = np.loadtxt(filename_bn, dtype=str)

    filename_bn_nd = FILES.get_filename_block_names(dirname)
    np.savetxt(filename_bn_nd, names, fmt='%s')

    for config in configs:
        print(config)
        polarization = config.split('_')[0]
        kstr = config.split('_')[1]
        model = load_model(
            nr_periods, polarization, kstr,
            solve=solved_shim,
            with_errors=False,
            remove_subdivision=remove_subdivision)
        print('model loaded')

        meas = load_measurement(nr_periods, polarization, kstr)
        print('meas loaded')

        traj_params = get_trajectory_params(model.nr_periods)
        pe_params = get_phase_error_params(model.nr_periods)
        sh = shimming.UndulatorShimming(
            traj_params['zmin'],
            traj_params['zmax'],
            traj_params['znpts'],
            cassettes=cassettes,
            block_type=block_type,
            segments_type=segments_type,
            include_pe=include_pe,
            zmin_pe=pe_params['zmin'],
            zmax_pe=pe_params['zmax'],
            solved_shim=solved_shim,
            )

        filename_sig = FILES.get_filename_sig(
            dirname, polarization=polarization, kstr=kstr)
        if os.path.isfile(filename_sig):
            period = model.period_length
            gap = model.gap
            shim_signature = sh.read_fieldmap(
                filename_sig, nr_periods, period, gap)
            print('load shim signature')
        else:
            shim_signature = sh.calc_shim_signature(
                model, shims, filename=filename_sig)
            print('calc shim signature')
        
        filename_shimmed = FILES.get_filename_shimmed(
            dirname, polarization=polarization, kstr=kstr)
        if os.path.isfile(filename_shimmed):
            period = model.period_length
            gap = model.gap
            shimmed_meas = sh.read_fieldmap(
                filename_shimmed, nr_periods, period, gap)
            print('load shimmed meas')
        else:
            shimmed_meas = sh.calc_shimmed_meas(
                meas, shim_signature, filename=filename_shimmed)
            print('calc shimmed meas')

        filename_results = FILES.get_filename_results(
            dirname, polarization=polarization, kstr=kstr)
        if os.path.isfile(filename_results):
            results = sh.read_results(filename_results)
            print('load results')
        else:
            if fast:
                filename_fieldmap = FILES.get_filename_fieldmap(
                    polarization=polarization, kstr=kstr,
                    with_errors=False, remove_subdivision=False)
                period = model.period_length
                gap = model.gap
                model_fm = sh.read_fieldmap(filename_fieldmap, nr_periods, period, gap)
            else:
                model_fm = model
            objs = [model_fm, meas, shimmed_meas]
            labels = ['Model', 'Meas', 'Shimmed']
            xls = []
            yls = []
            for obj in objs:
                kicks = calc_kicks(nr_periods, obj)
                xls.append(kicks[0])
                yls.append(kicks[1])
            results = sh.calc_results(
                objs, labels, xls, yls, filename=filename_results)
            print('calc results')
        
        suptitle = polarization.upper() + ' ' + kstr.capitalize()
        filename_fig = FILES.get_filename_fig(
            dirname, polarization=polarization, kstr=kstr)
        sh.plot_results(
            results, suptitle=suptitle, filename=filename_fig,
            trajx_lim=[-15, 15], trajy_lim=[-15, 15], pe_lim=[-10, 10])


def run_calc_ff_matrix():
    nr_periods = 21
    solve = True
    with_errors = False
    remove_subdivision = False
    polarization = 'hp'
    kstr = 'kmax'

    kick = 1e-5

    filename_matrix = FILES.get_filename_ffmatrix()
    if os.path.isfile(filename_matrix):
        raise Exception('file already exists: {0:s}'.format(filename_matrix))

    model = load_model(
        nr_periods, polarization, kstr,
        solve=solve,
        with_errors=with_errors,
        remove_subdivision=remove_subdivision)
    print('model loaded')

    params = get_trajectory_params(nr_periods)

    xl = 0
    yl = 0
    zl = np.sqrt(1 - xl**2 - yl**2)
    traj0 = model.calc_trajectory(
        params['energy'],
        [params['x'], params['y'], params['zmin'], xl, yl, zl],
        params['zmax'],
        params['rkstep'],
    )
    print('calc traj0')

    xl = kick
    yl = 0
    zl = np.sqrt(1 - xl**2 - yl**2)
    trajkx = model.calc_trajectory(
        params['energy'],
        [params['x'], params['y'], params['zmin'], xl, yl, zl],
        params['zmax'],
        params['rkstep'],
    )
    dxkx = (trajkx[-1, 0] - traj0[-1, 0])/kick
    dykx = (trajkx[-1, 1] - traj0[-1, 1])/kick
    dxlkx = (trajkx[-1, 3] - traj0[-1, 3])/kick
    dylkx = (trajkx[-1, 4] - traj0[-1, 4])/kick
    print('calc trajkx')

    xl = 0
    yl = kick
    zl = np.sqrt(1 - xl**2 - yl**2)
    trajky = model.calc_trajectory(
        params['energy'],
        [params['x'], params['y'], params['zmin'], xl, yl, zl],
        params['zmax'],
        params['rkstep'],
    )
    dxky = (trajky[-1, 0] - traj0[-1, 0])/kick
    dyky = (trajky[-1, 1] - traj0[-1, 1])/kick
    dxlky = (trajky[-1, 3] - traj0[-1, 3])/kick
    dylky = (trajky[-1, 4] - traj0[-1, 4])/kick
    print('calc trajk')

    matrix = np.transpose([
        [dxkx, dykx, dxlkx, dylkx],
        [dxky, dyky, dxlky, dylky],
    ])

    np.savetxt(filename_matrix, matrix)


def run_plot_correct_traj():
    nr_periods = 21
    polarization = 'cp'
    kstr = 'kmax'

    filename_matrix = FILES.get_filename_ffmatrix()
    matrix = np.loadtxt(filename_matrix)

    u, sv, vt = shimming.UndulatorShimming.calc_svd(matrix)
    svinv = 1/sv
    minv = vt.T*svinv @ u.T

    params = get_trajectory_params(nr_periods)

    meas = load_measurement(nr_periods, polarization, kstr)

    xl = 0
    yl = 0
    zl = np.sqrt(1 - xl**2 - yl**2)
    traji = meas.calc_trajectory(
        params['energy'],
        [params['x'], params['y'], params['zmin'], xl, yl, zl],
        params['zmax'],
        params['rkstep'],
    )

    dx = traji[-1, 0]
    dy = traji[-1, 1]
    dxl = traji[-1, 3]
    dyl = traji[-1, 4]
    d = np.array([dx, dy, dxl, dyl])*(-1)

    kicks = minv @ d
    print(kicks)

    xl = kicks[0]
    yl = kicks[1]
    trajf = meas.calc_trajectory(
        params['energy'],
        [params['x'], params['y'], params['zmin'], xl, yl, zl],
        params['zmax'],
        params['rkstep'],
    )

    fig, axs = plt.subplots(2)
    axs[0].plot(traji[:, 2], traji[:, 0]*1000, label='before')
    axs[0].plot(trajf[:, 2], trajf[:, 0]*1000, label='after')
    axs[0].grid(alpha=0.3)
    axs[0].set_ylabel('x [um]')

    axs[1].plot(traji[:, 2], traji[:, 1]*1000, label='before')
    axs[1].plot(trajf[:, 2], trajf[:, 1]*1000, label='after')
    axs[1].grid(alpha=0.3)
    axs[1].legend(loc='best')
    axs[1].set_xlabel('z [mm]')
    axs[1].set_ylabel('y [um]')

    plt.show()


def run_modify_matrix():
    configs = [
        'hp_kmax',
        'hp_kmed',
        'vp_kmax',
        'vp_kmed',
        'cp_kmax',
        'cp_kmed',
    ]

    cassettes_new = ['csd']

    cassettes_old = ['csd', 'cse']
    block_type = 'v'
    segments_type = 'half_period'
    include_pe = True
    solved_matrix = False

    for config in configs:
        print(config)
        polarization = config.split('_')[0]
        kstr = config.split('_')[1]
        
        filename_old = FILES.get_filename_matrix(
            cassettes=cassettes_old,
            block_type=block_type,
            segments_type=segments_type,
            solved_matrix=solved_matrix,
            include_pe= include_pe,
            polarization=polarization,
            kstr=kstr)
        matrix_old = np.loadtxt(filename_old)

        filename_new = FILES.get_filename_matrix(
            cassettes=cassettes_new,
            block_type=block_type,
            segments_type=segments_type,
            solved_matrix=solved_matrix,
            include_pe= include_pe,
            polarization=polarization,
            kstr=kstr)

        nc = matrix_old.shape[1]
        ncc = int(nc/len(cassettes_old))

        filt = []
        for cassette in cassettes_old:
            if cassette in cassettes_new:
                filt.append([True]*ncc)
            else:
                filt.append([False]*ncc)
        filt = np.ravel(filt)

        matrix_new = matrix_old[:, filt]
        np.savetxt(filename_new, matrix_new)


def run_add_column_to_excel():
    dirname = 'delta_sabia_shimming_a_shims_test8_checked_solved'

    polarization = ''
    kstr = ''
    avg = False
    rounded = True
    fname = 'shims.txt'
    
    shim_cassettes = ['csd', 'cse']
    all_cassettes = ['cie', 'cid', 'cse', 'csd']

    filename_shims = FILES.get_filename_shims(
        dirname, avg=avg, rounded=rounded, polarization=polarization, kstr=kstr)
    filename_shims = os.path.join(FILES.get_dir_results(dirname), fname)

    filename_block_names = FILES.get_filename_block_names(dirname)
    
    shims = shimming.UndulatorShimming.read_shims(filename_shims)
    names = shimming.UndulatorShimming.read_block_names(filename_block_names)

    shim_dict = {}
    for name, shim in zip(names, shims):
        s = name.split('_')
        subcassette = s[0]
        block_name = s[1]
        shim_dict[block_name] = {'subcassette': subcassette, 'shim': shim}

    filename_excel = os.path.join(
        FILES.get_dir_results(dirname), '21periods_check_shims.xlsx')
   
    dfs = []
    for cassette in all_cassettes:
        df = pd.read_excel(filename_excel, sheet_name=cassette.upper(), header=0)
        
        if cassette not in shim_cassettes:
            dfs.append(df)
        
        else:
            colblocks = []
            colsubs = []
            coldiff = []
            colshims = []

            for idx in range(len(df)):
                block_name = df.iloc[idx, 0]
                old_shim = df.iloc[idx, 8]

                if block_name in shim_dict:
                    new_shim = shim_dict[block_name]['shim']
                    
                    if new_shim == 0:
                        colblocks.append('')
                        colsubs.append('')
                        coldiff.append('')                
                        colshims.append(old_shim)

                    else:
                        colblocks.append(block_name)
                        colsubs.append(shim_dict[block_name]['subcassette'])
                        coldiff.append(new_shim)                
                        colshims.append(new_shim + old_shim)
                else:
                    colblocks.append('')
                    colsubs.append('')
                    coldiff.append('')                
                    colshims.append(old_shim)

            df['ShimmingA Subcassete'] = colsubs
            df['ShimmingA Bloco'] = colblocks
            df['ShimmingA Diferença'] = coldiff
            df['ShimmingA Valor Final'] = colshims
            dfs.append(df)

    fn = filename_excel.replace('.xlsx', '_new.xlsx')
    with pd.ExcelWriter(fn) as writer:
        for df, cassette in zip(dfs, all_cassettes): 
            df.to_excel(writer, sheet_name=cassette.upper(), index=False)


def run_group_shims():
    dirname = 'delta_sabia_shimming_a'
    avg = False
    rounded = False
    fname = 'test8.txt'
    
    filename_shim = FILES.get_filename_shims(
        dirname, avg=avg, rounded=rounded)
    shims = np.loadtxt(filename_shim)

    tol_small = 0.05

    new_shims = []
    for idx in range(0, len(shims)-1, 2):
        shim_ba = shims[idx]
        shim_bb = shims[idx + 1]

        if np.abs(shim_ba) <= tol_small or np.abs(shim_bb) <= tol_small:
            if np.abs(shim_ba) >= np.abs(shim_bb):
                shim_ba = shim_ba - shim_bb
                shim_bb = 0
            else:
                shim_bb = shim_bb - shim_ba
                shim_ba = 0

        if np.abs(shim_ba - shim_bb) <= tol_small:
            shim_ba = 0
            shim_bb = 0

        new_shims.append(shim_ba)
        new_shims.append(shim_bb)

    new_shims_rounded = round_shims(new_shims)
    print(new_shims_rounded)
    print('Nr shims: ', len(new_shims_rounded.nonzero()[0]))
    np.savetxt(
        os.path.join(FILES.get_dir_results(dirname), fname),
        new_shims_rounded)


def run_plot_meas_results():
    dirname = 'delta_sabia_meas_results_shimming_a_other_phases'

    nr_periods = 21
    polarization = 'cp'
    kstr = 'phase10'

    if polarization == 'vp':
        field_comp = 0
    else:
        field_comp = 1

    configure_plot()
    FILES.mkdir_results(dirname)

    meas_old = load_measurement(
        nr_periods, polarization, kstr, add_label='old')
    print('meas loaded old')

    meas = load_measurement(nr_periods, polarization, kstr)
    print('meas loaded')

    period = 52.5
    gap = 13.6

    # cte_by = -0.00012
    # cte_bx = -0.00075
    # raw_data = np.transpose([
    #     meas._raw_data[:, 0],
    #     meas._raw_data[:, 1],
    #     meas._raw_data[:, 2],
    #     meas._raw_data[:, 3]*0 + cte_bx,
    #     meas._raw_data[:, 4]*0 + cte_by,
    #     meas._raw_data[:, 5]*0,
    # ])
    # cte_field = insertiondevice.InsertionDeviceData(
    #     nr_periods=nr_periods, gap=gap, period_length=period, raw_data=raw_data)
    # meas.add_field(cte_field)

    # meas_old.add_field(cte_field)

    # raw_data = np.array(meas._raw_data)
    # raw_data[:, 3] = 0
    # raw_data[:, 5] = 0
    # meas = insertiondevice.InsertionDeviceData(
    #     nr_periods=nr_periods, gap=gap, period_length=period, raw_data=raw_data)
    # print(np.max(meas.by))
    # print(np.min(meas.by))

    traj_params = get_trajectory_params(nr_periods)
    pe_params = get_phase_error_params(nr_periods)
    sh = shimming.UndulatorShimming(
        traj_params['zmin'],
        traj_params['zmax'] - 50,
        traj_params['znpts'],
        cassettes=[],
        zmin_pe=pe_params['zmin'],
        zmax_pe=pe_params['zmax'],
        field_comp=field_comp,
        )

    # filename_shimmed = FILES.get_filename_shimmed(
    #         dirname, polarization=polarization, kstr=kstr)
    # shimmed_meas = sh.read_fieldmap(
    #     filename_shimmed, nr_periods, period, gap)
    # print('load shimmed meas')

    filename_sig = FILES.get_filename_sig(
        dirname, polarization=polarization, kstr='kmax')
    shim_signature = sh.read_fieldmap(
        filename_sig, nr_periods, period, gap)
    shim_signature.shift([0, 0, 3*52.5/8 - 52.5/2])
    print('load shim signature')

    # print(shim_signature.get_field_at_point([0, 0, shim_signature.pz[-1]]))
    # print(shim_signature.get_field_at_point([0, 0, traj_params['zmax']]))

    filename_shimmed = FILES.get_filename_shimmed(
        dirname, polarization=polarization, kstr=kstr)
    shimmed_meas = sh.calc_shimmed_meas(
        meas_old, shim_signature, filename=filename_shimmed)
    print('calc shimmed meas')

    filename_results = FILES.get_filename_results(
        dirname, polarization=polarization, kstr=kstr)

    # z = np.linspace(-800, 800, 801)
    # plt.plot(shimmed_meas.get_field(z=z)[:, 0])
    # plt.plot(meas.get_field(z=z)[:, 0])
    # plt.show()

    objs = [meas_old, shimmed_meas, meas]
    labels = ['Initial', 'Predicted IterA', 'Measured IterA']

    xls = []
    yls = []
    for obj in objs:
        kicks = calc_kicks(nr_periods, obj, dz=50)
        xls.append(kicks[0])
        yls.append(kicks[1])
        print(kicks)
    results = sh.calc_results(
        objs, labels, xls, yls, filename=filename_results)
    print('calc results')
    
    suptitle = polarization.upper() + ' ' + kstr.capitalize()
    filename_fig = FILES.get_filename_fig(
        dirname, polarization=polarization, kstr=kstr)
    sh.plot_results(
        results, suptitle=suptitle,
        filename=filename_fig)

    plt.show()


def run_compare_model_meas():
    nr_periods = 21
    polarization = 'vp'
    kstr = 'kmed'
    solve = False

    configure_plot()

    traj_params = get_trajectory_params(nr_periods)
    z = np.linspace(
        traj_params['zmin'],
        traj_params['zmax'],
        traj_params['znpts'])   

    model = load_model(
        nr_periods, polarization, kstr,
        solve=solve,
        with_errors=False,
        remove_subdivision=False)
    print('model loaded')

    bmodel = model.get_field(z=z)
    print('get field model')

    pv_bx_model = model.find_peaks_and_valleys(bmodel[:, 0])
    pv_by_model = model.find_peaks_and_valleys(bmodel[:, 1])
    pv_bz_model = model.find_peaks_and_valleys(bmodel[:, 2])

    meas = load_measurement(nr_periods, polarization, kstr, zshift=1.5)
    print('meas loaded')

    bmeas = meas.get_field(z=z)
    print('get field meas')

    pv_bx_meas = meas.find_peaks_and_valleys(bmeas[:, 0])
    pv_by_meas = meas.find_peaks_and_valleys(bmeas[:, 1])
    pv_bz_meas = meas.find_peaks_and_valleys(bmeas[:, 2])

    bdiff = bmeas - bmodel

    # cte = -0.00012
    # raw_data = np.transpose([
    #     meas._raw_data[:, 0],
    #     meas._raw_data[:, 1],
    #     meas._raw_data[:, 2],
    #     meas._raw_data[:, 3]*0,
    #     meas._raw_data[:, 4]*0 + cte,
    #     meas._raw_data[:, 5]*0,
    # ])
    # cte_field = insertiondevice.InsertionDeviceData(
    #     nr_periods=nr_periods, gap=gap, period_length=period, raw_data=raw_data)
    # meas.add_field(cte_field)

    # raw_data = np.array(meas._raw_data)
    # raw_data[:, -1] = 0
    # meas = insertiondevice.InsertionDeviceData(
    #     nr_periods=nr_periods, gap=gap, period_length=period, raw_data=raw_data)
    # print(np.max(meas.bz))
    # print(np.min(meas.bz))

    # print(np.mean(np.array(pv_by_meas) - np.array(pv_by_model)))

    fig, axs = plt.subplots(3)
    for idx, comp in enumerate(['bx', 'by', 'bz']):      
        axs[idx].plot(z, bmodel[:, idx])
        axs[idx].plot(z, bmeas[:, idx])
        axs[idx].grid(alpha=0.3)
        axs[idx].set_ylabel(comp + ' [T]')
    axs[2].set_xlabel('z [mm]')

    fig, axs = plt.subplots(3)
    for idx, comp in enumerate(['bx', 'by', 'bz']):      
        axs[idx].plot(z, bdiff[:, idx])
        axs[idx].grid(alpha=0.3)
        axs[idx].set_ylabel('diff' + comp + ' [T]')
    axs[2].set_xlabel('z [mm]')
   
    fig, axs = plt.subplots(3)
    for idx, comp in enumerate(['bx', 'by', 'bz']):
        if comp == 'bx':
            pv_model = pv_bx_model
            pv_meas = pv_bx_meas
        elif comp == 'by':
            pv_model = pv_by_model
            pv_meas = pv_by_meas
        else:
            pv_model = pv_bz_model
            pv_meas = pv_bz_meas
        
        axs[idx].plot(np.abs(bmodel[pv_model, idx])[2:-2], '-o')
        axs[idx].plot(np.abs(bmeas[pv_meas, idx])[2:-2], '-o')
        axs[idx].grid(alpha=0.3)
        axs[idx].set_ylabel('diff' + comp + ' [T]')
    axs[2].set_xlabel('z [mm]')

    plt.show()


print('start')
t0 = time.time()

utils.set_len_tol()
# run_apply_shimming()
# run_plot_shims()
# run_calc_joined_shims()
# run_compare_join_avg_shims()
# run_group_shims()
# run_plot_shims_results()
# run_add_column_to_excel()
run_plot_meas_results()
# run_compare_model_meas()

print('end')
print(time.time() - t0)

