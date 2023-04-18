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
import logging
# import abc
# from typing import List
import pprint
import xmltodict

# from xodrpy.utils import get_min_point2d, get_max_point2d, get_min_point,\
#     get_max_point, Vector2D
from xodrpy.dicttoobject import convert,\
    DictLookup, BaseElement, ensure_list, convert_to_list
 
# from xodrpy.types import *


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname( os.path.abspath(__file__) )


## ===========================================================


def load( rrdata_path ) -> 'RRMetadata':
    with open( rrdata_path, 'r', encoding="utf-8" ) as rrdata_file:
        content   = rrdata_file.read()
        data_dict = xmltodict.parse( content )
#         pprint.pprint( data_dict )

#         dict_ids  = get_identifiers( data_dict )
#         pprint.pprint( dict_ids )

        lookup = DictLookup()
        lookup.addConverter( ["RoadRunnerMetadata"], convert_to_RRMetadata )
        lookup.addConverter( ["SignalConfigurations"], lambda dict_data: convert_to_list( dict_data, "Signal" ) )
        lookup.addConverter( ["Signalization", "Junction"], lambda dict_data: convert_to_list( dict_data, "SignalPhase" ) )

        convert( data_dict, lookup )

        return data_dict[ "RoadRunnerMetadata" ]


## ===========================================================


class RRMetadata( BaseElement ):

    def getConfigurationSignaUUIDs(self):
        configurations = self[ "SignalConfigurations" ]
        signal_list = configurations[ "Signal" ]
        signal_ids = set()
        for signal in signal_list:
            sig_id = signal["ID"]
            signal_ids.add( sig_id )
        return signal_ids

    def getSignalizationSignalUUIDs(self):
        signalization = self[ "Signalization" ]
        junction_list = signalization[ "Junction" ]
        signal_ids = set()
        for junc in junction_list:
            ## pprint.pprint( junc )
            phase_list = junc[ "SignalPhase" ]
            for phase in phase_list:
                interval_list = phase[ "Interval" ]
                for interval in interval_list:
                    signal_list = interval[ "Signal" ]
                    for signal in signal_list:
                        asset_id = signal["ID"]
                        signal_ids.add( asset_id )
        return signal_ids

    def getJunctionUUIDs(self):
        signalization = self[ "Signalization" ]
        junction_list = signalization[ "Junction" ]
        junction_ids = set()
        for junc in junction_list:
            junc_id = junc["ID"]
            junction_ids.add( junc_id )
        return junction_ids

    def getConfigurationDict(self):
        ret_config = {}
        configuration = self[ "SignalConfigurations" ]
        signal_list = configuration[ "Signal" ]
        for sig_cfg in signal_list:
            sig_id   = sig_cfg[ "ID" ]
            sig_type = sig_cfg[ "Type" ]
            sig_data = ret_config.setdefault( sig_id, {} )
            sig_cfg_list = sig_cfg[ "Configuration" ]
            cfg_list = []
            for sig_cfg in sig_cfg_list:
                cfg_name = sig_cfg[ "Name" ]
                cfg_list.append( cfg_name )
            sig_data["type"] = sig_type
            sig_data["cfg"]  = cfg_list
        return ret_config

    def getSerializationDict(self):
        ret_config = {}
        signalization = self[ "Signalization" ]
        junction_list = signalization[ "Junction" ]
        for junc in junction_list:
            junc_id = junc["ID"]
            intervals_list = ret_config.setdefault( junc_id, [] )
            phase_list = junc[ "SignalPhase" ]
            for phase in phase_list:
                interval_list = phase[ "Interval" ]
                for interval in interval_list:
                    phase_duration = interval[ "Time" ]
                    sigs_config = []
                    signal_list = interval[ "Signal" ]
                    for signal in signal_list:
                        sig_id    = signal["ID"]
                        asset_id  = signal["SignalAsset"]
                        cfg_index = int( signal["ConfigurationIndex"] )
                        sigs_config.append( { "uuid": sig_id,
                                              "asset": asset_id,
                                              "cfg_index": cfg_index } )
                    intervals_list.append( { "duration": phase_duration,
                                             "signals":  sigs_config } )
        return ret_config
    
    def getPhasesDict(self, opendrive: 'OpenDRIVE' = None):
        configuration_dict = self.getConfigurationDict()
        serialization_dict = self.getSerializationDict()
        ret_config = {}
        for junc_uuid, junc_data_list in serialization_dict.items():
            if not junc_data_list:
                continue
            phases_list = ret_config.setdefault( junc_uuid, [] )
            for phase in junc_data_list:
                data_signals = phase[ "signals" ]
                signals_list = []
                for data_signal in data_signals:
                    asset_uuid  = data_signal["asset"]
                    state_index = data_signal["cfg_index"]
                    sig_cfg        = configuration_dict.get( asset_uuid, {} )
                    sig_type       = sig_cfg.get( "type", "unknown" )
                    sig_state_list = sig_cfg.get( "cfg", [] )
                    sig_state      = "unknown"
                    if state_index < len(sig_state_list):
                        sig_state = sig_state_list[ state_index ]

                    sig_uuid = data_signal["uuid"]

                    sign_data_dict = { "uuid":  sig_uuid,
                                       "type":  sig_type,
                                       "state": sig_state }
                    if opendrive:
                        sig = opendrive.signalByUUID( sig_uuid )
                        if sig:
                            sign_data_dict['id'] = sig.id()

                    signals_list.append( sign_data_dict )
                phases_list.append( { "duration": phase[ "duration" ],
                                      "signals":  signals_list } )
        return ret_config


## ===========================================================
 

def convert_to_RRMetadata( data_dict: dict ):
    obj = RRMetadata()
    obj.initialize( data_dict )
    return obj
 
 
# def convert_to_Road( data_dict: dict ):
#     obj = Road()
#     obj.initialize( data_dict )
# 
#     # _LOGGER.info( "converting Road %s", obj.id() )
#     planView = obj.get( "planView" )
#     geoms_list = ensure_list( planView, "geometry" )
# 
#     new_list = []
#     for geom in geoms_list:
#         derived = convert_geometry( geom )
#         new_list.append( derived )
#     planView[ "geometry" ] = new_list
# 
#     elevationProfile = ensure_dict( obj.data, "elevationProfile" )
#     # elevationProfile = obj.get( "elevationProfile", None )
#     
#     # _LOGGER.info( "converting Road %s %s", obj.id(), elevationProfile )
#     ensure_list( elevationProfile, "elevation" )
#     return obj
# 
# 
# def convert_geometry( geom: dict ):
#     if isinstance(geom, str):
#         pass
#     line: GeometryBase = geom.get( "line" )
#     if line is not None:
#         del geom[ "line" ]
#         line.extend( geom )
#         return line
#     arc: GeometryBase = geom.get( "arc" )
#     if arc is not None:
#         del geom[ "arc" ]
#         arc.extend( geom )
#         return arc
#     spiral: GeometryBase = geom.get( "spiral" )
#     if spiral is not None:
#         del geom[ "spiral" ]
#         spiral.extend( geom )
#         return spiral
# 
#     raise RuntimeError( f"unhandled geometry: {geom}" )
# 
# 
# def convert_base( data_dict: dict, target_object: BaseElement ):
#     target_object.initialize( data_dict )
#     return target_object
# 
# 
# ##
# def ensure_dict( data_dict, data_key ):
#     value_dict = data_dict.get( data_key, None )
#     if value_dict is None:
#         value_dict = {}
#         data_dict[ data_key ] = value_dict
#         return value_dict
#     if isinstance( value_dict, dict ) is False:
#         raise RuntimeError( "invalid case" )
#     return value_dict
# 
# 
# ##
# def ensure_list( data_dict, data_key ):
#     value_list = data_dict.get( data_key, None )
#     if value_list is None:
#         value_list = []
#         data_dict[ data_key ] = value_list
#         return value_list
#     if isinstance( value_list, list ) is False:
#         value_list = [ value_list ]
#         data_dict[ data_key ] = value_list
#     return value_list
