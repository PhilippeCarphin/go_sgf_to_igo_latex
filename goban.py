#!/usr/bin/python
# TODO Make it so that goban doesn't need to import move_tree
import movetree
from operator import add
""" Copyright 2016, 2017 Philippe Carphin"""

""" This file is part of go_sgf_to_igo_latex.

go_sgf_to_igo_latex is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

go_sgf_to_igo_latex is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>."""


def goban_to_sgf(goban_coord):
    char_x = chr(goban_coord[0] + ord('a') - 1)
    char_y = chr(goban_coord[1] + ord('a') - 1)
    return char_x + char_y


def sgf_to_goban(sgf_coord):
    x = 1 + ord(sgf_coord[0]) - ord('a')
    y = 1 + ord(sgf_coord[1]) - ord('a')
    return x, y


RULESET_CHINESE = 1
RULESET_JAPANESE = 2

################################################################################
""" Goban is used to memorize board state and implement go rules """


################################################################################
class Goban:
    """ Goban class : Used to keep track of the board position and take into
    account the rules of Go.

    Attributes:
        board : Dictionary in which keys are board coordinates and values are
            either 'W' or 'B', if board.has_key(coord) returns false, it means that
            coordinate is empty.
        height : Integer height of the board
        width : Integer width of the board
            stone that was captured.
        positionStack : Board positions are pushed to this stack when moves are
            played and popped when moves are undone.  It is also used to try a
            move to see if it is legal.  Since we can iterate over the stack, we
            can implement the moves with an upgraded ko rule wher no position
            can be repeated.
        """

    def __init__(self, width, height):
        if width < 1 or height < 1:
            raise ValueError
        self.board = {}
        self.width = int(width)
        self.height = int(height)
        self.positionStack = []
        self.rule_set = RULESET_CHINESE

    def clear_goban(self):
        self.board = dict()
        self.positionStack = []

    def push(self):
        self.positionStack.append(dict(self.board))

    def undo(self):
        try:
            self.board = self.positionStack.pop()
        except IndexError as e:
            if not self.positionStack:
                raise GobanError("Goban error : " + str(e))
            else:
                raise e

    def get_neighbors(self, coord):
        x, y = coord
        return [t for t in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)] if self.in_board(t)]

    def put_stone(self, color, coord):
        if coord in self.board:
            raise GobanError("GobanError : Already a stone there")
        self.board[coord] = color

    def remove_stone(self, coord):
        del self.board[coord]

    def get_group(self, coord):
        """ Returns the group of stones that the stone at coord is part of."""
        assert coord in self.board, "__getGroup() : coord " + str(coord) + " must be in board"
        color = self.color_at(coord)
        group = {coord}
        to_visit = [coord]
        visited = []
        while to_visit:
            current = to_visit.pop()
            visited.append(current)
            if self.color_at(current) == color:
                group.add(current)
                to_visit += [n for n in self.get_neighbors(current) if n not in visited]
        return group

    def color_at(self, coord):
        return 'E' if coord not in self.board else self.board[coord]

    def remove_group(self, group):
        for goban_coord in group:
            self.remove_stone(goban_coord)

    def get_liberties(self, goban_coord):
        group = self.get_group(goban_coord)
        return self.get_group_liberties(group)

    def get_group_liberties(self, group):
        seen = set()
        for goban_coord in group:
            seen |= {n for n in self.get_neighbors(goban_coord) if n not in self.board}
        return len(seen)

    def get_group_stones(self, group):
        return [movetree.Stone(self.board[coord], goban_to_sgf(coord)) for coord in group]

    def in_board(self, goban_coord):
        return 1 <= goban_coord[0] <= self.width and 1 <= goban_coord[1] <= self.height

    def resolve_capture(self, goban_coord):
        group = self.get_group(goban_coord)
        captured_stones = []
        if self.get_group_liberties(group) == 0:
            captured_stones = self.get_group_stones(group)
            self.remove_group(group)
        return captured_stones

    def resolve_captures_adj_captures(self, goban_coord):
        color = self.board[goban_coord]
        captured_stones = list()
        for adj in filter(lambda n: n in self.board and self.board[n] != color, self.get_neighbors(goban_coord)):
            captured_stones += self.resolve_capture(adj)
        return captured_stones

    def ko_legal(self):
        if self.rule_set == RULESET_CHINESE:
            for previous_pos in self.positionStack:
                if previous_pos == self.board:
                    return False
        elif self.rule_set == RULESET_JAPANESE:
            if len(self.positionStack) > 2 and self.board == self.positionStack[-2]:
                return False
        return True

    def play_move(self, color, goban_coord):
        if not self.in_board(goban_coord):
            raise GobanError("GobanError : Outside of playable area")

        self.push()

        try:
            self.put_stone(color, goban_coord)
        except GobanError as e:
            self.undo()
            raise e

        captured_stones = self.resolve_captures_adj_captures(goban_coord)

        if not self.ko_legal():
            self.undo()
            raise GobanError('GobanError : Move violates ko rule')

        if self.rule_set == RULESET_CHINESE:
            captured_stones += self.resolve_capture(goban_coord)
        elif self.rule_set == RULESET_JAPANESE:
            if self.get_liberties(goban_coord) == 0:
                self.undo()
                raise GobanError("GobanError : Suicide move cannot be played")

        return {'captured': captured_stones, 'move': color + str(goban_to_sgf(goban_coord))}

    def print_stack(self):
        for pos in self.positionStack:
            print("        " + str(pos))

    def in_atari(self, coord):
        return self.get_liberties(coord) == 1

    def get_stones(self):
        stones = {'W': [], 'B': []}
        for coord in self.board:
            color = self.board[coord]
            stones[color].append(movetree.Stone(color, goban_to_sgf(coord)))
        return stones


class GobanError(Exception):
    pass
