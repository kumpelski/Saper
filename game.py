import random
import time


class GameHandler:

    def __init__(self):
        self.w = 30
        self.h = 16
        self.b = 99
        self.is_checked = None
        self.is_bomb = None
        self.is_flag = None
        self.field_value = None
        self.won = None
        self.lost = None
        self.first_lmb = None
        self.timer_start = None
        self.timer_stop = None

    def start(self, w, h, b):
        self.w = w
        self.h = h
        self.b = b
        self.start_custom()

    def start_custom(self):
        self.first_lmb = True
        self.won = False
        self.lost = False
        self.timer_start = None
        self.timer_stop = None
        self.is_checked = [[False for _ in range(self.h)] for _ in range(self.w)]
        self.is_bomb = [[False for _ in range(self.h)] for _ in range(self.w)]
        for pos in random.sample(range(self.h * self.w), self.b):
            self.is_bomb[pos % self.w][pos // self.w] = True
        self.is_flag = [[False for _ in range(self.h)] for _ in range(self.w)]
        self.field_value = [[0 for _ in range(self.h)] for _ in range(self.w)]
        for row in range(self.h):
            for col in range(self.w):
                if self.is_bomb[col][row]:
                    self.field_value[col][row] = 9
                    continue
                self.field_value[col][row] = self.count_around(col, row, self.is_bomb)

    @staticmethod
    def count_around(at_x, at_y, arr):
        ans = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                col, row = at_x + dx, at_y + dy
                if 0 <= col < len(arr) and 0 <= row < len(arr[0]) and arr[col][row]:
                    ans += 1
        return ans

    def get_time(self):
        if self.timer_start is None:
            return 0
        if self.timer_stop is None:
            return time.time() - self.timer_start
        return self.timer_stop - self.timer_start

    def handle_lmb(self, wx, wy, gh, special=False):
        x = wx - (gh.grid_width - self.w) // 2
        y = wy - (gh.grid_height - self.h) // 2

        # game over
        if self.won or self.lost:
            return

        # out of bounce
        if x < 0 or x >= self.w:
            return
        if y < 0 or y >= self.h:
            return

        # handle flag
        if self.is_flag[x][y]:
            return

        # handle special move
        if self.is_checked[x][y]:
            if not special:
                flags = self.count_around(x, y, self.is_flag)
                if flags > 0 and flags == self.field_value[x][y]:
                    for nx in [-1, 0, 1]:
                        for ny in [-1, 0, 1]:
                            if nx == 0 and ny == 0:
                                continue
                            self.handle_lmb(wx + nx, wy + ny, gh, special=True)
            return

        # handle bomb
        if self.is_bomb[x][y]:

            if self.first_lmb:
                self.start_custom()
                self.handle_lmb(wx, wy, gh)
                return

            self.lost = True
            self.timer_stop = time.time()
            return

        # handle miss
        if self.first_lmb:
            self.timer_start = time.time()
        self.first_lmb = False
        self.is_checked[x][y] = True

        # handle zeros
        if self.field_value[x][y] == 0:
            for nx in [-1, 0, 1]:
                for ny in [-1, 0, 1]:
                    if nx == 0 and ny == 0:
                        continue
                    self.handle_lmb(wx + nx, wy + ny, gh)

        # handle win
        checked = sum(sum(row) for row in self.is_checked)
        if checked == self.w * self.h - self.b:
            self.won = True
            self.timer_stop = time.time()

    def handle_rmb(self, x, y, gh):
        x = x - (gh.grid_width - self.w) // 2
        y = y - (gh.grid_height - self.h) // 2

        # game over
        if self.won or self.lost:
            return

        # out of bounce
        if x < 0 or x >= self.w:
            return
        if y < 0 or y >= self.h:
            return

        if not self.is_checked[x][y]:
            self.is_flag[x][y] = not self.is_flag[x][y]
