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

task1 = Task("./a.out.js", ["./blub"])
task1.output_files(["./blub.arr1", "./blub.arr2"])

task2 = Task("./a2.out.js", ["./blub.arr1"])
task2.input_files(["./blub.arr1"])
task2.output_files(["./blub.arr1.sort"])
task2.depends_on(task1)

task3 = Task("./a2.out.js", ["./blub.arr2"])
task3.input_files(["./blub.arr2"])
task3.output_files(["./blub.arr2.sort"])
task3.depends_on(task1)

task4 = Task("./a4.out.js", ["./blub.arr1.sort", "./blub.arr2.sort"])
task4.input_files(["./blub.arr1.sort", "./blub.arr2.sort"])
task4.output_files(["./blub.arr1.sort.merged"])
task4.depends_on(task2)
task4.depends_on(task3)

tasks.append(task1)
tasks.append(task2)
tasks.append(task3)
tasks.append(task4)

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
                
                if not task.done:
                    alltasksdone = False

            if alltasksdone:
                break
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

        #time.sleep(1)


def on_newConnection(connection):
    machines.append(Machine(connection))

if __name__ == "__main__":
    run()
