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
from testxodrpy import get_data_path

from xodrpy.xodr import load, OpenDRIVE, Road, LineGeometry
from xodrpy.utils import Vector2D


class LineGeometryTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_positionByOffset(self):
        data_dict = { "@s": "0.0", "@x": "10.0", "@y": "0.0", "@hdg": "1.57079632679", "@length": "5.0" }
        geom = LineGeometry.create( data_dict )
        position = geom.positionByOffset( 10.0 )
        self.assertEqual( Vector2D(x=10.000000000048965, y=10.0), position )


class RoadTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_elevationValue(self):
        input_path = get_data_path( "town1_road1.xodr" )
        opendrive: OpenDRIVE = load( input_path )
        self.assertTrue( opendrive is not None )
        road: Road = opendrive.roadById("0")
        self.assertTrue( road is not None )

        elevation_value = road.elevationValue( 10.0 )
        self.assertEqual( 0.0, elevation_value )

    def test_boundingBox_simple(self):
        input_path = get_data_path( "town1_road1_simple.xodr" )
        opendrive: OpenDRIVE = load( input_path )
        self.assertTrue( opendrive is not None )
        road: Road = opendrive.roadById("0")
        self.assertTrue( road is not None )

        bbox = road.boundingBox()
        self.assertEqual( ((10.0, 10.0, 0.0), (30.0, 10.0, 0.0)), bbox )

    def test_boundingBox(self):
        input_path = get_data_path( "town1_road1.xodr" )
        opendrive: OpenDRIVE = load( input_path )
        self.assertTrue( opendrive is not None )
        road: Road = opendrive.roadById("0")
        self.assertTrue( road is not None )

        bbox = road.boundingBox()
        self.assertEqual( ((-197.22096263420357, -153.31995050960072, 0.0),
                           (-197.14107134062706, 154.3200554954873, 0.0)), bbox )
