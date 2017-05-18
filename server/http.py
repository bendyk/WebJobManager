import os
import os.path
import sys
import time
from http.server import BaseHTTPRequestHandler



class RequestHandler(BaseHTTPRequestHandler):

    #TODO Save MainHtml in File 

    main_html = """
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8" />
          </head>
          <body>

            <h1>Websocket Test</h1>

            <p id="state">IDLE</p>

            <script>
              var ws       = new WebSocket("ws://localhost:9999/");
              ws.onopen    = function() {};
              ws.onmessage = function(msg){
		document.getElementById("state").innerHTML = "RUNNING";
		eval(msg.data);
		document.getElementById("state").innerHTML = "IDLE";
	      };
            </script>

          </body>
        </html> """

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()


    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        #print("Get-request: %s" % s.path)
        if len(s.path) > 1:
            filepath = s.path.split('/')[-1]
            # first check if file exists
            if os.path.isfile(filepath):
                with open(s.path.split("/")[-1], "rb") as f:
                    s.wfile.write(f.read())
            else:
                s.send_error(404, "File not found")
        else: 
            s.wfile.write(bytes(s.main_html, "utf-8"))

