
from copy import deepcopy as _deepcopy
import json as _json
import numpy as _np
import radia as _rad

from . import utils as _utils
from . import materials as _materials
from . import fieldsource as _fieldsource


class Block(_fieldsource.FieldModel):
    """Magnetic material block."""

    PREDEFINED_SHAPES = {
        'delta_prototype': [
            [
                [-2.75, 0], [-11.2662, -8.9645], [-7.73071, -12.5],
                [7.73071, -12.5], [11.2662, -8.9645], [2.75, 0]],
            [
                [-7.73071, -12.5], [-11.2662, -16.0355], [-2.75, -25],
                [2.75, -25], [11.2662, -16.0355], [7.73071, -12.5]]],
        'delta_sabia': [
            [
                [-5.25, 0], [-22.5, -19.3], [-22.5, -29.2], [-17.8, -33.2],
                [17.8, -33.2], [22.5, -29.2], [22.5, -19.3], [5.25, 0]],
            [
                [-17.8, -33.2], [-17.8, -38.4], [17.8, -38.4], [17.8, -33.2]],
            [
                [-17.8, -38.4], [-22.5, -42.4], [-22.5, -49], [-21.5, -50],
                [21.5, -50], [22.5, -49], [22.5, -42.4], [17.8, -38.4]]],
        'apple_delta_sabia_flip': [
            [
                [17.25,-50.0],[0.0,-30.7],[0.0,-20.8],[4.7,-16.8],[40.3,-16.8],
                [45.0,-20.8],[45.0,-30.7],[27.75,-50.0]],
            [
                [4.7,-16.8],[4.7,-11.6],[40.3,-11.6],[40.3,-16.8]],
            [
                [4.7,-11.6],[0.0,-7.6],[0.0,-1.0],[1.0,0.0],[44.0,0.0],
                [45.0,-1.0],[45.0,-7.6],[40.3,-11.6]]],
        'delta_carnauba': [
            [
                [-2.55, 0.0], [-11.25, -9.65], [-11.25, -14.6],
                [-8.9, -16.6], [8.9, -16.6], [11.25, -14.6],
                [11.25, -9.65], [2.55, 0.0]],
            [
                [-8.9, -16.6], [-8.9, -19.2], [8.9, -19.2], [8.9, -16.6]],
            [
                [-8.9, -19.2], [-11.25, -21.2], [-11.25, -24.5],
                [-10.75, -25.0], [10.75, -25.0], [11.25, -24.5],
                [11.25, -21.2], [8.9, -19.2]]],
        'apple_sabia': [
            [
                [0.1, 0], [50, 0], [50, -50], [0.1, -50]]],
        'apple_carnauba': [
            [
                [0.1, 0], [25, 0], [25, -25], [0.1, -25]]],
        'apple_uvx': [
            [
                [0.1, 0], [40, 0], [40, -40], [0.1, -40]]],
        'kyma_22': [
            [
                [15, 0], [18, -3], [18, -17], [15, -20],
                [-15, -20], [-18, -17], [-18, -3], [-15, 0]]],
        'kyma_58': [
            [
                [23.5, 0], [28.5, -5], [28.5, -29], [23.5, -39],
                [-23.5, -39], [-28.5, -29], [-28.5, -5], [-23.5, 0]]],
        'hybrid_block': [
            [
                [30, 0], [30, -40], [-30, -40], [-30, 0]]],
        'hybrid_pole': [
            [
                [20, 0], [20, -40], [-20, -40], [-20, 0]]],
        }

    PREDEFINED_SUBDIVISION = {
        'delta_prototype': [[3, 3, 2], [3, 3, 2]],
        'delta_sabia': [[3, 3, 2], [1, 1, 2], [1, 1, 2]],
        'apple_delta_sabia_flip': [[3, 3, 2], [1, 1, 2], [1, 1, 2]],
        'delta_carnauba': [[3, 3, 2], [1, 1, 1], [1, 1, 1]],
        'apple_sabia': [[3, 3, 3]],
        'apple_carnauba': [[3, 3, 3]],
        'kyma_22': [[6, 3, 3]],
        'kyma_58': [[6, 3, 3]],
        'hybrid_block': [[3, 3, 3]],
        'hybrid_pole': [[6, 6, 3]],
    }

    def __init__(
            self, shape, length, longitudinal_position,
            magnetization=[0, 1.37, 0], subdivision=None, rectangular=False,
            name='', material=None, **kwargs):
        """Create the radia object for a block with magnetization. 

        Args:
            shape (list, Mx2 or NxMx2): nested list specifying cross sections
                of N subblocks in (x,y) as N lists of M points. Each M points
                list should define vertex points of a convex polyhedron. In mm.
                The N lists of points represent subblocks which will be grouped
                in a single container Radia object. Subblocks are useful for
                specifying a non-convex block as composed by convex subblocks.
                This argument also defines the block position in the x,y plane. 
                For N=1 (no subblocks), a Mx2 list of points may be provided.
            length (float): block longitudinal (z) length in mm. Must be a
                positive number. If the length is 0, the radia object will 
                not be created.
            longitudinal_position (float): longitudinal (z) position of the
                block center in mm. Transversal (xy) position is defined by
                the points position in the shape attribute.
            magnetization (list, optional): list of three real numbers
                specifying the magnetization vector of the block in Tesla.
                If material argument is also provided, this vector determines
                only the magnetization direction (and easy axis for anisotropic
                material), while the modulus is determined by the material.
                If material=None, the default material is linear and uses this
                argument for determining the magnetization modulus as well.
                Can be set to [0, 0, 0]. Defaults to [0, 1.37, 0].
            subdivision (list, 3 or Nx3, optional): nested list specifying 
                the number of subdivisions of each subblock in the cartesian
                directions [x, y, z].
                For N=1 (no subblocks), a len=3 [x, y, z] list may be provided.
                Defaults to None (no subdivision).
            rectangular (bool, optional): If True the block is created using 
                the radia function ObjRecMag. If False the block is create 
                using the radia function ObjThckPgn. Either way, cross-section
                and thickness of the block must be specifyed by the shape
                and length attributes. Defaults to False.
            name (str, optional): Block label. Defaults to ''.
            material (Material, optional): Material object to apply to block.
                Defaults to None, in which case a default material is used.
                Default material is created with default arguments (including
                linear=True) except for the magnetization modulus, which is
                defined as the modulus of the magnetization vector argument.
            **kwargs: if material==None additional keyword arguments are passed
                to the Material initialization, overriding default arguments.
                Default magnetization can not be overwridden, in this case
                the magnetization vector modulus should be adjusted instead.
                Note that if default material linearity is overridden, the
                modulus of the magnetization vector argument is ignored.

        Raises:
            ValueError: if the block length is a negative number.
            ValueError: if the length of the magnetization list is different
                from three.
            ValueError: if the lengths of block_sudivision and block_shape
                arguments (numbers of subblocks) are inconsistent.
        """
        if _utils.depth(shape) != 3:
            self._shape = [shape]
        else:
            self._shape = shape

        if length < 0:
            raise ValueError('The block length must be a positive number.')
        self._length = length

        if len(magnetization) != 3:
            raise ValueError('Invalid magnetization argument.')
        self._magnetization = magnetization

        if subdivision is None or len(subdivision) == 0:
            sub = [[1, 1, 1]]*len(self._shape)
        else:
            sub = subdivision

        if _utils.depth(sub) != 2:
            sub = [sub]

        if len(sub) != len(self._shape):
            raise ValueError(
                'Inconsistent length between block_sudivision ' +
                'and block_shape arguments.')
        self._subdivision = sub

        self._rectangular = rectangular

        self._longitudinal_position = longitudinal_position

        if material is None:
            self._material = _materials.Material(
                mr=_np.linalg.norm(self._magnetization), **kwargs)
        else:
            self._material = material

        self.name = name

        self._radia_object = None
        self.create_radia_object()

    @property
    def shape(self):
        """Block list of shapes [mm]."""
        return _deepcopy(self._shape)

    @property
    def length(self):
        """Block length [mm]."""
        return self._length

    @property
    def longitudinal_position(self):
        """Initial block longitudinal position [mm]."""
        return self._longitudinal_position

    @property
    def magnetization(self):
        """Block magnetization vector [T]."""
        return _deepcopy(self._magnetization)

    @property
    def subdivision(self):
        """Block list of shape subdivisions."""
        return _deepcopy(self._subdivision)

    @property
    def rectangular(self):
        """True if the shape is rectangular, False otherwise."""
        return self._rectangular

    @property
    def state(self):
        data = {
            'shape': self._shape,
            'length': self._length,
            'longitudinal_position': self._longitudinal_position,
            'magnetization': self._magnetization,
            'subdivision': self._subdivision,
            'rectangular': self._rectangular,
            'name': self.name,
        }
        data.update(self._material.state)
        return data

    @classmethod
    def get_predefined_shape(cls, device_name):
        """Get predefined block shape(s) for the device.

        Args:
            device_name (str): name of the device. See the options defined in
                the PREDEFINED_SHAPES class attribute.

        Returns:
            list: nested list specifying the block shape(s).
        """
        return cls.PREDEFINED_SHAPES.get(device_name)

    @classmethod
    def get_predefined_subdivision(cls, device_name):
        """Get predefined block subdivision(s) for the device.

        Args:
            device_name (str): name of the device. See the options defined in
                the PREDEFINED_SUBDIVISION class atribute.

        Returns:
            list: nested list specifying the block subdivision(s).
        """
        return cls.PREDEFINED_SUBDIVISION.get(device_name)

    def create_radia_object(self, magnetization=None):
        """Creates the radia object."""
        if self._radia_object is not None:
            _rad.UtiDel(self._radia_object)

        if self._length == 0:
            return

        self._magnetization = magnetization or self._magnetization

        # In both ObjRecMag and ObjThckPgn, 'Frame->Lab' is used so that
        # div determines the number of divisions in each cartesian direction.
        # The default option, ('Frame->Loc') would use a local reference
        # system in which the x direction is the extrusion direction.

        if self._rectangular:
            center = []
            width = []
            height = []
            for shp in self._shape:
                shp = _np.array(shp)
                min0 = _np.min(shp[:, 0])
                max0 = _np.max(shp[:, 0])
                min1 = _np.min(shp[:, 1])
                max1 = _np.max(shp[:, 1])
                center.append([(max0 + min0)/2, (max1 + min1)/2])
                width.append(max0 - min0)
                height.append(max1 - min1)

            subblock_list = []
            for ctr, wdt, hgt, div in zip(
                    center, width, height, self._subdivision):
                subblock = _rad.ObjRecMag(
                    [ctr[0], ctr[1], self._longitudinal_position],
                    [wdt, hgt, self._length], self._magnetization)
                subblock = _rad.MatApl(subblock, self._material.radia_object)
                subblock = _rad.ObjDivMag(subblock, div, 'Frame->Lab')
                subblock_list.append(subblock)
            self._radia_object = _rad.ObjCnt(subblock_list)

        else:
            subblock_list = []
            for shp, div in zip(self._shape, self._subdivision):
                subblock = _rad.ObjThckPgn(
                    self._longitudinal_position, self._length, shp, 'z',
                    self._magnetization)
                subblock = _rad.MatApl(subblock, self._material.radia_object)
                subblock = _rad.ObjDivMag(subblock, div, 'Frame->Lab')
                subblock_list.append(subblock)
            self._radia_object = _rad.ObjCnt(subblock_list)

    def bounding_box(self):
        """Bounding box of block geometrical limits.
        
        Raises:
            ValueError: If there is no radia object referenced by the Block.

        Returns:
            numpy.ndarray, 3x2: Array of the form:
                [[xmin, xmax], [ymin,ymax], [zmin,zmax]]
                where the min and max values are the coordinates' upper and
                lower bounds for the points forming the block geometry.
        """
        if self.radia_object is None:
            raise ValueError('There is no linked Radia object.')
        
        points = _np.concatenate(self.shape, axis=0)
        x = points[:,0]
        y = points[:,1]
        zmin = self.longitudinal_position - 0.5*self.length
        zmax = self.longitudinal_position + 0.5*self.length

        bounding_box = [[x.min(), x.max()], [y.min(), y.max()], [zmin, zmax]]
        return _np.array(bounding_box)

    def bounding_box_center(self):
        """Coordinates of the center of the block's bounding box.
        
        Each coordinate is the mean of the upper and lower bounds for the
            point cooreinates forming the block geometry.

        Note that this is different from the geometrical center returned
            by the center_point method.
        
        Raises:
            ValueError: If there is no radia object referenced by the Block.

        Returns:
            list, 3: x,y,z coorinates of bounding box center.
        """
        if self.radia_object is None:
            raise ValueError('There is no linked Radia object.')

        center = _np.mean(self.bounding_box(), axis=1)
        
        return list(center)
