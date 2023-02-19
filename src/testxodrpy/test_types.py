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

import math
from xodrpy.utils import Vector2D, Vector3D
from xodrpy.types import OpenDRIVE, Road, LineGeometry, ArcGeometry,\
    ClothoidGeometry
from xodrpy.xodr import load


##
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


##
class ArcGeometryTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_countercockwise_angle_positive(self):
        start_vector = [ 1, 0 ]
        end_vector   = [ 0, 1 ]
        angle = ArcGeometry.countercockwise_angle( start_vector, end_vector )
        self.assertEqual( 1.5707963267948966, angle )

    def test_countercockwise_angle_negative(self):
        start_vector = [ 1, 0 ]
        end_vector   = [ 0, -1 ]
        angle = ArcGeometry.countercockwise_angle( start_vector, end_vector )
        #TODO: should return negative value
        self.assertEqual( 1.5707963267948966, angle )

    def test_centerPoint_negative(self):
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": "1.57079632679", "@length": "1.57079632679", "@curvature": -1.0 }
        geom = ArcGeometry.create( data_dict )
        center_point = geom.centerPoint()
        self.assertAlmostEqual( Vector2D(x=1.0, y=0.0), center_point, delta=0.001 )

    def test_centerPoint_positive(self):
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": "1.57079632679", "@length": "1.57079632679", "@curvature": 1.0 }
        geom = ArcGeometry.create( data_dict )
        center_point = geom.centerPoint()
        self.assertAlmostEqual( Vector2D(x=-1.0, y=0.0), center_point )

    def test_radiusVector_negative(self):
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": "1.57079632679", "@length": "1.57079632679", "@curvature": -1.0 }
        geom = ArcGeometry.create( data_dict )
        radius_vec = geom.radiusVector()
        self.assertAlmostEqual( Vector2D(x=-1.0, y=0.0), radius_vec )
        radius_vec = geom.radiusVector( 1.57079632679 )
        self.assertAlmostEqual( Vector2D(x=0.0, y=1.0), radius_vec )

    def test_radiusVector_positive(self):
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": "1.57079632679", "@length": "1.57079632679", "@curvature": 1.0 }
        geom = ArcGeometry.create( data_dict )
        radius_vec = geom.radiusVector()
        self.assertAlmostEqual( Vector2D(x=1.0, y=0.0), radius_vec )
        radius_vec = geom.radiusVector( 1.57079632679 )
        self.assertAlmostEqual( Vector2D(x=0.0, y=1.0), radius_vec )

    def test_positionByOffset_curv_neg(self):
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": "1.57079632679", "@length": "1.57079632679", "@curvature": -1.0 }
        geom = ArcGeometry.create( data_dict )

        position_start = geom.positionByOffset( 0.0 )
        self.assertAlmostEqual( Vector2D(x=0.0, y=0.0), position_start )

        position_end = geom.positionByOffset( 1.57079632679 )
        self.assertAlmostEqual( Vector2D(x=1.0, y=1.0), position_end )

    def test_positionByOffset_curv_pos(self):
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": "1.57079632679", "@length": "1.57079632679", "@curvature": 1.0 }
        geom = ArcGeometry.create( data_dict )

        position_start = geom.positionByOffset( 0.0 )
        self.assertAlmostEqual( Vector2D(x=0.0, y=0.0), position_start )

        position_end = geom.positionByOffset( 1.57079632679 )
        self.assertAlmostEqual( Vector2D(x=-1.0, y=1.0), position_end )

    def test_heading_positive(self):
        ## full circle with radius 1.0
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": math.pi / 2.0, "@length": 2.0 * math.pi, "@curvature": 1.0 }
        geom = ArcGeometry.create( data_dict )
        
        heading = geom.headingByOffsetRaw( 0.0 )
        self.assertEqual( math.pi / 2.0, heading )

        heading = geom.headingByOffsetRaw( math.pi / 2.0 )
        self.assertEqual( math.pi, heading )

    def test_heading_negative(self):
        ## full circle with radius 1.0
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": math.pi / 2.0, "@length": 2.0 * math.pi, "@curvature": -1.0 }
        geom = ArcGeometry.create( data_dict )
        
        heading = geom.headingByOffsetRaw( 0.0 )
        self.assertEqual( math.pi / 2.0, heading )

        heading = geom.headingByOffsetRaw( math.pi / 2.0 )
        self.assertEqual( 0.0, heading )

    def test_boundingBox(self):
        data_dict = { "@s": "0.0", "@x": "0.0", "@y": "0.0", "@hdg": "0.0", "@length": "5.0", "@curvature": 1.0 }
        geom = ArcGeometry.create( data_dict )
 
        bbox = geom.boundingBox()
        self.assertEqual( ((-0.9996902853162233, 0.0), (0.999965585678249, 1.9998623450816866)), bbox )


##
class ClothoidGeometryTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_positionByOffsetRaw_00(self):
        data = { "@x": "0.0",
                 "@y": "0.0",
                 "@hdg": "0.0",
                 "@length": "10.0",
                 "@curvStart": "0.0",
                 "@curvEnd": "0.2"
            }
        geom = ClothoidGeometry()
        geom.initialize( data )
        
        start_point = geom.positionByOffsetRaw(  0.0 )
        end_point   = geom.positionByOffsetRaw( 10.0 )
        
        self.assertAlmostEqual( Vector2D(x=0.0, y=0.0), start_point )
        self.assertAlmostEqual( Vector2D(x=9.04524237900272, y=3.1026830172338116), end_point )

    def test_positionByOffsetRaw_01(self):
        data = { "@x": "0.0",
                 "@y": "0.0",
                 "@hdg": "0.0",
                 "@length": "10.0",
                 "@curvStart": "0.2",
                 "@curvEnd": "0.4"
            }
        geom = ClothoidGeometry()
        geom.initialize( data )
        
        start_point = geom.positionByOffsetRaw(  0.0 )
        end_point   = geom.positionByOffsetRaw( 10.0 )
        
        self.assertAlmostEqual( Vector2D(x=0.0, y=0.0), start_point )
        self.assertAlmostEqual( Vector2D(x=1.7672645240329674, y=6.400083840459464), end_point )


##
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

    def test_position(self):
        input_path = get_data_path( "town1_road1_simple.xodr" )
        opendrive: OpenDRIVE = load( input_path )
        self.assertTrue( opendrive is not None )
        road: Road = opendrive.roadById("0")
        self.assertTrue( road is not None )
        
        possition = road.position( 0.0, 0.0, 0.0 )
        self.assertEqual( Vector3D(10.0, 10.0, 0.0), possition )
        
        possition = road.position( 5.0, 2.0, 1.0 )
        self.assertEqual( Vector3D(15.0, 12.0, 1.0), possition )

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
        self.assertEqual( ((-197.22099855593865, -153.31995050960072, 0.0),
                           (-197.14107134062706, 154.3200554954873, 0.0)), bbox )
