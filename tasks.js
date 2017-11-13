var Module        = {};
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

console.log("job received");

function load_binary(info, callback){
  ws.onmessage = function(msg){
                   console.log("binary loaded");
                   WebAssembly.instantiate(new Uint8Array(msg.data), info).then(function(output){
                     callback(output.instance);
                   }).catch(function(reason){
                     console.log("couldn't instantiate wasm");
                     Module['printErr']("could not instantiate wasm:" + reason);
                     Module['quit'](1, reason);
                   });
                                                                
                 }; 
  console.log("request binary");
  ws.send('\u000b');
  return {};
}

function request_input_file(){ 
    cur_request = request_queue.shift();
  
    if(request_queue.length == 0){
      all_in_files_loaded();
    }
    else {
      storage_file_path = "/storage/" + wf_path + "/" + cur_request["file"];

      if(FS.analyzePath(storage_file_path).exists){
        console.log("Load file: " + cur_request["file"]);
        var msg = {};
        msg.data = FS.readFile(storage_file_path, {encoding:'binary', flags:'r'});
        recv_input_file(msg);  
      }
      else{
        console.log("request file: " + cur_request["file"]);
        ws.onmessage = recv_input_file;
        ws.send('\u0001' + cur_request['file']);
      }
    }
}

function recv_input_file(msg){
    path = cur_request["file"].slice(cur_request["file"].indexOf("/")+1);
    FS.writeFile(path, new Uint8Array(msg.data), {encoding:'binary'});
    Module['removeRunDependency'](cur_request["dep_id"]);
    request_input_file();
}


function all_in_files_loaded() {
    ts_prerun_stop  = Date.now();
    console.log(FS.readdir("/"));
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

    ws.onmessage = function(msg) {};
    
    ts_mainrun_start = Date.now();
    Module['removeRunDependency'](cur_request["dep_id"]);
}


function load_in_files(){
  console.log("\nPRERUN...");
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
            console.log(std_out);
          }, 
          error  = function(msg){
            std_err = std_err.concat(String.fromCharCode(msg));
            console.log(std_err);
          }
  );

  var dependency_id;

  %(inputs)s

  dependency_id = getUniqueRunDependency(1);
  Module['addRunDependency'](dependency_id);
  request_queue.push({"dep_id": dependency_id, "file":"init_dummy"});

  FS.mkdir("/storage");
  FS.mount(IDBFS, {}, '/storage');
  FS.syncfs(true, function(err){
    request_input_file(); 
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
