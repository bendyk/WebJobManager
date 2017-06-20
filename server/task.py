import time
import glob

class Task:

    ESSENTIALS = """
var Module        = {};
var cur_request   = {};
var request_queue = [];
var time_prerun   = 0;
var time_mainrun  = 0;
var time_postrun  = 0;


function request_input_file(f_name){  
  console.log(  "load file: " + f_name);
  ws.send('\\u0001' + f_name);
}

function recv_input_file(msg){
  FS.writeFile(cur_request["file"], new Uint8Array(msg.data), {encoding:'binary'});

  if(request_queue.length == 0){
    console.log("RUNNING ... " + Module['thisProgram']);
    ws.onmessage = function(msg) {};
    time_prerun  = Date.now() - time_prerun; 
    time_mainrun = Date.now();
    Module['removeRunDependency'](cur_request["dep_id"]);
  }
  else{
    Module['removeRunDependency'](cur_request["dep_id"]);
    cur_request = request_queue.shift();
    request_input_file(cur_request["file"]);
  }
}


function load_in_files(){
  console.log("PRERUN...");
  time_prerun  = Date.now();
  ws.onmessage = recv_input_file;

  %(inputs)s

  cur_request  = request_queue.shift();

  if(cur_request !== undefined){
    request_input_file(cur_request["file"]); 
  }
  else{
    console.log("RUNNING ... " + Module['thisProgram']);
    time_prerun = Date.now() - time_prerun;
  }
};


function upload_out_files(){
  console.log("POSTRUN...");
  time_mainrun = Date.now() - time_mainrun;
  time_postrun = Date.now();
  %(outputs)s

  ws.onmessage = recv_executable;
  
  time_postrun = Date.now() - time_postrun;
  ws.send('\\u0005' + time_prerun);
  ws.send('\\u0006' + time_mainrun);
  ws.send('\\u0007' + time_postrun);
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
        self.abs_time     = 0
        self.wait_time    = time.time()
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
        self.abs_time     = time.time()
        self.wait_time    = int(round((time.time() - self.wait_time) * 1000)) 

        js_inputs  = self.__generate_js_input_files()
        js_outputs = self.__generate_js_output_files()
        data.append(self.ESSENTIALS % {"inputs": js_inputs, "outputs": js_outputs})

        if self.args:
            self.__append_args(data)
        self.__append_exe(data)

        connection.send_text("\n".join(data))


    def __generate_js_input_files(self):
        data = []

        for f_path in self.in_files:
            for f_name in glob.glob(f_path):
                data.append("  var dependency_id = getUniqueRunDependency(1);")
                data.append("  Module['addRunDependency'](dependency_id);") 
                data.append("  request_queue.push({\"dep_id\": dependency_id,") 
                data.append("                      \"file\": \"%s\"});" % f_name)

        return "\n".join(data)
      

    def __generate_js_output_files(self):
        data      = []
        read_opts = "{encoding:'binary', flags:'r'}"
     
        for f_path in self.out_files:
            for f_name in glob.glob(f_path):
                data.append("  console.log(  \"send file: %s\");" % f_name)
                data.append("  var file = FS.readFile(\"%s\", %s);" % (f_name, read_opts))
                data.append("  ws.send('\\u0003' + \"%s\");" % f_name)
                data.append("  ws.send(new Blob(['\\u0002', file]));")
        return "\n".join(data)


    def __append_args(self, data):
        argc = 0
        for arg in self.args:
            argc += 1
            data.append("arguments['%d'] = \"%s\";" % (argc-1, arg))
            print("Argument :" + arg)
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
        self.abs_time     = int(round((time.time() - self.abs_time) * 1000))
