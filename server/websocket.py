import os
import sys
import socket
import threading
import hashlib
import base64
import binascii
from .logging import Debug

WEBSOCKET_HANDSHAKE = '\
HTTP/1.1 101 Web Socket Protocol Handshake\r\n\
Upgrade: websocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %(hash)s\r\n\r\n\
'

class WSServer(threading.Thread):
    
    def __init__(self, address, on_newConnection):
        threading.Thread.__init__(self)
        self.addr = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.onConnection  = on_newConnection
        self.__connections = {}
        self.setDaemon(True)


    def run(self):
        print("WebSocketServer running on port %d" % self.addr[1])
        self.sock.bind(self.addr)
        self.sock.listen(10)
        
        try:
            while True:
                client, address = self.sock.accept()
                if not address in self.__connections:
                    self.__connections[address] = WSConnection(client, address)
                    self.onConnection(self.__connections[address])
                else:
                    Debug.error(DEBUG.ERROR.CONNECTION_REFUSED, address)
        except OSError:
            pass


    def get_connections(self):
        return list(self.__connections.keys())


    def shutdown(self):
        Debug.log("shutdown..." , ("Server", 0))
        for con in list(self.__connections.values()):
            con.shutdown()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


    def send_to(self, address, data, callback=None):
        try:
            self.__connections[address].send_data(data, callback)
        except IOError:
            self.__connections[address].shutdown()
            del self.__connections[address]




class WSConnection(threading.Thread):

    BINARY        = 0
    TEXT          = 1
    MAX_FRAG_SIZE = 2**63-1
    closed        = False


    def __init__(self, client, address):
        Debug.log("New Connection request", address)
        threading.Thread.__init__(self)
        self.connection = client
        self.address    = address
        self.listener   = None
        self.__onClose  = None
        self.setDaemon(True)
        self.start()


    def run(self):
        self.handshake()
        while True:
            try:
                self.receive()
            except IOError:
                self.shutdown()
                break


    def handshake(self):
        handshaken = False
        while not handshaken:
            header = self.connection.recv(1024).decode("utf-8")

            for line in header.split("\n"):
                if "WebSocket-Key" in line:
                    accept     = self.hash_key(line.split(":")[1])
                    handshaken = True
                    msg = WEBSOCKET_HANDSHAKE % {"hash": accept}
                    self.connection.send(msg.encode())

        Debug.log("Connection established", self.address)


    def hash_key(self, key):
        ha = hashlib.sha1(key.strip().encode())
        ha.update("258EAFA5-E914-47DA-95CA-C5AB0DC85B11".encode())
        return base64.b64encode(binascii.unhexlify(ha.hexdigest())).decode('utf-8')


    def send_binary(self, data):
        self.send_data(data, self.BINARY)


    def send_text(self, data):
        self.send_data(data, self.TEXT)


    def send_data(self, data, data_type):
        try:	
            for i in range(int(len(data) / self.MAX_FRAG_SIZE)):            
                frag  = b'\x01' if data_type == self.TEXT else b'\x02'
                frag += b'\x7f'
                frag += (self.MAX_FRAG_SIZE).to_bytes(8, byteorder="big")
                frag += data[:MAX_FRAG_SIZE]
                data = data[MAX_FRAG_SIZE:]
                self.connection.send(frag)
  
            last = b'\x81' if data_type == self.TEXT else b'\x82'

            if len(data) < 126:
                last += len(data).to_bytes(1, byteorder="big")
            elif len(data) < 2**16:
                last += b'\x7e'
                last += len(data).to_bytes(2, byteorder="big")
            else:
                last += b'\x7f'
                last += len(data).to_bytes(8, byteorder="big")

            if data_type == self.TEXT: data = data.encode()

            last += data

            self.connection.send(last)
            Debug.log("%d bytes send" % len(data), self.address)

        except IOError:
            Debug.warn("failed to send data", self.address)
            self.shutdown()


    def receive(self):
        recv = self.connection.recv(1)

        if (len(recv) == 0):
            Debug.log("received empty message", self.address)
            return

        fin      = recv[0] >> 7
        op_code  = recv[0] %  2**4

        if (op_code == 1) | (op_code == 2) | (op_code == 0):
            self.recv_data(fin)
        elif op_code == 8:
            self.shutdown()
        else:
            Debug.warn("Not supported op_code", self.address)


    def recv_data(self, fin):
        data       = bytearray()

        recv     = self.connection.recv(1)
        mask_bit = recv[0] >> 7
        rawlength   = recv[0] % 2**7

        if not mask_bit: raise ValueError('WSConnection: Message from client not masked')
    
        bytelength = self.get_bytelength(rawlength)
        mask       = self.connection.recv(4) * 256
        remaining  = bytelength

        while remaining > 0:
            read_bytes = 1024 if remaining > 1024 else remaining 
            recv = self.connection.recv(read_bytes)
            data.extend(bytearray(mask[pos] ^ value for pos,value in enumerate(recv)))
            remaining -= len(recv)

        Debug.log("%d bytes received" % bytelength, self.address)
        self.listener(data)


    def get_bytelength(self, length):
        if length == 126:
            recv     = self.connection.recv(2)
            length   = int.from_bytes(recv, byteorder='big')

        elif length == 127:
            recv     = self.connection.recv(8)
            length   = int.from_bytes(recv, byteorder='big')

        return length


    def set_listener(self, listener):
        self.listener = listener


    def set_onClose(self, onClose):
        self.__onClose = onClose

    def recv_ping(self):
        Debug.log("Ping received", self.address)


    def recv_pong(self):
        Debug.log("Pong received", self.address)


    def shutdown(self):
        if not self.closed:
            if self.__onClose: self.__onClose()
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
            except OSError:
                pass

            self.closed = True
            Debug.warn("Connection closed", self.address)


