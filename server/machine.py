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
    OUTPUT_FILE_END = 8


    def __init__(self, connection):
        connection.set_listener(self.conn_listener)
        self.connection = connection
        self.__busy      = True
        self.task        = None
        self.output_path = None
        self.abs_time    = 0.0
        self.receiving_file = False


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


    def recv_file(self, data, openmode):
        #print("try to write to %s" % self.output_path)
        with open(self.output_path, openmode) as f:
            f.write(data)


    def conn_listener(self, data):

        if (self.receiving_file): # append data to file or detect end of file
            if (len(data) == 1 and data[0] == self.OUTPUT_FILE_END):
                print("%s: output file %s received" % (self.connection.address[0], self.output_path))
                self.receiving_file = False
            else:
                self.recv_file(data, "ab") # append subsequent data of received file
        else:
            cmd  = data[0]
            payload = data[1:]

            if cmd == self.EXECUTABLE:
                self.set_ready()
                #print("%s: ABSOLUTE time: %dms" %(self.connection.address[0], int(round(self.abs_time * 1000))))

            elif cmd == self.INPUT_FILE:
                #print("%s: command input file: %s" % (self.connection.address[0], payload.decode()))
                self.send_file(payload.decode())

            elif cmd == self.OUTPUT_FILE:
                #print("%s: command output file: %s" % (self.connection.address[0], payload[0:10]))
                self.receiving_file = True
                self.recv_file(payload, "wb")

            elif cmd == self.OUTPUT_PATH:
                #print("%s: command output path: %s" % (self.connection.address[0], payload.decode()))
                self.output_path = payload.decode()

            elif cmd == self.CLIENT_MSG:
                print("%s: client msg %s received" % (self.connection.address[0], payload.decode()))

            elif cmd == self.PRE_TIME:
                self.task.set_pre_time(int(payload.decode()))
                #print("%s: PRERUN time: %sms" %(self.connection.address[0], payload.decode()))

            elif cmd == self.MAIN_TIME:
                self.task.set_main_time(int(payload.decode()))
                #print("%s: MAINRUN time: %sms" %(self.connection.address[0], payload.decode()))

            elif cmd == self.POST_TIME:
                self.task.set_post_time(int(payload.decode()))
                #print("%s: POSTRUN time: %sms" %(self.connection.address[0], payload.decode()))
            
            else: 
                print("%s: UNKNOWN data received." % self.connection.address[0])
                #print("%s: UNKNOWN data received: %s" % (self.connection.address[0], payload.decode()))

