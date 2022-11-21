#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


TOOL_SRC_DIR="$SCRIPT_DIR/../src"

XODR_PATH="$TOOL_SRC_DIR/testxodrpy/data/town1.xodr"


$TOOL_SRC_DIR/xodrpy/draw.py --xodr "$XODR_PATH" --outsvg "$SCRIPT_DIR/draw/town1.svg"


convert -density 400 -flip "$SCRIPT_DIR/draw/town1.svg" "$SCRIPT_DIR/draw/town1.png"
