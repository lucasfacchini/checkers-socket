from tkinter import Tk, Canvas
from itertools import product
from json_socket import *
from checkers_game import PIECE_WHITE, PIECE_KING_WHITE, PIECE_BLACK, PIECE_KING_BLACK, FIELD_WHITE, FIELD_BLACK, MIN_POS_BOARD, MAX_POS_BOARD
import logging

from server import Server


class Board(Tk):
    def __init__(self, width, height, cellsize):
        Tk.__init__(self)
        self.cellsize = cellsize
        self.width = width
        self.height = height
        self.canvas = Canvas(self, width=width, height=height)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.pack()
        #self.canvas.create_text(width / 2, height / 2, text="Aguardando oponente...")

        self.selected = None
        self.logic_board = []

        self.connection = JsonSocketClient()
        self.connection.on('board_response', self.update_board)
        self.connection.on('move_response', self.update_board)
        self.connection.on('start_game', self.update_board)
        self.connection.on('reset_game', self.reset_game)

    def start_game(self, logic_board, _):
        self.update_board(logic_board)

    def reset_game(self, _=None):
        self.canvas.delete("all")
        self.canvas.create_text(self.width / 2, self.height / 2, text="Aguardando oponente...")

    def update_board(self, logic_board, _):
        self.logic_board = logic_board
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        r = range(MIN_POS_BOARD, MAX_POS_BOARD + 1)
        for (i, j) in product(r, r):
            x1, y1 = (i * self.cellsize), (j * self.cellsize),
            x2, y2 = x1 + self.cellsize, y1 + self.cellsize
            cell = self.logic_board[i][j]
            color = "white" if cell == FIELD_WHITE else "grey"
            board.draw_rectangle(x1, y1, x2, y2, color)
            pawnColor = None
            if cell == PIECE_WHITE:
                pawnColor = "white"
            elif cell == PIECE_BLACK:
                pawnColor = "black"

            if pawnColor != None:
                board.draw_circle(x1, y1, x2, y2, pawnColor)

    def draw_rectangle(self, x1, y1, x2, y2, color):
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def draw_circle(self, x1, y1, x2, y2, color):
        self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black")

    def on_click(self, event):
        x = int(event.x / self.cellsize)
        y = int(event.y / self.cellsize)

        if self.selected != None:
            from_x, from_y = self.selected
            self.selected = None
            self.connection.call('move', [from_x, from_y, x, y])
        elif self.logic_board[x][y] > 0:
            self.selected = (x, y)

        print("You clicked on cell (%s, %s)" % (x, y))

    def run(self):
        self.title("Draughts")
        self.reset_game()
        self.connection.connect()
        self.mainloop()
        self.connection.call('leave', [])
        self.connection.call(SOCKET_CLOSE_HANDLE, [])

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    board = Board(400, 400, 40)
    board.run()