#include <stdio.h>
#include <emscripten/emscripten.h>

#ifdef __cplusplus
extern "C" {
#endif
extern void sow1();
#ifdef __cplusplus
}
#endif

int main(){
  printf("MAIN WASM\n");
  printf("CALL SOW\n");
  sow1();
  printf("SOW CALLED\n");
  emscripten_sleep(10000);
  printf("RETURNED TO WASM\n");
  return 0;
}

//EMSCRIPTEN_KEEPALIVE void go_on(){
//  receive_on_websocket();
//  return;
//}
