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
              function function_to_url(js_function){
                var blob = new Blob(['('+ js_function.toString() + ')()'], {type: 'application/javascript'});
                return URL.createObjectURL(blob);
              }

              function starter(){
                var ws;

                if(typeof(ws) == "undefined"){
                  console.log("Create new Websocket connection");
                  ws = new WebSocket("ws://localhost:9999/");
                }

                function recv_executable(msg){
                  eval(msg.data);
                }

                function request_executable(){
                  ws.send(new ArrayBuffer(1));
                }

                ws.binaryType = "arraybuffer";
                ws.onmessage  = recv_executable;
                ws.onopen     = request_executable;
              }


              var wworker;

              if(typeof(Worker) !== undefined){

                wworker = new Worker(function_to_url(starter));

              }else{

                starter(); 
              }

            </script>

          </body>
        </html> """

    main1_html = """
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8" />
          </head>
          <body>

            <h1>Websocket Test</h1>

            <p id="state">IDLE</p>

            <script>
              if(typeof(Worker) !== "undefined"){
                if(typeof(w) == "undefined"){
                  w = new Worker("webworker.js");
                }
                w.onmessage = function(worker_state) { 
                  document.getElementById("state").innerHTML = worker_state.data;
                  console.log(worker_state.data);
                };

              } else {
		document.getElementById("state").innerHTML = "Sorry your browser doesnt support WebWorker";
              } 
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
            s.wfile.write(bytes(s.main_html, "utf-8"))

