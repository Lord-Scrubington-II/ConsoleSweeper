'''
This file and its dependencies define the logic that controls the front end for a version of MineSweeper that runs in the terminal.
The Curses library was used to handle formatted console output, mouse events, and key events to simulate a GUI.
Author: Zane Wang

Settings for the game can be changed in the settings.json file.
'''

import curses
from curses import textpad

import time
import string
from random import *
from enum import Enum
from array import *
import json
import math

# TODO These might need to be changed before the final build
from bin import ConsoleSweeperBones
from bin import CursesUtils

class GLOBAL_STATES(Enum):
	MAIN_MENU = 0;
	MINESWEEPER = 1;
	MINESWEEPER_LOSS = 2;
	SETTINGS = 3;
	SCOREBOARD = 4;

APP_GLOBAL_STATE = GLOBAL_STATES.MAIN_MENU;

# load settings from JSON
try:
	APP_GLOBAL_SETTINGS_JSON = json.load(open("./bin/settings.json"))
except:
	#emergency default values
	APP_GLOBAL_SETTINGS_JSON = { 
		"grid_rows": 12,
		"grid_cols": 12,
		"difficulty": "NORMAL",
		"colours": True,
		"time_trial": False,
		"time_limit": 100 
	}

SCENE_TRANSITION_DELAY = 2 

# information about the minesweeper board
MS_BOARD_SIZE_ROWS = APP_GLOBAL_SETTINGS_JSON['grid_rows']
MS_BOARD_SIZE_COLS = APP_GLOBAL_SETTINGS_JSON['grid_cols']
MS_USING_COLOURS = APP_GLOBAL_SETTINGS_JSON['colours']
MS_BOARD_DIFFICULTY = "";
try:
	APP_GLOBAL_SETTINGS_JSON['difficulty'] = APP_GLOBAL_SETTINGS_JSON['difficulty'].upper()
	MS_BOARD_DIFFICULTY = ConsoleSweeperBones.CSDifficulty[APP_GLOBAL_SETTINGS_JSON['difficulty'].upper()].value;
except:
	MS_BOARD_DIFFICULTY = ConsoleSweeperBones.CSDifficulty["NORMAL"].value;

def main(stdscr) -> int:
	CursesUtils.init_curses_protocols(stdscr);
	
	GAME_EXIT_SIGNAL = False;

	while not GAME_EXIT_SIGNAL:
		APP_GLOBAL_STATE = GLOBAL_STATES.MAIN_MENU
		
		choice = handle_main_menu(stdscr);
		# resolve app state by use choice, 
		# then reroute the user to a different screen depending on app state
		if (choice == MAIN_MENU_CHOICES.LEAVE):
			GAME_EXIT_SIGNAL = True;
		elif (choice == MAIN_MENU_CHOICES.PLAY):
			APP_GLOBAL_STATE = GLOBAL_STATES.MINESWEEPER
			minesweeper_main(stdscr);
		
		# TODO: these are unimplemented
		elif (choice == MAIN_MENU_CHOICES.SETTINGS):
			APP_GLOBAL_STATE = GLOBAL_STATES.SETTINGS
			handle_settings_menu(stdscr);
			
		elif (choice == MAIN_MENU_CHOICES.SCOREBOARD):
			APP_GLOBAL_STATE = GLOBAL_STATES.SCOREBOARD
		else:
			raise AssertionError("Main Menu function returned unresolvable value.");
			return 1;

	#write settings back to JSON
	with open("./bin/settings.json", 'w') as json_fp:
		json.dump(APP_GLOBAL_SETTINGS_JSON, json_fp);
	return 0;


line_delim_pad = "--------------------------------"
logo_text      =     "WELCOME TO CURSEDSWEEPER"
version_text   = "--------------v0.1--------------"
funny_emoticon = "(*^-^*)/"

title_logo = [line_delim_pad, logo_text, version_text, funny_emoticon]
menu_elems = ['Play', 'Settings', 'ScoreBoard', 'Exit'];
completed_menu_features = [0, 3]

# main menu choices
class MAIN_MENU_CHOICES(Enum):
	PLAY = 0
	SETTINGS = 1
	SCOREBOARD = 2
	LEAVE = 3

def handle_main_menu(stdscr) -> int:
	menu_row_ind = 0; # reference menu elements by index
	print_main_menu(stdscr, menu_row_ind);
	selection_made = False;
	height, width = stdscr.getmaxyx();

	while not selection_made:
		key = stdscr.getch(); 
		stdscr.clear();

		if (key == curses.KEY_UP):
			if (menu_row_ind == 0):
				menu_row_ind = len(menu_elems) - 1;
			else: 
				menu_row_ind -= 1;

		elif (key == curses.KEY_DOWN):
			menu_row_ind = (menu_row_ind + 1) % 4;

		elif (key == curses.KEY_ENTER or key in [10, 13]):
			
			if(menu_row_ind not in completed_menu_features):
				stdscr.addstr(0, 0, "Feature Coming Soon!");
				stdscr.refresh();
				stdscr.getch();
			else:
				selection_made = True;
				
		# mouse on main menu elements
		elif(key == curses.KEY_MOUSE):
			_, x, y, _, _ = curses.getmouse();

			for ind, text in enumerate(menu_elems):
				menu_x = (width // 2) - (len(text) // 2);
				menu_y = (height // 2) - (len(menu_elems) // 2);
				menu_y_true = menu_y + ind;
				
				if y == menu_y_true and x in range(menu_x, menu_x + len(text)):
					menu_row_ind = ind;
					stdscr.refresh();
					return MAIN_MENU_CHOICES(menu_row_ind);
		print_main_menu(stdscr, menu_row_ind);
	
	return MAIN_MENU_CHOICES(menu_row_ind);

def print_main_menu(stdscr, selected_row_ind: int):
	stdscr.clear();
	height, width = stdscr.getmaxyx();

	# draw a box
	box = [[1,3], [height - 1, width - 3]]
	textpad.rectangle(stdscr, box[0][0], box [0][1], box[1][0], box[1][1])

	#display title
	for ind, text in enumerate(title_logo):

		# align the text
		x = (width // 2) - (len(text) // 2);

		# center the text around the midpoint of the screen 
		# and increment the y level for each element
		y = (height // 4) - (len(menu_elems) // 2) + ind;
		stdscr.addstr(y, x, text)

	#display main menu elems
	for ind, text in enumerate(menu_elems):
		x = (width // 2) - (len(text) // 2);
		y = (height // 2) - (len(menu_elems) // 2) + ind;

		# highlight element by index selected
		if ind == selected_row_ind:
			CursesUtils.write_text_with_colour(stdscr, y, x, text, CursesUtils.MENU_SELECT);
		else:
			stdscr.addstr(y, x, text);	
	
	stdscr.refresh();
	return 0;

def handle_settings_menu(stdscr):
	return 0;

return_button    = "<< Return to Menu "
return_button_row_col = (2, 5);
line_delim_pad_2 = "--------------------------------"
game_top_text    =         "MINESWEEPER TIME"
tame_top_text_funny =      "MEMESWEEPER TIME"
game_top_text_win        = "YOU WIN!"
game_top_text_game_over  = "YOU LOSE."
funny_emoticon_game      = "(>*-*)>"
funny_emoticon_win       = "\(*^-^*)/"
funny_emoticon_game_over =  "(/>_<)/"

game_top_logo = [line_delim_pad_2, game_top_text, line_delim_pad_2, funny_emoticon_game]
game_over_top_logo = [line_delim_pad_2, game_top_text_game_over, line_delim_pad_2, funny_emoticon_game_over]
game_won_top_logo = [line_delim_pad_2, game_top_text_win, line_delim_pad_2, funny_emoticon_win]

def minesweeper_main(stdscr):
	time_start = time.time();
	elapsed = 0;
	game_over = False;
	voluntary_exit = False;
	row_char_length = 3 * MS_BOARD_SIZE_COLS;
	height, width = stdscr.getmaxyx();

	num_mines = MS_BOARD_DIFFICULTY * (MS_BOARD_SIZE_ROWS * MS_BOARD_SIZE_COLS);
	board = ConsoleSweeperBones.CSBoard(MS_BOARD_SIZE_ROWS, MS_BOARD_SIZE_COLS, num_mines);
	game_grid = board.grid;
	print_ms_grid(stdscr, board, height, width);

	while not (game_over or voluntary_exit):
		key = stdscr.getch(); 
		height, width = stdscr.getmaxyx();		

		if(key == curses.KEY_MOUSE):
			_, x, y, _, bstate = curses.getmouse();
			
			grid_start_x = (width // 2) - (row_char_length // 2);
			grid_start_y = int(height * 0.6) - (board.rows // 2);
			
			grid_coords = get_grid_coords_from_mouseyx(grid_start_y, grid_start_x, y, x);
			temp_row = grid_coords[0];
			temp_col = grid_coords[1];

			# the board ignores out of bounds mouse events
			if(board.in_bounds(temp_row, temp_col)):

				temp_tile = game_grid[temp_row][temp_col];

				# flag
				if (bstate & curses.BUTTON3_PRESSED):

					if (board.flags_left > 0):
						if (not temp_tile.is_clicked()):
							game_grid[temp_row][temp_col].plant_flag(not game_grid[temp_row][temp_col].is_flagged());
							board.flags_left = board.flags_left - 1 if game_grid[temp_row][temp_col].is_flagged() else board.flags_left + 1;
					else:
						if temp_tile.is_flagged():
							board.flags_left += 1;
							game_grid[temp_row][temp_col].plant_flag(False);
				#reveal
				elif((bstate & curses.BUTTON1_PRESSED) and not temp_tile.is_flagged()): 

						# populate board with mines at random locations,
						# but only after the first click.
						if board.clicks_so_far == 0:
							board.emplace_mines([temp_row, temp_col]);
						
						is_fine = board.reveal_tile(temp_row, temp_col);
						board.clicks_so_far += 1;

						if (not is_fine):
							game_over = True;
							elapsed = time.time() - time_start;
							print_ms_grid_true(stdscr, board, game_over, temp_row, temp_col, height, width, elapsed);
							break;

				print_ms_grid(stdscr, board, height, width);
				if (board.check_win_cond()):
					elapsed = time.time() - time_start;
					print_ms_grid_true(stdscr, board, game_over, -1, -1, height, width, elapsed);
					break;
			else:
				if (y == return_button_row_col[0] and x in range(return_button_row_col[1], return_button_row_col[1] + len(return_button))):
					return;
		elif key == CursesUtils.ESC_KEY:
			# for some reason ESC key events have an implicit delay associated with them.
			# I seriously have no idea why.
			return;

	# there's probably a much cleaner, less bad way to prevent the mouseUp event
	# from un-halting the program, but I don't have time to figure it out.
	time.sleep(SCENE_TRANSITION_DELAY);
	stdscr.getch();
	stdscr.getch();
	

def print_ms_grid(stdscr, board: ConsoleSweeperBones.CSBoard, height: int, width: int):
	stdscr.clear();
	
	num_rows = board.rows;
	num_cols = board.cols;

	row_char_length = 3 * num_cols;

	# draw a box, again
	box = [[1, 3], [height - 1, width - 3]]
	textpad.rectangle(stdscr, box[0][0], box [0][1], box[1][0], box[1][1])

	# anchor grid to the centre of the screen
	msgrid = board.grid;
	grid_start_x = calc_grid_start_x(width, row_char_length);
	grid_start_y = calc_grid_start_y(height, num_rows);

	#display logo
	for ind, text in enumerate(game_top_logo):
		x = (width // 2) - (len(text) // 2);
		y = (height // 6) - (len(menu_elems) // 2) + ind;
		stdscr.addstr(y, x, text)
		
	# display return text
	CursesUtils.write_text_with_colour(stdscr, return_button_row_col[0], return_button_row_col[1], return_button, CursesUtils.MENU_SELECT);

	for col_ind in range(0, num_cols * 3, 3):
		stdscr.addstr(grid_start_y - 1, grid_start_x + col_ind + 1, str(col_ind // 3 + 1) + "  ");

	#render grid tiles
	for row_ind in range(num_rows):

		# this should be updated to support coloured numbers.
		# the string-splicing might get expensive eventually, though.
		row_str = board.grid_row_to_string(row_ind, False, -1, -1);
		grid_start_y_true = grid_start_y + row_ind;
		stdscr.addstr(grid_start_y_true, grid_start_x - 2, str(row_ind + 1));

		#colours support
		if(MS_USING_COLOURS):
			for offset, symbol in enumerate(row_str):
				colour_to_use = get_colour_by_symbol(symbol)
				CursesUtils.write_text_with_colour(stdscr, grid_start_y_true, grid_start_x + offset, symbol, colour_to_use);
		else:
			stdscr.addstr(grid_start_y_true, grid_start_x, row_str);
	
	# print flags left
	stdscr.addstr(grid_start_y + num_rows, grid_start_x, "Flags left: " + str(int(board.flags_left)));
	
	stdscr.refresh();

	return 0;

def print_ms_grid_true(stdscr, board: ConsoleSweeperBones.CSBoard, loss: bool, mine_row: int, mine_col: int, height: int, width: int, elapsed: float):
	stdscr.clear();
	
	num_rows = board.rows;
	num_cols = board.cols;

	row_char_length = 3 * num_cols;

	# draw a box, again
	box = [[1,3], [height - 1, width - 3]]
	textpad.rectangle(stdscr, box[0][0], box [0][1], box[1][0], box[1][1])

	msgrid = board.grid;
	grid_start_x = calc_grid_start_x(width, row_char_length);
	grid_start_y = calc_grid_start_y(height, num_rows);
	
	to_display = game_won_top_logo if not loss else game_over_top_logo;
	
	#display logo
	display_logo(stdscr, to_display);

	for col_ind in range(0, num_cols * 3, 3):
		stdscr.addstr(grid_start_y - 1, grid_start_x + col_ind + 1, str(col_ind // 3 + 1) + "  ");

	#render grid tiles
	for row_ind in range(num_rows):

		# this should be updated to support coloured numbers.
		# the string-splicing might get expensive eventually, though.
		row_str = board.grid_row_to_string(row_ind, True, mine_row, mine_col);
		grid_start_y_true = grid_start_y + row_ind;
		stdscr.addstr(grid_start_y_true, grid_start_x - 2, str(row_ind + 1));

		#colours support
		if(MS_USING_COLOURS):
			for offset, symbol in enumerate(row_str):
				colour_to_use = get_colour_by_symbol(symbol);		
				CursesUtils.write_text_with_colour(stdscr, grid_start_y_true, grid_start_x + offset, symbol, colour_to_use);
		else:
			stdscr.addstr(grid_start_y_true, grid_start_x, row_str);
	
	# print flags left and time used
	stdscr.addstr(grid_start_y + num_rows, grid_start_x, "Flags left: " + str(int(board.flags_left)));
	stdscr.addstr(grid_start_y + num_rows + 1, grid_start_x, "Time elapsed: " + str(math.floor(elapsed * 1000) / 1000) + " seconds");
	stdscr.refresh();

	return 0;

def display_logo(stdscr, to_display):
	height, width = stdscr.getmaxyx();
	for ind, text in enumerate(to_display):
		x = (width // 2) - (len(text) // 2);
		y = (height // 6) - (len(menu_elems) // 2) + ind;
		stdscr.addstr(y, x, text)
	stdscr.refresh()

# this is some lame shit right here, but it works, I guess.
def get_colour_by_symbol(symbol):
	if(symbol not in ['(', ')']):
		if (symbol == "0"):
			colour_to_use = CursesUtils.DEFAULT;
		elif (symbol == "1"):
			colour_to_use = CursesUtils.TEXT_GREEN;
		elif (symbol == "2"):
			colour_to_use = CursesUtils.TEXT_BLUE;
		elif (symbol == "3"):
			colour_to_use = CursesUtils.TEXT_RED;
		elif (symbol == "P"):
			colour_to_use = CursesUtils.TEXT_YELLOW;
		elif (symbol == "*"):
			colour_to_use = CursesUtils.MENU_SELECT;
		elif (symbol == "#"):
			colour_to_use = CursesUtils.BUTTON_BLACK_RED;
		else:
			colour_to_use = CursesUtils.TEXT_MAGENTA;
	else:
		colour_to_use = CursesUtils.DEFAULT;
	return colour_to_use;

def calc_grid_start_y(window_height: int, num_rows: int):
	return int(window_height * 0.6) - (num_rows // 2);

def calc_grid_start_x(window_width: int, row_char_length: int):
	return (window_width // 2) - (row_char_length // 2);

def get_grid_coords_from_mouseyx(grid_start_y: int, grid_start_x: int, mouse_y: int, mouse_x: int) -> (int, int):
	true_grid_y = mouse_y - grid_start_y;
	true_grid_x = (mouse_x - grid_start_x) // 3;
	return (true_grid_y, true_grid_x)


curses.wrapper(main);
