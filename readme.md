Python SGF manipulation package
===============================
The initial reason for this was the automation of creating go diagrams in LaTeX
from an SGF file.  I later decided to use what I had done to do more things:
* Display a board,
* Manipulate SGF files (rather than just reading them)

The two main modules are 
* movetree.py : used for parsing an sgf file into a tree structure
* goban.py : used for implementing the rules of go and keeping track of the
  state of the goban (captured stones, rule of ko, etc)

Other modules use these.  The following modules are still in development but are
not completely experimental.
* igo.py is a module for creating LaTeX output from sgf files and
* menu.py is a module providing a text based interface for igo.py
* cli.py is a command line interface in it's infancy, the goal is to use
  this as part of a makefile build system for LaTeX documents.

The following are completely experimental:
* boarddisplay.py : a tkinter based module for displaying a board position
  (given in the form of the board attribute of a goban.Goban() object).
* interface.py : fiddling with tkinter to get a gui for opening files and
  doing more complex stuff with them.

Cool feature
============

This package can rotate SGF files which is nice if your opponent was the one
writing the moves to one of your games.  Simply open a terminal and navigate to
where the SGF that you want to rotate is.  Then enter the command

python3 cli.py filename > target-filename

or

python3 cli.py filename --output target-filename.




