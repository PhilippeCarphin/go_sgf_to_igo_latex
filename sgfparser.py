import re
import cProfile

simple_text = r'.*?'
prop_ident = r'[A-Z]+'
prop_value = r'\[' + simple_text + r'[^\\]\]\r?\n?'
property = prop_ident + '(?:' + prop_value + ')+'
node = ';(?:' + property + ')+'
tree = '\(' + '(?:' + node + ')+' + '\)'
paren = '[()]'

node_re = re.compile(node, re.DOTALL)
property_re = re.compile(property, re.DOTALL)
prop_ident_re = re.compile(prop_ident, re.DOTALL)
prop_value_re = re.compile(prop_value, re.DOTALL)

def name(self):
    return {'LB':'labels'}
def make_file_tokens(string):
    token_regex = re.compile(node + '|' + paren, re.DOTALL)
    token_list = token_regex.findall(string)
    # token_list = token_list[1:len(token_list) - 1]
    # print(string)
    return token_list

def make_tree(file_content):
    """ More elegant way of doing it """
    file_tokens = make_file_tokens(file_content)
    root = SGFnode(0)
    tip = root
    branch_point_stack = []
    for token in file_tokens:
        if token == '(':
            branch_point_stack.append(tip)
        elif token == ')':
            tip = branch_point_stack.pop()
        else:
            new_move = SGFnode(0)
            new_move.read_token(token)
            tip.children.append(new_move)
            tip = new_move
    root = root.children[0]
    root.parent = 0
    return root

class Glyph(object):
    def __init__(self):
        self.circles = []
        self.squares = []
        self.triangles = []

    def __str__(self):
        return str([l for l in [self.circles, self.squares, self.triangles] if l])

class SGFnode(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.properties = {}
        self.children = []
        self.sgf_coord = 'XX'
        self.text = ""
        self.glyphs = Glyph()

    def read_token(self, node_token):
        self.text = node_token
        for p in property_re.findall(node_token):
            self.read_property(p)

    def read_property(self, p):
        pid = prop_ident_re.match(p).group(0)
        vals = [v[1:-1] for v in prop_value_re.findall(p)]
        if pid in ['W', 'B']:
            self.color = pid
            self.sgf_coord = vals[0]
        elif pid == 'LB':
            self.labels = {a[0:2]: a[3] for a in vals}
        elif pid == 'CR':
            self.glyphs.circles = vals
        elif pid == 'TR':
            self.glyphs.triangles = vals
        else:
            self.properties[pid] = vals

    def get_text(self):
        text = ';'
        for p in self.properties:
            text += p + ''.join(['[' + v + ']' for v in self.properties[p]])
        return text


    def print_node(self):
        print(" N " + str(self.properties) + str(self.glyphs))
        for c in self.children:
            c.print_node()


def is_alpha(ch):
    return ch in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def is_whitespace(ch):
    return ch in ' \n\t'

class Parser:
    def __init__(self, text):
        self.text = text
        self.state = self.init_state
        self.current_node = SGFnode()
        self.root_node = self.current_node
        self.branch_point_stack = []
        self.current_prop_ident = ""
        self.current_prop_value = ""


    def run(self):
        for ch in self.text:
            self.state(ch)

    def init_state(self, ch):
        if is_whitespace(ch):
            self.state = self.init_state
        elif ch == '(':
            self.state = self.read_to_node_start_state
            self.make_branch()
        else:
            raise Exception

    def read_to_node_start_state(self, ch):
        if is_whitespace(ch):
            self.state = self.read_to_node_start_state
        elif ch == ';':
            self.start_node()
            self.state = self.node_start_state
        else:
            raise Exception

    def node_start_state(self, ch):
        if is_whitespace(ch):
            self.state = self.node_start_state
        elif is_alpha(ch):
            self.current_prop_ident = ch
            self.state = self.read_prop_ident_state
        elif ch == ';':
            self.start_node()
            self.state = self.node_start_state
        elif ch == '(':
            self.make_branch()
            self.state = self.read_to_node_start_state
        elif ch == ')':
            self.un_branch()
            self.state = self.branching_state
        else:
            raise Exception

    def read_prop_ident_state(self, ch):
        if is_alpha(ch):
            self.current_prop_ident += ch
            self.state = self.read_prop_ident_state
        elif ch == '[':
            self.start_property(self.current_prop_ident)
            self.current_prop_value = ""
            self.state = self.read_prop_value
        else:
            raise Exception

    def branching_state(self, ch):
        if ch == ')':
            self.un_branch()
            self.state = self.branching_state
        elif is_whitespace(ch):
            self.state = self.branching_state
        elif ch == '(':
            self.make_branch()
            self.state = self.read_to_node_start_state
        else:
            raise Exception

    def read_prop_value(self, ch):
        if ch == '\\':
            self.state = self.read_prop_value_escaped_char
        elif ch == ']':
            self.finish_prop_value()
            self.state = self.prop_value_finished_state
        else:
            self.current_prop_value += ch

    def read_prop_value_escaped_char(self, ch):
        self.current_prop_value += ch
        self.state = self.read_prop_value

    def prop_value_finished_state(self, ch):
        if is_whitespace(ch):
            self.state = self.prop_value_finished_state
        elif ch == '[':
            self.current_prop_value = ''
            self.state = self.read_prop_value
        elif ch == ';':
            self.start_node()
            self.state = self.node_start_state
        elif is_alpha(ch):
            self.current_prop_ident = ch
            self.state = self.read_prop_ident_state
        elif ch == ')':
            self.un_branch()
        elif ch == '(':
            self.make_branch()
            self.state = self.read_to_node_start_state

    def main(self):
        for ch in self.text:
            self.state(ch)
        return self.root_node.children[0]

    def make_branch(self):
        self.branch_point_stack.append(self.current_node)

    def un_branch(self):
        self.current_node = self.branch_point_stack.pop()

    def start_property(self, prop_ident):
        self.current_node.properties[prop_ident] = []

    def end_property(self):
        self.current_prop_ident = ""

    def start_prop_value(self):
        self.current_prop_value = ""

    def finish_prop_value(self):
        self.current_node.properties[self.current_prop_ident].append(self.current_prop_value)
        self.current_prop_value = ""

    def start_node(self):
        new_node = SGFnode(self.current_node)
        self.current_node.children.append(new_node)
        self.current_node = new_node


def write_sgf(move_tree):
    stack = [')', move_tree, '(']
    text = ''
    while len(stack) > 0:
        current = stack.pop()
        if current in ['(', ')(', ')']:
            text += current
        else:
            text += current.get_text()
            n = len(current.children)
            if n > 1:
                stack.append(')')
                while n > 1:
                    n -= 1
                    stack.append(current.children[n])
                    stack.append(')(')
                stack.append(current.children[0])
                stack.append('(')
            elif n == 1:
                stack.append(current.children[0])
    return text

import os
if __name__ == "__main__":
    filename = os.path.join(os.getcwd(), 'variations.sgf')
    with open(filename) as f:
        file_content = f.read()

    t = make_tree(file_content)
    t.print_node()

    # p = Parser(file_content)
    #tree = p.main()
    #tree.print_node()
    #text = write_sgf(tree)
    #print(text)
