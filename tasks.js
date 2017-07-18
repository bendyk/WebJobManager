var Module        = {};
var cur_request   = {};
var request_queue = [];

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


function request_input_file(f_name){  
//console.log("load file: " + f_name);
  ws.send('\u0001' + f_name);
}

function recv_input_file(msg){
    FS.writeFile(cur_request["file"], new Uint8Array(msg.data), {encoding:'binary'});

    if(request_queue.length == 0) {
        all_in_files_loaded();
        Module['removeRunDependency'](cur_request["dep_id"]);
    }
    else {
        Module['removeRunDependency'](cur_request["dep_id"]);
        cur_request = request_queue.shift();
        request_input_file(cur_request["file"]);
    }
}

function all_in_files_loaded() {
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

    console.log("RUNNING ... " + Module['thisProgram']);

    ws.onmessage = function(msg) {};
    
    ts_mainrun_start = Date.now();
}

function load_in_files(){
  console.log("PRERUN...");
  if (typeof(setExecutionState) == "undefined")
    self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_RECV"});
  else
	setExecutionState(TXT_EXEC_RECV);

  ts_prerun_start = Date.now();

  ws.onmessage = recv_input_file;

  var dependency_id;
  %(inputs)s

  if (request_queue.length === 0) { // task has no input files
    all_in_files_loaded();
    return;
  }
  else { // start chain of input requests here
    cur_request = request_queue.shift();
    request_input_file(cur_request["file"]); 
  }
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

function upload_out_files(){
  ts_mainrun_stop = Date.now();

  console.log("POSTRUN...");
  if (typeof(setExecutionState) == "undefined")
    self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_SEND"});
  else
	setExecutionState(TXT_EXEC_SEND);

  ts_postrun_start = Date.now();

  %(outputs)s

  ws.onmessage = recv_executable;
  
  ts_postrun_stop = Date.now();
  calc_send_durations();

  console.log("FINISHED");
  console.log("-------------------");
  if (typeof(setExecutionState) == "undefined")
    self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_FINISHED"});
  else
	setExecutionState(TXT_EXEC_FINISHED);

  if (typeof(setJobAssignment) == "undefined")
	self.postMessage({"cmd": "setJobAssignment", "arg": "TXT_NO_JOB"});
  else
	setJobAssignment(TXT_NO_JOB);

  request_executable();
};


Module['postRun'] = upload_out_files;
Module['preRun']  = load_in_files;


