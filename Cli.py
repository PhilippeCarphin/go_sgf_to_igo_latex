#!/usr/bin/python

import igo
import MoveTree
import sys, getopt

def diagram(argv):

    sgf_file = argv[0]
    argv = argv[1:]

    options = "m:f:v:"
    longopts = ["move=","find=","variation="]
    opts , args = getopt.getopt(argv,options,longopts)
    if len(opts) != 1:
        print "specify exactly one move"
        sys.exit(2)
    else :
        bm = igo.BeamerMaker()
        mt = MoveTree.Tree(sgf_file)
        moveOpt = opts[0]
        lookuptType = moveOpt[0]
        arg = moveOpt[1]
        if lookuptType in ['--move','-m']:
            current = mt.head
            for i in range(int(arg)):
                current = current.getChild(0)
        elif lookuptType in ['--find', '-f']:
            tsv = MoveTree.textSearchVisitor(arg)
            mt.head.acceptVisitor(tsv)
            current = tsv.getResult()
        # current.nodePrint()
        string = igo.makeDiagram(current)
        print string

        
    # print( "command = ", command)
    # print("opts =", opts)
    # print("args =", args)

command = sys.argv[1]
if command == 'beamer':
    diagram(sys.argv[2:])
elif command == 'diagram':
    diagram(sys.argv[2:])
else:
    print("Invalid command ",command)

# Produce a diagram of the position at move three.

# Produce a diagram of the position at move containing "%MARKER"

# Produce beamer pages for move containting %Marker1 to leaf.

# Produce beamer pages for move containing %marker to 

# Produce beamer pages for move number X variation 3

# Produce beamer pages for move containing marker %Marker variation 2



# Diagrams or beamer pages, or beamer page.




