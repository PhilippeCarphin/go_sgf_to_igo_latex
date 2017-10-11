import re
import os
from new_tree import Move, MoveTree
from goban import sgf_to_goban
""" I want all the other files to not have any idea about what SGF is """
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
        self.charset      = 'UTF-8'
        self.file_format  = 0
        self.game         = 1
        self.ST           = 2

    def parse_props(self, props):
        props = {pid: props[pid][0] for pid in props}
        self.annotator         = props.get('AN', None)  # AN (simpletext)
        self.black_rank        = props.get('BR', None)  # BR (simpletext)
        self.black_team        = props.get('BT', None)  # BT (simpletext)
        self.copyright         = props.get('CP', None)  # CP (simpletext)
        self.date              = props.get('DT', None)  # DT (simpletext)
        self.event             = props.get('EV', None)  # EV (simpletext)
        self.game_name         = props.get('GN', None)  # GN (simpletext)
        self.komi              = float(props.get('KM', 0.0))  # KM (real)
        self.game_comment      = props.get('GC', None)  # GC (text)
        self.opening           = props.get('ON', None)  # ON (simpletext)
        self.black_player      = props.get('PB', None)  # PB (simpletext)
        self.place             = props.get('PC', None)  # PC (simpletext)
        self.white_player      = props.get('PB', None)  # PB (simpletext)
        self.result            = props.get('RE', None)  # RE (simpletext)
        self.round             = props.get('RO', None)  # RO (simpletext)
        self.rule_set          = props.get('RU', None)  # RU (simpletext)
        self.source            = props.get('SO', None)  # SO (simpletext)
        self.time_control      = props.get('TM', None)  # TM (real)
        self.user              = props.get('US', None)  # US (simpletext)
        self.white_rank        = props.get('WR', None)  # WR (simpletext)
        self.white_team        = props.get('WT', None)  # WT (simpletext)
        self.application       = props.get('AP', None)  # (simpletext:simpletext)
        self.charset           = props.get('CA', 'UTF-8') # (simpletext)
        self.file_format       = int(props.get('FF', 0)) # simpletest
        self.game              = 1 # see sgf reference (1 means go)
        self.ST                = 2 # see sgf reference (2 means no board markup)

    def __str__(self):
        d = {k:self.__dict__[k] for k in self.__dict__ if self.__dict__[k] is not None}
        return str(d)

simple_text = r'.*?'
prop_ident = r'[A-Z]+'
prop_value = r'\[' + simple_text + r'[^\\]\]\r?\n?'
inner_value = r'\[(.*?[^\\])\]'
property = prop_ident + '(?:' + prop_value + ')+'
node = ';(?:' + property + ')+'
tree = '\(' + '(?:' + node + ')+' + '\)'
paren = '[()]'

node_re = re.compile(node, re.DOTALL)
property_re = re.compile(property, re.DOTALL)
prop_ident_re = re.compile(prop_ident, re.DOTALL)
prop_value_re = re.compile(prop_value, re.DOTALL)
inner_value_re = re.compile(inner_value, re.DOTALL)

def props_from_node_token(t):
    return property_re.findall(t)
def values_from_property(p):
    return inner_value_re.findall(p)
def read_property(p):
    pid = prop_ident_re.match(p).group(0)
    vals = values_from_property(p)
    return pid, vals
def make_file_tokens(string):
    token_regex = re.compile(node + '|' + paren, re.DOTALL)
    token_list = token_regex.findall(string)
    # token_list = token_list[1:len(token_list) - 1]
    # print(string)
    return token_list
def move_from_token(t):
    move = Move()
    props = props_from_node_token(t)
    for p in props:
        pid, vals = read_property(p)
        if pid in ['W', 'B']:
            move.color = pid
            move.coord = sgf_to_goban(vals[0])
        elif pid == 'C':
            move.properties['C'] = vals[0]
        elif pid == 'CR':
            move.glyphs.circles = vals
        elif pid == 'TR':
            move.glyphs.triangles = vals
        elif pid == 'SQ':
            move.glyphs.squares = vals
        else:
            move.properties[pid] = vals
    return move
def make_tree_from_file_content(file_content):
    """ More elegant way of doing it """
    file_tokens = make_file_tokens(file_content)
    root = Move(0)
    tip = root
    branch_point_stack = []
    for token in file_tokens:
        if token == '(':
            branch_point_stack.append(tip)
        elif token == ')':
            tip = branch_point_stack.pop()
        else:
            new_move = move_from_token(token)
            tip.add_child(new_move)
            tip = new_move
    info_move = root.children[0]
    info_props = info_move.properties
    root_move = info_move.children[0]
    root_move.parent = None
    info_node = Info()
    info_node.parse_props(info_props)
    tree = MoveTree(info_props['SZ'], info_props['SZ'])
    tree.root_move = root.children[0]
    tree.info = info_node
    root.parent = 0
    return tree

def make_tree_from_file_name(file_name):
    file_path = os.path.join(os.getcwd(), file_name)
    with open(file_path) as f:
        file_content = f.read()
    return make_tree_from_file_content(file_content)

if __name__ == "__main__":
    tree = make_tree_from_file_name('Variations.sgf')
    tree.print()