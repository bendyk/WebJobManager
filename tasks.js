var Module         = {};
var request_files  = {};
var upload_files   = [];
var uploading_file = false;
var cur_request    = {};
var request_queue  = [];
var upload_queue   = [];
var wf_path        = "";
var task_id        = "";
var std_out        = "#STDOUT\n";
var std_err        = "#STDERR\n";

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

function trimPath(path){
  path = path.replace(/\.\//g, "/");
  path = path.replace(/\/{2,}/g , "/"); 
  if(path[0] == "/") path = path.slice(1);
  return path;
}

function indexOfFile(file_path){
  for(var id in request_files){
    if(file_path == request_files[id]['f_path']){
      return id;
    }      
  }
  return -1;
}

//syscall open
function pre___syscall5(which, varargs){
  var fd           = -2;
  SYSCALLS.varargs = varargs;
  var file_path    = SYSCALLS.getStr();
  var flags        = SYSCALLS.get();
  var mode         = SYSCALLS.get();

  if(!FS.analyzePath(file_path).exists && (indexOfFile(trimPath(file_path)) >= 0)){
    var receive_interval = setInterval(function(){
      if(FS.analyzePath(file_path).exists){
        fd = ___syscall5(which, varargs);
        setValue(___async_retval, fd, 'i32');
        clearInterval(receive_interval);
        Module["_emscripten_async_resume"]();
      }
      else{
        console.log('waiting for file' + file_path + " ...");
      }
      return 0;
    }, 100);
    Module.ccall("emscripten_sleep", null, ['number'], [100000]);
    fd = -2;   
  }
  else{
    console.log("direct open: " + file_path);
    console.log(request_files);
    fd = ___syscall5(which, varargs);
  }

  return(fd);
}


//syscall close
function pre___syscall6(which, varargs){
  SYSCALLS.varargs = varargs;
  var stream = SYSCALLS.getStreamFromFD();
  var path   = stream.path;
  var size   = stream.node.usedBytes;
  var ret    = ___syscall6(which, varargs);


  var files = upload_files.slice();
  for(var x = 0; x < files.length; x++){files[x] = trimPath(files[x])};
  var index = files.indexOf(trimPath(path));
  
  ws.onmessage = function (msg){
    store_or_send_file(path, msg);
    upload_files.splice(index, 1);
    uploading_file = false;
    setValue(___async_retval, ret, 'i32');
    Module["_emscripten_async_resume"]();
  };

  if(index >= 0){
    ws.send('\u0003' + path + ":" + size.toString()); 
    uploading_file = true;
    Module.ccall("emscripten_sleep", null, ['number'], [100000]);
  }
  return ret;
}


function load_binary(info, callback){
  
  if(typeof(_emscripten_sleep) == "function"){
      info['env']['___syscall5'] = pre___syscall5;
      info['env']['___syscall6'] = pre___syscall6;
  }

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
  var storage_path = "/storage/" + wf_path + "/" + file['origin'];

  if(FS.analyzePath(storage_path).exists){
    console.log("Load file from DB: " + file['origin']);
    var data = FS.readFile(storage_path, {encoding:'binary', flags:'r'});
    FS.writeFile(file['f_path'], new Uint8Array(data), {encoding:'binary'}); 
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
  var path = request_files[id]['f_path'];
  FS.writeFile(path, new Uint8Array(msg.data, 4), {encoding: 'binary'}); 
  console.log("received file: " + path);
  delete request_files[id];
  return id;
}

function send_request(id, file_path){
  id_string = String.fromCharCode(id[0], id[1], id[2], id[3]);
  ws.send('\u0001' + id_string + file_path); 
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
  console.log("load file async: " + file['f_path']);
  send_request(new Uint32Array([id]), file['origin']);
}

function preload_file(id, file){
  console.log("preload file: " + file['f_path']);
  var new_id = getUniqueRunDependency(id);
  delete request_files[id];
  request_files[new_id] = file;
  send_request(new Uint32Array([new_id]), file['origin']);
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

  FS.init(input = function(){
            return null;
          },
          output = function(msg){
            std_out = std_out.concat(String.fromCharCode(msg));
          }, 
          error  = function(msg){
            std_err = std_err.concat(String.fromCharCode(msg));
          }
  );

  var receive_file = typeof(_emscripten_sleep) == "function" ? receive_asyncload : receive_preload; 
  var load_file    = typeof(_emscripten_sleep) == "function" ? asyncload_file    : preload_file;
  
  %(inputs)s
  %(outputs)s

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
  
  if(!FS.analyzePath(storage_path).exists) FS.createPath("/", storage_path);
  
  FS.writeFile(storage_path + "/" + f_name, new Uint8Array(data), {encoding:'binary'}); 
}

function send_file(path, data){
  //send file to server
  console.log("send file: " + path);
  ws.send('\u0002');
  ws.send(data);
  ws.send('\u0008');  
}


function store_or_send_file(path, msg){

    try{
      var buffer  = FS.readFile(path, {encoding:'binary', flags:'r'});    
      var op_code = String.fromCharCode((new Uint8Array(msg.data))[0]);

      if(op_code == '\u0009'){
        store_file(path, buffer);
      }
      else{
        send_file(path, buffer);
      }
    }
    catch(error){
      console.log("WARNING: "+ path +" not found");
      console.log(FS.readdir("/"));
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


function check_for_exit(){
  if(uploading_file){
    setTimeout(check_for_exit, 100);
  }
  else{
    upload_std_and_finish();
  }
}


function upload_std_and_finish(){
  console.log("\nPOSTRUN...");
  ws.onmessage = function(){};

  var buf1 = new TextEncoder("utf-8").encode(std_out);
  var buf2 = new TextEncoder("utf-8").encode(std_err);

  ws.send('\u0003' + "/std.out" + ":" + buf1.length.toString());
  store_file("/std.out", buf1);
  send_file("/std.out", buf1);

  ws.send('\u0003' + "/std.err" + ":" + buf2.length.toString());
  store_file("/std.err", buf2);
  send_file("/std.err", buf2);

  finish();
}

function upload_run(){
  if(upload_files.length > 0){    
    uploading_file = true;
    f = upload_files.shift();
    ws.send('\u0003' + f + ":1"); // maybe change this to actual filesize

    ws.onmessage = function(msg){
      store_or_send_file(f, msg);
      uploading_file = false;
      upload_run();
    }        
  }
}

function post_run(){
  if(Object.keys(request_files).length > 0){
    setTimeout(post_run, 100);
  }
  else{
    upload_run();
    check_for_exit();
  }
}

function finish(){

  ts_mainrun_stop = Date.now();

//  Module["noExitRuntime"] = true;
  if (typeof(setExecutionState) == "undefined")
    self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_SEND"});
  else
	setExecutionState(TXT_EXEC_SEND);

  ts_postrun_start = Date.now();
  FS.syncfs(false, all_files_uploaded);
  return;
}


function onAbort(){
  console.log("\nERROR...");
  console.log("An errror ocurred...");
  upload_out_files();
}


Module['preRun']          = load_in_files;
Module['postRun']         = post_run;
Module['onAbort']         = onAbort;
Module['instantiateWasm'] = load_binary;
