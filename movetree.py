import os
import re
import goban

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
along with go_sgf_to_igo_latex.  If not, see <http://www.gnu.org/licenses/>."""


################################################################################
# Utility functions for treating tokens
################################################################################
listTypes = ['AB', 'AE', 'AW', 'CR', 'TR', 'SQ', 'LB']
elistTypes = ['LB']



def un_escape(string):
    """ Un-escapes the characters ] and \ characters """
    return string.replace('\\\\', '\\').replace('\\]', ']')

def escape(string):
    """ Escapes the characters ] and \ characters """
    return string.replace('\\', '\\\\').replace(']', '\\]')

def make_file_tokens(string):
    """ Returns a list of tokens that are either a perentheses, a move, or the
    info thing at the start. Extracted by regexp from string """
    paren = r'[()]'
    component = r'(?:[A-Z]*(?:\[.*?[^\\]\]\r?\n?)+)'
    token_regex = re.compile(paren + '|' + component + '+', re.DOTALL)
    token_list = token_regex.findall(string)
    token_list = token_list[1:len(token_list) - 1]
    return token_list

def break_token_data(type_token, data_token):
    """ Subdivides token data into the right bits based on the type """
    token_data = re.compile(r'\[(.*?[^\\])\]', re.DOTALL).findall(data_token)
    if type_token in ['W', 'B']:
        assert 0
    elif type_token == 'LB':
        i = 0
        while i < len(token_data):
            token_data[i] = (token_data[i][0:2], token_data[i][3])
            i += 1
    elif type_token not in listTypes:
        token_data = un_escape(token_data[0])
    return token_data




def create_move(token, parent, move_number):
    """ Returns a move created by the supplied token with specified parent and move
    number """
    move = Move(parent)
    move.moveNumber = move_number
    component = r'([A-Z]+)((?:\[.*?[^\\]\]\r?\n?)+)'
    sub_tokens = re.compile(component, re.DOTALL).findall(token)
    for sub_token in sub_tokens:
        if sub_token[0] == 'W' or sub_token[0] == 'B':
            move.color = sub_token[0]
            move.sgf_coord = sub_token[1][1:3]
        else:
            move.data[sub_token[0]] = break_token_data(sub_token[0], sub_token[1])
    return move




def make_tree(file_content):
    """ Returns the head of a move tree based on the content of an SGF_file """
    file_tokens = make_file_tokens(file_content)
    root = Node(0)
    tip = root
    branch_point_stack = []
    move_number = 1
    for token in file_tokens:
        if token == '(':
            branch_point_stack.append(tip)
            branch_point_stack.append(move_number)
        elif token == ')':
            move_number = branch_point_stack.pop()
            tip = branch_point_stack.pop()
        else:
            new_move = create_move(token, tip, move_number)
            if new_move.color != 'E':
                move_number += 1
            tip.add_child(new_move)
            tip = new_move
    root = root.get_child(0)
    root.parent = 0
    return root




def make_token(move, turned180=False):
    """ Returns the SGF_token corresponding to move """
    token = ';'
    if move.color in ['W', 'B']:
        if turned180:
            coord = move.sgf_coord
            x = ord(coord[0]) - ord('a') + 1
            y = ord(coord[1]) - ord('a') + 1
            turned_x = 19 - x + 1
            turned_y = 19 - y + 1
            turned_sgf = chr(turned_x + ord('a') - 1) + chr(turned_y + ord('a') - 1)
            token += move.color + '[' + turned_sgf + ']'
        else:
            token += move.color + '[' + str(move.sgf_coord) + ']'
    for key in move.data:
        token += key + '['
        if key in elistTypes:
            for elem in move.data[key]:
                token += ':'.join(elem)
        elif key in listTypes:
            token += ''.join(move.data[key])
            for elem in move.data[key]:
                token += elem
        else:
            token += escape(move.data[key])
        token += ']'
    return token


def write_sgf(move_tree, turned180=False):
    stack = [')', move_tree.info, '(']
    text = ''
    while len(stack) > 0:
        current = stack.pop()
        if current in ['(', ')(', ')']:
            text += current
        else:
            text += make_token(current, turned180)
            n = len(current.children)
            if n > 1:
                stack.append(')')
                while n > 1:
                    n -= 1
                    stack.append(current.children[n])
                    stack.append(')(')
                stack.append(current.children[0])
                stack.append('(')
            elif n == 1:
                stack.append(current.get_child(0))
    return text


def sgf_to_igo(sgf_coord, height):
    char_x = sgf_coord[0]
    if ord(char_x) >= ord('i'):
        char_x = chr(ord(sgf_coord[0]) + 1)
    num_y = str(height - (ord(sgf_coord[1]) - ord('a')))
    return char_x + num_y


################################################################################
# Class node.  Base class of move Tree composite pattern
################################################################################
class Node:
    def __init__(self, parent):
        self.children = []
        self.parent = parent
        self.childNumber = 0

    def has_next(self):
        if self.children:
            return True
        else:
            return False

    def has_parent(self):
        if self.parent == 0:
            return False
        else:
            return True

    def get_child(self, i=0):
        return self.children[i]

    def get_parent(self):
        return self.parent

    def add_child(self, child):
        child.childNumber = len(self.children)
        self.children.append(child)

    def has_next_sibling(self):
        if self.parent == 0:
            return False
        return len(self.parent.children) > self.childNumber + 1

    def get_next_sibling(self):
        if self.has_next_sibling():
            return self.parent.children[self.childNumber + 1]

    def is_branch_point(self):
        if len(self.children) > 1:
            return True
        else:
            return False

    def is_leaf(self):
        if len(self.children) == 0:
            return True
        else:
            return False

    def clear_children(self):
        self.children = []

    def accept_visitor(self, visitor):
        visitor.visit(self)

    def node_print(self):
        print('Node')


################################################################################
# Class Stone.  Represents a stone on the goban
################################################################################
class Stone:
    def __init__(self, color=None, sgf_coord='XX'):
        self.color = color
        self.sgf_coord = sgf_coord

    def igo_coord(self, height):
        return sgf_to_igo(self.sgf_coord, height)

    def sgf_coord(self):
        """ returns SGF coordinates of stone """
        return self.sgf_coord


    def goban_coord(self):
        """ returns goban coordinates of stone """
        return tuple(1 + ord(c) - ord('a') for c in self.sgf_coord)

    def __str__(self):
        return str(self.color) + self.sgf_coord

    def __repr__(self):
        return str(self.color) + self.sgf_coord
        # return self.color + self.igo(19)


################################################################################
# Class Move(Node) Contains move data and methods
################################################################################
class Move(Node, Stone):
    def __init__(self, parent, color='E', sgf_coord='XX'):
        Node.__init__(self, parent)
        Stone.__init__(self, color, sgf_coord)
        self.moveNumber = 0
        self.data = {}
        self.goban_data = {}

    def node_print(self):
        print('%%% MoveInfo')
        print('%%% Number    : ', self.moveNumber)
        print('%%% Color     : ', self.color)
        print('%%% Coord     : ', self.sgf_coord)
        print('%%% Data      : ', self.data)
        print('%%% SGF_token : ', make_token(self))
        print('%%% GobanState: ', self.goban_data)
        print('%%% Children  : ', self.children)

    def get_comment(self):
        if 'C' in self.data:
            return self.data['C']
        else:
            return ''

    def __repr__(self):
        return self.color + str(self.sgf_coord)

################################################################################
# Master class of composite pattern
################################################################################
class Tree:
    def __init__(self, filename):
        file_path = os.path.join(os.getcwd(), filename)
        try:
            with open(file_path) as f:
                file_content = f.read()
        except IOError:
            print("No such file " + filename)
            raise IOError('No such file ' + file_path)

        self.head = make_tree(file_content)
        self.info = self.head
        self.head = self.head.get_child(0)
        self.head.parent = 0
        state_visit(self)
        # self.accept_visitor(goban.StateVisitor())

    def accept_visitor(self, visitor):
        self.head.accept_visitor(visitor)

    def print_info(self):
        print('%%%% GAME INFO')
        for key in self.info.data:
            print('%%% ' + key + ' : ' + self.info.data[key])


################################################################################
# Pre order printing visitor
################################################################################
class NodeVisitor:
    def __init__(self):
        pass

    def visit(self, node):
        node.node_print()
        for child in node.children:
            child.accept_visitor(self)


class TextSearchVisitor:
    def __init__(self, search_string):
        self.searchString = search_string
        self.result = Move(0)

    def get_result(self):
        return self.result

    def visit(self, node):
        if self.searchString in node.get_comment():
            self.result = node
        else:
            for child in node.children:
                child.accept_visitor(self)


################################################################################
# Single branch printing visitor
################################################################################
class MainlineVisitor:
    def __init__(self):
        pass

    def visit(self, node):
        node.node_print()
        if node.has_next():
            node.get_child(0).accept_visitor(self)


def depth_first_visit(root, f):
    stack = [root]
    while len(stack) > 0:
        current = stack.pop()
        f(current)
        for child in reversed(current.children):
            stack.append(child)


def state_visit(tree):
    """ Go through the nodes of a tree and add goban_state information to each node """
    stack = []
    done = False
    board_size = int(tree.info.data['SZ'])
    my_goban = goban.Goban(board_size, board_size)
    # todo Place handicap stones
    # Traverse move tree
    current = tree.head
    while not done:
        while current.has_next():
            move_diff = my_goban.play_move(current.color, current.goban_coord())
            if move_diff is not None:
                current.goban_data['captured'] = move_diff['captured']
            current.goban_data['gobanState'] = my_goban.get_stones()
            stack.append(current)
            current = current.get_child(0)

        move_diff = my_goban.play_move(current.color, current.goban_coord())
        if move_diff is not None:
            current.goban_data['captured'] = move_diff['captured']
        current.goban_data['gobanState'] = my_goban.get_stones()
        my_goban.undo()
        while not current.has_next_sibling() and len(stack) > 0:
            current = stack.pop()
            my_goban.undo()
        if len(stack) == 0:
            done = True
        else:
            current = current.get_next_sibling()

################################################################################
# Visitor vists move tree in parallel with a goban.  Assigns goban state and
# stones captured to each move Node
################################################################################
class StateVisitor:
    def __init__(self):
        self.goban = goban.Goban(19, 19)

    def visit(self, move):
        move_diff = self.goban.play_move(move.color, move.goban_coord())
        move.goban_data = dict()
        move.goban_data['gobanState'] = self.goban.get_stones()
        move.goban_data['captured'] = move_diff['captured']
        for child in move.children:
            child.accept_visitor(self)
        self.goban.undo()


if __name__ == "__main__":
    moveTree = Tree('nassima_phil.sgf')
    print(write_sgf(moveTree, False))
