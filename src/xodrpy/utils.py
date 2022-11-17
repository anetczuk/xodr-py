#!/usr/bin/env python3
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

# pylint: disable=C0413

import os
import logging
from dataclasses import dataclass

import numpy as np
# import scipy.spatial.transform as trans


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname( os.path.abspath(__file__) )


## =============================================================


@dataclass
class Vector2D():
    x: float
    y: float

    def __getitem__(self, index):
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError( f"invalid index: {index}" )

    def __add__(self, U):
        return Vector2D( self.x + U.x, self.y + U.y )

    def rotateXY( self, angle_rad ):
        # angle_rad = -angle_rad              ## rotate counter-clockwise direction
        vec = [ self.x, self.y ]
        cos_val, sin_val = np.cos(angle_rad), np.sin(angle_rad)
        rot = np.array([ [cos_val, -sin_val], [sin_val, cos_val] ])
        rotated = np.dot( rot, vec )
        self.x = rotated[0]
        self.y = rotated[1]

#         rotation_axis   = np.array([1, 0])
#         rotation_vector = angle_rad * rotation_axis
#         rotation = trans.Rotation.from_rotvec(rotation_vector)
#         rotated_vec = rotation.apply(vec)
#         self.x = rotated_vec[0]
#         self.y = rotated_vec[0]


@dataclass
class Vector3D():
    x: float
    y: float
    z: float


## =============================================================


def get_min_point( pointA: tuple, pointB: tuple ):
    return [  get_min_val( pointA[0], pointB[0] ),
              get_min_val( pointA[1], pointB[1] ),
              get_min_val( pointA[2], pointB[2] )
              ]


def get_max_point( pointA: tuple, pointB: tuple ):
    return [  get_max_val( pointA[0], pointB[0] ),
              get_max_val( pointA[1], pointB[1] ),
              get_max_val( pointA[2], pointB[2] )
              ]


def get_min_point2d( pointA: tuple, pointB: tuple ):
    return [  get_min_val( pointA[0], pointB[0] ),
              get_min_val( pointA[1], pointB[1] )
              ]


def get_max_point2d( pointA: tuple, pointB: tuple ):
    return [  get_max_val( pointA[0], pointB[0] ),
              get_max_val( pointA[1], pointB[1] )
              ]


## ================================================================


def get_min_val(valueA, valueB):
    if valueA is None:
        return valueB
    if valueB is None:
        return valueA
    return min( valueA, valueB )


def get_max_val(valueA, valueB):
    if valueA is None:
        return valueB
    if valueB is None:
        return valueA
    return max( valueA, valueB )
