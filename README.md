# WebJobManager

Insert your javascript jobs generated with emscripten in the main.py and run it with python3. 
Access the JobServer via localhost:8888 to run your jobs in your Browser.

Creating a javascript job:
- Download latest emscripten version from http://kripken.github.io/emscripten-site/docs/getting_started/downloads.html#sdk-download-and-install and follow the install instructions 
- cd to EMSCRIPTEN/emscripten/VERSION/
- cross-compile your CPP source code with emcc
  ./emcc -O3 --memory-init-file 0 -s TOTAL_MEMORY=33554432 YOUR_CPP_FILE.cpp






