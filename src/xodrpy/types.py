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
from typing import List, Any, Dict

import math
import numpy as np
import pprint

from xodrpy.utils import get_min_point2d, get_max_point2d, get_min_point,\
    get_max_point, Vector2D, Vector3D
from xodrpy.dicttoobject import convert,\
    DictLookup, BaseElement
from xodrpy.OdrSpiral import OdrSpiral


_LOGGER = logging.getLogger(__name__)

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

    def roadById(self, road_id: str ) -> 'Road':
        roads_list = self.roads()
        for road in roads_list:
            if road.id() == road_id:
                return road
        return None

    def junctions(self) -> List[ 'Junction' ]:
        return self.get("junction")

    def junctionControllerSignals(self) -> Dict[ Any, List ]:
        """Return dict mapping junction id to list of controlled signals"""
        ret_dict = {}
        junc_list = self.junctions()
        for junc in junc_list:
            junc_signals = set()
            junc_controllers_list = junc.controllersData()
            for item in junc_controllers_list:
                controller_id = item[0]
                controller: SignalController = self.controllerById(controller_id)
                if controller is None:
                    continue
                controller_signals = controller.signalIDList()
                junc_signals.update( controller_signals )
            junc_signals = list( junc_signals )
            junc_signals.sort()
            ret_dict[ junc.id() ] = junc_signals 
        return ret_dict

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

    def signalIDList(self):
        road_list = self.roads()
        signal_ids = set()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue
            sig_list = signals.get( "signal", [] )
            for sig in sig_list:
                sig_id = sig.get( "@id", None )
                if sig_id is None:
                    continue
                signal_ids.add( sig_id )

            ## signalReference does not have own ID - attribute 'id' points to proper signal

        return signal_ids

    def signalUUIDList(self):
        road_list = self.roads()
        signal_ids = set()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue

            sig_list = []
            sig_list.extend( signals.get( "signal", [] ) )
            ## sig_list.extend( signals.get( "signalReference", [] ) )
            
            for sig in sig_list:
                sig_uuid = sig.uuid()
                if sig_uuid is None:
                    continue
                signal_ids.add( sig_uuid )

        return signal_ids

    def signalList(self) -> List[ 'RoadSignal' ]:
        ret_list  = list()
        road_list = self.roads()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue
            ret_list.extend( signals.get( "signal", [] ) )
        return ret_list

    def signalReferenceList(self) -> List[ 'RoadSignalReference' ]:
        ret_list  = list()
        road_list = self.roads()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue
            ret_list.extend( signals.get( "signalReference", [] ) )
        return ret_list

    def signalGateList(self) -> List[ 'RoadSignalReference' ]:
        road_list = self.roads()
        signal_ids = list()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue

            sig_list = []
            ## sig_list.extend( signals.get( "signal", [] ) )
            sig_list.extend( signals.get( "signalReference", [] ) )

            for sig in sig_list:
                user_data   = sig.get( "userData", {} )
                signal_meta = user_data.get( "vectorSignal", {} )
                gate_id     = signal_meta.get("@gateId", None)
                if gate_id:
                    signal_ids.append( sig )
        return signal_ids

    def signalGateUUIDList(self):
        road_list = self.roads()
        signal_ids = set()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue

            sig_list = []
            ## sig_list.extend( signals.get( "signal", [] ) )
            sig_list.extend( signals.get( "signalReference", [] ) )

            for sig in sig_list:
                user_data   = sig.get( "userData", {} )
                signal_meta = user_data.get( "vectorSignal", {} )
                gate_id     = signal_meta.get("@gateId", None)
                if gate_id:
                    signal_ids.add( gate_id )
        return signal_ids

    def signalById(self, signal_id) -> 'RoadSignal':
        road_list = self.roads()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue
            sig_list = signals.get( "signal", [] )
            for sig in sig_list:
                sig_id = sig.get( "@id", None )
                if sig_id == signal_id:
                    return sig

            ## signalReference does not have own ID - attribute 'id' points to proper signal
        return None

    def signalByUUID(self, signal_uuid) -> 'RoadSignal':
        road_list = self.roads()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue
            sig_list = signals.get( "signal", [] )
            for sig in sig_list:
                if sig.uuid() == signal_uuid:
                    return sig
            ## signalReference does not have own ID - attribute 'id' points to proper signal
        return None

    def signalReferencesByID(self, signal_id) -> List[ 'RoadSignalReference' ]:
        ret_list = []
        road_list = self.roads()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue
            sig_list = signals.get( "signalReference", [] )
            for sig in sig_list:
                if sig.id() == signal_id:
                    ret_list.append( sig )
        return ret_list

    def signalReferencesByUUID(self, signal_uuid) -> List[ 'RoadSignalReference' ]:
        ret_list = []
        road_list = self.roads()
        for road in road_list:
            ## pprint.pprint( road )
            signals = road.get( "signals", None )
            if signals is None:
                continue
            sig_list = signals.get( "signalReference", [] )
            for sig in sig_list:
                if sig.uuid() == signal_uuid:
                    ret_list.append( sig )
        return ret_list

    def objectIDList(self):
        road_list = self.roads()
        object_ids = set()
        for road in road_list:
            ## pprint.pprint( road )
            objects = road.get( "objects", None )
            if objects is None:
                continue
            object_list = objects.get( "object", [] )
            for obj in object_list:
                obj_id = obj.get( "@id", None )
                if obj_id is None:
                    continue
                object_ids.add( obj_id )
        return object_ids

    def objectById(self, object_id) -> 'RoadObject':
        road_list = self.roads()
        for road in road_list:
            ## pprint.pprint( road )
            objects = road.get( "objects", None )
            if objects is None:
                continue
            obj_list = objects.get( "object", [] )
            for obj in obj_list:
                obj_id = obj.get( "@id", None )
                if obj_id == object_id:
                    return obj
        return None

    ## ==============================================

    def controllers(self) -> List[ 'SignalController' ]:
        return self.get("controller")

    def controllerById(self, controller_id) -> 'SignalController':
        controller_list = self.controllers()
        for controller in controller_list:
            if controller.id() == controller_id:
                return controller
        return None


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

    def positionByOffset( self, offset_on_road, t_coord=0.0 ) -> Vector2D:
        raw_offset = offset_on_road - self.offset()
        position = self.positionByOffsetRaw( raw_offset )
        heading  = self.headingByOffsetRaw( raw_offset )
        heading_vec = Vector2D( t_coord, 0.0 )
        heading_vec.rotate90()                      ## orthogonal
        heading_vec.rotateXY( heading )
        return position + heading_vec

    @abc.abstractmethod
    def positionByOffsetRaw( self, value_offset ) -> Vector2D:
        raise NotImplementedError('You need to define this method in derived class!')

    def headingByOffset( self, offset_on_road ) -> Vector2D:
        raw_offset = offset_on_road - self.offset()
        return self.headingByOffsetRaw( raw_offset )

    @abc.abstractmethod
    def headingByOffsetRaw( self, value_offset ) -> float:
        """ returns value in radians """
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

    def headingByOffsetRaw( self, value_offset ) -> float:
        return self.hdg()

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

    def radiusVector( self, geom_offset=0.0 ) -> Vector2D:
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

    def headingByOffsetRaw( self, value_offset ) -> float:
        curv = self.curvature()
        if abs( curv ) < 0.00001:
            ## line
            return self.hdg()
        radius = 1.0 / curv
        return value_offset / radius + self.hdg()


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

    def headingByOffsetRaw( self, value_offset ) -> float:
        raise NotImplementedError('You need to define this method in derived class!')


## ================================================================


##
class Road( BaseElement ):

#     def __init__(self):
#         super().__init__()

    def id(self):
        return self.attr("id")

    def junctionId(self):
        return self.attr("junction")

    def length(self):
        return float( self.attr("length") )

    def geometries(self) -> List[ GeometryBase ]:
        planView = self.get( "planView" )
        return planView.get( "geometry" )

    def geometryByIndex( self, geom_index ):
        geoms = self.geometries()
        return geoms[ geom_index ]

    def geometryByOffset(self, offset_on_road) -> GeometryBase:
        geoms = self.geometries()
        return get_item_by_offset( geoms, offset_on_road )

    def elevationByOffset(self, offset_on_road) -> Polynomial3:
        elevation_profile = self.get( "elevationProfile" )
        elevation_list    = elevation_profile.get( "elevation" )
        return get_item_by_offset( elevation_list, offset_on_road )

    def elevationValue(self, offset_on_road):
        elevation: Polynomial3 = self.elevationByOffset( offset_on_road )
        if elevation is None:
            return 0.0
        return elevation.value( offset_on_road )

    def laneSections(self) -> List[ 'LaneSection' ]:
        lanes = self.get( "lanes" )
        return lanes.get( "laneSection" )
    
    def laneSectionById(self, section_id):
        sections = self.laneSections()
        return next( (item for item in sections if item.id() == section_id), None )
    
    def laneSectionByOffset(self, offset_on_road) -> 'LaneSection':
        sections = self.laneSections()
        return get_item_by_offset( sections, offset_on_road )
    
    def laneById(self, section_id, lane_id):
        section = self.laneSectionById( section_id )
        if section is None:
            return none
        return section.laneById( lane_id )

    def position( self, s_coord, t_coord, z_coord ) -> Vector3D:
        geom = self.geometryByOffset( s_coord )
        if not geom:
            return None
        geom_pos: Vector2D = geom.positionByOffset( s_coord, t_coord )    
        elevation = self.elevationValue( s_coord ) + z_coord
        return Vector3D( geom_pos.x, geom_pos.y, elevation )

    def position2d( self, s_coord, t_coord ) -> Vector2D:
        geom = self.geometryByOffset( s_coord )
        if not geom:
            return None
        return geom.positionByOffset( s_coord, t_coord )    

    def heading(self, s_coord):
        geom = self.geometryByOffset( s_coord )
        if not geom:
            return None
        return geom.headingByOffset( s_coord )

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
    
    def signalsList(self) -> List[ 'RoadSignal' ]:
        sigs_dict = self.get("signals")
        if not sigs_dict:
            return []
        sigs_list = sigs_dict.get("signal")
        if not sigs_list:
            return []
        return sigs_list
    
    def signalReferencesList(self):
        sigs_dict = self.get("signals")
        if not sigs_dict:
            return []
        sigs_list = sigs_dict.get("signalReference")
        if not sigs_list:
            return []
        return sigs_list

    def signalById(self, signal_id) -> 'RoadSignal':
        ## pprint.pprint( road )
        signals = self.get( "signals", None )
        if signals is None:
            return None
        sig_list = signals.get( "signal", [] )
        for sig in sig_list:
            sig_id = sig.get( "@id", None )
            if sig_id == signal_id:
                return sig
        return None

    def objectsList(self):
        obj_dict = self.get("objects")
        if not obj_dict:
            return []
        obj_list = obj_dict.get("object")
        if not obj_list:
            return []
        return obj_list


## ================================================================


##
class LaneSection( BaseElement ):

#     def __init__(self):
#         super().__init__()

    def id(self):
        return self.attr("id")

    def offset(self):
        return float( self.attr("s") )

    def laneById(self, lane_id) -> 'Lane':
        lane_id = str( lane_id )
        lanes = self.get( "lanes", [] )
        return next( (item for item in lanes if item.id() == lane_id), None )

    def laneIndexById(self, lane_id: int) -> int:
        lane_id = str( lane_id )
        lanes = self.get( "lanes", [] )
        return next( (index for index, item in enumerate(lanes) if item.id() == lane_id), -1 )

    def minMaxTOffset(self, lane_id: int, offset_on_road):
        if lane_id == 0:
            return (0.0, 0.0)
        center_index = self.laneIndexById( 0 )
        if center_index < 0:
            return None
        lane_index = self.laneIndexById( lane_id )
        if lane_index < 0:
            return None
        offset_on_section = offset_on_road - self.offset()
        lanes = self.get( "lanes", [] )
        if lane_index < center_index:
            ## positive side
            min_offset = 0.0
            for lane_index in range( lane_index + 1, center_index ):
                curr_lane   = lanes[ lane_index ]
                curr_width  = curr_lane.width( offset_on_section )
                min_offset += curr_width
            curr_lane  = lanes[ lane_index ]
            curr_width = curr_lane.width( offset_on_section )
            max_offset = min_offset + curr_width
            return ( min_offset, max_offset )
        else:
            ## negative side
            max_offset = 0.0
            for lane_index in range( center_index + 1, lane_index ):
                curr_lane   = lanes[ lane_index ]
                curr_width  = curr_lane.width( offset_on_section )
                max_offset -= curr_width
            curr_lane  = lanes[ lane_index ]
            curr_width = curr_lane.width( offset_on_section )
            min_offset = max_offset - curr_width
            return ( min_offset, max_offset )


## ================================================================


##
class Lane( BaseElement ):

#     def __init__(self):
#         super().__init__()

    def id(self):
        return self.attr("id")

    def widthList(self):
        return self.get( "width", [] )

    def width(self, offset_on_section):
        width_list = self.widthList()
        width_item: LaneWidth = get_item_by_offset( width_list, offset_on_section )
        if width_item is None:
            ## center lane
            return 0.0
        return width_item.width(offset_on_section)


##
class LaneWidth( BaseElement ):

#     def __init__(self):
#         super().__init__()

    def startOffset(self):
        return float( self.attr("sOffset") )

    ## alias
    def offset(self):
        return self.startOffset()

    def width(self, offset_on_section):
        offset = offset_on_section - self.startOffset()
        return self.widthRaw( offset )
        
    def widthRaw(self, offset):
        width  = 0.0
        param  = 1.0

        width += float( self.attr("a") ) * param

        param *= offset
        width += float( self.attr("b") ) * param

        param *= offset
        width += float( self.attr("c") ) * param

        param *= offset
        width += float( self.attr("d") ) * param

        return width


## return item from list by 'offset_value'
## list item have to have 'offset()' member
def get_item_by_offset( item_list, offset_value ):
    list_size = len( item_list )
    if list_size < 1:
        return None
    for i in range( 0, list_size ):
        item = item_list[i]
        item_offset = item.offset()
        if item_offset > offset_value:
            if i < 1:
                return item
            return item_list[ i - 1 ]
    return item_list[ -1 ]


## ================================================================


class RoadSignalBase( BaseElement ):

    def __init__(self):
        super().__init__()
        self.road = None        ## road owning the signal

    def id(self):
        return self.attr("id")

    def uuid(self):
        """Return UUID of RR meta data."""
        user_data = self.get( "userData", None )
        if user_data is None:
            return None
        signal_meta = user_data.get( "vectorSignal", None )
        if signal_meta is None:
            return None
        return signal_meta.get( "@signalId", None )

    def gateUUID(self):
        """Return gate UUID of RR meta data."""
        user_data = self.get( "userData", None )
        if user_data is None:
            return None
        signal_meta = user_data.get( "vectorSignal", None )
        if signal_meta is None:
            return None
        return signal_meta.get( "@gateId", None )

    def position2d(self):
        s_coord = float( self.attr("s") )
        t_coord = float( self.attr("t") )
        return self.road.position2d( s_coord, t_coord )

    def validity(self):
        validity = self.get("validity", None)
        if not validity:
            return None
        fromLane = int( validity.get("@fromLane", None) )
        toLane   = int( validity.get("@toLane", None) )
        return (fromLane, toLane)
    
    ## returns "+" or "-"
    def orientation(self):
        return self.attr( "orientation" )


##
class RoadSignal( RoadSignalBase ):

    def __init__(self):
        super().__init__()

    def name(self):
        return self.attr("name")

    def type(self):
        return self.attr("type")

    def subtype(self):
        return self.attr("subtype")

    def zOffset(self):
        return float( self.attr("zOffset") )

    def coords(self):
        s_coord = float( self.attr("s") )
        t_coord = float( self.attr("t") )
        z_coord = float( self.attr("zOffset") )
        return { "s": s_coord, "t": t_coord, "z": z_coord }

    def position(self):
        s_coord = float( self.attr("s") )
        t_coord = float( self.attr("t") )
        z_coord = float( self.attr("zOffset") )
        return self.road.position( s_coord, t_coord, z_coord )

    def headingRaw(self):
        return float( self.attr( "hOffset" ) )

    def heading(self):
        obj_heading = self.headingRaw()
        s_coord = float( self.attr("s") )
        road_heading = self.road.heading( s_coord )
        return obj_heading + road_heading
    

##
class RoadSignalReference( RoadSignalBase ):

    def __init__(self):
        super().__init__()

    def turnRelation(self):
        user_data = self.get( "userData", None )
        if user_data is None:
            return None
        signal_meta = user_data.get( "vectorSignal", None )
        if signal_meta is None:
            return None
        return signal_meta.get( "@turnRelation", None )

    def coords(self):
        s_coord = float( self.attr("s") )
        t_coord = float( self.attr("t") )
        return ( s_coord, t_coord )

    def position(self):
        s_coord = float( self.attr("s") )
        t_coord = float( self.attr("t") )
        ## signal reference does not have Z coord
        return self.road.position( s_coord, t_coord, 0.0 )

    def heading(self):
        s_coord = float( self.attr("s") )
        road_heading = self.road.heading( s_coord )
        orient = self.orientation()
        if orient == "+":
            road_heading += math.pi
#         elif orient == "+":
#             orient_angle -= math.pi * 0.5
        return road_heading

    def gateCoords(self):
        """Coords of gate (specific to RoadRunner)."""
        validity = self.validity()
        if validity is None:
            _LOGGER.warning( "no validity data found" )
            return self.coords()

        s_coord = float( self.attr("s") )
        section: LaneSection = self.road.laneSectionByOffset( s_coord )
        if section is None:
            _LOGGER.warning( "no lane section found" )
            return self.coords()

        from_lane_id = validity[0]
        to_lane_id   = validity[1]

        if from_lane_id == to_lane_id:
            ## one lane
            lane_offsets = section.minMaxTOffset( from_lane_id, s_coord )
            min_offset = lane_offsets[0]
            max_offset = lane_offsets[1]
            t_coord    = ( max_offset + min_offset ) * 0.5
            return ( s_coord, t_coord )

        # lanes span
        from_offsets = section.minMaxTOffset( from_lane_id, s_coord )
        if from_offsets is None:
            return self.coords()

        to_offsets   = section.minMaxTOffset( to_lane_id, s_coord )
        if to_offsets is None:
            return self.coords()

        min_offset = min( from_offsets[0], to_offsets[0] )
        max_offset = min( to_offsets[0], to_offsets[0] )
        t_coord    = ( max_offset + min_offset ) * 0.5
        return ( s_coord, t_coord )

    def gatePosition2d(self):
        """Position of gate (specific to RoadRunner)."""
        coords = self.gateCoords()
        return self.road.position2d( coords[0], coords[1] )


## ================================================================


class RoadObject( BaseElement ):

    def __init__(self):
        super().__init__()
        self.road = None        ## road owning the signal

    def id(self):
        return self.attr("id")

    def name(self):
        return self.attr("name")

    def type(self):
        return self.attr("type")

    def offsetOnRoad(self):
        return self.attr("s")

    def zOffset(self):
        return float( self.attr("zOffset") )

    def position(self) -> Vector3D:
        s_coord = float( self.attr("s") )
        t_coord = float( self.attr("t") )
        z_coord = float( self.attr("zOffset") )
        return self.road.position( s_coord, t_coord, z_coord )

    def headingRaw(self):
        return float( self.attr( "hdg" ) )

    def heading(self):
        obj_heading = self.headingRaw()
        s_coord = float( self.attr("s") )
        road_heading = self.road.heading( s_coord )
        return obj_heading + road_heading

#         orient_angle = 0.0
# #         orient_angle -= math.pi * 0.5
#
#         orient = self.orientation()
#         if orient == "-":
#             orient_angle += math.pi * 0.5
# #         elif orient == "+":
# #             orient_angle -= math.pi * 0.5
#
# #         t_coord = float( self.attr("t") )
# #         if t_coord < 0.0:
# #             orient_angle += math.pi * 0.5
# #         else:
# #             orient_angle -= math.pi * 0.5
#
#         return obj_heading + road_heading + orient_angle
#
# #         s_coord = float( self.attr("s") )
# #         road_heading = self.road.heading( s_coord )
# #         obj_heading  = self.headingRaw()
# #         orient = self.orientation()
# #         orient_angle = 0.0
# #         if orient == "-":
# #             orient_angle -= math.pi * 0.5
# #         elif orient == "+":
# #             orient_angle += math.pi * 0.5
# #         return road_heading + obj_heading - orient_angle

    ## returns "+" or "-"
    def orientation(self):
        return self.attr( "orientation" )


## ================================================================


class Junction( BaseElement ):

    def id(self):
        return self.attr("id")

    def name(self):
        return self.attr("name")

    def uuid(self):
        """Return UUID of RR meta data."""
        user_data = self.get( "userData", None )
        if user_data is None:
            return None
        junc_meta = user_data.get( "vectorJunction", None )
        if junc_meta is None:
            return None
        return junc_meta.get( "@junctionId", None )

    def controllersData(self):
        controller_list = self.get("controller")
        if not controller_list:
            return []
        ret = []
        for item in controller_list:
            ret.append( (item["@id"], item["@type"], item["@sequence"]) )
        return ret


## ================================================================


class SignalController( BaseElement ):

    def id(self):
        return self.attr("id")

    def name(self):
        return self.attr("name")

    def signalIDList(self):
        ret = []
        signals_list = self.get("control")
        for item in signals_list:
            ret.append( item["@signalId"] )
        return ret
