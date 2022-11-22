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

import os
import sys
import logging


SCRIPT_DIR = os.path.dirname( os.path.abspath(__file__) )


if __name__ == '__main__':
    ## allow having executable script inside package and have proper imports
    ## replace directory of main package (prevent inconsistent imports)
    sys.path[0] = os.path.join( SCRIPT_DIR, os.pardir )


# import pprint
import svgwrite

from xodrpy.utils import move_strip
from xodrpy.types import OpenDRIVE


_LOGGER = logging.getLogger(__name__)


## ===========================================================


def draw_data( opendrive: OpenDRIVE, outsvg_path=None ):
#     width   = "100%"
#     height  = "100%"
#     min_pos = (0, 0)
    
    bbox = opendrive.boundingBox( 3.0 )
    width  = bbox[1][0] - bbox[0][0]
    height = bbox[1][1] - bbox[0][1]
    min_pos = ( -bbox[0][0], -bbox[0][1] )
    
    _LOGGER.info( "data size: %s", (width, height) )
    _LOGGER.info( "data offset: %s", min_pos )
    
    drawer = svgwrite.Drawing( outsvg_path, size=(width, height), profile='tiny' )

    draw_svg( drawer, opendrive, min_pos, "red" )

    drawer.save( pretty=True )


def draw_svg( drawer, opendrive: OpenDRIVE, move_offset=None, line_color="red" ):
    if move_offset is None:
        move_offset = (0.0, 0.0)

#     road = opendrive.roadById( "508" )
#     if road is not None:
    roads_list: List[ Road ] = opendrive.roads()
    for road in roads_list:
#         geom = road.geometryByIndex( 2 )
#         if geom is not None:
        geoms_list: List[ GeometryBase ] = road.geometries()
        for geom in geoms_list:
#             if geom.isLine() is False:
#                 continue
            line_strip = geom.lineApprox( 1.0 )
#             pprint.pprint( line_strip )
            move_strip( line_strip, move_offset )
            params = { "stroke": 'red',
                       "fill": "none"
                       }
            new_line = drawer.polyline( line_strip, **params )
            drawer.add( new_line )


## ===========================================================


def main():
    parser = argparse.ArgumentParser(description='XODR drawer')
    parser.add_argument( '-la', '--logall', action='store_true', help='Log all messages' )
    # pylint: disable=C0301
    parser.add_argument( '--xodr', action='store', required=False, default="", help="Input XODR file" )
    parser.add_argument( '--outsvg', action='store', required=False, default="", help="SVG output" )

    args = parser.parse_args()

    logging.basicConfig()
    if args.logall is True:
        logging.getLogger().setLevel( logging.DEBUG )
    else:
        logging.getLogger().setLevel( logging.INFO )

    opendrive: OpenDRIVE = load( args.xodr )
    if opendrive is None:
        _LOGGER.error( "unable to find file: %s", args.xodr )
        return 1
    
    draw_data( opendrive, outsvg_path=args.outsvg )


if __name__ == '__main__':
    import argparse
    from xodrpy.xodr import load

    main()
