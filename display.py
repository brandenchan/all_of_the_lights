import curses
# from pyfiglet import Figlet

INDENT = 3
TITLE_LINE = 2
TEMPO_LINE = 4
DEBUG_LINE = 12
FREQ_LINE = 13

class Display:
    def __init__(self):
        # self.f = Figlet(font="speed", outputwidth="1")
        self.s = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.s.keypad(1)
        self.s.nodelay(1)
        title = "ALL OF THE LIGHTS"
        self.s.addstr(TITLE_LINE,
                      INDENT,
                      title)
        # self.s.box()
        self.s.addstr(TEMPO_LINE,
                      INDENT,
                      "Tempo: ")
        self.s.refresh()

    def getch(self):
        return self.s.getch()


    def update(self, cat, val, indent=3, word_len=0):

        if cat == "tempo":
            line = TEMPO_LINE
            word_len = 7
            string = str(round(val, 1))

        elif cat == "debug":
            line = DEBUG_LINE
            word_len = 0
            string = str(val)

        elif cat == "freq":
            line = FREQ_LINE
            string = str(val)
        
        self.s.move(line, indent + word_len)
        self.s.clrtoeol()
        self.s.addstr(line, indent + word_len, string)
        self.s.move(0,0)
        self.s.refresh()

    def close(self):
        curses.nocbreak()
        self.s.keypad(0)
        curses.echo()
        curses.endwin()

    # def draw_box(self):
    #     self.std