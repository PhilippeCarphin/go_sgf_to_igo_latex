import os

import dirs
import movetree
import sgfparser


def goban_to_sgf(goban_coord):
    char_x = chr(goban_coord[0] + ord('a') - 1)
    char_y = chr(goban_coord[1] + ord('a') - 1)
    return char_x + char_y


nm = {
    'annotator': 'AN',  # (simpletext)
    'black_rank': 'BR',  # (simpletext)
    'black_team': 'BT',  # (simpletext)
    'copyright': 'CP',  # (simpletext)
    'date': 'DT',  # (simpletext)
    'event': 'EV',  # (simpletext)
    'game_name': 'GN',  # (simpletext)
    'komi': 'KM',  # (real)
    'game_comment': 'GC',  # (text)
    'opening': 'ON',  # (simpletext)
    'black_player': 'PB',  # (simpletext)
    'place': 'PC',  # (simpletext)
    'white_player': 'PB',  # (simpletext)
    'result': 'RE',  # (simpletext)
    'round': 'RO',  # (simpletext)
    'rule_set': 'RU',  # (simpletext)
    'source': 'SO',  # (simpletext)
    'time_control': 'TM',  # (real)
    'user': 'US',  # (simpletext)
    'white_rank': 'WR',  # (simpletext)
    'white_team': 'WT',  # (simpletext)
    'application': 'AP',  # (simpletext:simpletext)
    'charset': 'CA',  # (simpletext)
    'size': 'SZ',  # integer
    'file_format': 'FF',  # simpletest
    'game': 'GA',  # gf reference (1 means go)
    'ST': 'AT',  # gf reference (2 means no board markup)
    'handicap': 'HA'}  # (number) I thinknm = {


def write_sgf(tree):
    return '(' + make_info_token(tree.info) + tree_to_sgf(tree) + ')'


def tree_to_sgf(tree):
    if not tree.root_node.children: return ''
    if len(tree.root_node.children) > 1:
        sgf = ''
        for c in tree.root_node.children:
            sgf += tree_to_sgf_internal(c)
        return sgf
    else:
        return tree_to_sgf_internal(tree.root_node)[1:-1]


def tree_to_sgf_internal(node):
    sgf = '(' + node_to_token(node)
    if len(node.children) == 1:
        sgf += tree_to_sgf_internal(node.children[0])[1:-1]
    elif len(node.children) > 1:
        for c in node.children:
            sgf += tree_to_sgf_internal(c)
    sgf += ')'
    return sgf


def node_to_token(node):
    if not isinstance(node, movetree.Move): return ''
    return ';' + make_move_token(node) \
           + properties(node.properties) \
           + glyph_token(node)


def make_move_token(node):
    if node.coord is None: return ''
    return node.color + '[' + goban_to_sgf(node.coord) + ']'


def make_info_token(info):
    d = info.__dict__
    props = {k: d[k] for k in d if d[k] is not None}
    return ';' + properties({nm[k]: props[k]
                             for k in sorted(props.keys())
                             if props[k] is not None})


def properties(props):
    return ''.join([property(key, props[key])
                    for key in sorted(props.keys())])


def property(key, values):
    return key + prop_values_from_list(values)


def prop_values_from_list(values):
    if values is not None and not isinstance(values, list):
        return '[' + str(values) + ']'
    if isinstance(values, str):  # comments
        return '[' + values + ']'
    return '[' + ']['.join(values) + ']'


def glyph_token(node):
    token = ''
    if node.glyphs.triangles:
        token += 'TR' + prop_values_from_list(node.glyphs.triangles)
    if node.glyphs.squares:
        token += 'SQ' + prop_values_from_list(node.glyphs.squares)
    if node.glyphs.circles:
        token += 'CR' + prop_values_from_list(node.glyphs.circles)
    return token

def write_sgf_file(tree, file_path):
    output = write_sgf(tree)
    with open(file_path, 'w') as f:
        f.write(output)

if __name__ == "__main__":
    t = sgfparser.make_tree_from_file_name('writer_test_input.sgf')
    output = write_sgf(t).replace('\n', '')
    with open(os.path.join(dirs.SGF, 'writer_test_input.sgf'), 'r') as f:
        expected_output = f.read().replace('\n', '')
    assert expected_output == output
