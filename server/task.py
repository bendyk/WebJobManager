import time
import glob

class Task:

    ESSENTIALS = """
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


function request_input_file(f_name){  
//console.log("load file: " + f_name);
  ws.send('\\u0001' + f_name);
}

function recv_input_file(msg){
  FS.writeFile(cur_request["file"], new Uint8Array(msg.data), {encoding:'binary'});

  if(request_queue.length == 0){
    all_in_files_loaded();
    Module['removeRunDependency'](cur_request["dep_id"]);
  }
  else{ 
    Module['removeRunDependency'](cur_request["dep_id"]);
    cur_request = request_queue.shift();
    request_input_file(cur_request["file"]);
  }
}

function all_in_files_loaded() {
    ts_prerun_stop  = Date.now();
    
    console.log("RUNNING ... " + Module['thisProgram']);
    ws.onmessage = function(msg) {};
    
    ts_mainrun_start = Date.now();
}

function load_in_files(){
  console.log("PRERUN...");
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

  ws.send('\\u0005' + duration_prerun);
  ws.send('\\u0006' + duration_mainrun);
  ws.send('\\u0007' + duration_postrun);
}

function upload_out_files(){
  ts_mainrun_stop = Date.now();

  console.log("POSTRUN...");
  ts_postrun_start = Date.now();

  %(outputs)s

  ws.onmessage = recv_executable;
  
  ts_postrun_stop = Date.now();
  calc_send_durations();

  console.log("FINISHED");
  console.log("-------------------");
  request_executable();
};


Module['postRun'] = upload_out_files;
Module['preRun']  = load_in_files;

    """

    def __init__(self, executable, args=None):
        self.args         = args
        self.in_files     = []
        self.out_files    = []
        self.done         = False
        self.executable   = executable
        self.dependencies = []
        self.pre_time     = 0
        self.main_time    = 0
        self.post_time    = 0
        self.abs_time_start = 0
        self.abs_time_stop = 0
        self.abs_time = 0
        self.wait_time_start = time.time()
        self.wait_time_stop = 0
        self.wait_time = 0
        self.in_execution = False


    def input_files(self, file_list):
        self.in_files = file_list


    def output_files(self, file_list):
        self.out_files = file_list


    def depends_on(self, tasks):
        self.dependencies.append(tasks)


    def ready(self):
        for task in self.dependencies:
            if not task.done:
                return False
        return not self.in_execution


    def start(self, connection):
        data              = []
        self.in_execution = True
        self.wait_time_stop = time.time()
        self.wait_time = int(round((self.wait_time_stop - self.wait_time_start) * 1000)) 

        js_inputs  = self.__generate_js_input_files()
        js_outputs = self.__generate_js_output_files()
        #print("generated inputs: %s" % js_inputs)
        #print("generated outputs: %s" % js_outputs)
        data.append(self.ESSENTIALS % {"inputs": js_inputs, "outputs": js_outputs})

        if self.args:
            self.__append_args(data)
        self.__append_exe(data)

        self.abs_time_start = time.time()
        connection.send_text("\n".join(data))


    def __generate_js_input_files(self):
        data = []

        for f_path in self.in_files:
            #for f_name in glob.glob(f_path): # this does not work, as some of these files do not exist, yet!
            data.append("  dependency_id = getUniqueRunDependency(1);")
            data.append("  Module['addRunDependency'](dependency_id);") 
            data.append("  request_queue.push({\"dep_id\": dependency_id,") 
            data.append("                      \"file\": \"%s\"});" % f_path)

        return "\n".join(data)
      

    def __generate_js_output_files(self):
        data      = []
        read_opts = "{encoding:'binary', flags:'r'}"
     
        for f_path in self.out_files:
            #for f_name in glob.glob(f_path): # this does not work, as these files do not exist, yet!
            data.append("  console.log(\"send file: %s\");" % f_path)
            data.append("  var file = FS.readFile(\"%s\", %s);" % (f_path, read_opts))
            data.append("  ws.send('\\u0003' + \"%s\");" % f_path)
            data.append("  ws.send('\\u0002');")
            data.append("  ws.send(file);")
            #data.append("  ws.send(new Blob(['\\u0002', file], {type: \"application/octet-binary\"}));") # this strangely crashes on firefox 54, but not with other browsers
            data.append("  ws.send('\\u0008');")
        return "\n".join(data)


    def __append_args(self, data):
        argc = 0
        for arg in self.args:
            argc += 1
            data.append("arguments['%d'] = \"%s\";" % (argc-1, arg))
            #print("Argument: " + arg)
        data.append("arguments.length = %d;" % argc)


    def __append_exe(self, data):
        data.append("Module['thisProgram']=\"%s\";" % self.executable) 

        with open(self.executable, "r") as f:
            data.append(f.read())

        data.append("//# sourceURL=debugger.js")

   
    def set_pre_time(self, ms_time):
        self.pre_time = ms_time


    def set_main_time(self, ms_time):
        self.main_time = ms_time


    def set_post_time(self, ms_time):
        self.post_time = ms_time


    def finish(self):
        self.done         = True
        self.in_execution = False
        self.abs_time_stop = time.time()
        self.abs_time     = int(round((self.abs_time_stop - self.abs_time_start) * 1000))


