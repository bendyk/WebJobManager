import os
import sys
import socket
import time
import threading
import hashlib
import base64
import binascii
from http.server import HTTPServer
from server.websocket import WSServer, WSConnection
from server.http import RequestHandler
from server.machine import Machine
from server.task import Task

machines = []
tasks    = []

task1 = Task("./mjob-tasks-js/mjob1.js", ["./data"])
genFiles = ["./data.arr1", "./data.arr2"]
task1.output_files(genFiles)

task2 = Task("./mjob-tasks-js/mjob2.js", [genFiles[0]])
task2.input_files([genFiles[0]])
sortFiles = ["./data.srt1", "./data.srt2"]
task2.output_files([sortFiles[0]])
task2.depends_on(task1)

task3 = Task("./mjob-tasks-js/mjob2.js", [genFiles[1]])
task3.input_files([genFiles[1]])
task3.output_files([sortFiles[1]])
task3.depends_on(task1)

task4 = Task("./mjob-tasks-js/mjob4.js", sortFiles)
task4.input_files(sortFiles)
task4.output_files(["./data.mrge"])
task4.depends_on(task2)
task4.depends_on(task3)

tasks.append(task1)
tasks.append(task2)
tasks.append(task3)
tasks.append(task4)
# TODO bugfix: full workflow with 500000 integers fails to produce correct result
# but if each task is called separately, the result is correct (but browser hangs for some time even after result was completely transmitted to server)

def run():

    try:
        wsd = WSServer(("", 9999), on_newConnection)
        wsd.start()
        httpd = HTTPServer(("", 8888), RequestHandler)
        httpd.allow_reuse_address = True
        t = threading.Thread(target=httpd.serve_forever)
        t.setDaemon(True)
        t.start()
        print("Running HttpServer on port 8888")

        while True:
            alltasksdone = True
            for task in tasks:
                if task.ready() and not task.done:
                    execute(task)
                
                if alltasksdone and not task.done:
                    alltasksdone = False

            if alltasksdone:
                break

            time.sleep(1)
        
        print("all tasks done.")

    except(KeyboardInterrupt, SystemExit):
        print("Main: Exception occured.")

    finally:
        print("\nshutdown HttpServer")
        httpd.shutdown()
        print("shutdown WebSocketServer")
        wsd.shutdown()
        exit()

def execute(task):
    started = False
    while not started:
        for machine in machines:
            if not machine.is_busy():
                machine.run_task(task)
                started = True
                break

        time.sleep(1)


def on_newConnection(connection):
    machines.append(Machine(connection))

if __name__ == "__main__":
    run()
