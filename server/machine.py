import os
import time
from .sheduler import Sheduler


class Machine:

    NEW_JOB     = 0
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
    WASM_FILE   = 11
    TEST_PING   = 12
    INPUT_OPEN  = 13
    INPUT_DATA  = 14

    def __init__(self, connection):
        connection.set_listener(self.conn_listener)
        connection.set_onClose(self.connection_closed)
        self.connection  = connection
        self.open_files  = {}
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
        self.files    = [];
        self.abs_time = time.time() - self.abs_time
        if self.task: 
            self.task.finish()
        self.__busy = False
        self.task   = None
        print("%s:%d: waiting for executable" % self.connection.address)
        


    def send_file(self, f_name, f_id = None):
        data = bytes()
        if(f_id): data += f_id

        with open(f_name, "rb") as f:
            data += f.read()

        self.connection.send_binary(data)
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
        print("cleaning %s on %s:%d" % ((wf_path,) + self.connection.address))

        with open("rm_workflow.js", "r") as f:
            self.connection.send_text("\n".join(['wf_path="%s";' % wf_path, f.read()]))        

 
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

            if cmd == self.NEW_JOB:
                self.set_ready()
                #print("%s: ABSOLUTE time: %dms" %(self.connection.address[0], int(round(self.abs_time * 1000))))

            elif cmd == self.INPUT_FILE:
                file_id = payload[:4];
                f_path  = self.task.wf_path + "/" + payload[4:].decode()
                self.send_file(f_path, file_id)

            elif cmd == self.INPUT_OPEN:
                fd       = int.from_bytes(payload[:4], byteorder='little') 
                f_path   = self.task.wf_path + "/" + payload[4:].decode()

                if os.path.isfile(f_path):
                    if not f_path in self.open_files:
                        self.open_files[f_path] = {'fd': None, 'file': None, 'size': os.stat(f_path).st_size}

                    self.open_files[f_path]['fd']   = fd
                    self.open_files[f_path]['file'] = open(f_path, "rb") 

                    print("%s: command input file: %s" % (self.connection.address[0], f_path))
                    time.sleep(1)
                    response  = self.open_files[f_path]['size'].to_bytes(4, byteorder="little")

                    self.connection.send_binary(response)
                else:
                    print("File not found: " + f_path)

            elif cmd == self.INPUT_DATA:
 
                filepointer = None
                response    = bytes()
                fd          = int.from_bytes(payload[:4], byteorder='little')
                length      = int.from_bytes(payload[4:8], byteorder = 'little')
                print('read bytes: ' + str(length)) 
  
                for obj in self.open_files.values():
                    if obj['fd'] == fd:
                        filepointer = obj['file']
                        break
 
                if filepointer:
                    response = filepointer.read(length)
                print("bytes send" + str(len(response)))      
                self.connection.send_binary(response)


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
            
            elif cmd == self.WASM_FILE:
                self.send_file(self.task.wasm)

            elif cmd == self.TEST_PING:
                response = 1
                print("received testping")
                self.connection.send_binary(response.to_bytes(1, byteorder='big'))
                print("send back ping")

            else: 
                print("%s:%d: UNKNOWN command (%d)  received." % (self.connection.address + (cmd,)))
                #print("%s: UNKNOWN data received: %s" % (self.connection.address[0], payload.decode()))

