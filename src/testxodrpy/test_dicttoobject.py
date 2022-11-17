# MIT License
#
# Copyright (c) 2020 Arkadiusz Netczuk <dev.arnet@gmail.com>
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

import unittest

from xodrpy.dicttoobject import get_identifiers, PathsExtractor,\
    DictBuilder, convert, DictLookup, BaseElement


class ModuleTest(unittest.TestCase):

    class TestElement( BaseElement ):
        pass
#         def __init__(self):
#             super().__init__()

    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_get_identifiers_attr(self):
        builder = DictBuilder()
        builder.addPath( ["attr1"], "val1" )
        data_dict = builder.getData()

        ids = get_identifiers( data_dict )
        self.assertEqual( [ ('attr1',) ], ids )

    def test_get_identifiers_obj01(self):
        builder = DictBuilder()
        builder.addPath( ["obj1", "attr1"], "val1" )
        data_dict = builder.getData()

        ids = get_identifiers( data_dict )
        self.assertEqual( [ ("obj1",), ('attr1',) ], ids )

    def test_get_identifiers_obj02(self):
        builder = DictBuilder()
        builder.addPath( ["obj1", "attr1"], "val1" )
        builder.addPath( ["obj2", "attr1"], "val2" )
        data_dict = builder.getData()

        ids = get_identifiers( data_dict )
        self.assertEqual( [('obj1',), ('obj1', 'attr1'), ('obj2', 'attr1'), ('obj2',)], ids )

    def test_get_identifiers_obj03(self):
        builder = DictBuilder()
        builder.addPath( ["obj3", "obj1", "attr1"], "val1" )
        builder.addPath( ["obj3", "obj2", "attr1"], "val2" )
        data_dict = builder.getData()

        ids = get_identifiers( data_dict )
        self.assertEqual( [ ("obj3",), ("obj1",), ("obj1", "attr1"), ("obj2", "attr1"), ("obj2",) ], ids )

    def test_get_identifiers_list01(self):
        data_dict = [ {"obj1": { "attr1": "val1" }},
                      {"obj2": { "attr1": "val1" }}
                      ]
        ids = get_identifiers( data_dict )
        self.assertEqual( [ ("obj1",), ("obj1", "attr1"), ("obj2", "attr1"), ("obj2",) ], ids )

    ## ==================================================================

    def test_convert_simple(self):
        builder = DictBuilder()
        builder.addPath( ["obj1", "attr1"], 10 )
        data_dict = builder.getData()

        lookup = DictLookup()
        lookup.addClass( ["obj1"], ModuleTest.TestElement )
        convert( data_dict, lookup )

        self.assertEqual( "{'obj1': {'attr1': 10}}", str( data_dict ) )
        self.assertEqual( dict, type( data_dict ) )
        self.assertEqual( ModuleTest.TestElement, type( data_dict['obj1'] ) )
        self.assertEqual( int, type( data_dict['obj1']['attr1'] ) )

    def test_convert_simple_none(self):
        builder = DictBuilder()
        builder.addPath( ["obj1", "attr1"], 10 )
        data_dict = builder.getData()

        lookup = DictLookup()
        lookup.addClass( ["obj1"], None )
        convert( data_dict, lookup )

        self.assertEqual( "{'obj1': {'attr1': 10}}", str( data_dict ) )
        self.assertEqual( dict, type( data_dict ) )
        self.assertEqual( dict, type( data_dict['obj1'] ) )
        self.assertEqual( int, type( data_dict['obj1']['attr1'] ) )

    def test_convert_list(self):
        data_dict = [ {"obj1": { "attr1": "val1" }},
                      {"obj2": { "attr1": "val1" }}
                      ]

        lookup = DictLookup()
        convert( data_dict, lookup )

        self.assertEqual( "[{'obj1': {'attr1': 'val1'}}, {'obj2': {'attr1': 'val1'}}]", str( data_dict ) )

#     def test_convert_01(self):
#         builder = DictBuilder()
#         builder.addPath( ["obj3", "obj1", "attr1"], "val1" )
#         builder.addPath( ["obj3", "obj2", "attr1"], "val2" )
#         data_dict = builder.getData()
#
#         lookup = DictLookup()
#         lookup.addClass( ["obj3"], None )
#         lookup.addClass( ["obj3", "obj1"], None )
#         convert( data_dict, lookup )
#
#         self.assertEqual( "{'obj1': {'attr1': 10}}", str( data_dict ) )
#         self.assertEqual( dict, type( data_dict ) )
#         self.assertEqual( dict, type( data_dict['obj1'] ) )
#         self.assertEqual( int, type( data_dict['obj1']['attr1'] ) )


### ======================================================================


class DictLookupTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_addClass_nested(self):
        lookup = DictLookup()
        lookup.addClass( ["obj3"], int )
        lookup.addClass( ["obj3", "obj1"], str )

        found_type = lookup.lookupType( ["obj3"] )
        self.assertEqual( int, found_type )

        found_type = lookup.lookupType( ["obj3", "obj1"] )
        self.assertEqual( str, found_type )


### ======================================================================


##
class PathsExtractorTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_get_identifiers_obj03(self):
        builder = DictBuilder()
        builder.addPath( ["obj3", "obj1", "attr1"], "val1" )
        builder.addPath( ["obj3", "obj2", "attr1"], "val2" )
        data_dict = builder.getData()

        extractor = PathsExtractor()
        ids = extractor.extract( data_dict )
        self.assertEqual( [ ("obj3",), ("obj3", "obj1",), ("obj3", "obj1", "attr1"), ("obj3", "obj2",),
                            ("obj3", "obj2", "attr1") ], ids )

    def test_getUnique(self):
        builder = DictBuilder()
        builder.addPath( ["obj2", "obj1", "attr1"], "val1" )
        builder.addPath( ["obj3", "obj1", "attr1"], "val2" )
        data_dict = builder.getData()

        extractor = PathsExtractor()
        extractor.extract( data_dict )
        ids = extractor.getUnique()
        self.assertEqual( [ ("obj2",), ("obj2", "obj1",), ('obj3', 'obj1'), ("obj2", "obj1", "attr1"),
                            ("obj3", "obj1", 'attr1'), ("obj3",) ], ids )

    def test_getUnique_list(self):
        data_dict = [
                      {"obj2": {"obj1": { "attr1": "val1" }}},
                      {"obj3": {"obj1": { "attr1": "val1" }}},
                    ]

        extractor = PathsExtractor()
        extractor.extract( data_dict )
        ids = extractor.getUnique()
        self.assertEqual( [ ("obj2",), ("obj2", "obj1",), ("obj3", "obj1",), ('obj2', 'obj1', 'attr1'),
                            ('obj3', 'obj1', 'attr1'), ("obj3",) ], ids )
