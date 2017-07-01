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

# specify which tasks have to be executed

# Montage workflow
#import workflows.montagedag as pre_tasks

# mJob workflow
import workflows.mjobdag as pre_tasks

# plainjs example
#import workflows.plainjs as pre_tasks

machines = []
tasks = pre_tasks.tasks


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
        print()
        print("shutdown HttpServer")
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
