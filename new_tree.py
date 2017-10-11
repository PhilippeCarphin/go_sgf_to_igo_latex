from new_goban import Goban

class Glyphs():
    def __init__(self):
        self.circles = []
        self.squares = []
        self.triangles = []

class Node(object):
    def __init__(self, parent=None):
        self.children = []
        self.parent = parent
        self.child_number = 1
    def add_child(self, node):
        self.children.append(node)
        node.parent = self
        node.child_number = len(self.children)

class Stone(object):
    def __init__(self, color=None, coord=(None,None)):
        self.color = color
        self.coord = coord

class Move(Node, Stone):
    def __init__(self, parent=None, color=None, coord=(None,None)):
        Node.__init__(self, parent)
        Stone.__init__(self, color, coord)
        self.properties = {}
        self.glyphs = Glyphs()
        self.position = None
    def __str__(self):
        return "M" + str(self.coord) + str(self.properties)
    def print(self):
        print(str(self))
        for c in self.children:
            c.print()

class MoveTree(object):
    def __init__(self, goban_height=19, goban_width=19):
        self.root_move = Move()
        self.current_move = self.root_move

    def add_move(self, move):
        move.parent = self.current_move
        self.current_move.children.append(move)