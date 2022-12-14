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
import logging
from typing import List
import xmltodict

from xodrpy.utils import get_min_point2d, get_max_point2d, get_min_point,\
    get_max_point, Vector2D
from xodrpy.dicttoobject import convert,\
    DictLookup, BaseElement

from xodrpy.types import *


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname( os.path.abspath(__file__) )


## ===========================================================


def load( xodr_path ) -> OpenDRIVE:
    with open( xodr_path, 'r', encoding="utf-8" ) as xodr_file:
        content   = xodr_file.read()
        data_dict = xmltodict.parse( content )
#         pprint.pprint( data_dict )

#         dict_ids  = get_identifiers( data_dict )
#         pprint.pprint( dict_ids )

        lookup = DictLookup()
        lookup.addConverter( ["OpenDRIVE"], convert_to_OpenDRIVE )
        lookup.addConverter( ["OpenDRIVE", "road"], convert_to_Road )
        lookup.addClass( ["OpenDRIVE", "road", "planView", "geometry", "line"], LineGeometry )
        lookup.addClass( ["OpenDRIVE", "road", "planView", "geometry", "arc"], ArcGeometry )
        lookup.addClass( ["OpenDRIVE", "road", "planView", "geometry", "spiral"], ClothoidGeometry )
        lookup.addClass( ["OpenDRIVE", "road", "elevationProfile", "elevation"], Polynomial3 )
        convert( data_dict, lookup )

        return data_dict[ "OpenDRIVE" ]


## ===========================================================


def convert_to_OpenDRIVE( data_dict: dict ):
    obj = OpenDRIVE()
    obj.initialize( data_dict )

    ensure_list( obj.data, "road" )
    return obj


def convert_to_Road( data_dict: dict ):
    obj = Road()
    obj.initialize( data_dict )

    # _LOGGER.info( "converting Road %s", obj.id() )
    planView = obj.get( "planView" )
    geoms_list = ensure_list( planView, "geometry" )

    new_list = []
    for geom in geoms_list:
        derived = convert_geometry( geom )
        new_list.append( derived )
    planView[ "geometry" ] = new_list

    elevationProfile = ensure_dict( obj.data, "elevationProfile" )
    # elevationProfile = obj.get( "elevationProfile", None )
    
    # _LOGGER.info( "converting Road %s %s", obj.id(), elevationProfile )
    ensure_list( elevationProfile, "elevation" )
    return obj


def convert_geometry( geom: dict ):
    if isinstance(geom, str):
        pass
    line: GeometryBase = geom.get( "line" )
    if line is not None:
        del geom[ "line" ]
        line.extend( geom )
        return line
    arc: GeometryBase = geom.get( "arc" )
    if arc is not None:
        del geom[ "arc" ]
        arc.extend( geom )
        return arc
    spiral: GeometryBase = geom.get( "spiral" )
    if spiral is not None:
        del geom[ "spiral" ]
        spiral.extend( geom )
        return spiral

    raise RuntimeError( f"unhandled geometry: {geom}" )


def convert_base( data_dict: dict, target_object: BaseElement ):
    target_object.initialize( data_dict )
    return target_object


##
def ensure_dict( data_dict, data_key ):
    value_dict = data_dict.get( data_key, None )
    if value_dict is None:
        value_dict = {}
        data_dict[ data_key ] = value_dict
        return value_dict
    if isinstance( value_dict, dict ) is False:
        raise RuntimeError( "invalid case" )
    return value_dict


##
def ensure_list( data_dict, data_key ):
    value_list = data_dict.get( data_key, None )
    if value_list is None:
        value_list = []
        data_dict[ data_key ] = value_list
        return value_list
    if isinstance( value_list, list ) is False:
        value_list = [ value_list ]
        data_dict[ data_key ] = value_list
    return value_list
