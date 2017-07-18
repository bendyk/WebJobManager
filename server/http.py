import os
import os.path
import sys
import time
from http.server import BaseHTTPRequestHandler



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

