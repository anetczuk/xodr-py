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
from collections import UserDict
from typing import Callable, Dict, Any


SCRIPT_DIR = os.path.dirname( os.path.abspath(__file__) )


##
class DictTraverser():

    def __init__(self):
        self.curr_path = ()

    def traverse( self, data_dict: dict ):
        if isinstance( data_dict, dict ):
            self._traverseDict( data_dict )
            return
        if isinstance( data_dict, list ):
            self._traverseList( data_dict )
            return
        raise RuntimeError( 'invalid data: dict or list expected' )

    def _traverseDict( self, data_dict: dict ):
#         if contains_dict_or_list( data_dict ) is False:
#             return

        for key, value in data_dict.items():
#             if is_dict_or_list( value ) is False:
#                 continue

            old_path = self.curr_path
            self.curr_path = self.curr_path + tuple( [key] )
#                     self.curr_path = self.curr_path.copy()
            self._nextPath( key )

            if isinstance( value, list ):
                self._traverseList( value )
            else:
                self._traverseStep( data_dict, key, value )

            self.curr_path = old_path

    def _traverseList( self, value: list ):
        v_size = len(value)
        for index in range(0, v_size):
            item = value[ index ]

            if isinstance( item, dict ):
                self._traverseStep( value, index, item )
#                 self._traverseDict( item )
                continue
            if isinstance( item, list ):
                self._traverseList( item )
                continue

    ## 'data_dict' is associative container like list or dict
    def _traverseStep( self, data_dict, data_key, data_value ):
        self._traversePre( data_dict, data_key, data_value )

        if isinstance( data_value, dict ):
            self._traverseDict( data_value )
#         elif isinstance( data_value, list ):
#             self._traverseList( data_dict, data_key, data_value )

        self._traversePost( data_dict, data_key, data_value )

    def _traversePre( self, data_dict: dict, data_key, data_value ):
        pass

    def _traversePost( self, data_container, data_key, data_value ):
        pass

    def _nextPath(self, key):
        pass


##
class BaseElement( UserDict ):

    def __init__(self):
        super().__init__(self)

    def initialize( self, data: dict ):
        if isinstance( data, dict ):
            self.extend( data )
        self._init()

    def extend( self, data_dict: dict ):
        for key, val in data_dict.items():
            self[ key ] = val

    ## post deserialize init stage
    def _init(self):
        pass

    def attr( self, name ):
        return self.get( "@" + name )


##
class ConverterLookup():

    def __init__(self):
        pass

    # def lookupConverter(self, curr_path ) -> Callable[ [Dict], Any ]:
    def lookupConverter(self, _ ) -> Callable[ [Dict], Any ]:
        return None


## ====================================================


def convert( data_dict, lookup_object: ConverterLookup = None ):
    if lookup_object is None:
        return
    converter = ConvertTraverser( lookup_object )
    converter.convert( data_dict )


##
class BaseElementConverter():

    def __init__(self, class_type ):
        self.class_type = class_type

    def __call__(self, data_value) -> BaseElement:
        if self.class_type is None:
            return None
        target: BaseElement = self.class_type()
        target.initialize( data_value )
        return target


##
class DictLookup( ConverterLookup ):

    def __init__(self):
        super().__init__()
        ##self.builder = DictBuilder()
        self.convert_list = []

    def addClass( self, path, class_type ):
        if class_type is None:
            return
        converter = BaseElementConverter( class_type )
        self.convert_list.append( ( tuple(path), converter ) )
    
    def addConverter( self, path, converter ):
        self.convert_list.append( ( tuple(path), converter ) )

    def lookupType(self, curr_path ):
        converter: Callable[ [Dict], Any ] = self.lookupConverter( curr_path )
        if converter is None:
            return None
        if isinstance( converter, BaseElementConverter ):
            return converter.class_type
        return converter

    def lookupConverter(self, curr_path ) -> Callable[ [Dict], Any ]:
        if isinstance( curr_path, tuple ) is False:
            path = tuple( curr_path )
            return self._get( path )
        return self._get( curr_path )

    def _get(self, curr_path) -> Callable[ [Dict], Any ]:
#         factory_dict = self.builder.data_dict
#         ## print( "a:", factory_dict, "b:", curr_path, "c:", None )
#         target_type = get_by_path( factory_dict, curr_path, None )

        ## check exact
        for pair in self.convert_list:
            if pair[0] == curr_path:
                return pair[1]

        ## check subpath
        for pair in self.convert_list:
            if is_matching( pair[0], curr_path ):
                return pair[1]
        return None


##
def is_matching( type_path, search_path ):
    type_len    = len( type_path )
    search_len  = len( search_path )
    search_diff = search_len - type_len
    if search_diff < 0:
        return False
    if type_len == search_len:
        return type_path == search_path
    for i in range( search_diff + 1, 0, -1 ):
        sub_type = search_path[ i: i + search_len ]
        if sub_type == type_path:
            return True
    return False


##
class ConvertTraverser( DictTraverser ):

    def __init__(self, lookup: ConverterLookup = None):
        super().__init__()
        self.lookup: ConverterLookup = lookup

    def convert( self, data_dict: dict ):
        self.traverse( data_dict )

    def _traversePost( self, data_container, data_key, data_value ):
        if self.lookup is None:
            return
        converter: Callable[ [Dict], Any ] = self.lookup.lookupConverter( self.curr_path )
        if converter is None:
            return
        result = converter( data_value )
        data_container[ data_key ] = result


##
def get_identifiers( data_dict ):
    extractor = PathsExtractor()
    extractor.extract( data_dict )
    return extractor.getUnique()


##
class PathsExtractor( DictTraverser ):

    def __init__(self):
        super().__init__()
        self.ret_list = []

    def extract( self, data_dict ):
        self.traverse( data_dict )
        return self.ret_list

    def _nextPath(self, key):
        if self.curr_path not in self.ret_list:
            self.ret_list.append( self.curr_path )

    def getUnique( self ):
        return self._getUnique( self.ret_list, -1 )

    def _getUnique( self, paths_list, split_index=-1 ):
        leaf_dict = self._splitDict( paths_list, split_index )

        unique_ids = []
        for _, paths in leaf_dict.items():
            if len(paths) < 2:
                path = paths[0]
                v_size = len(path)
                sub_list = path[ v_size + split_index: v_size ]
                unique_ids.append( sub_list )
                continue

            ret_list = self._getUnique( paths, split_index - 1 )
            unique_ids.extend( ret_list )

        return unique_ids

    def _isItemUnique(self, paths_list, sublist_list):
        list_set = []
        for curr_path in paths_list:
            curr_list = curr_path
            if sublist_list < len(curr_path):
                curr_list = curr_path[ 0: sublist_list ]
#             if len( item_set ) < 1:
#                 check_item = curr_path[ check_index ]
#                 item_set.add( check_item )
#                 continue
            if curr_list in list_set:
                return False
            list_set.append( curr_list )
        return True

    def _splitDict( self, path_list, item_index ):
        leaf_dict = {}
        for item in path_list:
            leaf = item[ item_index ]
            leaf_list = leaf_dict.get( leaf, None )
            if leaf_list is None:
                leaf_dict[ leaf ] = []
            leaf_dict[ leaf ].append( item )
        return leaf_dict


def contains_dict_or_list( data ):
    if isinstance( data, dict ):
        for _, value in data.items():
            if is_dict_or_list( value ):
                return True
    if isinstance( data, list ):
        for value in data:
            if is_dict_or_list( value ):
                return True
    return False


def is_dict_or_list( data ):
    if isinstance( data, dict ):
        return True
    if isinstance( data, list ):
        return True
    return False


## ====================================================


##
class DictBuilder():

    def __init__(self):
        self.data_dict = {}

    def getData(self):
        return self.data_dict.copy()

    def addPath( self, path_list, value ):
        self._addPath( self.data_dict, path_list, value )

    def _addPath( self, data_dict, keys_list, value ):
    #     print( "addd:", data_dict, keys_list, value )
        p_size = len( keys_list )
        if p_size < 1:
            return
        item = keys_list[0]
        if p_size == 1:
            data_dict[ item ] = value
            return
        sub_data = get_or_create( data_dict, item, {} )
        sub_list = keys_list[ 1: ]
        self._addPath( sub_data, sub_list, value )


def get_or_create( data_dict, key, default_value ):
    if key not in data_dict:
        data_dict[ key ] = default_value
    return data_dict[ key ]


def get_by_path( data_dict, keys_list, default_value=None ):
#     print( "keys:", keys_list, "data:", data_dict )
    if data_dict is None:
        return None
    if isinstance( data_dict, dict ) is False:
        return None
    p_size = len( keys_list )
    if p_size < 1:
        return default_value
    key = keys_list[0]
    if p_size == 1:
#         print( "xxx:", key, p_size, type(key), keys_list, data_dict )
        return data_dict.get( key, default_value )
    sub_data = data_dict.get( key, default_value )
    sub_list = keys_list[ 1: ]
    return get_by_path( sub_data, sub_list, default_value )
