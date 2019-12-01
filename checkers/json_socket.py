import socket
import sys
import json 
from threading import Thread
import logging

BIND_ADDRESS = 'localhost'
BIND_PORT = 8000


class JsonSocket():

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def encode_message(self, data):
        json_message = json.dumps(data)
        return str(len(json_message)).zfill(4) + json_message

    def send_data(self, data, socket):
        socket.sendall(self.encode_message(data).encode())

    def receive_data(self, socket):
        while True:
            message_length_recv = socket.recv(4)
            if message_length_recv:
                message_length = int(message_length_recv)

                if message_length > 0:
                    data = ''
                    while True:
                        data = data + socket.recv(5)
                        logging.info('received "%s"' % data)

                        if len(data) >= message_length:
                            break

                    return json.loads(data)

        return None

    def close(self, sock=None):
        if sock:
            sock.close()
        else:
            self.sock.close()
    

class JsonSocketClient(JsonSocket):

    def __init__(self):
        JsonSocket.__init__(self)

    def connect(self):
        self.sock.connect((BIND_ADDRESS, BIND_PORT))

    def call(self, handle, data):
        self.send_data([handle, data], self.sock)

        return self.receive_data(self.sock)


class JsonSocketServer(Thread, JsonSocket):

    def __init__(self):
        Thread.__init__(self)
        JsonSocket.__init__(self)

        self.daemon = True
        self.handles = {}
        self.connections = []

    def on(self, event, handle):
        self.handles[event] = handle

    def call_handle(self, data):
        event, args = tuple(data)

        res = None
        if event in self.handles:
            logging.info('call_handle "%s"' % event)
            res = self.handles[event](*args)
        else:
           logging.info('No handle for "%s"' % event)

        return res

    def serve(self):
        self.sock.bind((BIND_ADDRESS, BIND_PORT))
        self.sock.listen(1)
        self.start()

    def run(self):
        while True:
            logging.info('waiting for a connection')
            connection, client_address = self.sock.accept()

            try:
                logging.info('connection from %s', client_address)

                while True:
                    data = self.receive_data(connection)

                    if data:
                        res = self.call_handle(data)
                        self.send_data(res, connection)

            except:
                connection.close()