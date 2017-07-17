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
	<meta name="viewport" content="width=device-width, initial-scale=1"/>
	<style type="text/css">
body {
	font-family: Verdana, sans-serif;
	margin: 40px auto;
	max-width: 750px;
	line-height: 1.6;
	font-size: 18px;
	color: #444;
	padding: 0 10px;
}

h1, h2 {
	font-family: "Segoe UI", Arial, sans-serif;
	line-height: 1.2;
	border-radius: 4px;
}
h1 {
	background-color: #4CAF70;
	color: white;
	font-size: 36px;
	text-align: center;
}
h2 {
	background-color: #AFDDE9;
	font-size: 24px;
	padding: 8px 20px;
}
p {
	margin: 18px 32px;
}
table {
	margin: 0px auto;
	font-size: 14px;
}
th {
	background-color: #AA4400;
	color: white;
}
th, td {
	padding: 5px;
	text-align: right;
	border-bottom: 1px solid #ddd;
}
tr:hover {
	background-color: #f5f5f5;
}
	</style>
</head>
<body>
	<h1>WebFlowWorker</h1>

	<noscript><h2>Error: You cannot use WebFlowWorker if JavaScript is deactivated. Please enable JavaScript.</h2></noscript>

	<h2>Connection state</h2>
	<p id="connection_state"></p>

	<h2>Worker execution state</h2>
	<p id="execution_state"></p>

	<h2>Assigned job</h2>
	<p id="task_name"></p>

	<h2>Job history [ms]</h2>
	<table id="task_history">
		<tr><th>Jobname</th><th>Stage-in</th><th>Execution</th><th>Stage-out</th><th>Total runtime</th></tr>
	</table>

<script>
// display state management
var TXT_NOT_CONNECTED = "Not connected";
var TXT_TRY_CONNECT = "Establish connection...";
var TXT_CONNECTED = "Connected";
var TXT_WS_ERROR = "Error occured.";

var TXT_EXEC_IDLE = "Idle";
var TXT_EXEC_REQ = "Request job";
var TXT_EXEC_RECV = "Receiving input data...";
var TXT_EXEC_RUN = "Executing job...";
var TXT_EXEC_SEND = "Sending output data...";
var TXT_EXEC_FINISHED = "Finished";

var TXT_NO_JOB = "Not assigned";

var jobHistory; // stores past job execution times

function setConnectionState(text) {
	document.getElementById("connection_state").innerText = text;
}
function setExecutionState(text) {
	document.getElementById("execution_state").innerText = text;
}
function setJobAssignment(text) {
	document.getElementById("task_name").innerText = text;
}

function showJobInHistory(jobname, dur1, dur2, dur3, total) {
	var htmltr = "<tr><td>"+ jobname +"</td><td>"+ dur1 +"</td><td>"+ dur2 +"</td><td>"+ dur3 +"</td><td>"+ total +"</td></tr>";
	var row = document.getElementById("task_history").insertRow(1);
	row.insertCell(0).innerText = jobname;
	row.insertCell(1).innerText = dur1;
	row.insertCell(2).innerText = dur2;
	row.insertCell(3).innerText = dur3;
	row.insertCell(4).innerText = total;
}

function storeJobInHistory(jobname, dur1, dur2, dur3, total) {
	showJobInHistory(jobname, dur1, dur2, dur3, total);

	// store persistently
	jobHistory.push({"name": jobname, "dur1": dur1, "dur2": dur2, "dur3": dur3, "total": total});
	saveHistory();
}


// local storage functionality
function testStorageAvailability() {
	return (typeof(Storage) !== "undefined");
}

function getState() {
	return JSON.parse(localStorage.getItem("history"));
}

function saveHistory() {
	localStorage.setItem("history", JSON.stringify(jobHistory));
}

function loadHistory() {
	// test for storage availablity
	if (!testStorageAvailability()) {
		console.log("Persistent storage for job history is not supported by browser.");
		return;
	}

	jobHistory = getState();
	if (jobHistory == null) {
		jobHistory = []; // initialize empty array
	}
	
	// fill table with loaded entries
	for (var i in jobHistory)
		showJobInHistory(jobHistory[i]["name"], jobHistory[i]["dur1"], jobHistory[i]["dur2"], jobHistory[i]["dur3"], jobHistory[i]["total"]);
}


/** Helper to call a function by a webworker instance. */
function function_to_url(js_function) {
	var blob = new Blob(['('+ js_function.toString() + ')()'], { type: 'application/javascript' });
	return URL.createObjectURL(blob);
}

/** Establish a websocket connection from inside a running webworker instance. */
function establishConnection() {
	var ws; // websocket object
	var ws_address; // address to connect to

	/** Connect the websocket to the server. */
	function connectWebsocket() {
		if (typeof(setConnectionState) == "undefined")
			self.postMessage({"cmd": "setConnectionState", "arg": "TXT_TRY_CONNECT"});
		else
			setConnectionState(TXT_TRY_CONNECT);

		if(ws == undefined) {
			console.log("Create new Websocket connection to: ", ws_address);
			ws = new WebSocket(ws_address);
		}

		ws.binaryType = "arraybuffer"; // why not "blob"?
		ws.onmessage = recv_executable;
		ws.onopen = request_executable;
		ws.onerror = ws_error;
		ws.onclose = ws_close;
	}

	/** Listener for websocket: incoming data */
	function recv_executable(msg) {
		eval(msg.data);
	}

	/** Listener for websocket: called when connection established */
	function request_executable() {
		if (typeof(setConnectionState) == "undefined")
			self.postMessage({"cmd": "setConnectionState", "arg": "TXT_CONNECTED"});
		else
			setConnectionState(TXT_CONNECTED);

		if (typeof(setExecutionState) == "undefined")
			self.postMessage({"cmd": "setExecutionState", "arg": "TXT_EXEC_REQ"});
		else
			setExecutionState(TXT_EXEC_REQ);

		ws.send(new ArrayBuffer(1));
	}

	/** Listener for websocket: called on connection error. */
	function ws_error(msg) {
		console.log("Error: Cannot establish websocket connection. ", msg);
		if (typeof(setConnectionState) == "undefined")
			self.postMessage({"cmd": "setConnectionState", "arg": "TXT_WS_ERROR"});
		else
			setConnectionState(TXT_WS_ERROR);
	}
	/** Listener for websocket: called when connection is closed. */
	function ws_close(e) {
		if (typeof(setConnectionState) == "undefined")
			self.postMessage({"cmd": "setConnectionState", "arg": "TXT_NOT_CONNECTED"});
		else
			setConnectionState(TXT_NOT_CONNECTED);
	}

	if (ws_address == undefined) { // happens inside webworker
		self.onmessage = function(e) { // this is called when the target url is received
			ws_address = e.data[0];
			connectWebsocket();
		};
	} else { // happens not inside a webworker
		connectWebsocket();
	}
}

/** webworker object that is responsible for websocket connection and job execution */
var wworker;
/** target webserver address to connect to */
var ws_address = "ws:" + window.location.href.split(":").slice(1,-1).join(":") + ":9999/"

/** This will be called first after the page was loaded. */
function init() {
	setConnectionState(TXT_NOT_CONNECTED);
	setExecutionState(TXT_EXEC_IDLE);
	setJobAssignment(TXT_NO_JOB);
    loadHistory();

	// start the webworker or run directly, if not available
	if (typeof(Worker) !== "undefined") {
		wworker = new Worker(function_to_url(establishConnection));
		wworker.addEventListener("message", function(e) {
			var functionCallAsString = e.data["cmd"] + "(" + e.data["arg"] + ")";
			console.log("call: ", functionCallAsString);
			eval(functionCallAsString);
		}, false);
		wworker.postMessage([ws_address]);
	} else {
		establishConnection(); 
	}
}

// autorun initialization function after document is loaded
if (window.addEventListener) 
	window.addEventListener("load", init, false);
else if (window.attachEvent) 
	window.attachEvent("onload", init);
else 
	window.onload = init;
</script>

  </body>
</html> 
    """

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

