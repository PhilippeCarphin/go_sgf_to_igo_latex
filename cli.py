#!/usr/bin/python

import igo
import movetree
import sys, getopt

options = "m:f:v:"
longopts = ["move=","find=","variation="]

def diagram(argv):
    sgf_file = argv[0]
    argv = argv[1:]
    opts , args = getopt.getopt(argv,options,longopts)
    if len(opts) < 1:
        print "specify exactly one move: diagram filename (-m moveNumber | -f searchString) [-v variation]"
        sys.exit(2)
    else :
        mt = movetree.Tree(sgf_file)
        moveOpt = opts[0]
        move = findMove(moveOpt,mt)
        if len(opts) > 1:
            varOpt = opts[1]
            if varOpt[0] in ['--variation','-v']:
                varNum = varOpt[1]
            else:
                print "Additional argument can only be variation"
                sys.exit(2)
            move = move.getChild(int(varNum))
    string = igo.make_diagram(move)
    print string

def makeBeamer(argv):
    sgf_file = argv[0]
    argv = argv[1:]
    opts , args = getopt.getopt(argv,options,longopts)
    bm = igo.BeamerMaker()
    mt = movetree.Tree(sgf_file)
    if len(opts) >= 1:
        moveOpt = opts[0]
        startMove = findMove(moveOpt,mt)
        fileString = bm.mainline_from(startMove)
        if len(opts) == 2 and opts[1][0] in ['--variation','-v']:
            varNum = opts[1][1]
            secondMove = startMove.getChild(int(varNum))
            nodeList = [startMove] + bm.ml_from(secondMove)
        
    
    print fileString


def findMove(opt,tree):
    lookupType = opt[0]
    arg = opt[1]
    if lookupType in ['--move','-m']:
        current = tree.head
        for i in range(int(arg)):
            current = current.get_child(0)
    elif lookupType in ['--find','-f']:
        tsv = movetree.TextSearchVisitor(arg)
        tree.head.accept_visitor(tsv)
        current = tsv.get_result()
    elif lookupType in ['--variation','-v']:
        current = None
    return current

def rotate(opts):
    filename = opts[0]
    try:
        move_tree = movetree.Tree(filename)
    except IOError:
        print('Invalid filename ' + filename)
        exit(1)
    output = movetree.write_sgf(move_tree, True)
    if len(opts) > 1 and opts[1] == '--output':
        output_file = opts[2]
        with open(output_file, 'w') as f:
            f.write(output, True)
    else:
        print(output)

command = sys.argv[1]
if command == 'beamer':
    exit(makeBeamer(sys.argv[2:]))
elif command == 'diagram':
    exit(diagram(sys.argv[2:]))
elif command == 'rotate':
    exit(rotate(sys.argv[2:]))
else:
    print("Invalid command ",command)

# Produce a diagram of the position at move three.
    # ./Cli.py diagram Variations.sgf -m 3

# Produce a diagram of the position at move containing "%MARKER"
    # ./Cli.py diagram Variations.sgf -f honor

# Produce beamer pages for move containting %Marker1 to leaf.
    # ./Cli.py beamer Variations.sgf -f honor

# Produce beamer pages for move containing %marker to end

# Produce beamer pages for move number X variation 3

# Produce beamer pages for move containing marker %Marker variation 2



# Diagrams or beamer pages, or beamer page.




