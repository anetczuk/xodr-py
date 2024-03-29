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
import pprint

from xodrpy.utils import get_min_point2d, get_max_point2d, get_min_point,\
    get_max_point, Vector2D
from xodrpy.dicttoobject import convert,\
    DictLookup, BaseElement, ensure_dict, ensure_list, convert_to_list

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
        lookup.addClass( ["OpenDRIVE", "road", "planView", "geometry", "line"], LineGeometry )
        lookup.addClass( ["OpenDRIVE", "road", "planView", "geometry", "arc"], ArcGeometry )
        lookup.addClass( ["OpenDRIVE", "road", "planView", "geometry", "spiral"], ClothoidGeometry )
        lookup.addClass( ["OpenDRIVE", "road", "elevationProfile", "elevation"], Polynomial3 )
        lookup.addClass( ["lane", "width"], LaneWidth )
        lookup.addConverter( ["OpenDRIVE", "road", "lanes", "laneSection"], convert_to_LaneSection )
        lookup.addClass( ["OpenDRIVE", "road", "signals", "signal"], RoadSignal )
        lookup.addClass( ["OpenDRIVE", "road", "signals", "signalReference"], RoadSignalReference )
        lookup.addClass( ["OpenDRIVE", "road", "objects", "object"], RoadObject )
        lookup.addConverter( ["OpenDRIVE", "road"], convert_to_Road )
        lookup.addClass( ["OpenDRIVE", "junction"], Junction )
        lookup.addClass( ["OpenDRIVE", "controller"], SignalController )

        convert( data_dict, lookup )

        return data_dict[ "OpenDRIVE" ]


## ===========================================================


def convert_to_OpenDRIVE( data_dict: dict ) -> OpenDRIVE:
    obj = OpenDRIVE()
    obj.initialize( data_dict )

    ensure_list( obj.data, "road" )
    return obj


def convert_to_Road( data_dict: dict ) -> Road:
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

    lanes = obj.get( "lanes", None )
    if lanes:
        ensure_list( lanes, "laneSection" )

    signals = obj.get( "signals", None )
    if signals:
        ensure_list( signals, "signal" )
        ensure_list( signals, "signalReference" )

    sigs_list = obj.signalsList()
    for item in sigs_list:
        item.road = obj
    sigs_list = obj.signalReferencesList()
    for item in sigs_list:
        item.road = obj

    objects = obj.get( "objects", None )
    if objects:
        ensure_list( objects, "object" )

    objs_list = obj.objectsList()
    for item in objs_list:
        item.road = obj

    return obj


def convert_geometry( geom: dict ) -> GeometryBase:
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


def convert_to_LaneSection( data_dict: dict ) -> LaneSection:
    obj = LaneSection()
    obj.initialize( data_dict )

    all_lanes = []

    left_lanes = pop_lanes( obj, "left" )
    all_lanes.extend( left_lanes )

    left_lanes = pop_lanes( obj, "center" )
    all_lanes.extend( left_lanes )

    left_lanes = pop_lanes( obj, "right" )
    all_lanes.extend( left_lanes )

    lanes_list = []
    for lane_dict in all_lanes:
        lane = Lane()
        lane.initialize( lane_dict )
        ensure_list( lane, "width" )
        lanes_list.append( lane )
    obj[ "lanes" ] = lanes_list

    return obj


def pop_lanes( lanes_dict, lanes_key ):
    lanes_list = lanes_dict.get( lanes_key, None )
    if lanes_list is None:
        return []
    lanes_list = lanes_list.get( "lane", [] )
    if isinstance( lanes_list, list ) is False:
        lanes_list = [ lanes_list ]
    if lanes_key in lanes_dict:
        del lanes_dict[ lanes_key ]
    return lanes_list
