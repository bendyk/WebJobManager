#!/bin/sh

# start webserver and check results
python3 main.py && ( wc -l data.mrge; head -5 data.mrge; echo "..."; tail -5 data.mrge )

# check result
#wc -l data.mrge
#head -5 data.mrge
#tail -5 data.mrge

# remove all created files
rm data.*
