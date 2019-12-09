from json_socket import *
from checkers_game import CheckersGame
from threading import Lock
from time import sleep

class Server:
    STATUS_WAITING_PLAYERS = 1
    STATUS_ONGOING = 2
    STATUS_ENDGAME = 3

    def __init__(self):
        self.server = JsonSocketServer(max_clients=2)
        self.server.on('connect', self.handle_join)
        self.server.on('move', lambda *argv: ['move_response', [self.handle_move(*argv)]])
        self.server.on('get_board', lambda _: ['board_response', [self.get_board()]])
        self.server.on('leave', self.handle_leave)

        self.lock_running = Lock()

        self.players = []
        self.current_player = None
        self.status = None
        self.game = CheckersGame()

    def handle_join(self, connection):
        self.players.append(connection)
        if len(self.players) == 2:
            self.start_game()

    def handle_leave(self, connection):
        i = self.players.index(connection)
        self.players.pop(i)
        self.status = self.STATUS_WAITING_PLAYERS
        logging.info('PLAYER %d LEFT', i)

        self.send_all('reset_game', [])
        if len(self.players) == 0:
            self.lock_running.release()

    def start_game(self):
        self.status = self.STATUS_ONGOING
        logging.info('SERVER STARTED GAME')
        self.send_all('start_game', [self.game.board])
        self.current_player = self.players[0]

    def end_game(self):
        self.status = self.STATUS_ENDGAME
        self.lock_running.release()

    def handle_move(self, from_x, from_y, to_x, to_y, connection):
        logging.info(self.current_player)
        if connection == self.current_player:
            from_x = int(from_x)
            from_y = int(from_y)
            to_x = int(to_x)
            to_y = int(to_y)

            turn = self.game.move(player, from_x, from_y, to_x, to_y)

            self.send_all('board_response', [self.game.board])

            if turn != player:
                self.switch_player()

        return self.game.board

    def switch_player(self):
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]

    def send_all(self, event, data):
        for player in self.players:
            player.send_data([event , data])

    def get_board(self):
        return self.game.board

    def start(self):
        self.lock_running.acquire()
        self.server.serve()
        self.status = self.STATUS_WAITING_PLAYERS
        logging.info('SERVER WAITING PLAYERS')
        self.lock_running.acquire()


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    server = Server()
    server.start()
