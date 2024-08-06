import random
import numpy as np
#Fill up the correct values
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


def action_name(a):
    return "UP RIGHT DOWN LEFT".split()[a]


class IllegalAction(Exception):
    pass


class GameOver(Exception):
    pass


def compress(row):
    "remove 0s in the list"
    return [i for i in row if i != 0]


def merge(row):
    row = compress(row)
    reward = 0
    r = []
    hold = -1
    while len(row) > 0:
        v = row.pop(0)
        if hold != -1:
            if hold == v:
                reward += 2 ** (hold + 1)
                r.append(hold + 1)
                hold = -1
            else:
                r.append(hold)
                hold = v
        else:
            hold = v
    if hold != -1:
        r.append(hold)
        hold = -1
    while len(r) < 4:
        r.append(0)
    return reward, r


from copy import copy


class Board:
    def __init__(self, board=None):
        """board is a list of 16 integers"""
        if board is not None:
            self.board = board
        else:
            self.reset()

    def reset(self):
        self.clear()
        self.board[random.choice(self.empty_tiles())] = 1
        self.board[random.choice(self.empty_tiles())] = 2

    def spawn_tile(self, random_tile=False):
        empty_tiles = self.empty_tiles()
        if len(empty_tiles) == 0:
            raise GameOver("Board is full. Cannot spawn any tile.")
        if random_tile:
            self.board[random.choice(empty_tiles)] = random.choice([1, 2])
        else:
            self.board[random.choice(empty_tiles)] = 1

    def clear(self):
        self.board = [0] * 16 #complete the code here

    def empty_tiles(self):
        return [i for (i, v) in enumerate(self.board) if v == 0]

    def display(self):
        def format_row(lst):
            s = ""
            for l in lst:
                s += " {:3d}".format(l)
            return s

        for row in range(4):
            idx = row * 4
            print(format_row(self.base10_board[idx : idx + 4]))

    @property
    def base10_board(self):
        return [2 ** v if v > 0 else 0 for v in self.board]

    def act(self, a):
        original = self.board
        if a == LEFT:
            r = self.merge_to_left()
        if a == RIGHT:
            self.rotate().rotate()
            r = self.merge_to_left()
            self.rotate().rotate()
        if a == UP:
            r = self.rotate().rotate().rotate().merge_to_left()
            self.rotate()
        if a == DOWN:
            self.rotate()
            r = self.merge_to_left()
            self.rotate().rotate().rotate()
        if original == self.board:
            raise IllegalAction("Action did not move any tile.")
        return r

    def rotate(self):
        "Rotate the board inplace 90 degress clockwise."
        size = 4
        b = []
        for row in range(size):
            for col in range(size):
                b.append(self.board[(size - 1 - col) * size + row])   
        self.board = b
        return self

    def merge_to_left(self):
        "merge board to the left, returns the reward for mering tiles"
        "Raises IllegalAction exception if the action does not move any tile."
        r = []
        board_reward = 0
        for nrow in range(4):
            row = self.board[nrow * 4 : (nrow + 1) * 4]
            reward, merged = merge(row)
            board_reward += reward
            r += merged
        self.board = r
        return board_reward

    def copyboard(self):
        return list(self.board)