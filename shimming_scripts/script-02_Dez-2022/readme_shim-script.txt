All the relevant input variables for the shimming calculations are
stored in the par.json file, so that the python file does not need
to be modified from one calculation to the other.

More details on the shimming calculation steps and input parameters
may be found in the documentation of this package.

------------------------------------------------------------------------

The python code expects the .json files as input:
    > python d52_shim.py par.json

The inputs may be separated in several parameter .json files and passed
together to the script, which might be useful for running several tests
with a fixed set of parameters:
    > python d52_shim.py general_par.json specific_par.json

------------------------------------------------------------------------

The output files from are named based on the "out_filename_stem" key
on the .json file.
    Ex: "out_filename_stem": "hp_kmax"
    Output files:
            - hp_kmax_01_model.json
            - hp_kmax_02_rescale_log.json
            - hp_kmax_03_field-profiles.svg
            - hp_kmax_04_segs.txt
            - hp_kmax_05_matrix_mpe.txt
            - hp_kmax_05_matrix_mx.txt
            - hp_kmax_05_matrix_my.txt
            - hp_kmax_05_matrix.txt
            - hp_kmax_06-1_matrix-svalues.txt
            - hp_kmax_06-2_matrix-svalues.svg
            - hp_kmax_07_errors.txt
            - hp_kmax_08_shims.txt
            - hp_kmax_09-1_field-shim-signature.txt
            - hp_kmax_09-2_field-meas-corrected.txt
            - hp_kmax_10_results.json
            - hp_kmax_11_results.svg

------------------------------------------------------------------------

If one wants to continue a calculation from an specific step,
the "load_*" .json keys may be used. By setting one of its values to
true, the corresponding result will be loaded from a file.
    Ex: If a calculation was stopped after the response matrix was
        calculated, so that the output files are:
            - my-calc_01_model.json
            - my-calc_02_rescale_log.json
            - my-calc_03_field-profiles.svg
            - my-calc_04_segs.txt
            - my-calc_05_matrix_mpe.txt
            - my-calc_05_matrix_mx.txt
            - my-calc_05_matrix_my.txt
            - my-calc_05_matrix.txt
        The calculation may be continued by using:
            "load_rescale_factor":true,
            "load_segment_limits":true,
            "load_response_matrix":true,
            "load_errors":false,
            "load_shims":false,
            "load_field_signature":false,
            "load_field_corrected":false,
            "load_results":false,
        IMPORTANT: Here, one must set "out_filename_stem": "my-calc"