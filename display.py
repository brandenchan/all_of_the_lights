import curses

INDENT = 3
WORD_LEN = 20

PHASE_LINE = 4

TEMPO_LINE = 6
SPEED_LINE = 7
SYNC_LINE = 8

MODE_LINE = 10
BRIGHT_LINE = 11
SATURATION_LINE = 12

MUTE_MODE_LINE = 14
MUTE_LINE = 15

DEBUG_LINE = 16
FREQ_LINE = 17

# MAYBE DONT UPDATE SO MUCH

class Display:
    def __init__(self):
        self.s = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.s.keypad(1)
        self.s.nodelay(1)

        self.s.addstr(0, 0, "____ _    _       ____ ____    ___ _  _ ____    _    _ ____ _  _ ___ ____ ")
        self.s.addstr(1, 0, "|__| |    |       |  | |___     |  |__| |___    |    | | __ |__|  |  [__  ")
        self.s.addstr(2, 0, "|  | |___ |___    |__| |        |  |  | |___    |___ | |__] |  |  |  ___] ")

        self.s.addstr(TEMPO_LINE,
                      INDENT,
                      "(space) Tempo: ")
        self.s.addstr(MODE_LINE,
                      INDENT,
                      " (asd)  Mode: ")
        self.s.addstr(BRIGHT_LINE,
                      INDENT,
                      " (< >)  Brightness: ")
        self.s.addstr(SPEED_LINE,
                      INDENT,
                      " (^ v)  Speed: ")
        self.s.addstr(SATURATION_LINE,
                      INDENT,
                      " (- +)  Saturation: ")
        self.s.addstr(MUTE_MODE_LINE,
                      INDENT,
                      " (qwe)  Mute Mode: ")                     
        self.s.addstr(MUTE_LINE,
                      INDENT,
                      "(enter) Mute: ")
        self.s.addstr(SYNC_LINE,
                      INDENT,
                      "  (c)   Sync")
        self.s.refresh()

    def getch(self):
        return self.s.getch()

    def update(self,
               tempo,
               mode,
               brightness,
               speed,
               saturation,
               phase,
               direction,
               mute_name,
               mute):
        self.set_field("tempo", tempo)
        self.set_field("mode", mode)
        self.set_field("brightness", brightness)
        self.set_field("speed", speed)
        self.set_field("saturation", saturation)
        self.set_field("mute_mode", mute_name)
        self.set_field("mute", mute)

        self.draw_phase(phase, direction, speed)
        self.s.move(15,0)
        self.s.refresh()

    def set_field(self, cat, val, indent=3, word_len=0):

        if cat == "tempo":
            line = TEMPO_LINE
            word_len = WORD_LEN
            string = str(round(val, 1))

        elif cat == "debug":
            line = DEBUG_LINE
            string = str(val)

        elif cat == "freq":
            line = FREQ_LINE
            string = str(val)

        elif cat == "mode":
            line = MODE_LINE
            word_len = WORD_LEN
            string = str(val)

        elif cat == "brightness":
            line = BRIGHT_LINE
            word_len = WORD_LEN
            string = str(int(round(val, 2) * 100)) + "%" 

        elif cat == "speed":
            line = SPEED_LINE
            word_len = WORD_LEN
            if val >= 1:
                string = str(int(val)) + "x"
            else:
                n, d = (val).as_integer_ratio()
                string = "{}/{}".format(n, d) + "x"

        elif cat == "saturation":
            line = SATURATION_LINE
            word_len = WORD_LEN
            string = str(int(val * 100)) + "%"
        
        elif cat == "mute_mode":
            line = MUTE_MODE_LINE
            word_len = WORD_LEN
            string = val

        elif cat == "mute":
            line = MUTE_LINE
            word_len = WORD_LEN
            if val:
                string = "On"
            else:
                string = "Off"

        self.s.move(line, indent + word_len)
        self.s.clrtoeol()
        self.s.addstr(line, indent + word_len, string)

    def draw_phase(self, phase, direction, multiplier, size=30):            
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
