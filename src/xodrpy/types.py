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
import xmltodict

from xodrpy.utils import get_min_point2d, get_max_point2d, get_min_point,\
    get_max_point, Vector2D
from xodrpy.dicttoobject import convert,\
    DictLookup, BaseElement


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

    def roadsNumber(self):
        roads_list = self.get("road")
        return len( roads_list )

    def roadById(self, road_id: str ):
        roads_list = self.get("road")
        for road in roads_list:
            if road.id() == road_id:
                return road
        return None

    def boundingBox(self):
        min_pos = (None, None, None)
        max_pos = (None, None, None)
        roads_list = self.get("road")
        # road: Road = None
        for road in roads_list:
            bbox = road.boundingBox()
            min_pos = get_min_point( min_pos, bbox[0] )
            max_pos = get_max_point( max_pos, bbox[1] )
        return ( min_pos, max_pos )


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

    def length(self):
        return float( self.attr( "length" ) )

    def offset(self):
        return float( self.attr("s") )

    ## in radians
    def hdg(self):
        return float( self.attr("hdg") )

    def startPosition(self):
        xval = float( self.attr( "x" ) )
        yval = float( self.attr( "y" ) )
        return Vector2D( xval, yval )

    def positionByOffset( self, value_offset ):
        raw_offset = value_offset - self.offset()
        return self.positionByOffsetRaw( raw_offset )

    @abc.abstractmethod
    def positionByOffsetRaw( self, value_offset ):
        raise NotImplementedError('You need to define this method in derived class!')


##
class LineGeometry( GeometryBase ):

#     def __init__(self):
#         super().__init__()

    def positionByOffsetRaw( self, value_offset ):
        start_point = self.startPosition()
        heading     = self.hdg()
        heading_vec = Vector2D( value_offset, 0.0 )
        heading_vec.rotateXY( heading )
        return start_point + heading_vec

    @staticmethod
    def create( data_dict ):
        geom = LineGeometry()
        geom.initialize( data_dict )
        return geom


##
class ArcGeometry( GeometryBase ):

#     def __init__(self):
#         super().__init__()

    def positionByOffsetRaw( self, value_offset ):
        xval = float( self.attr( "x" ) )
        yval = float( self.attr( "y" ) )
        start_point = Vector2D( xval, yval )
        return start_point


##
class ClothoidGeometry( GeometryBase ):

#     def __init__(self):
#         super().__init__()

    def positionByOffsetRaw( self, value_offset ):
        xval = float( self.attr( "x" ) )
        yval = float( self.attr( "y" ) )
        start_point = Vector2D( xval, yval )
        return start_point


## ================================================================


##
class Road( BaseElement ):

#     def __init__(self):
#         super().__init__()

    def id(self):
        return self.attr("id")

    def length(self):
        return float( self.attr("length") )

    def geomsList(self) -> List[ GeometryBase ]:
        planView = self.get( "planView" )
        return planView.get( "geometry" )

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
            return None
        return elevation.value( offset_on_road )

    def boundingBox(self):
        min_pos = (None, None)
        max_pos = (None, None)
        geoms_list = self.geomsList()
        for geom in geoms_list:
            geom_len  = geom.length()
            start_pos = geom.positionByOffsetRaw( 0.0 )
            end_pos   = geom.positionByOffsetRaw( geom_len )

            min_pos = get_min_point2d( min_pos, start_pos )
            min_pos = get_min_point2d( min_pos, end_pos )
            max_pos = get_max_point2d( max_pos, start_pos )
            max_pos = get_max_point2d( max_pos, end_pos )
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
