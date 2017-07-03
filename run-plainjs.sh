#!/bin/sh

cp benchtasks-input/small.dat plainjs.in

# start webserver and check results
python3 main.py && ls -l plainjs.out

# remove all created files
rm plainjs.in plainjs.out
