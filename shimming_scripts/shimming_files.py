
import os as _os


class ShimmingFiles():

    def __init__(self, label, root=None):
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
        if not _os.path.isdir(dirname):
            return _os.mkdir(dirname)
        return False

    @staticmethod
    def _get_modelstr(with_errors, remove_subdivision):
        s = 'model'
        if with_errors:
            s += '_with_errors'
        if remove_subdivision:
            s += '_nosub'
        return s

    @staticmethod
    def _get_configstr(polarization, kstr):
        s = '_'.join([polarization, kstr]).strip('_') 
        return s

    def _get_shimsstr(self, avg, rounded, polarization, kstr):
        avgstr = 'avg' if avg else ''
        roundedstr = 'rounded' if rounded else ''       
        configstr = self._get_configstr(polarization, kstr)
        s = '_'.join([avgstr, roundedstr, configstr]).strip('_')
        s = s.replace('__', '_')
        return s

    def _get_filename_config(
            self, results_label, file_label, file_ext, **kwargs):
        polarization = kwargs.get('polarization', '')
        kstr = kwargs.get('kstr', '')

        dir_results = self.get_dir_results(results_label)
        
        configstr = self._get_configstr(polarization, kstr)
        name = '_'.join([file_label, configstr]).strip('_') 
        name += file_ext

        return _os.path.join(dir_results, name)        

    def get_dir_results(self, results_label):
        return _os.path.join(self.dir, results_label)

    def create_dir_structure(self):
        self.mkdir(self.dir)
        self.mkdir(self.dir_undulator_data)
        self.mkdir(self.dir_measurements)
        self.mkdir(self.dir_models)
        self.mkdir(self.dir_matrix)
        self.mkdir(self.dir_segments)

    def mkdir_results(self, results_label):
        return self.mkdir(self.get_dir_results(results_label))

    def get_filename_model(self, **kwargs):
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
        add_label = kwargs.get('add_label')
        dir_results = self.get_dir_results(results_label)

        ext = '.txt'
        name = 'block_names'
        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(dir_results, name)

    def get_filename_error(self, results_label, **kwargs):
        file_label = 'error'
        file_ext = '.txt'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_sig(self, results_label, **kwargs):
        file_label = 'sig'
        file_ext = '.txt'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_shimmed(self, results_label, **kwargs):
        file_label = 'shimmed'
        file_ext = '.txt'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_fig(self, results_label, **kwargs):
        file_label = 'fig'
        file_ext = '.png'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_results(self, results_label, **kwargs):
        file_label = 'results'
        file_ext = '.txt'
        return self._get_filename_config(
            results_label, file_label, file_ext, **kwargs)

    def get_filename_undulator_data(self):
        name = 'undulator_data.xlsx'
        return _os.path.join(self.dir_undulator_data, name)

    def get_filename_segs(self, **kwargs):
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
        name = 'ffmatrix.txt'
        return _os.path.join(self.dir_matrix, name)

    def get_filename_matrix(self, **kwargs):       
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
        polarization = kwargs.get('polarization', '')
        kstr = kwargs.get('kstr', '')
        add_label = kwargs.get('add_label')

        ext = '.dat'
        name = self._get_configstr(polarization, kstr)
        if add_label is not None:
            name += '_' + add_label
        name += ext

        return _os.path.join(self.dir_measurements, name)

