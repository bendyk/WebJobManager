a WebJobManager

Insert your javascript jobs generated with emscripten in the main.py and run it with python3. 
Access the JobServer via localhost:8888 to run your jobs in your Browser.

Creating a javascript job:
- Download latest emscripten version from http://kripken.github.io/emscripten-site/docs/getting_started/downloads.html#sdk-download-and-install and follow the install instructions 
- cd to EMSCRIPTEN/emscripten/VERSION/
- cross-compile your CPP source code with emcc
  emcc -o test3.js main3.c -s WASM=1 -s FORCE_FILESYSTEM=1 -s ASYNCIFY=1 -s DEFAULT_LIBRARY_FUNCS_TO_INCLUDE='["memcpy", "emscripten_sleep", "memset", "malloc", "free"]' -s ASYNCIFY_FUNCTIONS='["__syscall_ret", "emscripten_sleep", "emscripten_wget", "emscripten_yield"]' -Werror -s NO_EXIT_RUNTIME=1






