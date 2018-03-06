import copy

from goban import Goban

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


class TreeError(Exception):
    pass


class Glyphs():
    def __init__(self):
        self.circles = []
        self.squares = []
        self.triangles = []


class Node(object):
    def __init__(self, parent=None):
        self.children = []
        self.parent = parent
        self.child_number = 0
        self.depth = 0

    def add_child(self, child):
        child.depth = self.depth + 1
        child.parent = self
        child.child_number = len(self.children)
        self.children.append(child)

    def __str__(self):
        return 'node instance'

    def print(self):
        print(str(self))
        for c in self.children:
            c.print()

    def rotate(self):
        pass

def rotate_coord(coord):
    return (19 - coord[0] + 1, 19 - coord[1] + 1)


class Stone(object):
    def __init__(self, color=None, coord=(None, None)):
        self.color = color
        self.coord = coord
    def rotate(self):
        self.coord = rotate_coord(self.coord)


class Move(Node, Stone):
    def __init__(self, parent=None, color=None, coord=(None, None)):
        Node.__init__(self, parent)
        Stone.__init__(self, color, coord)
        self.properties = {}
        self.glyphs = Glyphs()
        self.position = None

    def rotate(self):
        Stone.rotate(self)

    def __str__(self):
        parent_str = str(self.parent.coord) if isinstance(self.parent, Move) else "None"
        return "M" + str(self.coord) + str(self.properties) + " parent : " + parent_str + ' depth : ' + str(self.depth)


class Info(object):
    def __init__(self):
        self.annotator = None  # AN (simpletext)
        self.black_rank = None  # BR (simpletext)
        self.black_team = None  # BT (simpletext)
        self.copyright = None  # CP (simpletext)
        self.date = None  # DT (simpletext)
        self.event = None  # EV (simpletext)
        self.game_name = None  # GN (simpletext)
        self.komi = None  # KM (real)
        self.game_comment = None  # GC (text)
        self.opening = None  # ON (simpletext)
        self.black_player = None  # PB (simpletext)
        self.place = None  # PC (simpletext)
        self.white_player = None  # PB (simpletext)
        self.result = None  # RE (simpletext)
        self.round = None  # RO (simpletext)
        self.rule_set = None  # RU (simpletext)
        self.source = None  # SO (simpletext)
        self.time_control = None  # TM (real)
        self.user = None  # US (simpletext)
        self.white_rank = None  # WR (simpletext)
        self.white_team = None  # WT (simpletext)
        self.application = None
        self.size = 19
        self.charset = 'UTF-8'
        self.file_format = 0
        self.game = 1
        self.ST = 2

    def __str__(self):
        d = {k: self.__dict__[k] for k in self.__dict__ if self.__dict__[k] is not None}
        return str(d)


def cache_results(func):
    cache = {}

    def new_func(self, arg):
        if arg not in cache:
            ret_val = func(self, arg)
            cache[arg] = ret_val
        else:
            ret_val = cache[arg]
        return ret_val

    return new_func


class MoveTree(object):
    def __init__(self):
        self.info = Info()
        self.root_node = Node(parent=None)
        self.current_move = self.root_node
        self.position_cache = {}

    def add_move(self, move):
        self.current_move.add_child(move)
        self.current_move = move

    def print(self):
        print(str(self.info))
        self.root_node.print()

    def reverse_line_from(self, node):
        current = node
        line = []
        while current is not self.root_node:
            line.append(current)
            current = current.parent
        return line

    # @cache_results  # Now it works but I am not taking advantage that node.parent is in the cache
    def position_from_node(self, node):
        return self.position_from_node_recursive(node)

    def position_from_node_iterative(self, node):
        g = Goban(self.info.size, self.info.size)
        line = self.reverse_line_from(node)
        while line:
            mv = line.pop()
            if isinstance(mv, Move):
                g[mv.coord] = mv.color
                g.resolve_adj_captures(mv.coord)
            else:
                print("Something else than a move : root_node ? " + str(mv is self.root_node))
        return g

    def position_from_node_recursive(self, node):
        if node is self.root_node:
            return Goban(self.info.size, self.info.size)
        g = self.position_from_node_recursive(node.parent)
        g[node.coord] = node.color
        g.resolve_adj_captures(node.coord)
        g.resolve_capture(node.coord)
        return g

    def position_from_node_recursive_with_caching(self, node):
        if node in self.position_cache:
            return self.position_cache[node]
        if node is self.root_node:
            return Goban(self.info.size, self.info.size)
        g = copy.deepcopy(self.position_from_node_recursive_with_caching(node.parent))
        g[node.coord] = node.color
        g.resolve_adj_captures(node.coord)
        self.position_cache[node] = g
        return g

    def advance_move(self):
        try:
            self.current_move = self.current_move.children[0]
        except IndexError as e:
            raise TreeError("MoveTree.advance_move : No next move")

    def previous_move(self):
        if self.current_move is not self.root_node:
            self.current_move = self.current_move.parent

    def get_position(self):
        return self.position_from_node(self.current_move)

    def rotate(self):
        for n in self.root_node.children:
            self.rotate_internal(n)

    def rotate_internal(self, move):
        move.rotate()
        for m in move.children:
            self.rotate_internal(m)
