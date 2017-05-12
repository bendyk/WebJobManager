#!/bin/bash

# optimization O3 produces incorrect result
FLAGS='-O3 --memory-init-file 0 -s TOTAL_MEMORY=48MB'

emcc $FLAGS ../mjob-tasks-cpp/mjob1.cpp -o mjob1.js
emcc $FLAGS ../mjob-tasks-cpp/mjob2.cpp -o mjob2.js
emcc $FLAGS ../mjob-tasks-cpp/mjob4.cpp -o mjob4.js

