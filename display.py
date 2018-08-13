import curses
# from pyfiglet import Figlet

INDENT = 3
TITLE_LINE = 2
PHASE_LINE = 3
TEMPO_LINE = 5
MODE_LINE = 6
BRIGHT_LINE = 7
SPEED_LINE = 8
SATURATION_LINE = 9
DEBUG_LINE = 12
FREQ_LINE = 13

# MAYBE DONT UPDATE SO MUCH

class Display:
    def __init__(self, tempo, mode, brightness, speed, saturation):
        self.s = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.s.keypad(1)
        self.s.nodelay(1)
        title = "ALL OF THE LIGHTS"
        self.s.addstr(TITLE_LINE,
                      INDENT,
                      title)
        self.s.addstr(TEMPO_LINE,
                      INDENT,
                      "Tempo: ")
        self.s.addstr(MODE_LINE,
                      INDENT,
                      "Mode: ")
        self.s.addstr(BRIGHT_LINE,
                      INDENT,
                      "Brightness: ")
        self.s.addstr(SPEED_LINE,
                      INDENT,
                      "Speed: ")
        self.s.addstr(SATURATION_LINE,
                      INDENT,
                      "Saturation: ")
        self.update("tempo", tempo)
        self.update("mode", mode)
        self.update("brightness", brightness)
        self.update("speed", speed)
        self.update("saturation", saturation)
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

        elif cat == "mode":
            line = MODE_LINE
            word_len = 6
            string = str(val)

        elif cat == "brightness":
            line = BRIGHT_LINE
            word_len = 12
            string = str(int(round(val, 2) * 100)) + "%" 

        elif cat == "speed":
            line = SPEED_LINE
            word_len = 12
            if val >= 1:
                string = str(int(val)) + "x"
            else:
                n, d = (val).as_integer_ratio()
                string = "{}/{}".format(n, d) + "x"

        elif cat == "saturation":
            line = SATURATION_LINE
            word_len = 12
            string = str(int(val * 100)) + "%"
        
        self.s.move(line, indent + word_len)
        self.s.clrtoeol()
        self.s.addstr(line, indent + word_len, string)
        self.s.move(0,0)
        self.s.refresh()

    def draw_phase(self, phase, direction, multiplier, size=20):            
        step = 1. / size
        p = phase // step
        if direction == 1:
            p = size - p

        self.s.move(PHASE_LINE, INDENT)
        self.s.clrtoeol()
        self.s.addstr("|")
        for i in range(size):
            if i == p:
                self.s.addstr("X")
            else:
                self.s.addstr(" ")
        self.s.addstr("|")
        
        

    def close(self):
        curses.nocbreak()
        self.s.keypad(0)
        curses.echo()
        curses.endwin()

    # def draw_box(self):
    #     self.std