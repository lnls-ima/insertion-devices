
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import blocks as _blocks
from . import fieldsource as _fieldsource


class Cassette(
        _fieldsource.FieldModel, _fieldsource.SinusoidalFieldSource):
    """Insertion device cassette.
    
    The cassette is composed of magnetic blocks (blocks.Block objects),
    with specified materials, lengths and gaps, assembled in a line along
    the longitudinal direction (z).

    Cassettes are defined by periods of 4 blocks, which may be:
        > Non-hybrid (default): Linear material blocks (permanent magnets)
          in a Halbach array scheme, with magnetizations in directions following
          the sequence:
              (...)
              y+ (0, 1, 0)
              z- (0, 0,-1)
              y- (0,-1, 0)
              z+ (0, 0, 1)
              (...)
            * first core block magnetization may be chosen between y+ and y-.
        > Hybrid: 2nd and 4th blocks are permanent magnet blocks with
          magnetization in the z+/z- directions while 1st and 3rd blocks
          (poles) are made of a non-linear material characterized by an
          and with initial magnetization (0,0,0).

    Terminology:
        > Block: Permanent magnet block, made of linear anisotropic material.
        > Pole: Hybrid undulator pole, made of non-linear isotropic material.
        > Start/end block: optional additional blocks at cassette's start/end.
            They may have specific custom lengths and gaps between them.
        > Core block: block which is not a start nor an end block.
            All core blocks have the same lengths and gaps along all periods.
    """

    def __init__(
            self, nr_periods, period_length, block_shape,
            mr=1.37, upper_cassette=False, longitudinal_distance=0,
            block_subdivision=None, rectangular=False,
            ksipar=0.06, ksiper=0.17, hybrid=False,
            pole_shape=None, pole_length=None, pole_material=None,
            pole_subdivision=None,
            start_blocks_length=None, start_blocks_distance=None,
            end_blocks_length=None, end_blocks_distance=None,
            name='', init_radia_object=True):
        """Gathers cassette properties from arguments and calls method for
            creating Radia object.

        Args:
            nr_periods (int): Number of complete periods.
            period_length (float, optional): Period length in mm.             
            block_shape (list, Mx2 or NxMx2): List defining blocks
                geometry. Single list or N nested lists of M 2D points defining
                convex polygons which form the cross-section of a block (as
                described in blocks.Block). In mm.
            mr (float, optional): magnitude of remanent magnetization vector
                Defines magnetization vector modulus for linear material used
                at the blocks. In Tesla. Must be >= 0. Defaults to 1.37.  
            upper_cassette (bool, optional): Defines direction of the first
                core block magnetization and, consequentely, the directions
                sequency for the Halbach array period used:
                    If True:   y+, z-, y-, z+ 
                    If False:  y-, z+, y+, z-
                Defaults to False.
            longitudinal_distance (int, optional): Longitudinal gap between
                adjacent core blocks or between core blocks and poles in the
                case of a hybrid cassette, in mm. Must be >= 0. Defaults to 0.
            block_subdivision (list, 3 or Nx3, optional): Defines the block
                subdivision for the Radia calculation. Single list of (x,y,z)
                subdivisions or nested list of N 3-vector (x,y,z) subdivisoins,
                (as described in blocks.Blocks). Must have the same N length of
                block_shape list. Defaults to None, meaning no subdivision.
            rectangular (bool, optional): Used for initialization of blocks and
                poles. If True the both are created as Radia ObjRecMag objects.
                If False both are created as Radia ObjThckPgn objects.
                Defaults to False.
            ksipar (float, optional): Block susceptibility parallel to
                easy axis (magnetization diraction). Defaults to 0.06.
            ksiper (float, optional): Block susceptibility perpendicular to
                easy axis (magnetization diraction). Defaults to 0.17.
            hybrid (bool, optional): If True, hybrid undulator cassette is
                created with alternating blocks and poles. If False, cassette
                is created with only blocks. Defaults to False.                
            pole_shape (list, Mx2 or NxMx2,  optiona): Pole shape in the same
                format as block_shape, in mm. If None pole shape will be the
                same as block shape. Defaults to None. 
            pole_length (float, optional): Pole length in mm.
                If hybrid==True, must be not None. Defaults to None.                
            pole_material (materials.Material, optional): Material applyed to
                poles blocks.Block objects, which are generated with [0,0,0]
                initial magnetization.
                If hybrid==True, must be not None. Defaults to None.
            pole_subdivision (list, 3 or Nx3, optional): Pole subdivision in
                the same format as block_subdivision. Must have same N length
                of pole_shape (or block_shape, if pole_shape==None).
                Defaults to None, meaning no subdivision.       
            start_blocks_length (list, K, optional): List of K block lengths,
                one length for each start block, in mm. Only used if both
                start_blocks_length and start_blocks_distance are not None.
                Defaults to None.
            start_blocks_distance (list, K optional): List of K distances,
                one for each start block, in which each distance is the gap
                AFTER the corresponding block, in mm. Only used if both
                start_blocks_length and start_blocks_distance are not None.
                Defaults to None.            
            end_blocks_length (list, L, optional): List of L block lengths,
                one length for each end block, in mm. Only used if both
                end_blocks_length and end_blocks_distance are not None.
                Defaults to None.            
            end_blocks_distance (list, L optional): List of L distances,
                one for each end block, in which each distance is the gap
                BEFORE the corresponding block, in mm. Only used if both
                end_blocks_length and end_blocks_distance are not None.
                Defaults to None.
            name (str, optional): Name labeling the cassette. Defaults to ''.             
            init_radia_object (bool, optional): If True, Radia object is
                created at object initialization. Defaults to True.

        Note: length of core blocks is not given by an initialization argumnt,
        but determind by the number of periods, period length, longitudinal
        distance and (possibly, if hybrid==True) pole length. Such length
        determination is performed by the create_radia_object method.

        Raises:
            ValueError: If mr < 0.
            ValueError: If longitudinal_distance < 0.
            ValueError: If upper_cassette is not True or False.
            ValueError: If start_blocks_length and start_blocks_distance
                do not have the same number of elements.
            ValueError: If end_blocks_length and end_blocks_distance
                do not have the same number of elements.
            ValueError: If pole_length is not provided in the hybrid case
                (hybrid==True and pole_length==None).
            ValueError: If pole_material is not provided in the hybrid case
                (hybrid==True and pole_material==None).
        """
        _fieldsource.SinusoidalFieldSource.__init__(
            self, nr_periods=nr_periods, period_length=period_length)

        if mr is not None and mr < 0:
            raise ValueError('mr must be >= 0.')
        self._mr = float(mr)

        if longitudinal_distance is not None and longitudinal_distance < 0:
            raise ValueError('longitudinal_distance must be >= 0.')
        self._longitudinal_distance = longitudinal_distance

        if upper_cassette not in (True, False):
            raise ValueError('Invalid value for upper_cassette argument.')
        self._upper_cassette = upper_cassette

        self._block_shape = block_shape
        self._rectangular = rectangular

        if start_blocks_length and start_blocks_distance:
            if len(start_blocks_length) != len(start_blocks_distance):
                raise ValueError('Incosistent start blocks arguments.')
            self._start_blocks_length = start_blocks_length
            self._start_blocks_distance = start_blocks_distance
        else:
            self._start_blocks_length = []
            self._start_blocks_distance = []

        if end_blocks_length and end_blocks_distance:
            if len(end_blocks_length) != len(end_blocks_distance):
                raise ValueError('Incosistent end blocks arguments.')
            self._end_blocks_length = end_blocks_length
            self._end_blocks_distance = end_blocks_distance
        else:
            self._end_blocks_length = []
            self._end_blocks_distance = []

        self._hybrid = hybrid
        if self._hybrid:
            if pole_shape is None:
                pole_shape = block_shape
            if pole_length is None:
                raise ValueError('If hybrid, pole_length must be provided.')
            if pole_material is None:
                raise ValueError('If hybrid, pole_material must be provided.')

        self._pole_shape = pole_shape
        self._pole_length = pole_length
        self._pole_material = pole_material
        self._pole_subdivision = pole_subdivision

        self._block_subdivision = block_subdivision
        self._ksipar = ksipar
        self._ksiper = ksiper
        self.name = name

        # Attributes not directly given by __init__ arguments
        self._position_err = []
        self._blocks = []
        self._radia_object = None
        if init_radia_object:
            self.create_radia_object()
        
        # Also, there are the following @property methods which are not
        # directnly obtained from the __init__ arguments:
        # > nr_start_blocks
        # > nr_core_blocks
        # > nr_end_blocks
        # > nr_blocks
        # > cassette_length
        # > block_names
        # > magnetization_list
        # > longitudinal_position_list
        # Which are deinfed below.

    @property
    def block_shape(self):
        """Block list of shapes [mm]."""
        return _deepcopy(self._block_shape)

    @property
    def nr_period(self):
        """Number of complete periods."""
        return self._nr_periods

    @property
    def period_length(self):
        """Period length [mm]."""
        return self._period_length

    @property
    def mr(self):
        """Remanent magnetization [T]."""
        return self._mr

    @property
    def hybrid(self):
        """True for hybrid cassette, False otherwise."""
        return self._hybrid

    @property
    def pole_length(self):
        """Pole length [mm]."""
        return self._pole_length

    @property
    def pole_shape(self):
        """Pole list of shapes [mm]."""
        return _deepcopy(self._pole_shape)

    @property
    def pole_subdivision(self):
        """Pole shape subdivision."""
        return _deepcopy(self._pole_subdivision)

    @property
    def upper_cassette(self):
        """True for upper cassette, False otherwise."""
        return self._upper_cassette

    @property
    def longitudinal_distance(self):
        """Longitudinal distance between regular blocks [mm]."""
        return self._longitudinal_distance

    @property
    def block_subdivision(self):
        """Block shape subdivision."""
        return _deepcopy(self._block_subdivision)

    @property
    def rectangular(self):
        """True if the shape is rectangular, False otherwise."""
        return self._rectangular

    @property
    def ksipar(self):
        """Parallel magnetic susceptibility."""
        return self._ksipar

    @property
    def ksiper(self):
        """Perpendicular magnetic susceptibility."""
        return self._ksiper

    @property
    def start_blocks_length(self):
        """List of block lengths in the start of the cassette."""
        return _deepcopy(self._start_blocks_length)

    @property
    def start_blocks_distance(self):
        """List of distance between blocks in the start of the cassette."""
        return _deepcopy(self._start_blocks_distance)

    @property
    def end_blocks_length(self):
        """List of block lengths in the end of the cassette."""
        return _deepcopy(self._end_blocks_length)

    @property
    def end_blocks_distance(self):
        """List of distance between blocks in the end of the cassette."""
        return _deepcopy(self._end_blocks_distance)

    @property
    def blocks(self):
        """List of Block objects."""
        return self._blocks

    @property
    def position_err(self):
        """Position errors [mm]."""
        return _deepcopy(self._position_err)

    @property
    def nr_start_blocks(self):
        """Number of blocks in the start of the cassette."""
        return len(self._start_blocks_length)

    @property
    def nr_core_blocks(self):
        """Number of blocks in the core the cassette."""
        return 4*self._nr_periods

    @property
    def nr_end_blocks(self):
        """Number of blocks in the end of the cassette."""
        return len(self._end_blocks_length)

    @property
    def nr_blocks(self):
        """Total number of blocks in the cassette."""
        nr_blocks = (
            self.nr_start_blocks + self.nr_core_blocks + self.nr_end_blocks)
        return nr_blocks

    @property
    def cassette_length(self):
        """Cassette length."""
        start_len = sum(self.start_blocks_distance) + sum(
            self.start_blocks_length)
        end_len = sum(self.end_blocks_distance) + sum(
            self.end_blocks_length)
        return start_len + self.nr_periods*self.period_length + end_len

    @property
    def block_names(self):
        """List of block names."""
        name_list = [block.name for block in self._blocks]
        return name_list

    @property
    def magnetization_list(self):
        """List of magnetization vectors [T]."""
        mag_list = [block.magnetization for block in self._blocks]
        return mag_list

    @property
    def longitudinal_position_list(self):
        """List of initial longitudinal position of blocks [mm]."""
        pos_list = [block.longitudinal_position for block in self._blocks]
        return pos_list

    @property
    def state(self):
        """Dictionary representing cassette properties"""
        data = {
            'block_shape': self.block_shape,
            'nr_periods': self.nr_periods,
            'period_length': self.period_length,
            'mr': self.mr,
            'upper_cassette': self.upper_cassette,
            'longitudinal_distance': self.longitudinal_distance,
            'block_subdivision': self.block_subdivision,
            'rectangular': self.rectangular,
            'ksipar': self.ksipar,
            'ksiper': self.ksiper,
            'start_blocks_length': self.start_blocks_length,
            'start_blocks_distance': self.start_blocks_distance,
            'end_blocks_length': self.end_blocks_length,
            'end_blocks_distance': self.end_blocks_distance,
            'hybrid': self.hybrid,
            'pole_shape': self.pole_shape,
            'pole_length': self.pole_length,
            'pole_subdivision': self.pole_subdivision,
            'name': self.name,
            'block_names': list(self.block_names),
            'magnetization_list': list(self.magnetization_list),
            'position_err': list(self._position_err),
        }
        return data

    @classmethod
    def load_state(cls, filename):
        """Load state dictionary from .json file.

        Args:
            filename (str): Path to file.

        Returns:
            Cassette: New object created with attribute
                values read from input file.

        Note: State .json file stores lists of magnetizations, position errors
        and block names (magnetization_list, position_err and block_names).
        These parameters are not arguments of the Cassette initialization
        but are passed to the Radia object through an init_radia_object call
        executed by load_state before returning the Cassette object.
        """
        with open(filename) as f:
            kwargs = _json.load(f)

        block_names = kwargs.pop('block_names', None)
        magnetization_list = kwargs.pop('magnetization_list', None)
        position_err = kwargs.pop('position_err', None)

        cassette = cls(init_radia_object=False, **kwargs)
        cassette.create_radia_object(
            magnetization_list=magnetization_list,
            position_err=position_err, block_names=block_names)

        return cassette

    def create_radia_object(
            self,
            block_names=None,
            magnetization_list=None,
            position_err=None):
        """Creates new radia object and stores its index in _radia_object.

        If a Radia object bound to the Cassette object already exists, it is
            deleted before a new one is created.
        
        For creating the cassette blocks.Block objects, core block length is
        also determined at this method using:
            > longitudinal distances (gap between core blocks or poles)
            > Period length
            > Pole length, if hybrid.       
            so that 4 core blocks (or 2 poles and 2 core blocks, if hybrid)
            lead to a period of length equal to the period_length attribute. 

        Args:        
            block_names (list, nr_blocks, optional): List of names for the
                blocks.Block objects forming the cassette. List length must
                match the total number of blocks and poles (nr_blocks).
                If None, names will be empty strings. Defaults to None.
            magnetization_list (list, nr_blocks x 3, optional): List of
                magnetization directions for the blocks in the cassette.
                Directions on this list will be used only for permanent
                magnet blocks.
                If hybrid==True, poles will be the associated with a vector
                in magnetization_list mostly in the transversal direction
                (m=(mx,my,mz); |my|>|mz|). Poles are, nevertheless, created
                with [0,0,0] initial magnetization.
                Examples:
                    > For a cassette with 1 start block, 1 end block, 2 periods
                        and hybrid==True, for a magnetization_list:
                            [y+, z-, y-, z+, y+, z-, y-, z+, y+, z-]
                        The cassette objects will be initialized with:
                            [00, z-, 00, z+, 00, z-, 00, z+, 00, z-]
                                |  1st period  ||  2nd Period  |
                    > For a cassette with no start or end blocks, 3 periods and
                        hybrid==True, for a magnetization_list:
                            [z-, y-, z+, y+, z-, y-, z+, y+, z-, y-, z+, y+]
                        The cassette objects will be initialized with:
                            [z-, 00, z+, 00, z-, 00, z+, 00, z-, 00, z+, 00]
                            |  1st period  ||  2nd Period  ||  3rd Period  |
                    Where 00 = [0,0,0].
                If None, magnetization list will be calculated by the
                get_ideal_magnetization_list method (Halbach array).                
                Defaults to None.
            position_err (list, nr_blocks x 3, optional): List of translations
                additionally applied to blocks.Block objects for simulating
                position errors. Contains one 3D translation vector for each
                of the nr_blocks (blocks and poles) forming the cassette.
                In mm. Defaults to None, meaning no position errors.
        Raises:
            ValueError: If number of block names in block_names is different
                from the total number of blocks.
            ValueError: If number of translations in position_er is different
                from the total number of blocks.
        """
        if self._radia_object is not None:
            _rad.UtiDel(self._radia_object)

        if block_names is None:
            block_names = ['']*self.nr_blocks
        if len(block_names) != self.nr_blocks:
            raise ValueError(
                'Invalid length for block name list.')

        if position_err is None:
            position_err = [[0, 0, 0]]*self.nr_blocks
        if len(position_err) != self.nr_blocks:
            raise ValueError(
                'Invalid length for position errors list.')
        self._position_err = position_err

        # Core block length determination
        if self.hybrid:
            block_length = (
                self._period_length/2 - self._pole_length -
                2*self._longitudinal_distance)
        else:
            block_length = self._period_length/4 - self._longitudinal_distance

        if magnetization_list is None:
            magnetization_list = self.get_ideal_magnetization_list()

        if self.hybrid:
            mag0 = magnetization_list[0]
            # Check if first block has (mx,my,mz) with |my|>|mz|
            # to determine wether it is a core block or pole.
            if _np.abs(mag0[1]) > _np.abs(mag0[2]):
                length_list = _utils.flatten([
                    self._start_blocks_length,
                    [self._pole_length, block_length]*int(
                        self.nr_core_blocks/2),
                    self._end_blocks_length])
            else:
                length_list = _utils.flatten([
                    self._start_blocks_length,
                    [block_length, self._pole_length]*int(
                        self.nr_core_blocks/2),
                    self._end_blocks_length])
        else:
            length_list = _utils.flatten([
                self._start_blocks_length,
                [block_length]*self.nr_core_blocks,
                self._end_blocks_length])

        # For the nr_core_blocks core blocks, a list of nr_core_blocks-1
        # longitudinal distances is used, so that such list represents only
        # gaps between core blocks or core blocks and poles.
        # This way, start_blocks_distance represents distances AFTER start
        # blocks and end_blocks_distance represets distances BEFORE end blocks.
        # Example:
        # > 1 period of 20 mm and longitudinal distance of 1 mm.
        # > three start blocks of lengths [1,2,3] and distances [1,2,3]
        # > three end blocks of lengths [3,2,1] and distance [3,2,1]
        # will lead to:
        # Lengths:  | 1 | 2 | 3 | 4 | 4 | 4 | 4 | 3 | 2 | 1 |   (10 blocks)
        # Distances:    1,  2,  3,  1,  1,  1,  3,  2,  1       (9 distances)
        # * notice that "1 period" in this example is given by 4 blocks of
        #   4 mm and 4 gaps of 1 mm (= 20 mm), which does not fully appear in
        #   in the case of 1 period above (it lacks a 1 mm gap).
        #   For 20 periods, 19 full periods would be formed by the core blocks
        #   and the last period would, again, lack 1 well-defined gap.
        distance_list = _utils.flatten([
            self._start_blocks_distance,
            [self._longitudinal_distance]*(self.nr_core_blocks-1),
            self._end_blocks_distance])

        # Positions initialy start at 0 and are defined by adding the
        # longitudinal distances (gaps) and half lengths of their two adjacent
        # blocks or poles. Blocks/poles centers are then shifted so that they
        # are centered around the lontitudinal z=0.
        # For the example above, the positions are:
        # [-21, -18.5, -14, -7.5, -2.5, 2.5, 7.5, 14, 18.5, 21] 
        position_list = [0]
        for i in range(1, self.nr_blocks):
            position_list.append((
                length_list[i] + length_list[i-1])/2 + distance_list[i-1])
        position_list = _np.cumsum(position_list)
        position_list -= (position_list[0] + position_list[-1])/2

        self._blocks = []
        count = 0
        for length, position, magnetization in zip(
                length_list, position_list, magnetization_list):
            if self.hybrid and not count % 2:
                block = _blocks.Block(
                    self._pole_shape, length, position, [0, 0, 0],
                    subdivision=self._pole_subdivision,
                    rectangular=self._rectangular,
                    material=self._pole_material)
            else:
                block = _blocks.Block(
                    self._block_shape, length, position, magnetization,
                    subdivision=self._block_subdivision,
                    rectangular=self._rectangular,
                    ksipar=self._ksipar, ksiper=self._ksiper)
            self._blocks.append(block)
            count += 1

        for idx, block in enumerate(self._blocks):
            block.shift(position_err[idx])

        for name, block in zip(block_names, self._blocks):
            block.name = name

        # _blocks attribute becomes a single radia container object,
        # whose index is the one stored in _radia_object.
        rad_obj_list = []
        for block in self._blocks:
            if block.radia_object is not None:
                rad_obj_list.append(block.radia_object)
        self._radia_object = _rad.ObjCnt(rad_obj_list)

    def get_ideal_magnetization_list(self):
        """List of magnetization vector without amplitude and
        angular errors.

        Strength/modulus of returned matnetizations is given by mr.

        Magnetization directions are based on a Halbach indexed as follows:

        0   1   2   3   0   1   2   3   0   1  ...
        y+  z-  y-  z+  y+  z-  y-  z+  y+  z-  ...
        (^) (<) (v) (>) (^) (<) (v) (>) (^) (<) ...  

        In which:
            0: is the (0,  1,  0) direction; "transversal-horizontal up"
            1: is the (0,  0, -1) direction; "longitudinal backward"
            2: is the (0  -1,  0) direction; "transversal-horizontal down"
            3: is the (0,  0,  1) direction; "longitudinal foward"
        
        The final magnetization directions are defined in such a way that:
            if upper_cassette==False, the first CORE block always has
                magnetization in direction 0; (0,+1,0) 
            if upper_cassette==True, the first CORE block always has
                magnetization in direction 2; (0,-1,0)
            
        Example:
            * upper_cassette==True
            * 3 start blocks
            * 2 periods (8 core blocks)
            * 2 end blocks
            Magnetization directions will be:
            |start      |core                           |end
            |3   0   1  |2   3   0   1   2   3   0   1  |2   3

        Returns:
            list Nx3: Ideal Halbach magnetization 3-vectors of the N=nr_blocks
            blocks which form the cassette.
        """
        if self._upper_cassette:
            first_core_block = 2
        else:
            first_core_block = 0

        direction_list = [[0, 1, 0], [0, 0, -1], [0, -1, 0], [0, 0, 1]]

        # Magnetization of first block (CORE OR START):
        #   Base Halbach array is indexed by numbers modulo 4.
        #   nr_start subtracted for ensuring first core block magnetization.
        #   First core block magnetization shifted by 2 if upper_cassette.
        first_block = (4 + first_core_block - self.nr_start_blocks) % 4

        # Base directions (needs to be longer than final list)
        magnetization_list = direction_list*int(
            _np.ceil(self.nr_blocks/len(direction_list))+1)
        # Directions obtained by trimming base list
        magnetization_list = magnetization_list[
            first_block:self.nr_blocks+first_block]
        # Multiplying by mr to obtain final magnetizations list
        magnetization_list = self.mr*_np.array(magnetization_list)

        return magnetization_list.tolist()

    def get_random_errors_magnetization_list(
            self, max_amplitude_error=0, max_angular_error=0,
            termination_errors=True, core_errors=True):
        """List of magnetization vector with random amplitude
        and angular errors.

        The method applies amplitude errors (random scalings on magnetization
        modulus) and rotation errors (of random angles around random axis)
        to the get_ideal_magnetization_list() output and returns the result.

        Args:
            max_amplitude_error (float, optional): Maximum relative error for
                magnetization modulus.
                Example:
                    max_amplitude_error=0.02 represents 2% maximum modulus
                    error, meaning magnetization modulus beteen 98% and 102% of
                    the ideal value returned by get_ideal_magnetization_list().
                Defaults to 0.                 
            max_angular_error (float, optional): Maximum angular error, which
                is the angle by wich the magnetization vector will be rotated
                around a random axis. In radians. Defaults to 0.
            termination_errors (bool, optional): If True, errors are applied
                to termination (start and end) blocks. If False, ideal vectors
                will be used. Defaults to True.
            core_errors (bool, optional):  If True, errors are applied to core
                blocks. If False, ideal vectors will be used. Defaults to True.

        Returns:
            list Nx3: Magnetization 3-vectors of the N=nr_blocks blocks.Block
                objects forming the cassette with random amplitude and rotation 
                errors in relation to an ideal Halbach arrangement.
        """
        magnetization_list = self.get_ideal_magnetization_list()

        nr_start = self.nr_start_blocks
        nr_blocks = self.nr_blocks
        nr_end = self.nr_end_blocks

        magnetization_list_with_errors = []
        for idx, magnetization in enumerate(magnetization_list):
            is_termination = idx < nr_start or idx >= nr_blocks - nr_end
            if is_termination and not termination_errors:
                magnetization_list_with_errors.append(magnetization)
            elif not is_termination and not core_errors:
                magnetization_list_with_errors.append(magnetization)
            else:
                f = 1 + _np.random.uniform(-1, 1)*max_amplitude_error
                rot_angle = _np.random.uniform(-1, 1)*max_angular_error
                rot_axis = _utils.random_direction()
                rot_matrix = _utils.rotation_matrix(rot_axis, rot_angle)
                magnetization_list_with_errors.append(list(
                    _np.dot(rot_matrix, f*_np.array(magnetization))))

        return magnetization_list_with_errors

    def get_random_errors_position(
            self, max_horizontal_error=0,
            max_vertical_error=0, max_longitudinal_error=0,
            termination_errors=True, core_errors=True):
        """List of random translation vectors.

            The resulting random translations should be added to the cassette
            positions if one is to model position error in the cassette.
            This addition is automatically performed by the create_radia_object
            method, which recieves a position errors list as keyword argument.

        Args:
            max_horizontal_error (float, optional): Amplitude of random
                errors in the (x) horizontal direction. Defaults to 0.
            max_vertical_error (float, optional): Amplitude of random
                errors in the (y) vertical direction. Defaults to 0.
            max_longitudinal_error (float, optional): Amplitude of random
                errors in the (z) longitudinal direction. Defaults to 0.
            termination_errors (bool, optional): If true, errors are non-zero
                for termination (start and end) blocks. If False, [0,0,0]
                translation errors are used for such blocks. Defaults to True.
            core_errors (bool, optional): If true, errors are non-zero for core
                blocks. If False, [0,0,0] errors are used. Defaults to True.

        Returns:
            list Nx3: Translation 3-vectors for the N=nr_blocks blocks.Block
                objects forming the cassette.
        """
        position_err = []

        nr_start = self.nr_start_blocks
        nr_blocks = self.nr_blocks
        nr_end = self.nr_end_blocks

        for idx in range(nr_blocks):
            is_termination = idx < nr_start or idx >= nr_blocks - nr_end
            if is_termination and not termination_errors:
                position_err.append([0, 0, 0])
            elif not is_termination and not core_errors:
                position_err.append([0, 0, 0])
            else:
                herr = _np.random.uniform(-1, 1)*max_horizontal_error
                verr = _np.random.uniform(-1, 1)*max_vertical_error
                lerr = _np.random.uniform(-1, 1)*max_longitudinal_error
                position_err.append([herr, verr, lerr])

        return position_err
