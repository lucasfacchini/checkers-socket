import socket
import sys

BIND_ADDRESS = 'localhost'
BIND_PORT = 8000


class JsonSocket:

    def __init__(self):
        self.handles = {}
        self.connections = []

    def on(self, event, handle):
        self.handles[event] = handle

    def call_handle(self, event):
        self.handles[event]()

    def loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((BIND_ADDRESS, BIND_PORT))
        sock.listen(1)

        while True:
            # Wait for a connection
            print >> sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()
            try:
                print >> sys.stderr, 'connection from', client_address

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(16)
                    print >> sys.stderr, 'received "%s"' % data
                    if data:

                        pass
                    # print >> sys.stderr, 'sending data back to the client'
                    # connection.sendall(data)
                    else:
                        print >> sys.stderr, 'no more data from', client_address
                        break

            finally:
                # Clean up the connection
                connection.close()
