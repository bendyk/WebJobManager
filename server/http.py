import os
import sys
import time
from http.server import BaseHTTPRequestHandler



class RequestHandler(BaseHTTPRequestHandler):

    #TODO Save MainHtml in File 

    main_html = """
        <!DOCTYPE html>
        <html>
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


        if len(s.path) > 1:
            with open(s.path.split("/")[-1], "rb") as f:
                s.wfile.write(f.read())
        else: 
            s.wfile.write(bytes(s.main_html, "utf-8"))

