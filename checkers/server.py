from json_socket import *


class Server:

    def __init__(self):
        self.conn = JsonSocket()
        self.conn.on('join', self.handle_join)
        self.conn.on('move', self.handle_move)

        self.player1 = None
        self.player2 = None

        self.logic_board = [[-1, 2, -1, 2, -1, 2, -1, 2, -1, 2],
                            [2, -1, 2, -1, 2, -1, 2, -1, 2, -1],
                            [-1, 2, -1, 2, -1, 2, -1, 2, -1, 2],
                            [2, -1, 2, -1, 2, -1, 2, -1, 2, -1],
                            [-1, 0, -1, 0, -1, 0, -1, 0, -1, 0],
                            [0, -1, 0, -1, 0, -1, 0, -1, 0, -1],
                            [-1, 1, -1, 1, -1, 1, -1, 1, -1, 1],
                            [1, -1, 1, -1, 1, -1, 1, -1, 1, -1],
                            [-1, 1, -1, 1, -1, 1, -1, 1, -1, 1],
                            [1, -1, 1, -1, 1, -1, 1, -1, 1, -1]]

    def handle_move(self, from_x, from_y, to_x, to_y):
        from_x = int(from_x)
        from_y = int(from_y)
        to_x = int(to_x)
        to_y = int(to_y)
        print >> sys.stderr, 'handle_move from_x: "%d" from_y: %d to_x: %d to_y: %d' % (from_x, from_y, to_x, to_y)

        if self.logic_board[to_x][to_y] == 0:
            self.logic_board[to_x][to_y] = self.logic_board[from_x][from_y]
            self.logic_board[from_x][from_y] = 0

        return self.logic_board

    def handle_join(self, data):
        print >> sys.stderr, 'handle_join data: "%s"' % data
        pass

    def get_board(self):
        return self.logic_board

    def start(self):
        self.conn.loop()


server = Server()
server.start()
