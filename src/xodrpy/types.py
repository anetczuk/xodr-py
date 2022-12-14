#
# MIT License
#
# Copyright (c) 2022 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import abc
from typing import List

import math
import numpy as np

from xodrpy.utils import get_min_point2d, get_max_point2d, get_min_point,\
    get_max_point, Vector2D
from xodrpy.dicttoobject import convert,\
    DictLookup, BaseElement
from xodrpy.OdrSpiral import OdrSpiral


SCRIPT_DIR = os.path.dirname( os.path.abspath(__file__) )


## ===========================================================


##
class OpenDRIVE( BaseElement ):

#     def __init__(self):
#         super().__init__()

    def getStandardVesion(self):
        header_dict = self.get( "header", None )
        if header_dict is None:
            return "unknown"
        major = header_dict.get( "@revMajor", None )
        minor = header_dict.get( "@revMinor", None )
        if major is None or minor is None:
            return "unknown"
        return f"{major}.{minor}"

    def getDataVesion(self):
        header_dict = self.get( "header", None )
        if header_dict is None:
            return "unknown"
        version = header_dict.get( "@version", None )
        if version is None:
            return "unknown"
        return version

    def roads(self) -> List[ 'Road' ]:
        return self.get("road")

    def roadsNumber(self):
        return len( self.roads() )

    def roadById(self, road_id: str ):
        roads_list = self.roads()
        for road in roads_list:
            if road.id() == road_id:
                return road
        return None

    def boundingBox(self, margin=None):
        min_pos = (None, None, None)
        max_pos = (None, None, None)
        roads_list = self.roads()
        # road: Road = None
        for road in roads_list:
            bbox = road.boundingBox()
            min_pos = get_min_point( min_pos, bbox[0] )
            max_pos = get_max_point( max_pos, bbox[1] )
        if margin is None:
            return ( min_pos, max_pos )
        return ( (min_pos[0] - margin, min_pos[1] - margin, min_pos[2] - margin), 
                 (max_pos[0] + margin, max_pos[1] + margin, max_pos[2] + margin) )


## ================================================================


##
class Polynomial3( BaseElement ):

#     def __init__(self):
#         super().__init__()

    def offset(self):
        return float( self.attr("s") )

    def value(self, value_offset):
        raw_offset = value_offset - self.offset()
        return self.valueRaw( raw_offset )

    def valueRaw(self, value_offset):
        param_a = float( self.attr("a") )
        param_b = float( self.attr("b") )
        param_c = float( self.attr("c") )
        param_d = float( self.attr("d") )
        value  = param_a
        value += param_b * value_offset
        value += param_c * value_offset * value_offset
        value += param_d * value_offset * value_offset * value_offset
        return value


## ================================================================


##
class GeometryBase( BaseElement ):

    def __init__(self):
        super().__init__()
        self.base: dict = None

    def isLine(self):
        return False

    def length(self):
        return float( self.attr( "length" ) )

    def offset(self):
        return float( self.attr("s") )

    ## in radians
    def hdg(self):
        return float( self.attr("hdg") )

    def startPosition(self) -> Vector2D:
        xval = float( self.attr( "x" ) )
        yval = float( self.attr( "y" ) )
        return Vector2D( xval, yval )

    def positionByOffset( self, value_offset ):
        raw_offset = value_offset - self.offset()
        return self.positionByOffsetRaw( raw_offset )

    @abc.abstractmethod
    def positionByOffsetRaw( self, value_offset ):
        raise NotImplementedError('You need to define this method in derived class!')

    def boundingBox(self):
        min_pos = (None, None)
        max_pos = (None, None)
        geom_approx = self.lineApprox( 0.33 )
        for curr_point in geom_approx:
            min_pos = get_min_point2d( min_pos, curr_point )
            max_pos = get_max_point2d( max_pos, curr_point )
        return ( min_pos, max_pos )

    def lineApprox( self, step=1.0 ) -> List[ Vector2D ]:
        ret_list  = []
        length    = self.length()
        steps_num = int( length / step ) + 1
        step_size = length / steps_num
        for i in range( 0, steps_num + 1 ):
            curr_ds    = i * step_size
            curr_point = self.positionByOffsetRaw( curr_ds )
            ret_list.append( curr_point )
        return ret_list


##
class LineGeometry( GeometryBase ):

#     def __init__(self):
#         super().__init__()

    def isLine(self):
        return True

    def positionByOffsetRaw( self, value_offset ) -> Vector2D:
        start_point = self.startPosition()
        heading     = self.hdg()
        heading_vec = Vector2D( value_offset, 0.0 )
        heading_vec.rotateXY( heading )
        return start_point + heading_vec

    def boundingBox(self):
        min_pos = (None, None)
        max_pos = (None, None)
        
        length      = self.length()
        start_point = self.positionByOffsetRaw( 0.0 )
        end_point   = self.positionByOffsetRaw( length )
        
        min_pos = get_min_point2d( min_pos, start_point )
        min_pos = get_min_point2d( min_pos, end_point )
        max_pos = get_max_point2d( max_pos, start_point )
        max_pos = get_max_point2d( max_pos, end_point )

        return ( min_pos, max_pos )

    def lineApprox( self, step=1.0 ) -> List[ Vector2D ]:
        ret_list = []
        length = self.length()
        curr_point = self.positionByOffsetRaw( 0.0 )
        ret_list.append( curr_point )
        curr_point = self.positionByOffsetRaw( length )
        ret_list.append( curr_point )
        return ret_list

    @staticmethod
    def create( data_dict ):
        geom = LineGeometry()
        geom.initialize( data_dict )
        return geom


##
class ArcGeometry( GeometryBase ):

#     def __init__(self):
#         super().__init__()

    def isLine(self):
        return False

    def curvature(self):
        return float( self.attr( "curvature" ) )

    def centerPoint(self) -> Vector2D:
        start_point = self.startPosition()
        radius_vec  = self.radiusVector()
        return start_point - radius_vec

    def radiusVector( self, geom_offset=0.0 ):
        """ Vector from center point to point on arc. """
        curv = self.curvature()
        if abs( curv ) < 0.00001:
            ## line
            return Vector2D(0.0, 0.0)
        heading    = self.hdg() + math.pi / 2.0
        radius     = -1.0 / curv
        center_vec = Vector2D( radius, 0.0 )
    
        ## angle = 2*pi * geom_offset / (2*pi*r)
        ## angle = geom_offset / r
        ## angle = geom_offset * curv
        rot_angle  = geom_offset * curv
        center_vec.rotateXY( heading + rot_angle )
        return center_vec

    def positionByOffsetRaw( self, value_offset ):
#         start_point =  self.startPosition()
#         center_vec  = -self.radiusVector()
#         radius_vec  =  self.radiusVector( value_offset )
#         return start_point + center_vec + radius_vec
        center_point = self.centerPoint()
        radius_vec   = self.radiusVector( value_offset )
        return center_point + radius_vec


    @staticmethod
    def create( data_dict ):
        geom = ArcGeometry()
        geom.initialize( data_dict )
        return geom
    
#     @staticmethod
#     def create_arc( start_pos, end_pos, heading ):
#         dir = end_pos - start_pos

    @staticmethod
    def countercockwise_angle( start_vector, end_vector ):
        #TODO: handle negative angle
        unit_vector_1 = start_vector / np.linalg.norm( start_vector )
        unit_vector_2 = end_vector / np.linalg.norm( end_vector )
        dot_product   = np.dot( unit_vector_1, unit_vector_2 )
        return np.arccos( dot_product )


##
class ClothoidGeometry( GeometryBase ):

#     def __init__(self):
#         super().__init__()

    def isLine(self):
        return False

    def curvatureStart(self):
        return float( self.attr( "curvStart" ) )

    def curvatureEnd(self):
        return float( self.attr( "curvEnd" ) )

    def positionByOffsetRaw( self, value_offset ):
#         return self.startPosition()

        length     = self.length()
        curv_start = self.curvatureStart()
        curv_diff  = self.curvatureEnd() - curv_start
        curvDot    = curv_diff / length

        ## off = [1/m] / [1/m^2] = m^2 / m = m
        curv_offset = curv_start / curvDot
        
        spiral = OdrSpiral()
        (ref_x, ref_y, ref_hdg) = spiral.odrSpiral( curv_offset, curvDot )
        
        spiral = OdrSpiral()
        (x, y, _) = spiral.odrSpiral( value_offset + curv_offset, curvDot )
        x -= ref_x
        y -= ref_y
        spiral_point = Vector2D( x, y )

        start_point  = self.startPosition()
        heading      = self.hdg()
        spiral_point.rotateXY( heading - ref_hdg )
        return start_point + spiral_point


## ================================================================


##
class Road( BaseElement ):

#     def __init__(self):
#         super().__init__()

    def id(self):
        return self.attr("id")

    def length(self):
        return float( self.attr("length") )

    def geometries(self) -> List[ GeometryBase ]:
        planView = self.get( "planView" )
        return planView.get( "geometry" )

    def geometryByIndex( self, geom_index ):
        geoms = self.geometries()
        return geoms[ geom_index ]

    def elevationByOffset(self, offset_on_road) -> Polynomial3:
        elevation_profile = self.get( "elevationProfile" )
        elevation_list    = elevation_profile.get( "elevation" )
        e_size = len( elevation_list )
        if e_size < 1:
            return None
        for i in range( 0, e_size ):
            elevation = elevation_list[i]
            elevation_offset = elevation.offset()
            if elevation_offset > offset_on_road:
                if i < 1:
                    return elevation
                return elevation_list[ i - 1 ]
        return elevation_list[ -1 ]

    def elevationValue(self, offset_on_road):
        elevation: Polynomial3 = self.elevationByOffset( offset_on_road )
        if elevation is None:
            return 0.0
        return elevation.value( offset_on_road )

    def boundingBox(self):
        min_pos = (None, None)
        max_pos = (None, None)
        geoms_list = self.geometries()
        for geom in geoms_list:
            geom_bbox = geom.boundingBox()
            min_pos = get_min_point2d( min_pos, geom_bbox[0] )
            max_pos = get_max_point2d( max_pos, geom_bbox[1] )
#             geom_len  = geom.length()
#             start_pos = geom.positionByOffsetRaw( 0.0 )
#             end_pos   = geom.positionByOffsetRaw( geom_len )
# 
#             min_pos = get_min_point2d( min_pos, start_pos )
#             min_pos = get_min_point2d( min_pos, end_pos )
#             max_pos = get_max_point2d( max_pos, start_pos )
#             max_pos = get_max_point2d( max_pos, end_pos )
        road_length = self.length()
        start_z = self.elevationValue( 0.0 )
        end_z   = self.elevationValue( road_length )
        min_z   = min( start_z, end_z )
        max_z   = max( start_z, end_z )
        return ( (min_pos[0], min_pos[1], min_z), (max_pos[0], max_pos[1], max_z) )


##
def ensure_list( data_dict, data_key ):
    value_list = data_dict.get( data_key )
    if isinstance( value_list, list ) is False:
        value_list = [ value_list ]
        data_dict[ data_key ] = value_list
    return value_list
