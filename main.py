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
from server.logging import Debug

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
                      help="path to the cwl_workflow file.")
 
    parser.add_option("-d", "--data", dest="data_file", action="store", 
                      type="string", default="", 
                      help="path to an optional datafile for the workflow")

    parser.add_option("--http-port", dest="http_port", action="store",
                      type="int", default = 8888, 
                      help="Http port for the webinterface")

    parser.add_option("--ws-port", dest="ws_port", action="store",
                      type="int", default = 9999, 
                      help="Websocket port for data transfer")

    parser.add_option("-m", "--min-machines", dest="minimum_machines", action="store",
                      type="int", default = 1, 
                      help="Minimum of machines to start workflow")

    parser.add_option("-r", "--recover", dest="recovery_path", action="store",
                      type="string", default="",
                      help="path to the workflow you want to recover")


    (options, args) = parser.parse_args()

    if bool(options.wf_file) != bool(options.wf_files):
        print("workflow directory(-p) and workflow file(-w) required")
        exit(-1)

    return options


def run(opts):
    Sheduler.MINIMUM_MACHINES = opts.minimum_machines

    if opts.wf_file and os.path.isfile(opts.wf_file):
        wf = parse_workflow(opts)
        Sheduler.addWorkflow(wf)       

    try:
        wsd   = WSServer(("", opts.ws_port), on_newConnection)
        httpd = HTTPServer(("", opts.http_port), RequestHandler)

        httpd.allow_reuse_address = True
        t = threading.Thread(target=httpd.serve_forever)
        t.setDaemon(True)

        wsd.start()
        t.start()
        Debug.msg("Running WebsocketServer on port %d" % opts.ws_port, ("SERVER", opts.ws_port))
        Debug.msg("Running HttpServer on port %d" % opts.http_port, ("SERVER", opts.http_port))

        Sheduler.run()

    except(KeyboardInterrupt, SystemExit):
        print("Main: Interrupted.")
        log_remaining(wf)


def parse_workflow(opts):
    Debug.msg("Parsing workflow files ...")
    wf       = None
    wf_files = []

    for f in os.listdir(opts.wf_files):
        path = os.path.join(opts.wf_files, f)
        if os.path.isfile(path):
            wf_files.append(path)

    try:
        wf = Workflow(wf_files, opts.wf_file, opts.data_file, opts.recovery_path)

        if opts.recovery_path:
            wf.recover()
          
    except:
        Debug.error("Workflow files missing")
        exit()

    log_tasks(wf)
    return wf


def log_tasks(workflow):
    log_file = "tasks.log"
    content  = []

    for t in workflow.get_all_tasks():
        content.append(t.path)

        for d in t.dependencies:
            content.append("  %s" % d.path)

    Debug.log_file(log_file, content)


def log_remaining(workflow):
    log_file = "remaining.log"
    content  = []

    for task in workflow.get_all_tasks():
        if not task.done:
            content.append(task.path)

    Debug.log_file(log_file, content)


def on_newConnection(connection):
    Sheduler.addMachine(Machine(connection))
    

if __name__ == "__main__": 
    run(parse_args())

