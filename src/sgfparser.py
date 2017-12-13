import os
import re

import dirs
import movetree
from movetree import Move, Info

""" I want all the other files to not have any idea about what SGF is """

simple_text_re_str = r'.*?'
prop_ident_re_str = r'[A-Z]+'
prop_value_re_str = r'\[' + simple_text_re_str + r'[^\\]\]\r?\n?'
inner_value_re_str = r'\[(.*?[^\\])\]'
property_re_str = prop_ident_re_str + '(?:' + prop_value_re_str + ')+'
node_re_str = ';\r?\n?(?:' + property_re_str + ')+'
tree_re_str = '\(' + '(?:' + node_re_str + ')+' + '\)'
paren_re_str = '[()]'

node_re = re.compile(node_re_str, re.DOTALL)
property_re = re.compile(property_re_str, re.DOTALL)
prop_ident_re = re.compile(prop_ident_re_str, re.DOTALL)
prop_value_re = re.compile(prop_value_re_str, re.DOTALL)
inner_value_re = re.compile(inner_value_re_str, re.DOTALL)


def props_from_node_token(t):
    return property_re.findall(t)


def values_from_property(p):
    return inner_value_re.findall(p)


def read_property(p):
    pid = prop_ident_re.match(p).group(0)
    vals = values_from_property(p)
    return pid, vals


def make_file_tokens(string):
    token_regex = re.compile(node_re_str + '|' + paren_re_str, re.DOTALL)
    token_list = token_regex.findall(string)
    # token_list = token_list[1:len(token_list) - 1]
    # print(string)
    return token_list


def sgf_to_goban(sgf_coord):
    x = 1 + ord(sgf_coord[0]) - ord('a')
    y = 1 + ord(sgf_coord[1]) - ord('a')
    return x, y


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
    tree = movetree.MoveTree()
    root = movetree.Node()
    root.depth = -1
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
    tree.info = make_info_node(root.children[0].properties)
    first_move = root.children[0].children[0]
    first_move.parent = tree.root_node
    tree.root_node.children.append(first_move)
    tree.current_move = tree.root_node
    return tree


def make_tree_from_file_path(file_path):
    with open(file_path) as f:
        file_content = f.read()
    return make_tree_from_file_content(file_content)


def make_tree_from_file_name(file_name):
    file_path = os.path.join(dirs.SGF, file_name)
    return make_tree_from_file_path(file_path)


mn = {
    'AN': 'annotator',  # (simpletext)
    'BR': 'black_rank',  # (simpletext)
    'BT': 'black_team',  # (simpletext)
    'CP': 'copyright',  # (simpletext)
    'DT': 'date',  # (simpletext)
    'EV': 'event',  # (simpletext)
    'GN': 'game_name',  # (simpletext)
    'KM': 'komi',  # (real)
    'GC': 'game_comment',  # (text)
    'ON': 'opening',  # (simpletext)
    'PB': 'black_player',  # (simpletext)
    'PC': 'place',  # (simpletext)
    'PB': 'white_player',  # (simpletext)
    'RE': 'result',  # (simpletext)
    'RO': 'round',  # (simpletext)
    'RU': 'rule_set',  # (simpletext)
    'SO': 'source',  # (simpletext)
    'TM': 'time_control',  # (real)
    'US': 'user',  # (simpletext)
    'WR': 'white_rank',  # (simpletext)
    'WT': 'white_team',  # (simpletext)
    'AP': 'application',  # (simpletext:simpletext)
    'CA': 'charset',  # (simpletext)
    'SZ': 'size',  # integer
    'FF': 'file_format',  # simpletest
    'GA': 'game',  # gf reference (1 means go)
    'AT': 'ST',  # gf reference (2 means no board markup)
    'HA': 'handicap'}  # (number) I think


def make_info_node(props):
    info = Info()
    props = {pid: props[pid][0] for pid in props}
    info.annotator = props.get('AN', None)  # (simpletext)
    info.black_rank = props.get('BR', None)  # (simpletext)
    info.black_team = props.get('BT', None)  # (simpletext)
    info.copyright = props.get('CP', None)  # (simpletext)
    info.date = props.get('DT', None)  # (simpletext)
    info.event = props.get('EV', None)  # (simpletext)
    info.game_name = props.get('GN', None)  # (simpletext)
    info.komi = float(props.get('KM', 0.0))  # (real)
    info.game_comment = props.get('GC', None)  # (text)
    info.opening = props.get('ON', None)  # (simpletext)
    info.black_player = props.get('PB', None)  # (simpletext)
    info.place = props.get('PC', None)  # (simpletext)
    info.white_player = props.get('PB', None)  # (simpletext)
    info.result = props.get('RE', None)  # (simpletext)
    info.round = props.get('RO', None)  # (simpletext)
    info.rule_set = props.get('RU', None)  # (simpletext)
    info.source = props.get('SO', None)  # (simpletext)
    info.time_control = props.get('TM', None)  # (real)
    info.user = props.get('US', None)  # (simpletext)
    info.white_rank = props.get('WR', None)  # (simpletext)
    info.white_team = props.get('WT', None)  # (simpletext)
    info.application = props.get('AP', None)  # (simpletext:simpletext)
    info.charset = props.get('CA', 'UTF-8')  # (simpletext)
    info.size = int(props.get('SZ', 19))
    info.file_format = int(props.get('FF', 0))  # simpletest
    info.game = 1  # see sgf reference (1 means go)
    info.ST = 2  # see sgf reference (2 means no board markup)
    info.handicap = int(props.get('HA', 0))  # (number) I think, haven't looked at the SGF spec for this
    return info


if __name__ == "__main__":
    tree = make_tree_from_file_path(os.path.join(dirs.SGF, 'ShusakuvsInseki.sgf'))

    tree.print()
    # print(tree.check_ko_legal())
