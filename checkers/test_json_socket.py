from time import sleep
from json_socket import *
import unittest
import logging

class JsonSocketTest(unittest.TestCase):
    
    def test_encode_message(self):
        json_socket = JsonSocket()
        data = ['test', [1, 2, 3]]

        message = json_socket.encode_message(data)

        self.assertEqual('0019["test", [1, 2, 3]]', message)


class JsonSocketServerTest(unittest.TestCase):

    def test_server_call(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        server = JsonSocketServer()
        server.serve()
        client = JsonSocketClient()
        client.connect()

        server.on('test', lambda n: ['test_response', [n + 1]])

        def test_response(n):
            self.assertEqual(2, n)
            client.call(SOCKET_CLOSE_HANDLE, [0])

        client.on('test_response', test_response)

        response = client.call('test', [1])

        server.join()
        client.join()