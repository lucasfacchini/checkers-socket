from time import sleep
from json_socket import *
import unittest
import logging

class JsonSocketTest(unittest.TestCase):
    
    def test_encode_message(self):
        json_socket = JsonSocket()
        data = ['test', [1, 2, 3]]

        message = json_socket.encode_message(data)

        self.assertEquals('0019["test", [1, 2, 3]]', message)


class JsonSocketServerTest(unittest.TestCase):

    def test_server_call(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        server = JsonSocketServer()
        server.serve()

        server.on('test', lambda n: n + 1)

        client = JsonSocketClient()
        client.connect()
        response = client.call('test', [1])

        self.assertEquals(2, response)

        server.close()