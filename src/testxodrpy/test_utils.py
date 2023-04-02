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

from xodrpy.utils import Vector2D, Vector3D


##
class Vector2DTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_rotate90(self):
        vec = Vector2D( 1, 1 )
        vec.rotate90()
        self.assertAlmostEqual( Vector2D(x=-1.0, y=1.0), vec )

    def test_rotate_90(self):
        vec = Vector2D( 1, 1 )
        vec.rotate_90()
        self.assertAlmostEqual( Vector2D(x=1.0, y=-1.0), vec )

    def test_rotateXY_positive(self):
        vec = Vector2D( 1, 0 )
        vec.rotateXY( 1.57079632679 )
        self.assertAlmostEqual( Vector2D(x=0.0, y=1.0), vec )

    def test_rotateXY_negative(self):
        vec = Vector2D( 1, 0 )
        vec.rotateXY( -1.57079632679 )
        self.assertAlmostEqual( Vector2D(x=0.0, y=-1.0), vec )


##
class Vector3DTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_rotateXY90(self):
        vec = Vector3D( 1, 1, 1 )
        vec.rotateXY90()
        self.assertAlmostEqual( Vector3D(x=-1.0, y=1.0, z=1.0), vec )

    def test_rotateXY_90(self):
        vec = Vector3D( 1, 1, 1 )
        vec.rotateXY_90()
        self.assertAlmostEqual( Vector3D(x=1.0, y=-1.0, z=1.0), vec )

    def test_rotateXY_positive(self):
        vec = Vector3D( 1, 0, 1 )
        vec.rotateXY( 1.57079632679 )
        self.assertAlmostEqual( Vector3D(x=0.0, y=1.0, z=1.0), vec )

    def test_rotateXY_negative(self):
        vec = Vector3D( 1, 0, 1 )
        vec.rotateXY( -1.57079632679 )
        self.assertAlmostEqual( Vector3D(x=0.0, y=-1.0, z=1.0), vec )
