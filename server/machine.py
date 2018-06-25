import os
import time
from .sheduler import Sheduler
from .logging import Debug

class Machine:

    NEW_JOB     = 0
    INPUT_FILE  = 1
    OUTPUT_FILE = 2
    OUTPUT_PATH = 3
    OUTPUT_RECV = 13
    CLIENT_MSG  = 4
    PRE_TIME    = 5
    MAIN_TIME   = 6
    POST_TIME   = 7
    OUTPUT_FILE_END = 8
    OUTPUT_KEEP = 9
    OUTPUT_SEND = 10
    WASM_FILE   = 11
    TEST_PING   = 12

    def __init__(self, connection):
        connection.set_listener(self.conn_listener)
        connection.set_onClose(self.connection_closed)
        self.connection  = connection
        self.open_files  = {}
        self.__busy      = True
        self.__clean     = True
        self.task        = None
        self.output_path = None
        self.abs_time    = 0.0
        self.receiving_file = False


    def run_task(self, task):
        self.abs_time   = time.time()
        self.task       = task
        self.__busy     = True
        self.__clean    = False
        self.task.start(self.connection)
        Debug.log("task assigned %s" % task.executable, self.connection.address)


    def is_busy(self):
        return self.__busy


    def connection_closed(self):
        if self.task:
            Debug.warn("task abort" , self.connection.address)
            self.task.done         = False
            self.task.in_execution = False
            self.task              = None
        Sheduler.removeMachine(self)


    def set_ready(self):
        self.files    = []
        self.abs_time = time.time() - self.abs_time
        if self.task: 
            Debug.log("task finished", self.connection.address)
            if not self.connection.closed:
                self.task.finish()
        self.__busy = False
        self.task   = None
        Debug.log("waiting for new task", self.connection.address)
        

    def send_file(self, f_name, f_id = None):
        data = bytes()
        if(f_id): data += f_id

        if not os.path.exists(f_name):
            Debug.warn("File not found %s" % f_name, self.connection.address)
            return

        with open(f_name, "rb") as f:
            data += f.read()

        self.connection.send_binary(data)
        Debug.log("send input file %s" % f_name, self.connection.address)


    def receive_file(self, data):
        self.receiving_file = True
        if ("/" in self.output_path) and not os.path.exists(self.output_path.rsplit("/",1)[0]):
            os.makedirs(self.output_path.rsplit("/",1)[0])
        self.receive_file_data(data)
        

    def receive_file_data(self, data):
        if (len(data) == 1 and data[0] == self.OUTPUT_FILE_END):
            Debug.log("received output file %s" % self.output_path, self.connection.address)
            self.receiving_file = False
        else:
            with open(self.output_path, "ab") as f:
                f.write(data)
            Debug.log("receive file %s" % self.output_path, self.connection.address)


      
    def set_output_path(self, data):
        path, size       = data.split(":")
        self.output_size = size 
        self.output_path = self.task.path + "/" + path
        transfer_file    = Sheduler.check_file_transfer(self.task, self.output_path) 
        response         = self.OUTPUT_SEND if transfer_file else self.OUTPUT_KEEP

        self.connection.send_binary(response.to_bytes(1, byteorder='big'))

    def process_file_request(self, data):
        file_id = data[:4];
        f_path  = self.task.wf_path + "/" + data[4:].decode()
        Debug.log("requested file %s" % f_path, self.connection.address)
        f_path  = f_path.replace("\0", "")
        self.send_file(f_path, file_id)
       

    def clean_workflow_files(self, wf_path):
        ##Cleaning indexeddb files 
        if self.__clean:
          return

        self.__busy  = True
        self.__clean = True
        Debug.log("cleaning indexedDB of %s" % wf_path, self.connection.address)

        with open("rm_workflow.js", "r") as f:
            self.connection.send_text("\n".join(['wf_path="%s";' % wf_path, f.read()]))        

 
    def conn_listener(self, data):
        cmd     = None
        payload = []

        if(self.receiving_file):
            cmd     = self.OUTPUT_RECV
            payload = data
        else:
            cmd     = data[0]
            payload = data[1:]

        ############ OPERATION SWITCH######################################################
        if cmd == self.NEW_JOB:
            self.set_ready()

        elif cmd == self.INPUT_FILE:
            self.process_file_request(payload)

        elif cmd == self.OUTPUT_FILE:
            self.receive_file(payload)

        elif cmd == self.OUTPUT_RECV:
            self.receive_file_data(payload)

        elif cmd == self.OUTPUT_PATH:
            self.set_output_path(payload.decode())

        elif cmd == self.CLIENT_MSG:
            Debug.msg(payload.decode(), self.connection.address)

        elif cmd == self.PRE_TIME:
            self.task.set_pre_time(int(payload.decode()))

        elif cmd == self.MAIN_TIME:
            self.task.set_main_time(int(payload.decode()))

        elif cmd == self.POST_TIME:
            self.task.set_post_time(int(payload.decode()))
            
        elif cmd == self.WASM_FILE:
            self.send_file(self.task.wasm)

        elif cmd == self.TEST_PING:
            response = 1
            Debug.log("received test PING", self.connection.address)
            self.connection.send_binary(response.to_bytes(1, byteorder='big'))

        else: 
            Debug.log("unknown operation code(%d) received" % cmd, self.connection.address)

