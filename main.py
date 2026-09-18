from __future__ import annotations

import sys
import time
import shutil
import msvcrt

def cursor_hide():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def cursor_restore():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def cursor_move(x, y):
    sys.stdout.write(f"\033[{y + 1};{x + 1}H")    # Silly ANSI is 1 indexed wheras python is 0 indexed
    sys.stdout.flush()

def screen_clear():
    sys.stdout.write("\033[2J")
    sys.stdout.flush()

def cursor_reset():
    cursor_move(0, 0)

class Pane:
    def __init__(self, x = 3, y = 3, width = 7, height = 3, background = " "):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.background = background

        self.subPanes: list[Pane] = []

    def add_pane(self, pane: Pane):
        if pane not in self.subPanes:
            self.subPanes.append(pane)

    def remove_pane(self, pane: Pane):
        if pane in self.subPanes:
            self.subPanes.remove(pane)

    def generateContent(self) -> list[list]:
        # [TODO] Decide if I want to do 1D array or keep this 2D array (for performance reasons)
        content = [
            [self.background for _ in range(self.width)]
            for _ in range(self.height)
        ]

        # [BUG] There is a situation where a pane is drawn on the other side of the screen if it goes under x = 0
        for pane in self.subPanes:
            subContent = pane.generateContent()
            for y in range(len(subContent)):
                for x in range(len(subContent[y])):
                    try:
                        content[y + pane.y][x + pane.x] = subContent[y][x]
                    except:
                        pass

        return content

    def render(self):
        cursor_move(self.x, self.y)

        # [NOTE] Tradeoff of readability and speed
        content = self.generateContent()
        for row in content:
            sys.stdout.write("".join(row))

        sys.stdout.flush()

tWidth, tHeight = shutil.get_terminal_size()
mainPane = Pane(x = 0, y = 0, width = tWidth, height = tHeight, background = ".")
a = Pane(x = 1, y = 1, width = 21, height = 7, background = "a")
b = Pane(x = 1, y = 1, width = 5, height = 3, background = "b")

a.add_pane(b)
mainPane.add_pane(a)

try:
    cursor_hide()

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if   key == b"a": b.x -= 1
            elif key == b"d": b.x += 1
            elif key == b"w": b.y -= 1
            elif key == b"s": b.y += 1

        mainPane.render()
        time.sleep(1.0 / 30.0)
finally:
    cursor_restore()
