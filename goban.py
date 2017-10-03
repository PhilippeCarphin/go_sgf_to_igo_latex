#!/usr/bin/python
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
        board : Dictionnary in which keys are board coordinates and values are
            either 'W' or 'B', if board.has_key(coord) returns false, it means that
            coordinate is empty.
        height : Integer height of the board
        width : Integer witdh of the board
        ko : in case there is a possible ko, this is the coordinates of the last
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
        self.ko = (0, 0)
        self.positionStack = []
        self.moveStack = []
        self.currentMove = movetree.Move(0)

    def clear_goban(self):
        self.board = dict()
        self.positionStack = []
        self.moveStack = []
        self.ko = (0, 0)
        self.currentMove = movetree.Move(0)

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
        group = [coord]
        queue = self.__getNeighbors__(coord)
        seen = [coord]
        while len(queue):
            neighbor = queue.pop()
            seen.append(neighbor)
            if neighbor not in self.board:
                continue
            if neighbor not in group and self.board[neighbor] == color:
                group.append(neighbor)
                for coord in self.__getNeighbors__(neighbor):
                    if not (coord in seen):
                        queue.append(coord)
        return group

    def __removeGroup__(self, coord):
        group = self.__getGroup__(coord)
        for key in group:
            del self.board[key]
        return len(group)

    def __remove_stone(self, coord):
        del self.board[coord]

    """ Gets the liberties of a group
    Note: I think that this function will return that the white group in
    the following position
    BB
    BW
    BWWB
    BBBB
    will have two liberties when it has just one.  For now, the algorithm just
    needs to tell us when the group has 0 liberties or not 0 liberties."""

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

    def play_move(self, move):
        special = set(move.data.keys()).intersection(['AB', 'AW', 'AE'])
        if len(special) > 0:
            self.push()
            for key in special:
                if key == 'AB':
                    for sgf_coord in move.data[key]:
                        self.board[sgf_to_goban(sgf_coord)] = 'B'
                elif key == 'AW':
                    for sgf_coord in move.data[key]:
                        self.board[sgf_to_goban(sgf_coord)] = 'W'
                else:
                    for sgf_coord in move.data[key]:
                        if sgf_coord not in self.board:
                            del self.board[sgf_to_goban(sgf_coord)]
            return None
        else:
            self.push()
            color = move.color
            coord = move.goban_coord()
            self.put_stone(color, coord)

            captured_stones = self.resolve_captures(move)

            if not self.ko_legal():
                self.undo()
                raise GobanError("Move violates ko rule")
            if self.__get_liberties__(coord) == 0:
                self.undo()
                raise GobanError("Suicide move " + str(move.goban_coord()) + " cannot be played")

            return {'captured': captured_stones, 'move': move.color + str(move.sgf_coord)}

    def put_stone(self, color, coord):
        assert coord not in self.board, "There is already a move here"
        self.board[coord] = color

    def in_atari(self, coord):
        return self.__get_liberties__(coord) == 1

    def get_stones(self):
        stones = {'W': [], 'B': []}
        for coord in self.board:
            color = self.board[coord]
            stones[color].append(movetree.Stone(color, goban_to_sgf(coord)))
        return stones

    def resolve_captures(self, stone):
        adjacent = self.__getNeighbors__(stone.goban_coord())
        num_removed_stones = 0
        captured_stones = list()
        for adj in adjacent:
            if adj in self.board \
                    and self.board[adj] != stone.color \
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


################################################################################
""" Visitor vists move tree in parallel with a goban.  Assigns goban state and
stones captured to each move Node"""


################################################################################
class StateVisitor:
    def __init__(self):
        self.goban = Goban(19, 19)

    def visit(self, node):
        move_diff = self.goban.play_move(node)
        node.goban_data = dict()
        node.goban_data['gobanState'] = self.goban.get_stones()
        node.goban_data['captured'] = move_diff['captured']
        for child in node.children:
            child.accept_visitor(self)
        self.goban.undo()


def goban_test():
    test_goban = Goban(19, 19)
    # Todo: Refactor so that play_move only needs to take 'B', goban_coord (tuple)

    # Position:
    #
    # |WB
    # |BW
    # ---

    test_goban.clear_goban()

    test_goban.play_move(movetree.Move(parent=0, color='B', sgf_coord='of'))
    test_goban.play_move(movetree.Move(parent=0, color='W', sgf_coord='pf'))

    test_goban.play_move(movetree.Move(parent=0, color='B', sgf_coord='oh'))
    test_goban.play_move(movetree.Move(parent=0, color='W', sgf_coord='ph'))

    test_goban.play_move(movetree.Move(parent=0, color='B', sgf_coord='ng'))
    test_goban.play_move(movetree.Move(parent=0, color='W', sgf_coord='qg'))

    test_goban.play_move(movetree.Move(parent=0, color='B', sgf_coord='pg'))
    test_goban.play_move(movetree.Move(parent=0, color='W', sgf_coord='og'))

    try:
        test_goban.play_move(movetree.Move(parent=0, color='B', sgf_coord='pg'))
    except GobanError:
        print("Ko rule violation correctly detected")


def move_tree_test():
    print('Creating Move Tree')
    mt = movetree.Tree('nassima_phil.sgf')
    # mt.head.acceptVisitor(MoveTree.nodeVisitor())
    current = mt.head.get_child(0)
    current = current.get_child(0)
    # current = current.get_child(0)

    current.node_print()
    mt.accept_visitor(StateVisitor())
    mt.accept_visitor(movetree.NodeVisitor())


if __name__ == "__main__":
    goban = Goban(19, 19)
    try:
        badSize = Goban('bonjour', "bonjour")
        print("Non-int-able params not detected")
    except ValueError:
        print("Things not changeable to int are correctly detected")

    try:
        badNumbers = Goban(0, -1)
    except ValueError:
        print("Bad Numbers are correctly detected")

    goban_test()
    move_tree_test()
