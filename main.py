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
    def __init__(self, width = 7, height = 3, x = 3, y = 3):
        self.icon = "."

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.subPanes: list[Pane] = []

    def addPane(self, pane: Pane):
        self.subPanes.append(pane)

    def generateContent(self) -> list[list]:
        # [TODO] Decide if I want to do 1D array or keep this 2D array (for performance reasons)
        content = [
            [self.icon for _ in range(self.width)]
            for _ in range(self.height)
        ]

        for pane in self.subPanes:
            subContent = pane.generateContent()
            for y in range(len(subContent)):
                for x in range(len(subContent[y])):
                    content[y + pane.y][x + pane.x] = subContent[y][x]

        return content

    def render(self):
        cursor_move(self.x, self.y)

        # [NOTE] Tradeoff of readability and speed
        content = self.generateContent()
        for row in content:
            sys.stdout.write("".join(row))

        sys.stdout.flush()

tWidth, tHeight = shutil.get_terminal_size()
mainPane = Pane(x = 0, y = 0, width = tWidth, height = tHeight)

a = Pane(x = 1, y = 1, width = 21, height = 7)
a.icon = "S"

b = Pane(x = 1, y = 1, width = 5, height = 3)
b.icon = "m"
a.addPane(b)

mainPane.addPane(a)
try:
    cursor_hide()

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if   key == b"a": a.x -= 1
            elif key == b"d": a.x += 1
            elif key == b"w": a.y -= 1
            elif key == b"s": a.y += 1

        mainPane.render()
        time.sleep(1.0 / 30.0)
finally:
    cursor_restore()
