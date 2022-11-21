#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


TOOL_SRC_DIR="$SCRIPT_DIR/../src"


for xodr_file in $SCRIPT_DIR/samples/*.xodr; do     ## whitespace-safe but not recursive
    file_name=$(basename $xodr_file)
    echo "drawing $file_name"
    SVG_PATH="$SCRIPT_DIR/draw/${file_name}.svg"
    PNG_PATH="$SCRIPT_DIR/draw/${file_name}.png"
    
    $TOOL_SRC_DIR/xodrpy/draw.py --xodr "$xodr_file" --outsvg "$SVG_PATH"
    convert -density 200 -flip "$SVG_PATH" "$PNG_PATH"
    #convert -density 400 -flip "$SVG_PATH" "$PNG_PATH"
    
    ## remove metadata
    mogrify -strip "$PNG_PATH"
done
