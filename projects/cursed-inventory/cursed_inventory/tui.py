import curses

@curses.wrapper
def main(stdscr):
    """Interactive deck building."""
    stdscr.clear()
    stdscr.refresh()
    c = stdscr.getkey()
