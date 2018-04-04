import os
import os.path
import re
import sys
import time
from http.server import BaseHTTPRequestHandler
from .sheduler import Sheduler
from .workflow import Workflow
from .logging import Debug


class RequestHandler(BaseHTTPRequestHandler):

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()


    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        if len(s.path) > 1:

            Debug.log("GET request %s" % s.path)
            filepath = "./" + "/".join(s.path.split('/')[1:])

            # first check if file exists
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    s.wfile.write(f.read())
                Debug.log("GET response %s" % filepath)
            else:
                s.send_error(404, "File not found")

        else: 
            Debug.log("GET request index.html")
            with open("index.html", "r") as f:
                s.wfile.write(bytes(f.read(), "utf-8"))


    def do_POST(s):
        content_length = int(s.headers['Content-Length'])
        file_content   = s.rfile.read(content_length)
        boundary       = s.headers['Content-Type'].split("boundary=")[-1].encode()
  
        files = s.save_files(file_content, boundary)

        workflow = None
        try:
            workflow = Workflow(files, "workflow.cwl", "workflow.json")
        except:
            workflow = None
            pass
        
        response_file = ""
        if workflow:
            response_file = "manage_success.html"
            Debug.msg("New Workflow created", s.client_address)
        else:
            response_file = "manage_fail.html"
            Debug.warn("Failed to create new workflow", s.client_address)

        with open(response_file, "rb") as f:
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write(f.read())


    def save_files(s, data, boundary):
        files = []
        regex  = re.compile(b'.*\n.* name="(.*)".*filename="(.*)"\r\n.*', re.DOTALL)
        chunks = data.split(boundary)
  
        tmp_path = "/tmp/%d" % int(round(time.time() * 1000))
        os.makedirs(tmp_path)
        
        for chunk in chunks:
            filepointer = chunk.find(b'\r\n\r\n')
            meta_data   = chunk[0:filepointer]
            file_data   = chunk[filepointer+4:-4]
            matcher     = regex.match(meta_data)

            if matcher and (filepointer > -1):
                if matcher.group(2):
                    f_id   = matcher.group(1).decode()
                    f_name = matcher.group(2).decode()

                    if f_id in ["workflow.cwl", "workflow.json"]:
                        f_name = f_id

                    with open(tmp_path + "/" + f_name, "wb") as f:
                        f.write(file_data)

                    files.append(tmp_path + "/" + f_name)
                    Debug.log("Files received: %s -> %s" %(f_id, f_name), s.client_address)
        return files
        
        


