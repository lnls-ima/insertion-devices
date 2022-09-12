import os as _os


class ShimmingFiles():
    """_summary_
    """

    def __init__(self, label, root=None):
        """Initializes attributes representing base folder structure for
            shimming data:

        root/label/
        |
        |-- undulator_data/
        |-- measurements/
        |-- models/
        |-- matrix/
        |-- segments/

        Args:
            label (str): shimming data label, which is the name of the
                directory containing shimming data (of structure above).
            root (str, optional): root directory which contains the <label>
                directory. If None, is taken to be the current script
                directory. Defaults to None.
        """
        if root is None:
            root = _os.path.dirname(_os.path.abspath(__file__))
            if root is None:
                root = _os.getcwd()
        self.root = root
        self.label = label

        self.dir = _os.path.join(self.root, label)
        self.dir_undulator_data = _os.path.join(self.dir, 'undulator_data')
        self.dir_measurements = _os.path.join(self.dir, 'measurements')
        self.dir_models = _os.path.join(self.dir, 'models')
        self.dir_matrix = _os.path.join(self.dir, 'matrix')
        self.dir_segments = _os.path.join(self.dir, 'segments')

    @staticmethod
    def mkdir(dirname):
        """Create directory, if it does not already exist.

        Args:
            dirname (str): directory name.

        Returns:
            bool: False, if directory already exists and was not created.
            No return (None) if directory was created.
        """
        if not _os.path.isdir(dirname):
            return _os.mkdir(dirname)
        return False

    @staticmethod
    def _get_modelstr(with_errors, remove_subdivision):
        """Returns string 'model' + appended suffixes.

        Args:
            with_errors (bool): if True, '_with_errors' is appended to string.
            remove_subdivision (bool): if True, '_nsub' is appended to string.

        Returns:
            str: 'model', 'model_with_errors', 'model_nsub' or
                'model_with_errors_nsub', depending on input bools.
        """
        s = 'model'
        if with_errors:
            s += '_with_errors'
        if remove_subdivision:
            s += '_nosub'
        return s

    @staticmethod
    def _get_configstr(polarization, kstr):
        """Returns polarization+'_'+kstr string. Used as building block for
            generating file and directory names.

        '_' characters are stripped from the beginning and end of output.

        Args:
            polarization (str): polarization string.
            kstr (str): k string.

        Returns:
            str: String of the form polarization + '_' + kstr
        """
        s = '_'.join([polarization, kstr]).strip('_')
        return s

    def _get_shimsstr(self, avg, rounded, polarization, kstr):
        """Returns string of format 'avg_rounded_' + polarization + '_' + kstr.

        '_' characters are stripped from the beginning and end of output and
        '__' are replaced by '_'.

        Args:
            avg (bool): if true, output will contain 'avg' section.
            rounded (bool): if true, output will contain 'rounded' section.
            polarization (str): polarization string.
            kstr (str): k string.

        Returns:
            str: output string of format ('', 'avg_', 'rounded_' or
                'avg_rounded_') + polarization + '_' + kstr.
        """
        avgstr = 'avg' if avg else ''
        roundedstr = 'rounded' if rounded else ''
        configstr = self._get_configstr(polarization, kstr)
        s = '_'.join([avgstr, roundedstr, configstr]).strip('_')
        s = s.replace('__', '_')
        return s

    def _get_filename_config(
            self, results_label, file_label, file_ext, **kwargs):
        """Returns path for file with given name and extension inside a
            given results folder whose name is given by file_label, file_ext
                and **kwargs.

            kwargs may include 'polarization' and 'kstr' (inputs to
                _get_configstr).

        Args:
            results_label (str): results folder name, the same folder as
                would be created by the mkdir_results method.
            file_label (str): File stem/label name, without extension.
            file_ext (str): File extension.

        Returns:
            str: path to file inside results folder.
        """
        polarization = kwargs.get('polarization', '')
        kstr = kwargs.get('kstr', '')

        dir_results = self.get_dir_results(results_label)

        configstr = self._get_configstr(polarization, kstr)
        name = '_'.join([file_label, configstr]).strip('_')
        name += file_ext

        return _os.path.join(dir_results, name)

    def get_dir_results(self, results_label):
        """Generate path of results directory named by input argument.

        Path for new folder is situated inside self.dir parent folder.

        Args:
            results_label (str): results directory name.

        Returns:
            str: path to results folder inside parent self.dir folder.
        """
        return _os.path.join(self.dir, results_label)

    def create_dir_structure(self):
        """Creates base folder structure for shimming data. The parent folder
            is given by the path stored in self.dir.

        dir/    # given by self.dir
        |
        |-- undulator_data/
        |-- measurements/
        |-- models/
        |-- matrix/
        |-- segments/
        """
        self.mkdir(self.dir)
        self.mkdir(self.dir_undulator_data)
        self.mkdir(self.dir_measurements)
        self.mkdir(self.dir_models)
        self.mkdir(self.dir_matrix)
        self.mkdir(self.dir_segments)

    def mkdir_results(self, results_label):
        """Create results directory inside parent data folder (self.dir).

        Args:
            results_label (str): results directory name.

        Returns:
            bool: False, if directory already exists and was not created.
            No return (None) if directory was created.
        """
        return self.mkdir(self.get_dir_results(results_label))

    def get_filename_model(self, **kwargs):
        """Returns path to .txt file in self.dir_models directory whose name
        is given by **kwargs.

        kwargs may include 'with_errors', 'remove_subdivision' (inputs passed
        to _get_modelstr), and 'add_label' (additional suffix label separated
        by '_').

        Returns:
            str: path to file inside models folder.
        """
        with_errors = kwargs.get('with_errors')
        remove_subdivision = kwargs.get('remove_subdivision')
        add_label = kwargs.get('add_label')

        ext = '.txt'
        name = self._get_modelstr(with_errors, remove_subdivision)
        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(self.dir_models, name)

    def get_filename_fieldmap(self, **kwargs):
        """Returns path to .txt fieldmap file in self.dir_models directory
            whose name is given by **kwargs.

            kwargs may include 'with_errors', 'remove_subdivision' (inputs
            to _get_modelstr), polarization, kstr (inputs to _get_configstr),
            and 'add_label' (additional suffix label separated by '_').

        Returns:
            str: path to fieldmap file inside models folder.
        """
        with_errors = kwargs.get('with_errors')
        remove_subdivision = kwargs.get('remove_subdivision')
        polarization = kwargs.get('polarization', '')
        kstr = kwargs.get('kstr', '')
        add_label = kwargs.get('add_label')

        ext = '.txt'
        label = 'fieldmap'
        modelstr = self._get_modelstr(with_errors, remove_subdivision)
        configstr = self._get_configstr(polarization, kstr)
        name = '_'.join([label, modelstr, configstr]).strip('_')

        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(self.dir_models, name)

    def get_filename_shims(self, results_label, **kwargs):
        """Returns path to .txt shims file in a given results folder whose
            name is given by **kwargs.

            kwargs may include 'avg', 'rounded', 'polarization', 'kstr'
            (inputs to _get_shimsstr), and 'add_label' (additional suffix
            label separated by '_').

        Args:
            results_label (str): results directory name.

        Returns:
            str: path to sims file inside given results folder.
        """
        polarization = kwargs.get('polarization', '')
        kstr = kwargs.get('kstr', '')
        avg = kwargs.get('avg')
        rounded = kwargs.get('rounded')
        add_label = kwargs.get('add_label')

        dir_results = self.get_dir_results(results_label)

        ext = '.txt'
        label = 'shims'
        shimstr = self._get_shimsstr(avg, rounded, polarization, kstr)
        name = '_'.join([label, shimstr]).strip('_')

        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(dir_results, name)

    def get_filename_block_names(self, results_label, **kwargs):
        """Returns path to .txt block names file in a given results folder
            whose name is given by **kwargs.

            kwargs may include 'add_label' (additional suffix label
            separated by '_')

        Args:
            results_label (str): results directory name.

        Returns:
            str: path to block names file inside given results folder.
        """
        add_label = kwargs.get('add_label')
        dir_results = self.get_dir_results(results_label)

        ext = '.txt'
        name = 'block_names'
        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(dir_results, name)

    def get_filename_error(self, results_label, **kwargs):
        """Returns path to .txt errors file in a given results folder whose
            name is given by **kwargs.

            kwargs may include 'polarization' and 'kstr' (inputs to
            _get_configstr).

        Args:
            results_label (str): results directory name.

        Returns:
            str: path to errors file inside given results folder.
        """
        file_label = 'error'
        file_ext = '.txt'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_sig(self, results_label, **kwargs):
        """Returns path to .txt signature file in a given results folder 
            whose name is given by **kwargs.

            kwargs may include 'polarization' and 'kstr' (inputs to
            _get_configstr).

        Args:
            results_label (str): results directory name.

        Returns:
            str: path to signature file inside given results folder.
        """
        file_label = 'sig'
        file_ext = '.txt'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_shimmed(self, results_label, **kwargs):
        """Returns path to .txt shimmed data file in a given results folder
        whose name is given by **kwargs.

            kwargs may include 'polarization' and 'kstr' (inputs to
            _get_configstr).

        Args:
            results_label (str): results directory name.

        Returns:
            str: path to shimmed data file inside given results folder.
        """
        file_label = 'shimmed'
        file_ext = '.txt'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_fig(self, results_label, **kwargs):
        """Returns path to .png figure in a given results folder whose
        name is given by **kwargs.

            kwargs may include 'polarization' and 'kstr' (inputs to
            _get_configstr).

        Args:
            results_label (str): results directory name.

        Returns:
            str: path to figure inside given results folder.
        """
        file_label = 'fig'
        file_ext = '.png'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_results(self, results_label, **kwargs):
        """Returns path to .txt results file in a given results folder whose
        name is given by **kwargs.

            kwargs may include 'polarization' and 'kstr' (inputs to
            _get_configstr).

        Args:
            results_label (str): results directory name.

        Returns:
            str: path to file inside given results folder.
        """
        file_label = 'results'
        file_ext = '.txt'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_undulator_data(self):
        """Returns path to .xlsx undulator data file in the undulator_data
            folder.

        Returns:
            str: path to undulator data file inside undulator_data folder.
        """
        name = 'undulator_data.xlsx'
        return _os.path.join(self.dir_undulator_data, name)

    def get_filename_segs(self, **kwargs):
        """Returns path to segments file inside segments folder whose name
            is given by **kwargs.

        kwargs may include 'polarization', 'kstr' (inputs to _get_configstr),
            'block_type', 'segments_type' and 'add_label' (additional file
            name building blocks separated by '_')

        Returns:
            str: path to segments file inside segments folder.
        """
        block_type = kwargs.get('block_type', '')
        segments_type = kwargs.get('segments_type', '')
        polarization = kwargs.get('polarization', '')
        kstr = kwargs.get('kstr', '')
        add_label = kwargs.get('add_label')

        ext = '.txt'
        label = 'segs'
        configstr = self._get_configstr(polarization, kstr)
        name = '_'.join([label, configstr, block_type, segments_type]).strip('_')

        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(self.dir_segments, name)

    def get_filename_ffmatrix(self):
        """Returns path to 'ffmatrix.txt' file inside the dir_matrix folder.

        Returns:
            str: path to 'ffmatrix.txt' file inside dir_matrix folder.
        """
        name = 'ffmatrix.txt'
        return _os.path.join(self.dir_matrix, name)

    def get_filename_matrix(self, **kwargs):
        """Returns path to .txt response matrix file inside dir_matrix folder
            whose name is given by **kwargs.

        kwargs may include 'polarization', 'kstr' (inputs to _get_configstr),
            'segments_type', 'block_type', 'add_label' (additional file
            name building blocks separated by '_'), 'cassettes' (dictionary
            whose keys identify cassettes), 'solved_matrix' (boolean defining
            if '_solved' is added to file name) and 'include_pe' (boolean
            defining if '_includepe' is added to file name).

        Returns:
            str: path to response matrix file inside matrices folder.
        """
        cassettes = kwargs.get('cassettes')
        block_type = kwargs.get('block_type', '')
        segments_type = kwargs.get('segments_type', '')
        solved_matrix = kwargs.get('solved_matrix')
        include_pe = kwargs.get('include_pe')
        polarization = kwargs.get('polarization', '')
        kstr = kwargs.get('kstr', '')
        add_label = kwargs.get('add_label')

        ext = '.txt'
        label = 'matrix'
        configstr = self._get_configstr(polarization, kstr)
        name = '_'.join([label, block_type, segments_type]).strip('_')
        for cassette in cassettes:
            name += '_' + cassette
        if solved_matrix:
            name += '_solved'
        if include_pe:
            name += '_includepe'
        if len(configstr) > 0:
            name += '_' + configstr

        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(self.dir_matrix, name)

    def get_filename_measurement(self, **kwargs):
        """Returns path to .dat measurement file in the dir_measurements
            folder whose name is given by **kwargs.

            kwargs may include 'avg', 'rounded', 'polarization', 'kstr'
            (inputs to _get_shimsstr), and 'add_label' (additional label
            separated by '_').

        Returns:
            str: path to file inside measurements folder.
        """
        polarization = kwargs.get('polarization', '')
        kstr = kwargs.get('kstr', '')
        add_label = kwargs.get('add_label')

        ext = '.dat'
        name = self._get_configstr(polarization, kstr)
        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(self.dir_measurements, name)

