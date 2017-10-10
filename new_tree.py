from new_goban import Goban

class Node(object):
    def __init__(self, parent=None):
        self.children = []
        self.parent = parent

class Stone(object):
    def __init__(self, color=None, coord=(None,None)):
        self.color = color
        self.coord = coord

class Move(Node, Stone):
    def __init__(self, parent=None, color=None, coord=(None,None)):
        Node.__init__(self, parent)
        Stone.__init__(self, color, coord)
        self.position = None

class MoveTree(object):
    def __init__(self, goban_height=19, goban_width=19):
        self.root_move = Move()
        self.current_move = self.root_move

    def add_move(self, move):
        move.parent = self.current_move
        self.current_move.children.append(move)