'''
This file contains numeric bindings that refer to the colour settings of this application,
as well as a few other useful utilities.
'''

import curses;

# this is a terrible way of implementing C#-style enumerations,
# but it works for now I guess.

DEFAULT = 1; # white text black BG
MENU_SELECT = 2; # black-white highlight

# coloured text with black BG
TEXT_GREEN = 3;
TEXT_BLUE = 4;
TEXT_RED = 5;
TEXT_MAGENTA = 6;
TEXT_YELLOW = 7;

# special
BUTTON_RED = 8; # white-red highlight
BUTTON_BLACK_RED = 9; # black-red highlight

ESC_KEY = 27;

def init_curses_protocols(stdscr):
	curses.curs_set(False);
	curses.mousemask(-1);
	curses.mouseinterval(0);

	# colour bindings
	curses.init_pair(DEFAULT, curses.COLOR_WHITE, curses.COLOR_BLACK);
	curses.init_pair(MENU_SELECT, curses.COLOR_BLACK, curses.COLOR_WHITE);	
	
	curses.init_pair(TEXT_GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK);
	curses.init_pair(TEXT_BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK);
	curses.init_pair(TEXT_RED, curses.COLOR_RED, curses.COLOR_BLACK);
	curses.init_pair(TEXT_MAGENTA, curses.COLOR_MAGENTA, curses.COLOR_BLACK);
	curses.init_pair(TEXT_YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK);

	curses.init_pair(BUTTON_RED, curses.COLOR_WHITE, curses.COLOR_RED);
	curses.init_pair(BUTTON_BLACK_RED, curses.COLOR_BLACK, curses.COLOR_RED);
	

def write_text_with_colour(stdscr, y: int, x: int, text: str, colour_id: int):
	stdscr.attron(curses.color_pair(colour_id));
	stdscr.addstr(y, x, text);
	stdscr.attroff(curses.color_pair(colour_id));