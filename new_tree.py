from new_goban import Goban

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
        parent_str = str(self.parent.coord) if self.parent is not None else "None"
        return "M" + str(self.coord) + str(self.properties) + " parent : " + parent_str
    def print(self):
        print(str(self))
        for c in self.children:
            c.print()

class Info(object):
    def __init__(self):
        self.annotator    = None  # AN (simpletext)
        self.black_rank   = None  # BR (simpletext)
        self.black_team   = None  # BT (simpletext)
        self.copyright    = None  # CP (simpletext)
        self.date         = None  # DT (simpletext)
        self.event        = None  # EV (simpletext)
        self.game_name    = None  # GN (simpletext)
        self.komi         = None  # KM (real)
        self.game_comment = None  # GC (text)
        self.opening      = None  # ON (simpletext)
        self.black_player = None  # PB (simpletext)
        self.place        = None  # PC (simpletext)
        self.white_player = None  # PB (simpletext)
        self.result       = None  # RE (simpletext)
        self.round        = None  # RO (simpletext)
        self.rule_set     = None  # RU (simpletext)
        self.source       = None  # SO (simpletext)
        self.time_control = None  # TM (real)
        self.user         = None  # US (simpletext)
        self.white_rank   = None  # WR (simpletext)
        self.white_team   = None  # WT (simpletext)
        self.application  = None
        self.size = 19
        self.charset      = 'UTF-8'
        self.file_format  = 0
        self.game         = 1
        self.ST           = 2

    def __str__(self):
        d = {k: self.__dict__[k] for k in self.__dict__ if self.__dict__[k] is not None}
        return str(d)

class MoveTree(object):
    def __init__(self):
        self.info = None
        self.root_move = Move()
        self.current_move = self.root_move

    def add_move(self, move):
        move.parent = self.current_move
        self.current_move.children.append(move)

    def print(self):
        print(str(self.info))
        self.root_move.print()

    def reverse_line_from(self, node):
        current = node
        line = [node]
        guard = 0
        while current.parent is not None:
            line.append(current.parent)
            current = current.parent
            guard += 1
            if guard > 450:
                raise TreeError("reverse_line_from() : tree integrity error, going from parent to parent does not "
                                "find root node")
        return line

    def position_from_node(self, node):
        assert isinstance(node, Move)
        line = self.reverse_line_from(node)
        temp_goban = Goban(self.info.size, self.info.size)
        while line:
            mv = line.pop()
            if isinstance(mv, Move):
                temp_goban[mv.coord] = mv.color
                temp_goban.resolve_adj_captures(mv.coord)
            else:
                print("Something else than a move")
        return temp_goban

    def advance_move(self):
        try:
            self.current_move = self.current_move.children[0]
        except IndexError as e:
            raise TreeError("MoveTree.advance_move : No next move")

    def previous_move(self):
        self.current_move = self.current_move.parent

    def get_position(self):
        return self.position_from_node(self.current_move)
