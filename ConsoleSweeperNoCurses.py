#!/usr/bin/python3

from array import *
#from curses import *
from random import *
import string
from enum import Enum

debug = False

class Game:
	'''
	Games are abstract objects that are either finished or not.
	They also have a main loop, and a current score.
	'''
	def __init__(self):
		self.game_over = False
		self.score = 0
		self.started = False
	
	def main(self):
		'''
		All Games have main routine that comprises the core game loop.
		'''
		return 0

class CSBoard():
	'''
	This class encodes the board state of the ConsoleSweeper game.
	'''
	def __init__(self, grid_rows: int, grid_cols: int, num_mines: int):
		self.clicks_so_far = 0 #really, the number of "actions" so far
		self.rows = grid_rows
		self.cols = grid_cols
		self.mines = num_mines
		self.flags_left = num_mines + (grid_rows + grid_cols) // 4
		self.flags_placed = 0
		self.num_clicked_cells = 0
		self.make_board()

		if num_mines > grid_cols * grid_rows:
			raise Exception("The quantity of mines cannot exceed the size of the board.")

	def make_board(self):
		'''
		Constructs a 2-D List of CSTiles that represents the board.
		'''
		#initialization of board elements
		self.grid = []
		for i in range(self.rows):
			col = []
			for j in range(self.cols):
				col.append(CSTile())
			self.grid.append(col)
	
	def emplace_mines(self, forbidden: [int]):
		'''
		populates the board with mines.
		'''
		minecount = self.mines
		while minecount > 0:
			rowInt = randint(0, self.rows - 1)
			colInt = randint(0, self.cols - 1)
			while (self.grid[rowInt][colInt].is_mine() or (rowInt == forbidden[0] and colInt == forbidden[1])):
				rowInt = randint(0, self.rows - 1)
				colInt = randint(0, self.cols - 1) 

			self.grid[rowInt][colInt].plant_mine(True)
			minecount -= 1

		# update the mine counts of the board's occupants
		for i in range(self.rows):
			for j in range(self.cols):
				this_tile = self.grid[i][j]
				this_tile.num_mines_around = self.count_neighbours_deadly(i, j)

	def in_bounds(self, row: int, col: int) -> bool:
		'''
		Given a pair of integers, determine if the corresponding coordinates exist on the board.
		'''
		if row < 0 or col < 0:
			return False
		
		if row >= len(self.grid) or col >= len(self.grid[row]):
			return False 

		return True

	def count_neighbours_deadly(self, grid_row: int, grid_col: int) -> int:
		'''
		Counts the number of mines adjacent to this cell.
		'''
		neighbours = 0
		for x in [-1, 0, 1]:
			for y in [-1, 0, 1]:
				if self.in_bounds(grid_row + x, grid_col + y) and self.grid[grid_row + x][grid_col + y].is_mine():
					neighbours += 1
		return neighbours

	def grid_row_to_string(self, row: int, game_over: bool, mine_row: int, mine_col: int):
		this_row = self.grid[row]
		row_string = ""
		for col, tile in enumerate(this_row):
			if game_over:
				was_cause = False
				if row == mine_row and col == mine_col:
					was_cause = True
				row_string += tile.to_string_game_over(was_cause)
			else:
				row_string += tile.to_string()
		return row_string

	def print_grid_console(self):
		'''
		Produces formatted console output representing the board state.
		'''
		# TODO implement this lmao
		x = 1
		y = 1
		print("(^-^)7 \n")
		print("  ", end = "")
		#print column labels
		for col_elem in self.grid[0]:
			if (y >= 10):
				print(" " + str(y), end = "")
				y += 1
			elif (y < 10):
				print(" "+ str(y) +" ", end = "")
				y += 1
		print('')
		
		#print row labels
		for r in range(len(self.grid)):
			row_elem = self.grid[r]
			if (x < 10):
				print(str(x) + " ", end = "")
			else:
				print(str(x), end = "")
			
			#print cells
			for c in range(len(row_elem)):
				cell = row_elem[c]
				print(cell.to_string(), end = '')
			print('')
			x += 1
		print('')
	
	
	def print_grid_console_true(self, loss_row: int, loss_col: int):
		'''
		Produces formatted console output representing the true board state.
		'''
		x = 1
		y = 1
		print("(*-*) YOU LOST")
		print("  ", end = "")
		
		#print column labels
		for col_elem in self.grid[0]:
			if (y >= 10):
				print(" " + str(y), end = "")
				y += 1
			elif (y < 10):
				print(" " + str(y) + " ", end = "")
				y += 1
		print('')
		
		#print row labels
		for r in range(len(self.grid)):
			row_elem = self.grid[r]
			if (x < 10):
				print(str(x) + " ", end = "")
			else:
				print(str(x), end = "")
			
			#print cells
			for c in range(len(row_elem)):
				cell = row_elem[c]
				was_cause = (r == loss_row and c == loss_col)
				print(cell.to_string_game_over(was_cause), end = "")
			print('')
			x += 1
		print('')
	
	def reveal_tile(self, row_int: int, col_int: int) -> bool:
		'''
		Recursively "clicks" all tiles in a given cell's reveal group,
		i.e. all tiles reachable from this one with no surrounding mines
		up to the first tiles encountered with some number of surrounding mines.
		'''
		this_tile = self.grid[row_int][col_int]
		if(this_tile.is_clicked()):
			return True

		this_tile.click()
		self.num_clicked_cells += 1

		if this_tile.is_mine():
			return False
		else:
			deadlyneighbors = self.grid[row_int][col_int].num_mines_around
			if(deadlyneighbors == 0):
				for x in [-1, 0, 1]:
					for y in [-1, 0, 1]:
						x_nbr = row_int + x
						y_nbr = col_int + y
						if self.in_bounds(x_nbr, y_nbr) and not self.grid[x_nbr][y_nbr].is_clicked():
							self.reveal_tile(x_nbr, y_nbr)
		return True
	
	def check_win_cond(self) -> bool:
		#check normal win
		if(self.rows * self.cols == self.num_clicked_cells + self.mines):
			return True
		
		#check flags win
		mines_flagged = 0
		for row in range(self.rows):
			for col in range(self.cols):
				if (self.grid[row][col].is_mine() and self.grid[row][col].is_flagged()):
					mines_flagged += 1
		if (mines_flagged == self.mines):
			return True

		return False    



class CSTile:
	'''
	This class wraps all information about a minesweeper tile into one object.
	'''
	def __init__(self):
		self.contains_mine = False
		self.been_clicked = False
		self.flagged = False
		self.num_mines_around = 0 

		# these might be unnecessary
		#self._coords = [row, col] 
	
	'''
	def get_row(self):
		return self.row
	def get_col(self):
		return self.col
	'''

	def click(self):
		self.been_clicked = True
	def is_clicked(self) -> bool:
		return self.been_clicked

	def plant_flag(self, is_flag: bool):
		self.flagged = is_flag
	def is_flagged(self) -> bool:
		return self.flagged
	
	def plant_mine(self, mine: bool):
		self.contains_mine = mine
	def is_mine(self) -> bool:
		return self.contains_mine

	'''
	property(plant_flag, is_flagged)
	property(plant_mine, is_mine)
	'''

	def to_string(self) -> str:
		symbol = None
		string = None
		if(self.is_clicked()):
			symbol = str(self.num_mines_around)
		elif(self.is_flagged()):
			symbol = 'P'
		else:
			symbol = ' '
		string = "({})".format(symbol)
		return string

	def to_string_game_over(self, was_cause: bool) -> str:
		symbol = None
		string = None
		if(was_cause):
			symbol = '#'
		elif(self.is_mine()):
			symbol = '*'
		elif(self.is_flagged()):
			symbol = 'P'
		else:
			symbol = str(self.num_mines_around)
		string = "({})".format(symbol)
		return string
 
class CSChoice(Enum):
	EXIT = 0
	RETURN = 1
	FLAG = 2
	CLICK = 3

class CSDifficulty(Enum):
	EASY = 0.08
	NORMAL = 0.12
	HARD = 0.17
	BRUTAL = 0.25

class ConsoleSweeper(Game):

	def __init__(self):
	 super().__init__()

	def main(self):
		#ask for board dimensions and difficulty
		dimension = self.get_dimension()
		mine_count = self.get_difficulty(dimension)

		self.board = CSBoard(dimension, dimension, mine_count)

		num_rows = self.board.rows
		num_cols = self.board.cols
		game_grid = self.board.grid

		self.board.print_grid_console()

		# main game loop
		while not self.game_over:
			temp_col = self.get_column_input()
			temp_row = self.get_row_input()
			selection_switch = self.game_options_display()
			temp_tile = game_grid[temp_row][temp_col]

			if (not (selection_switch == CSChoice.EXIT or selection_switch == CSChoice.RETURN)):

				# toggle flag choice
				if (selection_switch == CSChoice.FLAG):
					if (self.board.flags_left > 0):
						if (not temp_tile.is_clicked()):
							game_grid[temp_row][temp_col].plant_flag(not game_grid[temp_row][temp_col].is_flagged())
							self.board.flags_left = self.board.flags_left - 1 if game_grid[temp_row][temp_col].is_flagged() else self.board.flags_left + 1
						else:
							print("This cell is already clicked. Boi")
					else:
						if temp_tile.is_flagged():
							self.board.flags_left += 1
							game_grid[temp_row][temp_col].plant_flag(False)
						else:
							print("You have no flags left.")

				# click choice
				elif (selection_switch == CSChoice.CLICK):

					# populate board with mines at random locations,
					# but only after the first click.
					if (self.board.clicks_so_far == 0): 
						self.board.emplace_mines((temp_row, temp_col))
					
					is_fine = self.board.reveal_tile(temp_row, temp_col)
					self.board.clicks_so_far += 1
					if debug:
						self.board.print_grid_console_true()

					if (not is_fine):
						self.game_over = True
						self.board.print_grid_console_true(temp_row, temp_col)
						break
			elif selection_switch == CSChoice.EXIT:
				break

			
			
			if (self.board.check_win_cond()):
				print("Congratulation  Y O U  W I N\n")
				print("Did it in " + str(self.board.clicks_so_far) + " clicks. Pretty Spicy.")
				self.board.print_grid_console_true()
				break
			else:
				self.board.print_grid_console()
		
		self.restart()
	
	def get_click(self):
		self.get_column_input()
		self.get_row_input()

	def get_dimension(self):
		valid = False
		
		# make the engine sound as unreasonable as possible
		while(not valid):
			dim_str = input("Give me a board size between 10 and 50: ")
			try:
				dim = (int(dim_str.strip(string.ascii_letters)))
				valid = True
				if(not (dim <= 50 and dim >= 10)):
					print("Can you even read? Try again.")
					valid = False
	
			except:
				print("Boi. Try something that makes sense this time.")
				valid = False
		
		return dim

	def get_difficulty(self, dim):
		valid = False
		choice = input("Easy, Normal, Hard, Brutal? (E, N, H, B): ")
		board_size = dim * dim

		if (choice.upper() == "E" or choice.upper() == "EASY"):
			return int(board_size * 0.1)
		elif (choice.upper() == "N" or choice.upper() == "NORMAL"):
			return int(board_size * 0.15)
		elif (choice.upper() == "H" or choice.upper() == "HARD"):
			return int(board_size * 0.20)
		elif (choice.upper() == "B" or choice.upper() == "BRUTAL"):
			return int(board_size * 0.30)
		else:
			print("Normal it is, then.")
			return int(board_size * 0.15)

	def get_column_input(self):
		valid = False

		while(not valid):
			col_string = input("X Co-ordinate from LEFT, Expressed as an Integer from 1-" + str(self.board.cols) + ": ")
			try:
				col = (int(col_string.strip(string.ascii_letters)))
				valid = True
				if(not (col <= len(self.board.grid[0]) and col > 0)):
					print("Can you even read? Try again.")
					valid = False
	
			except:
				print("Boi. Try something that makes sense this time.")
				valid = False
		
		col -= 1
		return col

	def get_row_input(self):
		valid = False
		
		while(not valid):
			row_string = input("Y Co-ordinate from TOP, Expressed as an Integer from 1-" + str(self.board.rows) + ": ")
			try:
				row = (int(row_string.strip(string.ascii_letters)))
				valid = True

				if(not (row <= len(self.board.grid) and row > 0)):
					print("Can you even read? Try again.")
					valid = False
				
			except:
				print("Boi. Try something that makes sense this time.")
				valid = False
		
		row -= 1
		return row
	
	def game_options_display(self):
		choice = input("Toggle Flag, Return, or Click (F, R, C)?: ")

		if (choice.upper() == "R" or choice.upper() == "RETURN"):
			return CSChoice.RETURN
		elif (choice.upper() == "F" or choice.upper() == "FLAG"):
			return CSChoice.FLAG
		elif (choice.upper() == "C" or choice.upper() == "CLICK"):
			return CSChoice.CLICK
		elif (choice.upper() == "EXIT" or choice.upper() == "QUIT"):
			return CSChoice.EXIT
		else:
			print("I'm not going to deal with this. Returning to co-ordinate selection.")
			return CSChoice.RETURN
	
	def restart(self):
		choice = input("Try again? y/n?: ")
		self.game_over = False
		self.board.flags_left = self.board.mines + ((self.board.rows + self.board.cols) / 4)
		self.board.clicks_so_far = 0
		if (choice.upper() == ("Y") or choice.upper() == ("YES")):
			self.started = True
			self.main()
		elif (choice.upper() == ("N") or choice.upper() == ("NO")):
			self.started = False
			self.main()
		else:
			print("You're really just impossible to reason with, you know? Bbbbbye")
			print("Logging off...")

def main_loop():
	Game = ConsoleSweeper()

	print("--------------------------------------")
	print(" WELCOME TO THE FUNNY CONSOLESWEEPER ")
	print("--------------------------------------\n")
	print("Please enter your first coordinates.\n")

	Game.main()

main_loop()
