class Server():
	
	def __init__(self):
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
		if self.logic_board[to_x][to_y] == 0:
			self.logic_board[to_x][to_y] = self.logic_board[from_x][from_y]
			self.logic_board[from_x][from_y] = 0

		return self.logic_board

	def get_board(self):
		return self.logic_board