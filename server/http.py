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
                var ws_address;

                function start(address){
                  if(typeof(ws) == "undefined"){
                    console.log("Create new Websocket connection");
                    ws = new WebSocket(ws_address);
                  }

                  ws.binaryType = "arraybuffer";
                  ws.onmessage  = recv_executable;
                  ws.onopen     = request_executable;
                }

                function recv_executable(msg){
                  eval(msg.data);
                }

                function request_executable(){
                  ws.send(new ArrayBuffer(1));
                }

                if(ws_address == undefined){
                  self.onmessage = function(e){
                                     ws_address = e.data[0];
                                     start();    
                                   }
                }else{
                  start();
                }


              }


              var wworker;
              var ws_address = "ws:" + window.location.href.split(":").slice(1,-1).join(":") + ":9999/"

              if(typeof(Worker) !== undefined){

                wworker = new Worker(function_to_url(starter));
                wworker.postMessage([ws_address]);

              }else{

                starter(); 
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
            #with open("./mjob-tasks-js/mjobs.html", "r") as f:
            #    s.wfile.write(bytes(f.read(), "utf-8"))

            s.wfile.write(bytes(s.main_html, "utf-8"))

