import os
import time
from .sheduler import Sheduler


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
    OUTPUT_KEEP = 9
    OUTPUT_SEND = 10


    def __init__(self, connection):
        connection.set_listener(self.conn_listener)
        connection.set_onClose(self.connection_closed)
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
        print("%s:%d: Task %s assigned" % (self.connection.address + (task.executable,)))


    def is_busy(self):
        return self.__busy

    def connection_closed(self):
        if self.task:
            self.task.in_execution = False
            self.task.done         = False
            self.task              = None
        Sheduler.removeMachine(self)

    def set_ready(self):
        self.abs_time = time.time() - self.abs_time
        if self.task: 
            self.task.finish()
        self.__busy = False
        self.task   = None
        print("%s:%d: waiting for executable" % self.connection.address)
        


    def send_file(self, f_name):
        with open(f_name, "rb") as f:
            self.connection.send_binary(f.read())
        print("%s:%d: input file %s send" % (self.connection.address + (f_name,)))


    def recv_file(self, data, openmode):
        #print("try to write to %s" % self.output_path)

        if ("/" in self.output_path) and not os.path.exists(self.output_path.rsplit("/",1)[0]):
            os.makedirs(self.output_path.rsplit("/",1)[0])

        with open(self.output_path, openmode) as f:
            f.write(data)


    def check_file_transfer(self):
        transfer_file = Sheduler.check_file_transfer(self.task, self.output_path) 

        response = self.OUTPUT_SEND if transfer_file else self.OUTPUT_KEEP
            
        self.connection.send_binary(response.to_bytes(1, byteorder='big'))
       

    def clean_workflow_files(self, wf_path):
        ##Cleaning indexeddb files 
        self.__busy = True
        execution = """
        console.log("cleanup workflow files(TODO)");
        /*FS.mkdir("/storage");
        FS.synfs(true,function(err){
          if(FS.analyzePath("/storage/%(wf)s").exists){
            FS.rmdir("/storage/%(wf)s");
            FS.syncfs(false, function(err){
              console.log("done");
              ws.onmessage = recv_executable;
              request_executable();
            });
          }            
        });*/
        """
        print("cleaning %s on %s:%d" % ((wf_path,) + self.connection.address))
        self.connection.send_text(execution % {"wf":wf_path})         

 
    def conn_listener(self, data):

        if (self.receiving_file): # append data to file or detect end of file
            if (len(data) == 1 and data[0] == self.OUTPUT_FILE_END):
                print("%s:%d: output file %s received" % (self.connection.address + (self.output_path,)))
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
                self.send_file(self.task.wf_path + "/" + payload.decode())

            elif cmd == self.OUTPUT_FILE:
                #print("%s: command output file: %s" % (self.connection.address[0], payload[0:10]))
                self.receiving_file = True
                self.recv_file(payload, "wb")

            elif cmd == self.OUTPUT_PATH:
                #print("%s: command output path: %s" % (self.connection.address[0], payload.decode()))
                path, size       = payload.decode().split(":")
                self.output_path = self.task.path + "/" + path
                self.output_size = size 
                self.check_file_transfer()

            elif cmd == self.CLIENT_MSG:
                print("%s:%d: client msg %s received" % (self.connection.address + (payload.decode(),)))

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
                print("%s:%d: UNKNOWN command (%d)  received." % (self.connection.address + (cmd,)))
                #print("%s: UNKNOWN data received: %s" % (self.connection.address[0], payload.decode()))

