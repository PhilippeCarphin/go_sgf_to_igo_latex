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

Running
=======

Note: This app requires python3, tkinter and pyperclip.

Simply execute the file run.py. Assuming that /usr/local/bin/python3 exists.
Otherwise do

	$ python3 run.py

Now I have packaged leelaz (the leela-zero executable file) with the submodule
leelainterface but that is not the one that is used by default.  The default one
will be the one that is findable in PATH.

Therefore, whatever platform you are on, you just have to have leelaz in your
path.  On OSX, the simplest way to do this is to make a symbolic link from
somewhere in you path pointing to the leelaz executable found in the submodule
leelainterface (in src/leelainterface/bin).

On other platforms, you will have to build leelaz from source and put the
produced executable where it will be findable.

In the future, I will build executables for linux and windows and put them in
with leelainterface.  Then all people will have to do is make a symlink
somewhere in their PATH that points to the right file for their platform.

Cool feature
============

This package can rotate SGF files which is nice if your opponent was the one
writing the moves to one of your games.  Simply open a terminal and navigate to
where the SGF that you want to rotate is.  Then enter the command

python3 cli.py rotate filename > target-filename

or

python3 cli.py rotate filename --output target-filename.

Or, on windows, just go to the misc/turner/dist to find turner.exe.  This
standalone application (bundled with the python interpreter) should work on
windows 10 64-bit.  Just place your files in the same directory as the
executable and double-click it.  It will prompt you for the filename and produce
the turned sgf corresponding to the input file as <input_file_name>_turned.sgf

Note on cloning
===============

This application now uses a submodule for interfacing with leela-zero.  Since
not everyone is familiar with git submodules, here's what you need to do when
you clone:

1) Clone normally

	$ git clone https://github.com/philippecarphin/go_sgf_to_igo_latex

2) Initialize submodule

	$ git submodule init

3) Clone the submodule and checkout

	$ git submodule update


