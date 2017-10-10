class Node(object):
    def __init__(self, parent=None):
        self.children = []
        self.parent = parent

class Stone(Node):
    def __init__(self, parent=None, color=None, coord=(None,None)):
        Node.__init__(self)
        self.color = color
        self.coord = coord

class Move(Stone):
    def __init__(self, parent=None, color=None, coord=(None,None)):
        Stone.__init__(self, color, coord)

class MoveTree(object):
    def __init__(self):
        self.root_move = Move()