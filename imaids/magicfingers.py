
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import blocks as _blocks
from . import fieldsource as _fieldsource

class MagicFingers(_fieldsource.FieldModel):
    
    def __init__(
            self, nr_blocks_group, block_shape, block_length, block_distance,
            nr_groups, group_distance, magnetization_init_list,
            block_shift_list=None, group_shift_list=None,
            group_rotation=90, device_rotation=0,
            block_subdivision=None, rectangular=False, ksipar=0.06,
            ksiper=0.17, init_radia_object=True, name='', block_names=None):

        if nr_blocks_group < 1:
            raise ValueError('nr_blocks must be >= 1.')
        if block_length < 0:
            raise ValueError('block_length must be >= 0.')
        if block_distance < 0:
            raise ValueError('block_distance must be >= 0.')    
        if nr_groups < 1:
            raise ValueError('nr_groups must be >= 1.')        
        if group_distance < 0:
            raise ValueError('group_distance must be >= 0.')

        if len(magnetization_init_list) != nr_blocks_group*nr_groups:
            raise ValueError(
                'Invalid length for magnetization initialization list.')

        if block_shift_list is None:
            block_shift_list = [0]*nr_blocks_group*nr_groups
        elif len(block_shift_list) != nr_blocks_group*nr_groups:
            raise ValueError('Invalid length for list of block shifts.') 
        
        if group_shift_list is None:
            group_shift_list = [0]*nr_groups
        elif len(group_shift_list) != nr_groups:
            raise ValueError('Invalid length for list of group shifts.')

        if device_rotation >= 2*_np.pi/nr_groups:
            raise ValueError('device_rotation must be < 2pi/nr_groups.')

        if block_names is None:
            block_names = ['']*nr_blocks_group*nr_groups
        elif len(block_names) != nr_blocks_group*nr_groups:
            raise ValueError('Invalid length for block name list.') 

        self._nr_blocks_group = int(nr_blocks_group)
        self._block_shape = block_shape
        self._block_length = float(block_length)
        self._block_distance = float(block_distance)
        self._nr_groups = int(nr_groups)        
        self._group_distance = float(group_distance)
        self._magnetization_init_list = magnetization_init_list
        self._block_shift_list = block_shift_list
        self._group_shift_list = group_shift_list
        self._group_rotation = float(group_rotation)
        self._device_rotation = float(device_rotation)   
        self._block_subdivision = block_subdivision
        self._rectangular = rectangular        
        self._ksipar = ksipar
        self._ksiper = ksiper
        self.name = name # "public"/mutable, no need for @property method
        self._block_names = block_names
        
        # More "private" attributes, not directly given by __init__ arguments
        self._blocks = []
        self._radia_object = None

        # Also, there are the following @property methods which are not
        # directnly obtained from the __init__ arguments:
        # > nr_blocks
        # > group_length
        # > block_names
        # > magnetization_list
        # Which are deinfed below.

        # Only call at __init__ is done for creating Radia object.
        if init_radia_object:
            self.create_radia_object()
        
    @property
    def nr_blocks_group(self):
        """Number of blocks in one group."""
        return self._nr_blocks_group

    @property
    def block_shape(self):
        """Block list of shapes [mm]."""
        return (self._block_shape)

    @property
    def block_length(self):
        """Pole length [mm]."""
        return self._block_length

    @property
    def block_distance(self):
        """Distance between blocks inside a group [mm]."""
        return self._block_distance

    @property
    def nr_groups(self):
        """Number of groups of blocks."""
        return self._nr_groups

    @property
    def group_distance(self):
        """Distance of groups to coordinates center (x=y=0)"""
        return self._group_distance

    @property
    def magnetization_init_list(self):
        """Magnetization initialization list"""
        return self._magnetization_init_list
    
    @property
    def block_shift_list(self):
        """Vector shifts (x,y,z) applied to blocks"""
        return self._block_shift_list
    
    @property
    def group_shift_list(self):
        """Longitudinal scalar shifts (z) applied to groups"""
        return self._group_shift_list
    
    @group_shift_list.setter
    def group_shift_list(self, new_group_shift_list):
        """Set longitudinal shifts (z) of groups and updates Radia objects"""

        # Test input.
        if len(new_group_shift_list) != self.nr_groups:
            raise ValueError('Invalid length for list of group shifts.')
        
        # Define necessary movement for updating group positions.
        delta_group_shift_list = _np.array(new_group_shift_list) - \
                            _np.array(self.group_shift_list)      

        # Update group positions.
        for idx_block, block in enumerate(self._blocks):
            # Get group index.
            idx_group = int(idx_block/self.nr_blocks_group)
            # Move blocks to appropriate new group positions.
            block.shift([0, 0, delta_group_shift_list[idx_group]])
        
        # Update group shift attribute
        self._group_shift_list = new_group_shift_list

    @property
    def group_rotation(self):
        """Group rotation around Y axis [degrees]"""
        return self._group_rotation
    
    @property
    def device_rotation(self):
        """Device rotation around Z axis [degrees]"""
        return self._device_rotation

    @property
    def block_subdivision(self):
        """Block shape subdivision."""
        return self._block_subdivision

    @property
    def rectangular(self):
        """True if the shape is rectangular, False otherwise."""
        return self._rectangular

    @property
    def ksipar(self):
        """Parallel magnetic susceptibility."""
        return self._ksipar

    @property
    def ksiper (self):
        """Perpendicular magnetic susceptibility."""
        return self._ksiper

    @property
    def block_names(self):
        """List of Block names."""
        return self._block_names

    @property
    def blocks(self):
        """List of Block objects."""
        return self._blocks

    @property
    def nr_blocks_total(self):
        """Total number of blocks."""
        return self.nr_blocks_group*self.nr_groups

    @property
    def group_length(self):
        """Length of a blocks group [mm]."""
        block_len = self.block_length*self.nr_blocks_group
        distance_len = self.block_distance*(self.nr_blocks_group-1)
        return block_len + distance_len

    @property
    def magnetization_list(self):
        """List of magnetization vectors READ FROM RADIA OBJECTS [T].
            
        This getter returns the current magnetizations of the blocks,
        regardless if they are set in intialization, read from file or altered
        by the solved magnetostaci problem.
        """
        mag_list = [block.magnetization for block in self._blocks]
        return mag_list
    
    @property
    def center_point_list(self):
        """List of block positions READ FROM RADIA OBJECTS [T].
            
        This getter returns the current position of the blocks, which is the
        final combination of translations and rotations used for getting
        the magic fingers device.
        """
        center_list = [block.center_point() for block in self._blocks]
        return center_list

    @property
    def state(self):
        """Dictionary representing magic fingers properties"""
        data = {
            'nr_blocks_group': self.nr_blocks_group,
            'block_shape': self.block_shape,
            'block_length': self.block_length,
            'block_distance': self.block_distance,
            'nr_groups': self.nr_groups,
            'group_distance': self.group_distance,
            'block_shift_list':self.block_shift_list,
            'group_shift_list':self.group_shift_list,
            'group_rotation': self.group_rotation,
            'device_rotation': self.device_rotation,
            'block_subdivision': self.block_subdivision,
            'rectangular': self.rectangular,
            'ksipar': self.ksipar,
            'ksiper': self.ksiper,
            'name': self.name,
            'block_names': list(self.block_names),
            'magnetization_list': list(self.magnetization_list),
        }
        return data

    @classmethod
    def load_state(cls, filename):
        """Load state dictionary from .json file.

        Args:
            filename (str): Path to file.

        Returns:
            MagicFingers: New object created with attribute
                values read from input file.

        Note: State .json file stores lists of magnetizations and block names,
        (magnetization_list, and block_names). These are not arguments of the
        MagicFingers initialization, but are passed to the Radia object through
        an init_radia_object call executed by load_state before returning the
        MagicFingers object.
        """
        with open(filename) as f:
            kwargs = _json.load(f)

        magnetization_list = kwargs.pop('magnetization_list', None)

        magicfingers = cls(init_radia_object=False, **kwargs)
        magicfingers.create_radia_object(
            magnetization_list=magnetization_list)

        return magicfingers
   
    def create_radia_object(self, magnetization_list=None):

        if self._radia_object is not None:
            _rad.UtiDel(self._radia_object)

        # Test magnetization list, giving default __init__ value if None.
        if magnetization_list is None:
            magnetization_list = self.magnetization_init_list
        elif len(magnetization_list) != self.nr_blocks_total:
            raise ValueError(
                'Invalid length for magnetization list.')

        position_list = []
        group_rotation_z_list = []

        for idx_group in range(self.nr_groups):
            for idx_block in range(self.nr_blocks_group):
                # Generate position, WITHOUT SHIFTS..
                position = idx_block*(self.block_length + self.block_distance)
                position_list.append(position)
                # Generate group rotation AROUND Z axis (for positioning
                # the magic fingers as the desired circualr array).
                group_rotation_z_list.append(2*_np.pi*idx_group/self.nr_groups)

        # Apply shift for centering positions list around z=0
        position_list = _np.array(position_list)
        position_list -= (position_list[0] + position_list[-1])/2

        self._blocks = []
        for idx_block, (position, magnetization,
                        group_rotation_z, block_shift) \
            in enumerate(zip(position_list, magnetization_list,
                             group_rotation_z_list, self.block_shift_list)):

            # Get group index (used later for shifting groups)
            idx_group = int(idx_block/self.nr_blocks_group)

            # Generate block with given magnetization and position
            # (position is already centered around z=0).
            block = _blocks.Block(
                self.block_shape, self.block_length, position, magnetization,
                subdivision=self.block_subdivision,
                rectangular=self.rectangular,
                ksipar=self.ksipar, ksiper=self.ksiper)

            # ------- START of block poisition manipulations ------- #

            # Ensure blocks upper y position is y=0 (for ensuring that
            # group distance correctly represents distance between device
            # center and block surface).
            block.shift([0, (-1)*block.bounding_box()[1,1], 0])

            # Apply block shifts (if given).
            if block_shift is not None:
                block.shift(block_shift)

            # Rotate block around y axis.
            block.rotate([0,0,0], [0,1,0], self.group_rotation)

            # Shift blocks by group distance (from device center to group).
            block.shift([0, (-1)*self.group_distance, 0])

            # Position group at its desired rotational position.
            block.rotate([0,0,0], [0,0,1], group_rotation_z)

            # Apply global device rotation around z axis.
            block.rotate([0,0,0], [0,0,1], self.device_rotation)

            # Apply group shifts (in z direction)
            block.shift([0,0,self.group_shift_list[idx_group]])

            # -------- END of block poisition manipulations -------- #

            self._blocks.append(block)

        # Applying names to the created blocks.
        for block_name, block in zip(self._block_names, self._blocks):
            block.name = block_name

        # _blocks attribute becomes a single radia container object,
        # whose index is the one stored in _radia_object.
        rad_obj_list = []
        for block in self._blocks:
            if block.radia_object is not None:
                rad_obj_list.append(block.radia_object)
        self._radia_object = _rad.ObjCnt(rad_obj_list)
