import re
import os
from new_tree import Move
from goban import sgf_to_goban

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
    root = root.children[0]
    root.parent = 0
    return root
def make_tree_from_file_name(file_name):
    file_path = os.path.join(os.getcwd(), file_name)
    with open(file_path) as f:
        file_content = f.read()
    return make_tree_from_file_content(file_content)

if __name__ == "__main__":
    root = make_tree_from_file_name('Variations.sgf')
    root.print()