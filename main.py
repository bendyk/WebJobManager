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

from util.statistics import Statistics
#only import this if youve task specified in tasks.py
import tasks as pre_tasks
#tasks = pre_tasks.tasks

#####

machines = []
tasks    = []

task1 = Task("./plainjs_test.js", ["aaa.in", "aaa.out"])
task1.input_files(["aaa.in"])
task1.output_files(["aaa.out"])

tasks.append(task1)

#task1 = Task("./montage-tasks-js/mProjectPP.js", ["-X", "-x 0.99330", "2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420198.fits", "big_region_20170518_153916_25237.hdr"])
#inFiles  = ["./2mass-atlas-990502s-j1420198.fits", "./big_region_20170518_153916_25237.hdr"]
#task1.input_files(inFiles)
#outFiles = ["./p2mass-atlas-990502s-j1420198.fits", "p2mass-atlas-990502s-j1420198_area.fits"]
#task1.output_files(outFiles)

#task1 = Task("./mjob-tasks-js/mjob1.js", ["data"])
#genFiles = ["data.arr1", "data.arr2"]
#task1.output_files(genFiles)

#task2 = Task("./mjob-tasks-js/mjob2.js", [genFiles[0]])
#task2.input_files([genFiles[0]])
#sortFiles = ["./data.srt1", "./data.srt2"]
#task2.output_files([sortFiles[0]])
#task2.depends_on(task1)

#task3 = Task("./mjob-tasks-js/mjob2.js", [genFiles[1]])
#task3.input_files([genFiles[1]])
#task3.output_files([sortFiles[1]])
#task3.depends_on(task1)

#task4 = Task("./mjob-tasks-js/mjob4.js", sortFiles)
#task4.input_files(sortFiles)
#task4.output_files(["./data.mrge"])
#task4.depends_on(task2)
#task4.depends_on(task3)

#tasks.append(task1)
#tasks.append(task2)
#tasks.append(task3)
#tasks.append(task4)

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
        Statistics.save_time_stats("task_times.stats", tasks)

    except(KeyboardInterrupt, SystemExit):
        print("Main: Interrupted.")

    except Exception as e:
        print("Main: Unknown exception %s occured" % type(e))
        print(e)

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
