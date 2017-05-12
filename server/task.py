import time

class Task:

    def __init__(self, executable, args=None):
        self.args         = args
        self.in_files     = None
        self.out_files    = None
        self.received     = 0
        self.done         = False
        self.executable   = executable
        self.dependencies = []


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
        return True


    def start(self, connection):
        self.start_time = time.time()
        data = []

        if self.in_files:
            self.__append_input(data)

        if self.args:
            self.__append_args(data)

        self.__append_exe(data)

        if self.out_files:
            self.__append_output(data)

        connection.send_data("\n".join(data), self.callback)



    def __append_input(self, data):
        data.append("function load_in_files(){")

        x = 0
        for f_name in self.in_files:
            with open(f_name, "r") as f:
                data.append("var in_file_%d = `%s`;" % (x, f.read()))
                #data.append("var in_file_%d = \"23\";" % x)
                data.append("FS.writeFile(\"%s\", in_file_%d);" % (f_name, x))
            x += 1

        data.append("};")
        data.append("var Module = {};")
        data.append("Module['preInit'] = load_in_files;")
        #data.append("Object.defineProperty(Module, 'preRun',")
        #data.append("  {value: [load_in_files], writable: false, enumerable: true, configurable: true});")

    def __append_args(self, data):
            argc = 0
            for arg in self.args:
                argc += 1
                data.append("arguments['%d'] = \"%s\";" % (argc-1, arg))
            data.append("arguments.length = %d;" % argc)


    def __append_exe(self, data):
        with open(self.executable, "r") as f:
            data.append(f.read())


    def __append_output(self, data):
            for f in self.out_files:
                data.append("ws.send(FS.readFile(\"%s\", {encoding:'binary', flags:'r'}));" % f)



    def callback(self, data, fin):

        if self.received < len(self.out_files):

            with open(self.out_files[self.received], "w") as f:
                f.write(data.decode())

        self.received += 1

        if (self.received >= len(self.out_files)) and not self.done:
            self.done = True
            print("Task %s done in %f s" % (self.executable, time.time()-self.start_time))
