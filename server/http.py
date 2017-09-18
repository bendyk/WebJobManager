import os
import os.path
import re
import sys
import time
from http.server import BaseHTTPRequestHandler
from .sheduler import Sheduler
from .workflow import Workflow



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
            print("GET for file %s received" % s.path)
            filepath = "./" + "/".join(s.path.split('/')[1:])
            # first check if file exists
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    s.wfile.write(f.read())
                print("File %s send" % filepath)
            else:
                s.send_error(404, "File not found")
        else: 
            with open("index.html", "r") as f:
                s.wfile.write(bytes(f.read(), "utf-8"))
            #s.wfile.write(bytes(s.main_html, "utf-8"))

    def do_POST(s):
        content_length = int(s.headers['Content-Length'])
        file_content   = s.rfile.read(content_length)

        workflow = None
        try:
            workflow = s.create_workflow(file_content)
        except:
            workflow = None
            pass
        
        response_file = ""
        if workflow:
            Sheduler.addWorkflow(workflow)
            response_file = "manage_success.html"
        else:
            response_file = "manage_fail.html"

        with open(response_file, "rb") as f:
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write(f.read())


    def create_workflow(s, data):
        files  = {}
        regex  = re.compile(b'.*\n.* name="(.*)".*filename="(.*)"\r\n.*', re.DOTALL)
        chunks = data.split(b'-'*29)

        wf_path = "./workflows/%d" % int(round(time.time() * 1000))

        if not os.path.exists(wf_path):
            os.makedirs(wf_path)
       
        for chunk in chunks:
            filepointer = chunk.find(b'\r\n\r\n')
            meta_data   = chunk[0:filepointer]
            file_data   = chunk[filepointer+4:-2]
            matcher     = regex.match(meta_data)

            if matcher and (filepointer > -1):
                if matcher.group(2):
                    f_id   = matcher.group(1).decode()
                    f_name = matcher.group(2).decode()

                    with open(wf_path + "/" + f_name, "wb") as f:
                        f.write(file_data)

                    files[f_id] = f_name
                    print("Files received: %s -> %s" %(f_id, f_name))


        data_file = wf_path + "/" + files["workflow.json"] if "workflow.json" in files else ""
    
        wf = Workflow(wf_path, wf_path + "/" + files["workflow.cwl"], data_file)
        
        if files["workflow.cwl"] and wf.check_required_files():
            return wf
        else: 
            for f in files.values(): os.remove(wf_path + "/" + f)
            return None


