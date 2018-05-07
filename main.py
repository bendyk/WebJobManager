import os
import sys
import socket
import time
import threading
import hashlib
import base64
import binascii
from optparse import OptionParser
from http.server import HTTPServer
from server.websocket import WSServer, WSConnection
from server.http import RequestHandler
from server.machine import Machine
from server.task import Task
from server.workflow import Workflow
from server.sheduler import Sheduler

from util.statistics import Statistics

# specify which tasks have to be executed

# Montage workflow
#import workflows.montagedag as pre_tasks

# mJob workflow
import workflows.mjobdag as pre_tasks

# plainjs example
#import workflows.plainjsdag as pre_tasks

# benchtasks workflows
#import workflows.benchtasks as pre_tasks

tasks = pre_tasks.tasks
#Sheduler.addWorkflow(Workflow("").set_tasks(tasks))

def parse_args():

    parser = OptionParser(usage="%prog [-p workflow_dir -w cwl_workflow_file [-d cwl_data_file]]")

    parser.add_option("-p", "--path", dest="wf_files", action="store",
                      type="string", default="", 
                      help="path to the workflow files.")

    parser.add_option("-w", "--workflow", dest="wf_file", action="store", 
                      type="string", default="", 
                      help="absolute path to the cwl_workflow file.")
 
    parser.add_option("-d", "--data", dest="data_file", action="store", 
                      type="string", default="", 
                      help="absolute path to an optional datafile for the workflow")

    parser.add_option("--http-port", dest="http_port", action="store",
                      type="int", default = 8888, 
                      help="Http port for the webinterface")

    parser.add_option("--ws-port", dest="ws_port", action="store",
                      type="int", default = 9999, 
                      help="Websocket port for data transfer")

    parser.add_option("-m", "--min-machines", dest="minimum_machines", action="store",
                      type="int", default = 1, 
                      help="Minimum of machines to start workflow")

    (options, args) = parser.parse_args()

    if bool(options.wf_file) != bool(options.wf_files):
        print("workflow directory(-p) and workflow file(-w) required")
        exit(-1)

    return options


def run(opts):
    Sheduler.MINIMUM_MACHINES = opts.minimum_machines
    if opts.wf_file and os.path.isfile(opts.wf_file):
        wf_files = []

        for f in os.listdir(opts.wf_files):
            path = os.path.join(opts.wf_files, f)
            if os.path.isfile(path):
                wf_files.append(path)

        try:
            wf = Workflow(wf_files, opts.wf_file, opts.data_file)
        except IOError:
            wf = None
            pass

        if not wf:
            print("Missing files in workflow")
            exit()
        
    try:
        wsd = WSServer(("", opts.ws_port), on_newConnection)
        wsd.start()
        httpd = HTTPServer(("", opts.http_port), RequestHandler)
        httpd.allow_reuse_address = True
        t = threading.Thread(target=httpd.serve_forever)
        t.setDaemon(True)
        t.start()
        print("Running HttpServer on port 8888")

        Sheduler.run()

    except(KeyboardInterrupt, SystemExit):
        print("Main: Interrupted.")

#    except Exception as e:
#        print("Main: Unknown exception %s occured" % type(e))
#        print(e)

#    finally:
#        print()
#        print("shutdown HttpServer")
#        httpd.shutdown()
#        print("shutdown WebSocketServer") 
#        wsd.shutdown()
#        exit()



def on_newConnection(connection):
    Sheduler.addMachine(Machine(connection))
    

if __name__ == "__main__": 
    run(parse_args())

