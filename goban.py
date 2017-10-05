#!/usr/bin/python
# TODO Make it so that goban doesn't need to import move_tree
import movetree

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
        self.board = {}
        self.width = int(width)
        self.height = int(height)
        if self.width < 1 or self.height < 1:
            raise ValueError
        self.positionStack = []

    def clear_goban(self):
        self.board = dict()
        self.positionStack = []

    """ Saves the current position to a stack of board positions.  This is
    useful for navigating a move tree and for implementing the upgraded ko
    rule"""

    def push(self):
        self.positionStack.append(dict(self.board))

    """ Pops an element from the position stack and sets it as the current board
    position."""

    def undo(self):
        self.board = self.positionStack.pop()

    """ For coordinates given by coord = (x,y) where x and y are two integers,
    the function returns those of (x+1,y),(x-1,y),(x,y-1),(x,y+1) that are in
    the board as elements of a list of tuples."""

    def __getNeighbors__(self, coord):
        neighbors = []
        x = coord[0]
        y = coord[1]
        if 1 <= x - 1:
            neighbors.append((x - 1, y))
        if x + 1 <= self.width:
            neighbors.append((x + 1, y))
        if 1 <= y - 1:
            neighbors.append((x, y - 1))
        if y + 1 <= self.height:
            neighbors.append((x, y + 1))
        return neighbors

    """ Returns the group of stones that the stone at coord is part of."""

    def __getGroup__(self, coord):
        assert coord in self.board, "__getGroup() : coord " + str(coord) + " must be in board"
        color = self.board[coord]
        group = set()
        group.add(coord)
        stack = self.__getNeighbors__(coord)
        seen = [coord]
        while len(stack):
            neighbor = stack.pop()
            seen.append(neighbor)
            if neighbor in self.board and self.board[neighbor] == color:
                group.add(neighbor)
                stack += [n for n in self.__getNeighbors__(neighbor) if n not in seen]
        return group

    def __removeGroup__(self, coord):
        group = self.__getGroup__(coord)
        for key in group:
            del self.board[key]
        return len(group)

    def __remove_stone(self, coord):
        del self.board[coord]

    def __get_liberties__(self, coord):
        # todo test this function in regards to the comment above
        color = self.board[coord]
        queue = self.__getNeighbors__(coord)
        seen = [coord]
        liberties = 0
        while len(queue):
            neighbor = queue.pop()
            seen.append(neighbor)
            if neighbor not in self.board:
                liberties += 1
                continue
            if self.board[neighbor] == color:
                for adj in self.__getNeighbors__(neighbor):
                    if adj not in seen:
                        queue.append(adj)
        return liberties

    def __get_group_stones__(self, group):
        group_stones = []
        for coord in group:
            assert coord in self.board, "__get_group_stones() stone should be in board"
            color = self.board[coord]
            group_stones.append(movetree.Stone(color, goban_to_sgf(coord)))
        return group_stones

    """ Updates the state based on a move being played """

    def play_move(self, color, goban_coord):
        self.push()
        if goban_coord[0] < 1 or goban_coord[0] > self.width or goban_coord[1] < 1 or goban_coord[1] > self.height:
            self.undo()
            raise GobanError("Outside of playable area")
        try:
            self.put_stone(color, goban_coord)
        except GobanError as e:
            self.undo()
            raise e
        captured_stones = self.resolve_captures(goban_coord)
        if not self.ko_legal():
            self.undo()
            raise GobanError("Move violates ko rule")
        if self.__get_liberties__(goban_coord) == 0:
            self.undo()
            raise GobanError("Suicide move cannot be played")
        return {'captured': captured_stones, 'move': color + str(goban_to_sgf(goban_coord))}

    def put_stone(self, color, coord):
        if coord in self.board:
            raise GobanError("Already a stone there")
        self.board[coord] = color

    def in_atari(self, coord):
        return self.__get_liberties__(coord) == 1

    def get_stones(self):
        stones = {'W': [], 'B': []}
        for coord in self.board:
            color = self.board[coord]
            stones[color].append(movetree.Stone(color, goban_to_sgf(coord)))
        return stones

    def resolve_captures(self, goban_coord):
        adjacent = self.__getNeighbors__(goban_coord)
        num_removed_stones = 0
        captured_stones = list()
        for adj in adjacent:
            if adj in self.board \
                    and self.board[adj] != self.board[goban_coord] \
                    and self.__get_liberties__(adj) == 0:
                adj_group = self.__getGroup__(adj)
                captured_stones.append(self.__get_group_stones__(adj_group))
                num_removed_stones += self.__removeGroup__(adj)
        return captured_stones

    def apply_liberty_rule(self, coord):
        if coord in self.board and self.__get_liberties__(coord) == 0:
            group = self.__getGroup__(coord)
            self.__removeGroup__(coord)
            return group

    """Answers the question 'does the rule of KO prevent me from playing this stone on
    this board."""

    def ko_legal(self):
        for previous_pos in self.positionStack:
            if previous_pos == self.board:
                return False
        return True

    def print_stack(self):
        for pos in self.positionStack:
            print("        " + str(pos))


class GobanError(Exception):
    pass
