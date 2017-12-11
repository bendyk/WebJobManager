
mergeInto(LibraryManager.library, {
  sow1: function(){
    sow2();
  },
  receive_on_websocket: function(){
    console.log("something received on websocket");
    _emscripten_async_resume();
  },
});

