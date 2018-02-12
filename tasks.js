var Module        = {};
var request_files = {};
var cur_request   = {};
var request_queue = [];
var upload_queue  = [];
var wf_path       = "";
var task_id       = "";
var std_out       = "#STDOUT\n";
var std_err       = "#STDERR\n";

// timestamps:
var ts_prerun_start = 0;
var ts_prerun_stop = 0;
var ts_mainrun_start = 0;
var ts_mainrun_stop = 0;
var ts_postrun_start = 0;
var ts_postrun_stop = 0;
// time durations
var duration_prerun = 0;
var duration_mainrun = 0;
var duration_postrun = 0;


/*function pre___syscall145(which, varargs){

  SYSCALLS.varargs = varargs;
  var stream       = SYSCALLS.getStreamFromFD();
  var iov          = SYSCALLS.get();
  var iovcnt       = SYSCALLS.get();
  var request_len  = 0;
  var ret;


  if(!("virtual" in stream.node)){
    Module.printErr("reading from fs");
    //ret = ___syscall145(which, varargs);
  }
  else{  
    Module.printErr("reading from server");
    if(stream.node.usedBytes >= stream.node.maxBytes) return 0;
    ws.onmessage = function(msg){
      var a = [];
      for(var x in msg) a.push(x);
      console.log(a);
      Module.printErr("received from server");
      //written = FS.write(stream, new Uint8Array(msg.data), 0, msg.data.byteLength, stream.node.usedBytes);
      written = stream.stream_ops.write(stream, new Uint8Array(msg.data), 0, msg.data.byteLength, stream.node.usedBytes);
      Module.printErr("written:" + msg.data.byteLength);
      Module.printErr("position:" + stream.position);
      Module.printErr("used_bytes:" + stream.node.usedBytes);
      Module.printErr("max_bytes:" + stream.node.maxBytes);
      //bytes_read = ___syscall145(which, varargs); 
      setValue(___async_retval, msg.data.byteLength, 'i32');
      Module.printErr('syscall! ' + [145, 'done']);
      ws.onmessage = function(){return;};
      Module["_emscripten_async_resume"]();
    };


    for(var x = 0; x < iovcnt; x++){ 
      request_len += HEAP32[(((iov)+(x*8+4))>>2)];
    }

    request_len = (stream.position + request_len) - stream.node.usedBytes;
    if(request_len < 1){
      //ret = ___syscall145(which, varargs);
    }
    else{
      sendbuf    = new Uint8Array(12);
      sendbuf[3] = 14; ////'\u000e'

      tmp    = new Uint32Array(sendbuf.buffer, 4);
      tmp[0] = stream.node.id;
      tmp[1] = request_len;

      Module.printErr("request length: " + request_len);
      Module.printErr(sendbuf.buffer.slice(3));
      ws.send(sendbuf.buffer.slice(3));
      Module.ccall("emscripten_sleep", null, ['number'], [10000]);
      Module.printErr('syscall! ' + [145, 'pending...']);
      ret = 1024;
    }
  }
  //return(ret); 
}
*/
/*
function pre___syscall5(which, varargs){
  var fd           = -2;
  SYSCALLS.varargs = varargs;
  var file_path    = SYSCALLS.getStr();
  var flags        = SYSCALLS.get();
  var mode         = SYSCALLS.get();

  if(!FS.analyzePath(file_path).exists){
      //CREATE FILE OR LOAD FROM DB IF NOT EXISTS
      if(FS.analyzePath(storage_path).exists){
        var data = FS.readFile(storage_path, {encoding:'binary', flags:'r'});
        FS.writeFile(file_path, new Uint8Array(data), {encoding:'binary'});
        Module.printErr("load file from DB: " + file_path);
      }
      else{
        new_node          = FS.createFile("/", file_path, {}, true, true);
        new_node.virtual  = true;
        new_node.maxBytes = 0;     
      }
  }
 
  var lookup = FS.lookupPath(file_path);

  if('virtual' in lookup.node){
    //READ FROM SERVER
    Module.printErr("request file open from server: " + file_path);

    ws.onmessage = function(msg){
      lookup.node.maxBytes = new Uint32Array(msg.data)[0];

      var new_fd = ___syscall5(which, varargs);
      setValue(___async_retval, new_fd, 'i32');
      Module.printErr('syscall! ' + [5, 'done']);
      ws.onmessage = function(){return;};
      Module["_emscripten_async_resume"]();
    };
    
    tmp = new Uint32Array([lookup.node.id]);
    ws.send('\u000d'+ String.fromCharCode(tmp[0], tmp[1], tmp[2], tmp[3]) + file_path);
    Module.ccall("emscripten_sleep", null, ['number'], [10000]);
    Module.printErr('syscall! ' + [5, 'pending...']);
    fd = -2; 
  }
  else{
    //READ LOCAL
    Module.printErr("REEEEADLOCAL");
    fd = ___syscall5(which, varargs);
  }
  
  return(fd);
}*/

function pre___syscall5(which, varargs){
  var fd           = -2;
  SYSCALLS.varargs = varargs;
  var file_path    = SYSCALLS.getStr();
  var flags        = SYSCALLS.get();
  var mode         = SYSCALLS.get();

  if(!FS.analyzePath(file_path).exists){
    var receive_interval = setInterval(function(){
      if(FS.analyzePath(file_path).exists){
        fd = ___syscall5(which, varargs);
        setValue(___async_retval, fd, 'i32');
        Module.printErr('syscall! ' + [5, 'done']);
        clearInterval(receive_interval);
        Module["_emscripten_async_resume"]();
      }
      else{
        Module.printErr('waiting for file' + file_path);
        Module.printErr('syscall! ' + [5, 'pending...']);
      }
    }, 2000);
    Module.ccall("emscripten_sleep", null, ['number'], [100000]);
    Module.printErr('syscall! ' + [5, 'pending...']);
    fd = -2;   
  }
  else{
    fd = ___syscall5(which, varargs);
  }

  return(fd);
}


function load_binary(info, callback){
  info['env']['___syscall5'] = pre___syscall5;

  ws.onmessage = function(msg){
                   var data = new Uint8Array(msg.data);
                   console.log("wasm file loaded: " + data.length + " bytes");
                    
                   if(WebAssembly.validate(data)){
                     console.log("wasm validation correct");
                   } else{
                     console.log("wasm validation problem");
                   }
                   WebAssembly.instantiate(data, info).then(function(output){
                     callback(output.instance);
                   }).catch(function(reason){
                     console.log("couldn't instantiate wasm");
                     Module['printErr']("could not instantiate wasm:" + reason);
                     Module['quit'](1, reason);
                   });
                                                                
                 }; 
  console.log("\nWEBASSEMBLY");
  ws.send('\u000b');

  return {};
}

function load_from_indexedDB(file){
  var success      = false;
  var storage_path = "/storage/" + wf_path + "/" + file;

  if(FS.analyzePath(storage_path).exists){
    console.log("Load file from DB: " + file);
    var data = FS.readFile(storage_path, {encoding:'binary', flags:'r'});
    FS.writeFile(file, new Uint8Array(data), {encoding:'binary'}); 
    success = true;
  }

  return success;
}



function preRun_finished() {
    ts_prerun_stop  = Date.now();
    // inform about starting job execution
    if (typeof(setExecutionState) == "undefined")
		self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_RUN"});
	else
		setExecutionState(TXT_EXEC_RUN);

    if (typeof(setJobAssignment) == "undefined")
		self.postMessage({"cmd": "setJobAssignment", "arg": "'" + Module["thisProgram"] + "'"});
	else
		setJobAssignment(Module["thisProgram"]);

    console.log("\nRUNNING... \n" + Module['thisProgram']);

    //ws.onmessage = function(msg) {};
    
    ts_mainrun_start = Date.now();
    Module['removeRunDependency']('indexed_DB');    
}


function save_received_file(msg){
  var id   = new Uint32Array(msg.data.slice(0,4))[0];
  var path = request_files[id];
  FS.writeFile(path, new Uint8Array(msg.data, 4), {encoding: 'binary'}); 
  console.log("received file: " + path);
  delete request_files[id];
  return id;
}

function send_request(id, file){
  ws.send('\u0001' + String.fromCharCode(id[0], id[1], id[2], id[3]) + file); 
}

function receive_asyncload(msg){
  save_received_file(msg);
}
function receive_preload(msg){
  var id = save_received_file(msg);
  Module['removeRunDependency'](id);    
  if(runDependencies == 1) preRun_finished();
}

function asyncload_file(id, file){
  console.log("load file async: " + file);
  send_request(new Uint32Array([id]), file);
}

function preload_file(id, file){
  console.log("preload file: " + file);
  var new_id = getUniqueRunDependency(id);
  delete request_files[id];
  request_files[new_id] = file;
  send_request(new Uint32Array([new_id]), file);
  Module['addRunDependency'](new_id);
}

function load_in_files(){
  console.log("\nPRERUN...");
  Module['env']
  if (typeof(setExecutionState) == "undefined")
    self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_RECV"});
  else
	setExecutionState(TXT_EXEC_RECV);

  ts_prerun_start = Date.now();

  /*FS.init(input = function(){
            return null;
          },
          output = function(msg){
            std_out = std_out.concat(String.fromCharCode(msg));
          }, 
          error  = function(msg){
            std_err = std_err.concat(String.fromCharCode(msg));
          }
  );*/

  var receive_file; 
  var load_file;
  
  %(inputs)s
 
  Module['addRunDependency']('indexed_DB');

  FS.mkdir("/storage");
  FS.mount(IDBFS, {}, '/storage');
  FS.syncfs(true, function(err){

    ws.onmessage = receive_file;

    for(var id in request_files){
      if(!load_from_indexedDB(request_files[id])){
        load_file(id, request_files[id]);
      }
    };
    
    if(runDependencies == 1) preRun_finished();
  });
}


function calc_send_durations() {
//console.log("prerun: " + ts_prerun_start + " " + ts_prerun_stop);
//console.log("mainrun: " + ts_mainrun_start + " " + ts_mainrun_stop);
//console.log("postrun: " + ts_postrun_start + " " + ts_postrun_stop);

  duration_prerun = ts_prerun_stop - ts_prerun_start;
  duration_mainrun = ts_mainrun_stop - ts_mainrun_start;
  duration_postrun = ts_postrun_stop - ts_postrun_start;

  ws.send('\u0005' + duration_prerun);
  ws.send('\u0006' + duration_mainrun);
  ws.send('\u0007' + duration_postrun);

  // update document about runtimes
  if (typeof(storeJobInHistory) == "undefined")
    self.postMessage({"cmd": "storeJobInHistory", "arg": "'"+Module["thisProgram"]+"', "+ duration_prerun.toString()+", "+duration_mainrun.toString()+", " + duration_postrun.toString()+", " + (duration_prerun+duration_mainrun+duration_postrun).toString()});
  else
    storeJobInHistory(Module["thisProgram"], duration_prerun, duration_mainrun, duration_postrun, duration_prerun+duration_mainrun+duration_postrun);
}


function store_file(path, data){
  //store file in indexed db
  tmp_path     = "/storage/" + wf_path + "/" + task_id + "/" + path;
  storage_path = tmp_path.slice(0, tmp_path.lastIndexOf("/"));
  f_name       = tmp_path.slice(tmp_path.lastIndexOf("/") + 1);
  console.log("store file: " + tmp_path);
  
  if(!FS.analyzePath(storage_path).exists){
    FS.createPath("/", storage_path);
  }

  FS.writeFile(storage_path + "/" + f_name, new Uint8Array(data), {encoding:'binary'}); 
}


function send_file(path, data){
  //send file to server
  console.log("send file: " + path);
  ws.send('\u0002');
  ws.send(data);
  ws.send('\u0008');  
}


function upload_next_file(){
  if(upload_queue.length == 0){
    FS.syncfs(false, all_files_uploaded);
  }
  else{
    cur_request = upload_queue.shift();
    ws.onmessage = function (msg){
                     var file;
                     var tmp;

                     if(FS.analyzePath(cur_request['file']).exists)
                       file = FS.readFile(cur_request['file'], {encoding:'binary', flags:'r'});
                     else
                       file = new ArrayBuffer(1);

                     tmp = new Uint8Array(msg.data);

                     if(String.fromCharCode(tmp[0]) == '\u0009'){
                       store_file(cur_request['file'], file);
                       if((cur_request['file'] == "/std.err") | (cur_request['file'] == "/std.out")){
                         send_file(cur_request['file'], file);
                       }
                     }
                     else{
                       send_file(cur_request['file'], file);
                     }
                     upload_next_file();
                   };
    size = 0;
    ws.send('\u0003' + cur_request['file'] + ":" + size.toString());
  } 
}


function all_files_uploaded(){
  ws.onmessage = recv_executable;
  
  ts_postrun_stop = Date.now();
  calc_send_durations();

  console.log("\nFINISHED");
  console.log("-------------------");
  if (typeof(setExecutionState) == "undefined")
    self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_FINISHED"});
  else
	setExecutionState(TXT_EXEC_FINISHED);

  if (typeof(setJobAssignment) == "undefined")
	self.postMessage({"cmd": "setJobAssignment", "arg": "TXT_NO_JOB"});
  else
	setJobAssignment(TXT_NO_JOB);
//  exitRuntime();
  request_executable();
}

function upload_out_files(){

  if(Object.keys(request_files).length > 0){
    setTimeout(upload_out_files, 500);
    return;
  } 

  ts_mainrun_stop = Date.now();

  console.log("\nPOSTRUN...");
//  Module["noExitRuntime"] = true;
  if (typeof(setExecutionState) == "undefined")
    self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_SEND"});
  else
	setExecutionState(TXT_EXEC_SEND);

  ts_postrun_start = Date.now();

  %(outputs)s
 
  upload_next_file();
  return;
}


function onAbort(){
  console.log("\nERROR...");
  console.log("An errror ocurred...");
  upload_out_files();
}


Module['preRun']          = load_in_files;
Module['postRun']         = upload_out_files;
Module['onAbort']         = onAbort;
Module['instantiateWasm'] = load_binary;
