import re
import os
from new_tree import Move, MoveTree, Info
from goban import sgf_to_goban
import movetree
""" I want all the other files to not have any idea about what SGF is """


simple_text = r'.*?'
prop_ident = r'[A-Z]+'
prop_value = r'\[' + simple_text + r'[^\\]\]\r?\n?'
inner_value = r'\[(.*?[^\\])\]'
property = prop_ident + '(?:' + prop_value + ')+'
node = ';\r?\n?(?:' + property + ')+'
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
    #print(file_tokens)
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

    tree = MoveTree()
    tree.info = make_info_node(root.children[0].properties)
    tree.root_move = root.children[0].children[0]
    tree.current_move = tree.root_move
    tree.root_move.parent = None
    return tree

def make_tree_from_file_path(file_path):
    with open(file_path) as f:
        file_content = f.read()
    return make_tree_from_file_content(file_content)
def make_tree_from_file_name(file_name):
    file_path = os.path.join(os.getcwd(), file_name)
    return make_tree_from_file_path(file_path)

def make_info_node(props):
    info = Info()
    props = {pid: props[pid][0] for pid in props}
    info.annotator         = props.get('AN', None)  # (simpletext)
    info.black_rank        = props.get('BR', None)  # (simpletext)
    info.black_team        = props.get('BT', None)  # (simpletext)
    info.copyright         = props.get('CP', None)  # (simpletext)
    info.date              = props.get('DT', None)  # (simpletext)
    info.event             = props.get('EV', None)  # (simpletext)
    info.game_name         = props.get('GN', None)  # (simpletext)
    info.komi              = float(props.get('KM', 0.0))  # (real)
    info.game_comment      = props.get('GC', None)  # (text)
    info.opening           = props.get('ON', None)  # (simpletext)
    info.black_player      = props.get('PB', None)  # (simpletext)
    info.place             = props.get('PC', None)  # (simpletext)
    info.white_player      = props.get('PB', None)  # (simpletext)
    info.result            = props.get('RE', None)  # (simpletext)
    info.round             = props.get('RO', None)  # (simpletext)
    info.rule_set          = props.get('RU', None)  # (simpletext)
    info.source            = props.get('SO', None)  # (simpletext)
    info.time_control      = props.get('TM', None)  # (real)
    info.user              = props.get('US', None)  # (simpletext)
    info.white_rank        = props.get('WR', None)  # (simpletext)
    info.white_team        = props.get('WT', None)  # (simpletext)
    info.application       = props.get('AP', None)  # (simpletext:simpletext)
    info.charset           = props.get('CA', 'UTF-8') # (simpletext)
    info.size              = int(props.get('SZ', 19))
    info.file_format       = int(props.get('FF', 0)) # simpletest
    info.game              = 1 # see sgf reference (1 means go)
    info.ST                = 2 # see sgf reference (2 means no board markup)
    return info

if __name__ == "__main__":
    tree = make_tree_from_file_name('ShusakuvsInseki.sgf')
    tree.print()
