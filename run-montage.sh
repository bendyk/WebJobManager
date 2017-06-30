#!/bin/sh

# copy input files for workflow execution
cp montage-input/2mass-atlas-990502s-j1420186.fits .
cp montage-input/2mass-atlas-990502s-j1420198.fits .
cp montage-input/2mass-atlas-990502s-j1430080.fits .
cp montage-input/2mass-atlas-990502s-j1430092.fits .
cp montage-input/big_region.hdr .
cp montage-input/cimages.tbl .
cp montage-input/pimages.tbl .
cp montage-input/statfile.tbl .

python3 main.py

# remove input files
rm 2mass-atlas-990502s-j1420186.fits
rm 2mass-atlas-990502s-j1420198.fits
rm 2mass-atlas-990502s-j1430080.fits
rm 2mass-atlas-990502s-j1430092.fits
rm big_region.hdr
rm cimages.tbl
rm pimages.tbl
rm statfile.tbl

# clean up temporary files
rm p2mass-atlas-*
rm diff.*
rm fit.*
rm fits.tbl
rm corrections.tbl
rm c2mass-atlas-*
rm newcimages.tbl
rm mosaic.fits mosaic_area.fits
rm shrunken.fits


