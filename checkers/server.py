from json_socket import *
from checkers_game import CheckersGame, PLAYER_BLACK, PLAYER_WHITE
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
        self.connections = {}
        self.current_player = None
        self.status = None
        self.game = CheckersGame()

    def handle_join(self, connection):
        player = Player(connection, PLAYER_BLACK if len(self.players) == 0 else PLAYER_WHITE)
        self.players.append(player)
        self.connections[connection] = player
        if len(self.players) == 2:
            self.start_game()

        connection.send_data(['connect_response', [player.color]])

    def handle_leave(self, connection):
        player = self.connections[connection]
        i = self.players.index(player)
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
        if self.connections[connection] == self.current_player:
            from_x = int(from_x)
            from_y = int(from_y)
            to_x = int(to_x)
            to_y = int(to_y)

            try:
                turn = self.game.move(self.current_player.color, from_x, from_y, to_x, to_y)
            except Exception as e:
                connection.send_data(['error', [str(e)]])
                return self.game.board

            self.send_all('board_response', [self.game.board])

            if turn != self.current_player.color:
                self.current_player = self.players[turn]

        return self.game.board

    def send_all(self, event, data):
        for player in self.players:
            player.connection.send_data([event , data])

    def get_board(self):
        return self.game.board

    def start(self):
        self.lock_running.acquire()
        self.server.serve()
        self.status = self.STATUS_WAITING_PLAYERS
        logging.info('SERVER WAITING PLAYERS')
        self.lock_running.acquire()


class Player:

    def __init__(self, connection, color):
        self.connection = connection
        self.color = color


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    server = Server()
    server.start()
