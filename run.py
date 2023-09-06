#!/usr/bin/env python3
import sys
from geotaste.imports import PORT
from geotaste.app import run
port = (
    int(sys.argv[1]) 
    if len(sys.argv)>1 and sys.argv[1].isdigit() 
    else PORT
)

debug = len(sys.argv)>2 and sys.argv[2].startswith('-d')

run(port=port, debug=debug)