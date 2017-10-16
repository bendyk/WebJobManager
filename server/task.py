import time
import glob

class Task:

    def __init__(self, executable, args=None, wf_path="./", identifier=""):
        self.identifier   = identifier
        self.args         = args
        self.path         = wf_path + "/" + identifier
        self.wf_path      = wf_path
        self.in_files     = []
        self.out_files    = []
        self.done         = False
        self.executable   = wf_path + "/" + executable
        self.dependencies = []
        self.pre_time     = 0
        self.main_time    = 0
        self.post_time    = 0
        self.abs_time     = 0
        self.abs_time_start = 0
        self.abs_time_stop  = 0
        self.wait_time_start = time.time()
        self.wait_time_stop  = 0
        self.wait_time       = 0
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
        with open("tasks.js", "r") as f:
            data.append(f.read() % {"inputs": js_inputs, "outputs": js_outputs})

        if self.args:
            self.__append_args(data)
        self.__append_exe(data)

        self.abs_time_start = time.time()
        connection.send_text("\n".join(data))


    def __generate_js_input_files(self):
        data = []
        data.append("  wf_path = \"%s\";" % self.wf_path)
        data.append("  task_id = \"%s\";" % self.identifier)
        data.append("  FS.createPath(\"/\", wf_path);")
        data.append("  FS.createLink(wf_path, task_id, \"/\");")
        data.append("  console.log(wf_path);")

        for f_path in self.in_files:
            #for f_name in glob.glob(f_path): # this does not work, as some of these files do not exist, yet!
            data.append("  dependency_id = getUniqueRunDependency(1);")
            data.append("  Module['addRunDependency'](dependency_id);") 
            data.append("  request_queue.push({\"dep_id\": dependency_id, \"file\": \"%s\"});" % f_path)
            if "/" in f_path:
              data.append("  if(!FS.analyzePath(\"%s\").exists){FS.createPath(\"/\", \"%s\");}" % (f_path.rsplit("/",1)[0], f_path.rsplit("/",1)[0]))

        return "\n".join(data)
      

    def __generate_js_output_files(self):
        data      = []
     
        data.append("  console.log(FS.readdir(\"/\"));")
        data.append("  console.log(\"STDOUT:\");");
        data.append("  console.log(std_out);");
        data.append("  console.log(\"STDERR:\");");
        data.append("  console.log(std_err);");
        data.append("  FS.writeFile(\"/std.out\", std_out, {encoding:'utf8'});");
        data.append("  FS.writeFile(\"/std.err\", std_err, {encoding:'utf8'});");
        data.append("  upload_queue.push({\"file\":\"./std.out\"});");
        data.append("  upload_queue.push({\"file\":\"./std.err\"});");

        for f_path in self.out_files:
          data.append("  upload_queue.push({\"file\": \"%s\"});" % f_path)

        return "\n".join(data)


    def __append_args(self, data):
        argc = 0
        data.append("console.log(\"\\nARGUMENTS...\");")
        for arg in self.args:
            if arg:
                argc += 1
                data.append("arguments['%d'] = \"%s\";" % (argc-1, arg))
                data.append("console.log(\"%s\");" % arg)
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


