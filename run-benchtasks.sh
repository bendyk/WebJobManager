#!/bin/sh

cp benchtasks-input/nothing.dat .

# start webserver and check results
python3 main.py && ( cat out.dat; echo "" )

# remove all created files
rm nothing.dat out.dat
