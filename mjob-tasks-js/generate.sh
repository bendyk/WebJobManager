#!/bin/sh

emcc -O3 --memory-init-file 0 -s TOTAL_MEMORY=48MB ../mjob-tasks-cpp/mjob1.cpp -o mjob1.js
emcc -O3 --memory-init-file 0 -s TOTAL_MEMORY=48MB ../mjob-tasks-cpp/mjob2.cpp -o mjob2.js
emcc -O3 --memory-init-file 0 -s TOTAL_MEMORY=48MB ../mjob-tasks-cpp/mjob4.cpp -o mjob4.js

