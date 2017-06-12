import time

class Machine:

    EXECUTABLE  = 0
    INPUT_FILE  = 1
    OUTPUT_FILE = 2
    OUTPUT_PATH = 3
    CLIENT_MSG  = 4
    PRE_TIME    = 5
    MAIN_TIME   = 6
    POST_TIME   = 7


    def __init__(self, connection):
        connection.set_listener(self.conn_listener)
        self.connection = connection
        self.__busy      = True
        self.task        = None
        self.output_path = None
        self.abs_time    = 0.0


    def run_task(self, task):
        self.abs_time   = time.time()
        self.task       = task
        self.__busy     = True
        self.task.start(self.connection)
        print("%s: Task %s assigned" % (self.connection.address[0], task.executable))


    def is_busy(self):
        return self.__busy


    def set_ready(self):
        self.abs_time = time.time() - self.abs_time
        if self.task: 
            self.task.finish()
        self.__busy = False
        print("%s: waiting for executable" % self.connection.address[0])
        


    def send_file(self, f_name):
        with open(f_name, "rb") as f:
            self.connection.send_binary(f.read())
        print("%s: input file %s send" % (self.connection.address[0], f_name))


    def recv_file(self, data):
        with open(self.output_path, "wb") as f:
            f.write(data)
        print("%s: output file %s received" % (self.connection.address[0], self.output_path))


    def conn_listener(self, data):
        cmd  = data[0]
        data = data[1:]

        if cmd == self.EXECUTABLE:
            self.set_ready()
            print("%s:ABSOLUTE time: %dms" %(self.connection.address[0], int(round(self.abs_time * 1000))))

        elif cmd == self.INPUT_FILE:
            self.send_file(data.decode())

        elif cmd == self.OUTPUT_FILE:
            self.recv_file(data)

        elif cmd == self.OUTPUT_PATH:
            self.output_path = data.decode()

        elif cmd == self.CLIENT_MSG:
            print("%s: msg %s received" % (self.connection.address[0], data.decode()))

        elif cmd == self.PRE_TIME:
            self.task.set_pre_time(int(data.decode()))
            print("%s:PRERUN time: %sms" %(self.connection.address[0], data.decode()))

        elif cmd == self.MAIN_TIME:
            self.task.set_main_time(int(data.decode()))
            print("%s:MAINRUN time: %sms" %(self.connection.address[0], data.decode()))

        elif cmd == self.POST_TIME:
            self.task.set_post_time(int(data.decode()))
            print("%s:POSTRUN time: %sms" %(self.connection.address[0], data.decode()))
