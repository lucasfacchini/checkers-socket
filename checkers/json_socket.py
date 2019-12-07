import socket
import sys
import json 
from threading import Thread
import logging

BIND_ADDRESS = 'localhost'
BIND_PORT = 8000
SOCKET_CLOSE_HANDLE = 'disconnect'


class JsonSocket:

    def __init__(self):
        self.handles = {}

    def on(self, event, handle):
        self.handles[event] = handle

    def call_handle(self, event, args):
        res = None
        if event in self.handles:
            logging.info('call_handle "%s"' % event)
            res = self.handles[event](*args)
        else:
           logging.info('No handle for "%s"' % event)

        return res

    def start_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def encode_message(self, data):
        json_message = json.dumps(data)

        return str(len(json_message)).zfill(4) + json_message

    def wait_data(self, sock, send_response=False, disconnected=False):
        while not disconnected:
            data = self.read_data(sock)

            if data:
                event, args = tuple(data)

                if event == SOCKET_CLOSE_HANDLE:
                    disconnected = True
                    args = [sock]

                res = self.call_handle(event, args)
                if send_response and res:
                    self.send_data(res, sock)

    def send_data(self, data, socket):
        logging.info('sent "%s"' % data)
        socket.sendall(self.encode_message(data).encode())

    def read_data(self, socket):
        while True:
            message_length_recv = socket.recv(4)
            if message_length_recv:
                message_length = int(message_length_recv)

                if message_length > 0:
                    data = ''
                    while True:
                        data = data + socket.recv(5).decode()
                        logging.info('received "%s"' % data)
                        if len(data) >= message_length:
                            break

                    return json.loads(data)

        return None


class JsonSocketClient(Thread, JsonSocket):

    def __init__(self):
        Thread.__init__(self)
        JsonSocket.__init__(self)

        self.daemon = True
        self.on(SOCKET_CLOSE_HANDLE, self.close)

    def connect(self):
        self.start_socket()
        self.sock.connect((BIND_ADDRESS, BIND_PORT))
        self.start()

    def call(self, handle, data=None):
        self.send_data([handle, data], self.sock)

    def run(self):
        self.wait_data(self.sock, False)

    def close(self, sock):
        sock.close()
        logging.info('closed connection')


class JsonSocketServer(Thread, JsonSocket):

    def __init__(self):
        Thread.__init__(self)
        JsonSocket.__init__(self)

        self.daemon = True
        self.connections = []
        self.on(SOCKET_CLOSE_HANDLE, self.close_connection)

    def serve(self):
        self.start_socket()
        self.sock.bind((BIND_ADDRESS, BIND_PORT))
        self.sock.listen(1)
        self.start()

    def run(self):
        while True:
            logging.info('waiting for a connection')
            connection, client_address = self.sock.accept()
            self.connections.append(connection)
            logging.info('connection from %s', client_address)

            self.wait_data(connection, True)
            if len(self.connections) == 0:
                break

    def close_connection(self, sock=None):
        self.send_data(['disconnect', []], sock)
        sock.close()
        i = self.connections.index(sock)
        self.connections.pop(i)
        logging.info('closed connection %d', i)
