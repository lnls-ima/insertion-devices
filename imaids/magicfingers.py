
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import blocks as _blocks
from . import fieldsource as _fieldsource

class MagicFingers(_fieldsource.FieldModel):
    """Defines a devices formed by groups of magnetic blocks layed over
        in a circular array around the z=0 axis. 

    Such arrangement represents devices (magic fingers/magic pads) usually
    coupled with insertion devices for magnetic tuning.

    Block shape and positions positions are defined by:
        block_shape
        block_length
        block_distance
        nr_blocks_group
        block_shift_list
        group_rotation
        group_distance           
        nr_groups
        device_rotation
        group_shift_list
        device_position
    
    nr_groups will be arranged in a counterclockwise arangement and
    (if group_rotation is in [0, +pi)) in each group the blocks
    order follows the counterclockwise ordering.

    | The /docs/magic_fingers_parameters.pdf file in the documentation     |
    | directory of the package illustrates the meaning of such parameters, |
    | which are alsodescribed at the initialization method bellow.               |

    """
    
    def __init__(
            self, nr_blocks_group, block_shape, block_length, block_distance,
            group_distance, nr_groups, magnetization_init_list,
            ksipar=0.06, ksiper=0.17, group_rotation=_np.pi/2,
            block_shift_list=None, group_shift_list=None,
            device_rotation=0, device_position = 0,
            block_subdivision=None, rectangular=False, 
            init_radia_object=True, name='', block_names=None):        
        """Pass and store attributes which define geometry and distribution
        of the blocks in the device and call radia object creation method.

        Args:
            nr_blocks_group (int): Number of blocks forming a group of blocks.
                A number of such groups will be distributed radially around
                the z=0 ([0,0,1]) axis forming the device.
            block_shape (list, Mx2 or NxMx2): List defining blocks geometry.
                Single list or N nested lists of M 2D points defining convex
                polygons which form the cross-section of a block (as
                described in blocks.Block). Same block_shape for all blocks.
                2D points coordinates in mm.
            block_length (float): Block longitudinal length, perpendicular to
                cross-section defined by block_shape. in mm.
            block_distance (float): Longitudinal distance between blocks in
                each group (in the direction perpendicular to cross-section
                defined by block_shape). The same for all groups. In mm.
            group_distance (float): Radial distance between the upper/innermost
                face of the blocks forming a group and the device center at the
                z=0 axis (without block shifts, see bellow). In mm.            
            nr_groups (int): Number of block groups forming the device. The
                groups are distributed evenly across the 2pi angle around the
                z=0 axis. Each n-th group is rotated by n*2pi/nr_groups around
                the z=0 axis, after already being translated by group_distance
                in the y- direction ("downwards"/"outwards"), thus arriving
                at its desired radial and angular position.
            magnetization_init_list (list, nr_blocks_group*nr_groups x 3):
                Magnetizations list for the device blocks. Block materials will
                always be linear with (possibly) anisotropic permeability.
                Magnetization modulus (remanence) and the direction (easy axis
                for anisotropy) are both defined by the magnetization vector.
                One vector for each block, in Tesla.
            ksipar (float, optional): Blocks susceptibility parallel to
                easy axis (magnetization direction). Defaults to 0.06.
            ksiper (float, optional): Blocks susceptibility perpendicular to
                easy axis (magnetization direction). Defaults to 0.17.
            group_rotation (float, optional): Rotation around the y local axis
                applied to the groups. The local coordinate system of each
                each group is the one in which:
                > the z axis points to the direction parallel to the blocks
                  transversal cross section (defined by block_shape);
                > the y axis points inwards to the center of the device;
                > the x axis coincides with the local z (device rotation axis);
                Same rotation is applied to each group in its respective
                respective local y axis. In radians, defaults to pi/2.
            block_shift_list (list, nr_blocks_group*nr_groups x 3, optional):
                Shifts [x,y,z] applied individually to the blocks, in mm.
                The shifts are described in the local coordinate system of the
                groups (as described for the group_rotation argument above).
                In mm, defaults to None (meaning [0, 0, 0] shifts.
            group_shift_list (list, nr_blocks_group*nr_groups, optional):
                Longitudinal shifts in the global z direction applied to each
                group. It is the only device geometrical property that may be
                set (altered) after the device is created, allowing for group
                movements analogous to cassettes motion in an undulator.
                When a new group_shift_list is set, groups are moved for
                matching the new shifts, but the overall longitudinal device
                position set by device_position (see bellow) is kept.
                In mm, defaults to None (meaning 0.0 shifts).        
            device_rotation (float, optional): Overall device rotation around
                the global z ([0,0,1]) axis, applied to all the blocks after
                their position and rotation is set by all the arguments above.
                Must be less than 2*pi/nr_groups. In radians, defaults to 0.
            device_position (float, optional): Overall device shift in the
                global z direction, applied to all the blocks after their
                position and rotation is set by all the arguments above.
                May be used for longitudinally positioning the whole device.
                In mn, defaults to 0.
            block_subdivision (list, 3 or Nx3, optional): Defines the block
                subdivision for the Radia calculation. Single list of (x,y,z)
                subdivisions or nested list of N 3-vector (x,y,z) subdivisions,
                (as described in blocks.Blocks). Must have the same N length of
                block_shape list. Defaults to None, meaning no subdivision.
            rectangular (bool, optional): Used for initialization of blocks.
                If True the both are created as Radia ObjRecMag objects.
                If False both are created as Radia ObjThckPgn objects.
                Defaults to False.
            init_radia_object (bool, optional): If True, Radia object is
                created at object initialization. Defaults to True.
            name (str, optional): Device label. Defaults to ''.
            block_names (list, nr_blocks_group*nr_groups): Labels applied
                to the individual blocks. Defaults to None, meaning labels
                = '' to all blocks.    

        Raises:
            ValueError: If nr_blocks_group is < 1
            ValueError: If block_length is negative.
            ValueError: If block_distance is negative.
            ValueError: If group_distance is negative.
            ValueError: If nr_groups is < 1
            ValueError: If number of magnetizations it not equal to the number
                of blocks (nr_blocks_group x nr_groups).
            ValueError: If number of block shifts is not equal to the number
                of blocks (nr_blocks_group x nr_groups).
            ValueError: If number of group shifts is not equal to the number
                of groups (nr_groups).
            ValueError: If device_rotation is >= 2*pi/nr_groups.
            ValueError: If number of block names is not equal to the number
                of blocks (nr_blocks_group x nr_groups).
        """

        if nr_blocks_group < 1:
            raise ValueError('nr_blocks must be >= 1.')

        if block_length < 0:
            raise ValueError('block_length must be >= 0.')

        if block_distance < 0:
            raise ValueError('block_distance must be >= 0.')

        if group_distance < 0:
            raise ValueError('group_distance must be >= 0.')

        if nr_groups < 1:
            raise ValueError('nr_groups must be >= 1.')

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
        self._group_distance = float(group_distance)
        self._nr_groups = int(nr_groups)        
        self._magnetization_init_list = magnetization_init_list
        self._ksipar = ksipar
        self._ksiper = ksiper
        self._group_rotation = float(group_rotation)
        self._block_shift_list = block_shift_list
        self._group_shift_list = group_shift_list
        self._device_rotation = float(device_rotation)
        self._device_position = float(device_position)
        self._block_subdivision = block_subdivision
        self._rectangular = rectangular        
        self.name = name # "public"/mutable, no need for @property method
        self._block_names = block_names
        
        # More "private" attributes, not directly given by __init__ arguments
        self._blocks = []
        self._radia_object = None

        # Also, there are the following @property methods which are not
        # directly obtained from the __init__ arguments (defined bellow):
        # > nr_blocks
        # > group_length
        # > block_names
        # > magnetization_list

        # The only call at __init__ is the one for creating Radia object.
        if init_radia_object:
            self.create_radia_object()
        
    @property
    def nr_blocks_group(self):
        """Number of blocks in one group."""
        return self._nr_blocks_group

    @property
    def block_shape(self):
        """Block shape (list of convex shapes) [mm]."""
        return (self._block_shape)

    @property
    def block_length(self):
        """Length of blocks forming a group [mm]."""
        return self._block_length

    @property
    def block_distance(self):
        """Distance between blocks inside a group [mm]."""
        return self._block_distance

    @property
    def group_distance(self):
        """Distance between z axis and the groups (the block face closest
            to the z axis, without block shifts) [mm]."""
        return self._group_distance

    @property
    def nr_groups(self):
        """Number of groups of blocks."""
        return self._nr_groups

    @property
    def magnetization_init_list(self):
        """Magnetization initialization list [T]."""
        return self._magnetization_init_list

    @property
    def ksipar(self):
        """Parallel magnetic susceptibility."""
        return self._ksipar

    @property
    def ksiper (self):
        """Perpendicular magnetic susceptibility."""
        return self._ksiper

    @property
    def group_rotation(self):
        """Group rotation around Y axis (local group coordinates) [degrees]."""
        return self._group_rotation
   
    @property
    def block_shift_list(self):
        """Vector shifts applied to blocks (local group coordinates) [mm]."""
        return self._block_shift_list
    
    @property
    def group_shift_list(self):
        """Scalar Z shifts applied to groups (global coordinates) [mm]."""
        return self._group_shift_list

    @property
    def device_rotation(self):
        """Global rotation around Z axis (global coordinates) [degrees]."""
        return self._device_rotation

    @property
    def device_position(self):
        """Global shift in the Z direction (global coordinates) [mm]."""
        return self._device_position
    
    @group_shift_list.setter
    def group_shift_list(self, new_group_shift_list):
        """Set longitudinal shifts (z) of groups and updates Radia objects.

        Setting/modifying the group shifts without creating a new object is
        is useful for matching the motion of cassettes in an undulator. Since
        the shift update is applied as new a shift, the device longitudinal
        position set by self.device_position is kept.
        """

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
    def block_subdivision(self):
        """Block shape subdivision (list of convex shapes subdivisions)."""
        return self._block_subdivision

    @property
    def rectangular(self):
        """True if the shape is rectangular, False otherwise."""
        return self._rectangular

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
        """Length of a blocks group. [mm]"""
        block_len = self.block_length*self.nr_blocks_group
        distance_len = self.block_distance*(self.nr_blocks_group-1)
        return block_len + distance_len

    @property
    def magnetization_list(self):
        """List of magnetization vectors READ FROM RADIA OBJECTS [T].
            
        This getter returns the current monetizations of the blocks,
        regardless if they are set in initialization, read from file or
        altered by the solved magnetostatic problem.
        """
        mag_list = [block.magnetization for block in self._blocks]
        return mag_list
    
    @property
    def center_point_list(self):
        """List of block positions READ FROM RADIA OBJECTS [T].
            
        This getter returns the current positions of the blocks in global
        coordinates, which is the result of all the translations and rotations
        applied to the blocks for setting up the magic fingers device.
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
            'group_distance': self.group_distance,
            'nr_groups': self.nr_groups,
            'ksipar': self.ksipar,
            'ksiper': self.ksiper,
            'group_rotation': self.group_rotation,
            'block_shift_list':self.block_shift_list,
            'group_shift_list':self.group_shift_list,
            'device_rotation': self.device_rotation,
            'block_subdivision': self.block_subdivision,
            'rectangular': self.rectangular,
            'name': self.name,
            'block_names': list(self.block_names),
            'magnetization_list': list(self.magnetization_list),
        }
        return data

    @classmethod
    def load_state(cls, filename):
        """Load state dictionary from .json file and create magic fingers.

        Args:
            filename (str): Path to file.

        Returns:
            MagicFingers: New object created with attribute
                values read from input file.

        Note: State .json file stores lists of magnetizations that might be
        resulting magnetizations obtained after relaxation (magnetostatic
        problem solve()), which are returned by the magnetization_list getter
        and stored in the state dictionary. The magnetizations list read from
        file is passed as initialization magnetizations list to the new object.
        
        """
        with open(filename) as f:
            kwargs = _json.load(f)

        magnetization_list = kwargs.pop('magnetization_list', None)
        kwargs['magnetization_init_list'] = magnetization_list

        return cls(**kwargs)

    def get_block_table(self):
        """Table string summarizing block information.
        
        Returns:
            str: String formated as table. First line labels the columns
                > block index - idx
                > group index - grp
                > center positions (block.center_point()) - x,y,z
                > magnetization components (block.magnetization) - mx,my,mz              
        """
        fmthd = 2*'{:>5}' + 3*' {:>12}' + 3*' {:>11}'
        fmtrw = 2*'{:>5d}' + 3*' {:>12.5f}' + 3*' {:>11.5f}'

        table = fmthd.format('idx', 'grp', 'xc (mm)', 'yc (mm)', 'zc (mm)',
                                'mx (T)', 'my (T)', 'mz (T)')
        for idx_block, block in enumerate(self._blocks):

            idx_group = int(idx_block/self.nr_blocks_group)
            xc, yc, zc = block.center_point()
            mx, my, mz = block.magnetization

            table += '\n'
            table += fmtrw.format(idx_block, idx_group,
                                        xc, yc, zc, mx, my, mz)

        return table
   
    def create_radia_object(self, magnetization_list=None):
        """Creates radia object with given magnetization and blocks
        distributed according to the object attributes.
        
        Args:
            magnetization_init_list (list, nr_blocks_group*nr_groups x 3):
                Magnetizations list for the device blocks (see documentation
                for initialization methods for details). This might manual
                input magnetizations or magnetizations read from a file saved
                from previous calculation.

        Raises:
            ValueError: If number of magnetizations it not equal to the number
                of blocks (nr_blocks_group x nr_groups).
        """

        if self._radia_object is not None:
            _rad.UtiDel(self._radia_object)

        # Test magnetization list, giving default __init__ value if None.
        if magnetization_list is None:
            magnetization_list = self.magnetization_init_list
        elif len(magnetization_list) != self.nr_blocks_total:
            raise ValueError('Invalid length for magnetizations list.')

        position_list = []
        group_rotation_z_list = []

        for idx_group in range(self.nr_groups):
            for idx_block in range(self.nr_blocks_group):
                # Generate position, WITHOUT SHIFTS.
                position = idx_block*(self.block_length + self.block_distance)
                position_list.append(position)
                # Generate group rotation AROUND Z axis (for positioning
                # the magic fingers as the desired circular array).
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

            # --------- START of block positioning --------- #

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

            # Apply global device shift (in z direction)
            block.shift([0,0,self.device_position])

            # ---------- END of block positioning ---------- #

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

class MagicFingersSabia(MagicFingers):

    """Magic fingers for Delta Sabia Model"""
        
    def __init__(
            self, magnetization_init_list,
            nr_blocks_group=4, block_shape='default', block_length=1.25,
            block_distance=7, group_distance=30.65, nr_groups=4,            
            ksipar=0.06, ksiper=0.17, group_rotation=_np.pi/2,
            block_shift_list=None, group_shift_list=None,
            device_rotation=_np.pi/4, device_position=0,
            block_subdivision='default', rectangular=False, 
            init_radia_object=True, name='magic_fingers_sabia',
            block_names='default'):
        
        '''Initialization function with default arguments adjusted for
        Delta Sabia magic fingers.
        
        Group distance is based on a distance between center of block and
        device center of 43.15 mm, with the block half length as 12.5 mm.    
        
        See help for MagicFingers class for details on arguments meaning.

        Args:
            magnetization_init_list (list, nr_blocks_group*nr_groups x 3) In T.
            nr_blocks_group (int, optional): Defaults to 4.
            block_shape (list, Mx2 or NxMx2, optional): Defaults to 'default',
                in which case, Block.get_predefined_shape('delta_prototype')
                will be used.
            block_length (float, optional): In mm. Defaults to 1.25.
            block_distance (float, optional): In mm. Defaults to 7.0.
            group_distance (float, optional): In mm. Defaults to 30.65.
            nr_groups (int, optional): Defaults to 4.
            ksipar (float, optional): Defaults to 0.06.
            ksiper (float, optional): Defaults to 0.17.
            group_rotation (float, optional): In radians. Defaults to pi/2.
            block_shift_list (list, nr_blocks_group*nr_groups x 3, optional):
                In mm, defaults to None (meaning [0, 0, 0] shifts.
            group_shift_list (list, nr_blocks_group*nr_groups, optional):
                In mm, defaults to None (meaning 0.0 shifts).        
            device_rotation (float, optional): In radians, defaults to pi/4.
            device_position (float, optional): In mn, defaults to 0.
            block_subdivision (list, 3 or Nx3, optional): Defaults
                 to 'default', in which case
                 Block.get_predefined_subdivision('delta_prototype') will be
                 used.
            rectangular (bool, optional): Defaults to False.
            init_radia_object (bool, optional): defaults to True.
            name (str, optional): Device label. Defaults to 
                'magic_fingers_sabia'.
            block_names (list, nr_blocks_group*nr_groups): Defaults to
                'default', in which case a list af names:
                [Block_00, Block_01, ..., Block_15] will be used.
        '''        
        if block_shape == 'default':
            block_shape = \
                _blocks.Block.get_predefined_shape('delta_prototype')
        if block_subdivision == 'default':
            block_subdivision = \
                _blocks.Block.get_predefined_subdivision('delta_prototype')
        if block_names == 'default':
            block_names = ['Block_{:02d}'.format(i) for i in range(16)]
        
        super().__init__(
            nr_blocks_group=nr_blocks_group, block_shape=block_shape, 
            block_length=block_length, block_distance=block_distance,
            group_distance=group_distance, nr_groups=nr_groups, 
            magnetization_init_list=magnetization_init_list,
            ksipar=ksipar, ksiper=ksiper, group_rotation=group_rotation,
            block_shift_list=block_shift_list,
            group_shift_list=group_shift_list,
            device_rotation=device_rotation, device_position=device_position,
            block_subdivision=block_subdivision, rectangular=rectangular, 
            init_radia_object=init_radia_object, name=name,
            block_names=block_names)
