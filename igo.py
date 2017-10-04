import os
import movetree
import goban

""" Copyright 2016, 2017 Philippe Carphin"""

""" This file is part of go_sgf_to_igo_latex.

go_sgf_to_igo_latex is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

go_sgf_to_igo_latex is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>."""

def goban_to_sgf(goban_coord):
    char_x = chr(goban_coord[0] + ord('a') - 1)
    char_y = chr(goban_coord[1] + ord('a') - 1)
    return char_x + char_y

def goban_to_igo(goban_coord, height=19):
    char_x = chr(ord('a') + goban_coord[0] - 1)
    if ord(char_x) >= ord('i'):
        char_x = chr(ord('a') + goban_coord[0])
    num_y = str(height - (ord(chr(ord('a') + goban_coord[1] - 1)) - ord('a')))
    return char_x + num_y

def sgf_list_to_igo(sgf_list):
    """ Creates a list of igo coordinates from a list of sgf coordinates """
    igo_list = []
    for sgf in sgf_list:
        igo_list.append(movetree.sgf_to_igo(sgf, 19))
    return igo_list


def glyph_command(node, symbol):
    """ Creates the latex command to add the glyphs of type 'symbol' at the
    given node """
    symbols = {'TR': '\\igotriangle', 'SQ': '\\igosquare', 'CR': '\\igocircle'}
    igo_list = comma_list_from_coord_list(sgf_list_to_igo(node.data[symbol]))
    return '\\gobansymbol[' + symbols[symbol] + ']{' + igo_list + '}\n'


def glyph_commands(node):
    """ Generates the three glyph commands at the node if the node has glyphs of
    that type """
    commands = ''
    for key in ['TR', 'SQ', 'CR']:
        if key in node.data:
            commands += glyph_command(node, key)
    return commands


def comma_list_from_coord_list(coord_list):
    """ Generates string with a comma separated list of the contents of the
    given coordinate list """
    comma_list = ''
    for coord in coord_list:
        comma_list += coord + ','
    return comma_list[0:len(comma_list) - 1]


def comma_list_from_stone_list(stone_list):
    """ Generates string with a comma separated list containing the igo-coordinates
    of the stones in the list. """
    comma_list = ''
    for stone in stone_list:
        comma_list += stone.igo_coord(19) + ','
    return comma_list[0:len(comma_list) - 1]


def make_diagram(node):
    """ Generates igo output for the diagram of the position at the given
    node."""
    diagram = '\\cleargoban\n'
    try:
        black_stones = comma_list_from_stone_list(node.goban_data['gobanState']['B'])
        white_stones = comma_list_from_stone_list(node.goban_data['gobanState']['W'])
    except KeyError:
        print("makeDiagram(): move does not have gobanState")
        raise KeyError
    diagram += '\\white{' + white_stones + '}\n'
    diagram += '\\black{' + black_stones + '}\n'
    diagram += '\\cleargobansymbols\n'
    diagram += glyph_commands(node)
    diagram += '\\showfullgoban\n'
    return diagram

def make_diagram_from_position(position):
    black_igo_coords = [goban_to_igo(goban_coord) for goban_coord in position if position[goban_coord] == 'B']
    white_igo_coords = [goban_to_igo(goban_coord) for goban_coord in position if position[goban_coord] == 'W']
    black_comma_list = comma_list_from_coord_list(black_igo_coords)
    white_comma_list = comma_list_from_coord_list(white_igo_coords)
    diagram = '\\cleargoban\n'
    diagram += '\\black{' + black_comma_list + '}\n'
    diagram += '\\white{' + white_comma_list + '}\n'
    diagram += '\\cleargobansymbols\n'
    diagram += '\\showfullgoban\n'
    return diagram

def make_diff_diagram(node):
    """ Generates igo output for the diagram by specifying stones to add and
    stones to remove. """
    diagram = ''
    if node.color == 'W':
        diagram += '\\white{' + node.igo_coord(19) + '}\n'
    else:
        diagram += '\\black{' + node.igo_coord(19) + '}\n'
    removed_stones = []
    for group in node.goban_data['captured']:
        removed_stones += group
    removed_list = comma_list_from_stone_list(removed_stones)
    if len(removed_list) > 0:
        diagram += '\\clear{' + removed_list + '}\n'
    diagram += '\\cleargobansymbols\n'
    diagram += glyph_commands(node)
    diagram += '\\showfullgoban\n'
    return diagram


# def put_labels(node):
#     """ Function to add labels like letters and numbers to the diagram. """
#     pass


class BeamerMaker:
    """ Creates the beamer-LaTeX code from go games 

    Attributes: 
        frame_title : string : text content of framestart.tex used to let the
            user customize title of beamer frames.
        pre_diagram : string : text content of prediag.tex lets the user define text
            that will be inserted right before diagrams.
        post_diagram : string : text content of postdiag.tex placed right after
            diagrams
        frame_start : string : text content of framestart.tex placed before
            SGF-commentary.
    """

    def __init__(self):
        """ Sets frametitle, framestart, prediag and postdiag with content from
        corresponding *.tex files """
        self.frame_start = open(os.path.join(os.getcwd(), 'framestart.tex')).read()
        self.pre_diagram = open(os.path.join(os.getcwd(), 'prediag.tex')).read()
        self.post_diagram = open(os.path.join(os.getcwd(), 'postdiag.tex')).read()
        self.frame_title = open(os.path.join(os.getcwd(), 'frametitle.tex')).read().replace('\n', '').replace('\r', '')

    def position_to_stone_lists(self, position):
        white_stones = []

    def make_page(self, node, page_type):
        """ Generate a beamer page (frame) from the given node. Frame beginning,
        SGF commentary, diagram (diff or position) and frame end, with contents
        of frametitle, framestart, prediag, postdiag added at the right places."""
        page = '%%%%%%%%%%%%%%%%%%%% MOVE ' + str(node.moveNumber) + ' %%%%%%%%%%%%%%%%%%%%%%%\n'
        page += '\\begin{frame}\n\n'
        page += '\\frametitle{' + self.frame_title + '}\n'
        page += self.frame_start
        page += '% % BEGIN SGF COMMENTS % %\n'
        page += node.get_comment() + '\n'
        page += '% % END SGF COMMENTS % %\n'
        page += self.pre_diagram
        if page_type == 'diff':
            page += make_diff_diagram(node)
        else:
            page += make_diagram(node)
        page += self.post_diagram
        page += '\\end{frame}\n'
        return page

    def make_page_from_postion(self, position):
        """ Generate a beamer page (frame) from the given node. Frame beginning,
        SGF commentary, diagram (diff or position) and frame end, with contents
        of frametitle, framestart, prediag, postdiag added at the right places."""
        page = '%%%%%%%%%%%%%%%%%%%% ' + "Diagram" + ' %%%%%%%%%%%%%%%%%%%%%%%\n'
        page += '\\begin{frame}\n\n'
        page += '\\frametitle{' + self.frame_title + '}\n'
        page += self.frame_start
        page += self.pre_diagram
        page += make_diagram_from_position(position)
        page += self.post_diagram
        page += '\\end{frame}\n'
        return page


    @staticmethod
    def ml_from(node):
        """ Visits the tree starting at the given node going to first child
        until a leaf is reached """
        path_stack = [node]
        current = node
        while current.has_next():
            current = current.get_child(0)
            path_stack.append(current)
        path_stack.reverse()
        return path_stack

    @staticmethod
    def ml_to(node):
        """ Generates a path of nodes starting at the root of the tree and
        ending at the given node. """
        path_stack = [node]
        current = node
        while current.has_parent:
            current = current.parent
            path_stack.append(current)
        return path_stack

    @staticmethod
    def ml_between(start, end):
        """ Generates a path of nodes starting at the start node and ending at
        the end node. """
        path_stack = [start]
        current = start
        while current.has_parent and current != end:
            current = current.parent
            path_stack.append(current)
        return path_stack

    def make_file(self, node_list):
        """ Creates a file from a node list. The file consists of the position
        at the first node in the list, the diff diagrams for each subsequent
        node until the end of the list."""
        file_str = self.make_page(node_list.pop(), 'position')
        while len(node_list) > 0:
            file_str += self.make_page(node_list.pop(), 'diff')
        return file_str

    @staticmethod
    def save_file(string, filename):
        """ Saves a string to a file with the given filename """
        f = open(filename, 'w')
        f.write(string)
        f.close()

    def mainline_from(self, node):
        """ Generates the beamer output for the mainline starting at the current
        node. """
        node_list = BeamerMaker.ml_from(node)
        return self.make_file(node_list)

    def all_options(self, node, prefix):
        """ Generates files for many of the options susceptible of being
        required by the user. In the future the files will have better unique
        names that will not require the to have a numeric ID to avoid name
        collisions."""
        todo_stack = []
        for branch in node.children:
            todo_stack.append((node, branch))
        unique_id = 0
        while len(todo_stack) > 0:
            todo = todo_stack.pop()
            branch_point = todo[0]
            branch = todo[1]
            file_str = self.make_page(branch_point, 'position')
            current = branch
            file_str += self.make_page(current, 'diff')
            while not current.is_leaf():
                current = current.get_child(0)
                file_str += self.make_page(current, 'diff')
                if current.is_branch_point():
                    for branch in current.children:
                        todo_stack.append((current, branch))
                        unique_id += 1
            BeamerMaker.save_file(file_str,
                                  prefix + str(unique_id) + 'branch_point'
                                  + str(branch_point.moveNumber) + '_branch' + str(branch))
