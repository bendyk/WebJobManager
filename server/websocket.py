import os
import sys
import socket
import threading
import hashlib
import base64
import binascii

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
        print("Running WebSocketServer on port %d" % self.addr[1])
        self.sock.bind(self.addr)
        self.sock.listen(10)
        
        try:
            while True:
                client, address = self.sock.accept()
                if not address in self.__connections:
                    self.__connections[address] = WSConnection(client, address)
                    self.onConnection(self.__connections[address])
                else:
                    print("Connection ERROR: Multiple connections from single address")
        except OSError:
            pass


    def get_connections(self):
        return list(self.__connections.keys())


    def shutdown(self):
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

    template_handshake = '\
HTTP/1.1 101 Web Socket Protocol Handshake\r\n\
Upgrade: websocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %(hash)s\r\n\r\n\
'

    MAX_FRAG_SIZE = 2**63-1
    closed        = False


    def __init__(self, client, address):
        threading.Thread.__init__(self)
        print("WSConnection request from %s:%d" % address)
        self.connection = client
        self.address    = address
        self.callback   = None
        self.setDaemon(True)
        self.start()


    def run(self):
        self.handshake()
        #try:
#        f = open("a.out.js", "r")
#        self.send_data(f.read())
#        f.close()
        while True:
            self.recv_data()
        #except(ValueError):
        #    print("something went wrong")
        #    self.shutdown()
        #    pass


    def handshake(self):
        handshaken = False
        while not handshaken:
            header = self.connection.recv(512).decode("utf-8")

            for line in header.split("\n"):
                if "WebSocket-Key" in line:
                    accept     = self.hash_key(line.split(":")[1])
                    handshaken = True
                    msg = self.template_handshake % {"hash": accept}
                    self.connection.send(msg.encode())



    def hash_key(self, key):
        ha = hashlib.sha1(key.strip().encode())
        ha.update("258EAFA5-E914-47DA-95CA-C5AB0DC85B11".encode())
        return base64.b64encode(binascii.unhexlify(ha.hexdigest())).decode('utf-8')


    def send_data(self, data, callback):
        self.callback = callback
	
        for i in range(int(len(data) / self.MAX_FRAG_SIZE)):            
            frag  = b'\x01\x7f'
            frag += (self.MAX_FRAG_SIZE).to_bytes(8, byteorder="big")
            frag += data[:MAX_FRAG_SIZE]
            data = data[MAX_FRAG_SIZE:]
            self.connection.send(frag)
  
        last = b'\x81'

        if len(data) < 126:
            last += len(data).to_bytes(1, byteorder="big")
        elif len(data) < 2**16:
            last += b'\x7e'
            last += len(data).to_bytes(2, byteorder="big")
        else:
            last += b'\x7f'
            last += len(data).to_bytes(8, byteorder="big")

        last += data.encode()
        self.connection.send(last)
        print("data send")



    def recv_data(self):
        ## recv = self.connection.recv(2)
        ## while not recv[0]
        recv    = self.connection.recv(1)

        fin      = recv[0] >> 7
        op_code  = recv[0] %  2**4
        print((op_code))

        if (op_code == 1) | (op_code == 2) | (op_code == 0):
            self.recv_text(fin)
        elif op_code == 8:
            self.shutdown()
        elif op_code == 9:
            self.recv_ping()
        elif op_code == 10:
            self.recv_pong()
        else:
            raise ValueError('WSConnection: Unsupported op_code')


    def recv_text(self, fin):
            print("WSConnection: Receive text data")
            data       = bytearray()

            recv     = self.connection.recv(1)
            mask_bit = recv[0] >> 7
            length   = recv[0] %  2**7

            if not mask_bit:
                raise ValueError('WSConnection: Message from client not masked')

            if   length == 126:
                recv     = self.connection.recv(2)
                length   = int.from_bytes(recv, byteorder='big')

            elif length == 127:
                recv     = self.connection.recv(8)
                length   = int.from_bytes(recv, byteorder='big')

            mask = self.connection.recv(4)
            print("Länge %d" %length)

            remaining = length

            while remaining > 0:
                read_bytes = 4 if remaining > 4 else remaining
                recv = self.connection.recv(read_bytes)
                for x in range(len(recv)):
                    data.append(recv[x] ^ mask[x])
                remaining -= len(recv)

            self.callback(data, fin)
            data = data.decode()
            print("FIN %s" % "True" if fin else "False") 
            if len(data) < 50:
                print(data)
            #print("DATA RECEIVED")


    def recv_ping(self):
        print("WSConnection: Ping received")


    def recv_pong(self):
        print("WSConnection: Pong received")


    def shutdown(self):
        if not self.closed:
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
            except OSError:
                pass

            self.closed = True
            print("Connection to: %s:%d closed" % self.address)


