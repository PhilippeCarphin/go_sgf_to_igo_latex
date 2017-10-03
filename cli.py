#!/usr/bin/python

import igo
import movetree
import sys
import getopt

options = "m:f:v:"
long_opts = ["move=", "find=", "variation="]


def diagram(argv):
    sgf_file = argv[0]
    argv = argv[1:]
    opts, args = getopt.getopt(argv, options, long_opts)
    if len(opts) < 1:
        print("specify exactly one move: diagram filename (-m moveNumber | -f searchString) [-v variation]")
        sys.exit(2)
    else:
        mt = movetree.Tree(sgf_file)
        move_opt = opts[0]
        move = find_move(move_opt, mt)
        if len(opts) > 1:
            var_opt = opts[1]
            if var_opt[0] in ['--variation', '-v']:
                var_num = var_opt[1]
            else:
                print("Additional argument can only be variation")
                sys.exit(2)
            move = move.getChild(int(var_num))
    string = igo.make_diagram(move)
    print(string)


def make_beamer(argv):
    sgf_file = argv[0]
    argv = argv[1:]
    opts, args = getopt.getopt(argv, options, long_opts)
    bm = igo.BeamerMaker()
    mt = movetree.Tree(sgf_file)
    file_string = ''
    if len(opts) >= 1:
        move_opt = opts[0]
        start_move = find_move(move_opt, mt)
        file_string = bm.mainline_from(start_move)
        if len(opts) == 2 and opts[1][0] in ['--variation', '-v']:
            pass
            # var_num = opts[1][1]
            # second_move = start_move.getChild(int(var_num))
            # node_list = [start_move] + bm.ml_from(second_move)
    print(file_string)


def find_move(opt, tree):
    lookup_type = opt[0]
    arg = opt[1]
    current = None
    if lookup_type in ['--move', '-m']:
        current = tree.head
        for i in range(int(arg)):
            current = current.get_child(0)
    elif lookup_type in ['--find', '-f']:
        tsv = movetree.TextSearchVisitor(arg)
        tree.head.accept_visitor(tsv)
        current = tsv.get_result()
    elif lookup_type in ['--variation', '-v']:
        current = None
    return current


def rotate(opts):
    filename = opts[0]
    move_tree = None
    try:
        move_tree = movetree.Tree(filename)
    except IOError:
        print('Invalid filename ' + filename)
        exit(1)
    output = movetree.write_sgf(move_tree, True)
    if len(opts) > 1 and opts[1] == '--output':
        output_file = opts[2]
        with open(output_file, 'w') as f:
            f.write(output)
    else:
        print(output)


command = sys.argv[1]
if command == 'beamer':
    exit(make_beamer(sys.argv[2:]))
elif command == 'diagram':
    exit(diagram(sys.argv[2:]))
elif command == 'rotate':
    exit(rotate(sys.argv[2:]))
else:
    print("Invalid command ", command)

# Produce a diagram of the position at move three.
    # ./Cli.py diagram Variations.sgf -m 3

# Produce a diagram of the position at move containing "%MARKER"
    # ./Cli.py diagram Variations.sgf -f honor

# Produce beamer pages for move containing %Marker1 to leaf.
    # ./Cli.py beamer Variations.sgf -f honor

# Produce beamer pages for move containing %marker to end

# Produce beamer pages for move number X variation 3

# Produce beamer pages for move containing marker %Marker variation 2

# Diagrams or beamer pages, or beamer page.
