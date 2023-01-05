"""
This script runs a shimming calculation based on a measurement
text file and a .xlsx file containing block names of the device.

The specific model is defined in this script as an exemple,
all remaining parameters are stored in a JSON file.

More information is found in the readme_shim-script.txt file
and in the package documentation.
"""

import datetime
import json
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from imaids.insertiondevice import InsertionDeviceData
from imaids.models import DeltaSabia
from imaids.shimming import UndulatorShimming

#---- FUNCTIONS --------------------------------------------------------------#

def time_log(s):
    time_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(s + ' (' + time_str + ')')

def group_block_names(names, subcassettes):
    """Returns list of group names based on lists of names and subcassettes.

    Args:
        names (list of str): Block names/labels, in which first two characters
            represent a block type.
        subcassettes (list of str): Subcassette labels list.

    Returns:
        list of str: List of block names, to which cassette names were
            prepended (<cassette>_<block>).
            If there are two consecutive blocks in the input names list which
            are of the same type, both labels are grouped in a single label
            (<cassette>_<block>_<block of the same type>).
    """
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

def block_names_from_xls(filename,
                            cassette_sheets={'cid':'CID', 'cie':'CIE',
                                            'csd':'CSD', 'cse':'CSE'},
                            names_column=0,
                            subcassettes_column=4):
    """Create blocks shimming info dictionaries from .xlsx file.

    In the .xlsx input file, the information of each cassette must
    be stores in a separate sheet.
    (!) The first line in each sheet is taken as column headers.

    Args:
        filename (str): .xls file path.
        cassette_sheets (dict): Cassette sheets in xls file. The keys
            in this dictioanary must match the model cassette names.
            Values are the sheet names in the .xlsx file.
        names_column (int): index (starting at 0) of the column of
            block names.
        subcassettes_column (int): index (starting at 0) of the column
            of subcassette names.

    Returns:
        dict: dictionary containing block names grouped by subcassette,
            as N lists corresponding to the cassettes specified in the
            cassettes argument and keyed by its strings.
    """

    block_names_dict = {}

    for cassette, sheet in cassette_sheets.items():
        df = pd.read_excel(filename, sheet_name=sheet, header=0)
        # Full block names list from original names and subcassettes.
        df_ns = df.iloc[:, names_column]
        df_sc = df.iloc[:, subcassettes_column]
        block_names_dict[cassette] = group_block_names(df_ns, df_sc)

    return block_names_dict

#--- BEGIN SCRIPT ------------------------------------------------------------#

time_log('Script start')

#--- INPORT AND DISPLAY PARAMETERS -------------------------------------------#

par = {}
for par_json in sys.argv[1:]:
    with open(par_json, 'r') as f:
        par.update(json.load(f))

print("Inported parameters:")
for key in par:
    print(f'\t{key:<29} : {par[key]}')
print()

#--- CREATE OBJECTS FOR RADIA MODEL AND MEASUREMENT DATA ---------------------#

model_filename = par['out_filename_stem'] + '_01_model.json'

model = DeltaSabia(init_radia_object=False)
# Names are taken from an xls file using a custom function for our case.
block_names = block_names_from_xls(par['model_xls_filename'],
                    cassette_sheets=par['model_xls_cassette_sheets'],
                    names_column=par['model_xls_names_column'],
                    subcassettes_column=par['model_xls_subcassettes_column'])
model.create_radia_object(block_names_dict=block_names)
model.set_cassete_positions(dgv=par['dgv'], dp=par['dp'])
model.save_state(model_filename)
print(f'> [output] Model parameters saved to {model_filename}')

meas = InsertionDeviceData(nr_periods=model.nr_periods,
                            period_length=model.period_length,
                            gap=model.gap,
                            selected_y=par['selected_y'],
                            filename=par['meas_filename'])

print('> Model and measurement objects set up')

#--- CREATE SHIMMING OBJECT -------------------------------------------#

sh = UndulatorShimming(
        zmin=par['zmin'], zmax=par['zmax'], znpts=par['znpts'],
        rkstep=par['rkstep'], include_pe=True,
        zmin_pe=par['zmin_pe'], zmax_pe=par['zmax_pe'],
        field_comp=par['field_comp'], cassettes=par['cassettes'],
        block_type=par['block_type'], segments_type=par['segments_type'],
        solved_matrix=par['solved_matrix'], solved_shim=par['solved_shim'])

#--- RESCALE MODEL MAGNETIZATION --------------------------------------#

if par['scale_mr']:

    fres_log_filename = par['out_filename_stem'] + '_02_rescale_log.json'

    if par['load_rescale_factor']:
        fres = UndulatorShimming.read_rescale_factor(fres_log_filename)
        print(f'> [input] Rescaling log read from: {fres_log_filename}')

    else:
        fres = sh.calc_rescale_factor(model, meas, filename=fres_log_filename)
        model_res = DeltaSabia(mr=model.cassette_properties['mr']*fres,
                            init_radia_object=False)
        model_res.create_radia_object(block_names_dict=model.block_names_dict)
        model_res.set_cassete_positions(dgv=model.dgv, dp=model.dp)
        model = model_res
        print(f'> [output] Rescaling log saved to: {fres_log_filename}')

    print(f'> Model magnetization multiplied by: {fres}', end='', flush=True)
    if par['load_rescale_factor']:
        print(' (from rescaling log file)')
    else:
        print(' (calculated rescale)')

else:

    print('> Skipped model rescaling')

#--- INITIAL SOLVE ----------------------------------------------------#

model.solve()
print('> Model initial solve() done')

#--- PLOT MODEL AND MEASUREMENT FIELD PROFILES ------------------------#

if par['plot_field_profiles']:

    z = np.linspace(par['zmin'], par['zmax'], par['znpts'])
    plot_profiles_filename = par['out_filename_stem'] + '_03_field-profiles.svg'

    fig, ax = plt.subplots(2,1,figsize=(10,5), constrained_layout=True)
    ax[0].plot(z, model.get_field(z=z), label=['Bx', 'By', 'Bz'])
    ax[0].legend()
    ax[0].set_title('Radia model')
    ax[1].plot(z, meas.get_field(z=z), label=['Bx', 'By', 'Bz'])
    ax[1].legend()
    ax[1].set_title('Measurement')

    fig.savefig(plot_profiles_filename)

    print(f'> [output] Exported: {plot_profiles_filename}')

#--- DETERMINE TRAJECTORY SEGMENT LIMITS ------------------------------#

segs_filename = par['out_filename_stem'] + '_04_segs.txt'

if par["load_segment_limits"]:
    segs = sh.read_segs(segs_filename)
    print(f'> [input] Segments read from: {segs_filename}')
else:
    segs = sh.calc_segments(model, filename=segs_filename)
    print(f'> [output] Segments saved to {segs_filename}')

#--- CALCULATE RESPONSE MATRIX ----------------------------------------#

matrix_filename = par['out_filename_stem'] + '_05_matrix.txt'

if par["load_response_matrix"]:
    matrix = sh.read_response_matrix(matrix_filename)
    print(f'> [input] Response matrix read from {matrix_filename}')
else:
    print('> Calculating response matrix... ', end='', flush=True)
    t1 = time.perf_counter()
    matrix = sh.calc_response_matrix(model, segs, filename=matrix_filename)
    t2 = time.perf_counter()
    print(f'DONE (took {(t2-t1)/60:.4f} min)')
    print(f'> [output] Response matrix saved to {matrix_filename}')

#--- DETERMINE NUMBER OF SINGULAR VALUES ------------------------------#

if par['nsv'] is None:
    _, sv, _ = UndulatorShimming.calc_svd(matrix)
    nsv = 2
    current_min_sv_ratio = sv[1]/sv[0]
    for i in range(2,len(sv)):
        if sv[i]/sv[i-1] < current_min_sv_ratio:
            nsv = i + 1
            current_min_sv_ratio = sv[i]/sv[i-1]

else:
    nsv = par['nsv']

print(f'> Number of singular values: {nsv}', end='', flush=True)
if par['nsv'] is None:
    print(' (automatic nsv)')
else:
    print()

#--- PLOT SINGULAR VALUES ---------------------------------------------#

if par["plot_singular_values"]:

    svalues_filename = par['out_filename_stem'] + '_06-1_matrix-svalues.txt'
    plot_svalues_filename = par['out_filename_stem'] + '_06-2_matrix-svalues.svg'

    _, sv, _ = UndulatorShimming.calc_svd(matrix)
    fig, ax = plt.subplots(figsize=(20,3), constrained_layout=True)
    ax.plot(np.arange(1, len(sv)+1), sv, 'o-', c='k')
    ax.plot(np.arange(1, nsv+1), sv[:nsv], 'o-', c='b')
    ax.axvspan(0.8, nsv, color='lavender')
    ax.set_xlabel('Index+1')
    ax.set_ylabel('Singular value')
    ax.set_yscale('log')
    ax.set_xticks(np.arange(1,len(sv)+1))
    ax.set_xlim([0.8,len(sv)+0.2])
    ax.grid()

    fig.savefig(plot_svalues_filename)
    np.savetxt(svalues_filename, sv)

    print(f'> Exported: {plot_svalues_filename}')

#--- CALCULATE SLOPE ERRORS AND PHASE ERRORS --------------------------#

errors_filename = par['out_filename_stem'] + '_07_errors.txt'

if par["load_errors"]:
    errors = sh.read_error(errors_filename)
    print(f'> [input] Errors read from: {errors_filename}')
else:
    errors = sh.calc_error(model=model, meas=meas,
                            model_segs=segs, meas_segs=segs,
                            filename=errors_filename)
    print(f'> [output] Errors saved to: {errors_filename}')

#--- DETERMINE WEIGHTS FOR ERRORS VECTOR ------------------------------#

# Initial weights array. This array will be populated considering
# three factors stored in a weight_factors array.
# If there are N segment slopes and M phase error poles:
#     > the first N values of error_weights will be weight_factors[0]
#       (x slope weights).
#     > the following N values will be weight_facotrs[1]
#       (y slope weights).
#     > the final M values of error_weights will be weight_factors[2]
#       (error weights).
error_weights = np.array([1.0]*int(matrix.shape[0]))

# If the weight factors are not provided at input, they are determined
# by the error values themselves. The weight for each kind of error
# (x slopes, y slopes and phase_errors) will be the inverse of that
# error values RMS, normalized with respect to the other weights.
if par['error_weight_factors'] is None:
    rms = lambda a: np.sqrt(np.sum(np.square(a)))
    inverse_weight_factors = np.array([
        rms(errors[:len(segs)]),
        rms(errors[len(segs):2*len(segs)]),
        rms(errors[2*len(segs):])
    ])
    weight_factors = 1/inverse_weight_factors
    weight_factors = weight_factors/np.max(weight_factors)

else:
    weight_factors = np.array(par['error_weight_factors'])

error_weights[:len(segs)] = weight_factors[0]
error_weights[len(segs):2*len(segs)] = weight_factors[1]
error_weights[2*len(segs):] = weight_factors[2]

print(f'> Weight Factors: {weight_factors}', end='', flush=True)
if par['error_weight_factors'] is None:
    print(' (automatic weights)')
else:
    print()

#--- CALCULATE SHIMS --------------------------------------------------#

shims_filename = par['out_filename_stem'] + '_08_shims.txt'

if par["load_shims"]:
    print(f'> [input] Shims read from: {segs_filename}')
    shims = sh.read_shims(shims_filename)
else:
    print(f'> [output] Shims saved to: {shims_filename}')
    shims = sh.calc_shims(response_matrix=matrix, error=errors, ws=error_weights,
                            nsv=nsv, filename=shims_filename)

#--- CALCULATE SHIM SIGNATURE AND CORRECTED MEASUREMENT FIELD ---------#

signature_filename = (par['out_filename_stem']
                                    + '_09-1_field-shim-signature.txt')
corrected_filename = (par['out_filename_stem']
                                    + '_09-2_field-meas-corrected.txt')

if par["load_field_signature"]:
    print(f'> [input] Shim field signature read from: {segs_filename}')
    model_signature = sh.read_fieldmap(filename=signature_filename,
                                       nr_periods=model.nr_periods,
                                       period=model.period_length,
                                       gap=model.gap)
else:
    model_signature = sh.calc_shim_signature(model=model,
                                            shims=shims,
                                            filename=signature_filename)
    print(f'> [output] Signature fieldmap saved to: {signature_filename}')

if par["load_field_corrected"]:
    print(f'> [input] Corrected field read from: {segs_filename}')
    meas_corrected = sh.read_fieldmap(filename=corrected_filename,
                                      nr_periods=model.nr_periods,
                                      period=model.period_length,
                                      gap=model.gap)
else:
    meas_corrected = sh.calc_shimmed_meas(meas=meas,
                                          shim_signature=model_signature,
                                          filename=corrected_filename)
    print(f'> [output] Corrected fieldmap saved to: {corrected_filename}')

#--- CALCULATE RESULTS DICTIONARY AND SAVE DO JSON FILE  --------------#

results_filename = par['out_filename_stem'] + '_10_results.json'

if par["load_results"]:
    results = sh.read_results(results_filename)
    print(f'> [input] Results read from: {segs_filename}')
else:
    results = sh.calc_results(objs=[meas, model_signature, meas_corrected],
                                labels=['meas', 'model_signature', 'meas_corrected'],
                                filename=results_filename)
    print(f'> [output] Results overview saved to: {results_filename}')

#--- PLOT RESULTS -------- ---------------------------------------------#

plot_results_filename = par['out_filename_stem'] + '_11_results.svg'

fig = sh.plot_results(results, figsize=(17,6))
fig.savefig(plot_results_filename)

print(f'> [output] Exported: {plot_results_filename}')

#--- END SCRIPT -------------------------------------------------------#

time_log('Script end')
