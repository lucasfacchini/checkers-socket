from tkinter import Tk, Canvas
from itertools import product

from server import Server


class Board(Tk):
    def __init__(self, server, width, height, cellsize):
        Tk.__init__(self)
        self.server = server
        self.cellsize = cellsize
        self.canvas = Canvas(self, width=width, height=height)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.pack()

        self.selected = None
        self.logic_board = server.get_board()

    def draw_board(self):
        self.canvas.delete("all")
        for (i, j) in product(range(10), range(10)):
            x1, y1 = (i * self.cellsize), (j * self.cellsize),
            x2, y2 = x1 + self.cellsize, y1 + self.cellsize
            cell = self.logic_board[i][j]
            color = "white" if cell == -1 else "black"
            board.draw_rectangle(x1, y1, x2, y2, color)
            if cell > 0:
                if cell == 1:
                    pawnColor = "red"
                elif cell == 2:
                    pawnColor = "blue"
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
            self.logic_board = self.server.handle_move(from_x, from_y, x, y)
            self.selected = None
            self.draw_board()
        elif self.logic_board[x][y] > 0:
            self.selected = (x, y)

        print("You clicked on cell (%s, %s)" % (x, y))

    def run(self):
        self.title("Draughts")
        self.draw_board()
        self.mainloop()


if __name__ == "__main__":
    server = Server()

    board = Board(server, 400, 400, 40)
    board.run()
