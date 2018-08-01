import os
# from goban import goban_to_sgf, GobanError
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
import time
# import pyperclip
import signal

from . import igo
import queue
from .model import Model, ModelError
from .movetree import TreeError
from .view import View
from .engineinterface import Gnugo, Leelaz
from .engineinterface import goban_coord_to_gtp_coord, goban_color_to_gtp_color, gtp_color_to_goban_color, gtp_coord_to_goban_coord
from . import sgfwriter
from . import leelaoutput

weights = os.path.join(os.path.dirname(__file__), '../bin/leelaz-model-5309030-128000.txt')
leelaz_cmd = [ 'leelaz', '-g', '-w', weights ]
leela_cmd = [ 'leela', '-g']
leela_opencl_cmd = [ 'leela-opencl', '-g']


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
along with go_sgf_to_igo_latex.  If not, see <http://www.gnu.org/licenses/>."""


class Controller(Tk):
    """ Top level GUI class, catches inputs from the user and dispatches the
    appropriate requests to the model and vies classes """

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Phil's SGF viewer")
        self.view = View(self)
        self.model = Model()
        self.bind('<Key>', self.key_pressed_dispatch)
        self.key_map = {'a': self.undo_key,
                        'b': self.make_beamer_slide,
                        'c': self.make_diagram,
                        'l': self.load_sgf,
                        'n': self.next_move,
                        'v': self.next_variation,
                        'd': self.previous_variation,
                        'e': self.execute_command,
                        's': self.save_game,
                        524291 : self.quit_handler, # CTRL-C
                        'q' : self.quit_handler,
                        'r': self.rotate,
                        'p': self.new_procedure,
                        'z': self.get_analysis,
                        3473435: self.stop_analysis}
        self.bm = igo.BeamerMaker()
        self.config(height=800, width=400)
        self.view.place(relwidth=1.0, relheight=1.0)
        self.minsize(400, 400 + 110)
        self.engine_black = None # Gnugo(self) #Leelaz(self, playouts=1000)
        self.engine_white = None # Gnugo(self)
        self.command_answer_handler = None
        signal.signal(signal.SIGINT, lambda signal, frame: self.quit_handler())
        self.analysis = ''
        self.current_move = None
        self.time_to_stop = False
        # self.poll_engine_messages()
        # self.execute_command('genmove black')

    def stop_analysis(self):
        self.time_to_stop = True

    def save_game(self):
        save_file = './' + filedialog.asksaveasfilename()
        sgfwriter.write_sgf_file(self.model.move_tree, save_file)


    def destroy(self, *args, **kwargs):
        self.quit_handler()
        Tk.destroy(self, *args, **kwargs)

    def execute_command(self, cmd=None, engine=None):
        # Change command to interface calls
        # Make interface call
        if engine is None:
            engine = self.engine_black
        self.engine_black.gtp_wrapper.get_stderr()
        if cmd is None:
            cmd = simpledialog.askstring("Execute command", "Enter command to execute")
            self.engine_black.genmove(gtp_color_to_goban_color(cmd.split(' ')[1]))
            return

    def engine_move(self, goban_coord, mover):
        if mover is self.engine_black:
            self.engine_white.playmove('B', goban_coord)
            self.engine_white.genmove('W')
        else:
            self.engine_black.playmove('W', goban_coord)
            self.engine_black.genmove('B')
        self.model.play_move(goban_coord)
        self.view.show_position(self.model.goban)

    def get_analysis(self):
        self.model.load_sgf('./sgf_files/nassima_phil.sgf')
        first_move = self.model.move_tree.root_node.children[0]
        self.view.show_position(self.model.move_tree.position_from_node(first_move))
        self.model.move_tree.current_move = first_move
        self.engine_black.genmove('B')

    def analysis_done(self):
        last_move = self.model.move_tree.current_move
        last_move.properties['C'] = self.engine_black.command_output
        last_move.analysis = leelaoutput.parse_output(self.engine_black.command_output)

        if self.time_to_stop or not last_move.children:
            sgfwriter.write_sgf_file(self.model.move_tree, './analyzed_game.sgf')
            self.view.show_info("Analysis stopped")
            move = self.model.move_tree.root_node.children[0]
            evals = []

            return

        self.engine_black.undo()
        self.engine_black.playmove(last_move.color, last_move.coord)

        self.model.move_tree.advance_move()

        current_move = self.model.move_tree.current_move
        self.view.show_position(self.model.move_tree.position_from_node(current_move))

        self.engine_black.genmove(current_move.color)

    def new_procedure(self):
        self.model.load_sgf('./sgf_files/nassima_phil.sgf')
        mt = self.model.move_tree
        cm = mt.root_node
        while cm.children:
            # do genmove
            # get output of genmove
            # do something with the output
            # undo move
            # play the move from the game
            cm = cm.children[0]
            self.engine_black.playmove(cm.color, cm.coord)
        self.engine_black.gtp_wrapper.ask('showboard')


    def quit_handler(self):
        if self.engine_black:
            self.engine_black.kill()
        if self.engine_white:
            self.engine_white.kill()
        quit(0)


    def poll_engine_messages(self):
        """ Polling of the stdout queue of leela process """
        self.engine_black.check_messages()
        self.engine_white.check_messages()
        self.after(200, self.poll_engine_messages)

    def rotate(self):
        self.model.rotate_tree();
        self.view.show_position(self.model.goban)

    def make_beamer_slide(self):
        """ Creates the LaTeX code for a beamer slide of the current position
        and outputs it to STDOUT and puts it in the system clipboard """
        diag = self.bm.make_page_from_postion(self.model.goban)
        try:
            pass
            # pyperclip.copy(diag)
        except:
            pass
        print(diag)

    def make_diagram(self):
        """ Creates the LaTeX code for a diagram of the current position
        and outputs it to STDOUT and puts it in the system clipboard """
        diag = igo.make_diagram_from_position(self.model.goban)
        try:
            pass
            # pyperclip.copy(diag)
        except:
            pass
        print(diag)

    def key_pressed_dispatch(self, event):
        """ Dispatches the key press events to the correct handler as per the
        self.key_map dictionary """
        try:
            self.key_map[event.char]()
        except KeyError:
            try:
                self.key_map[event.keycode]()
            except KeyError:
                print("No handler for key " + ("enter" if event.keycode == 13 else event.char) + "(" + str(
                    event.keycode) + ")")

    def board_clicked(self, goban_coord):
        """ Handler for the board clicked event.  The board canvas notifies us
        that it has been clicked at game coordinates goban_coord, we ask the
        model to play a move at that position and give the new position to the
        canvas for display. """
        self.model.play_move(goban_coord)
        self.view.show_position(self.model.goban)
        return

        if self.model.turn != 'B':
            return
        try:
            self.model.play_move(goban_coord)
            # Inform leela of the move played
            self.engine_white.playmove('B', goban_coord)
            self.view.show_info('Playing against\nLeela')
            self.engine_white.genmove(self.model.turn)
        except ModelError as e:
            print("Error when playing at " + str(goban_coord) + " : " + str(e))
            self.view.show_info(str(e))
        self.view.show_position(self.model.goban)

    def undo_key(self):
        """ Handler for undo key : Note the move stays in the movetree."""
        try:
            self.model.undo_move()
        except ModelError as e:
            print("Error when undoing " + str(e))
        self.view.show_position(self.model.goban)

    def load_sgf(self):
        """ Prompts the user to select an SGF file to load and loads the
        selected file """
        cwd = os.getcwd()
        file_path = filedialog.askopenfilename(initialdir=cwd, title="Select file",
                                               filetypes=(("Smart game format", "*.sgf"), ("all files", "*.*")))
        try:
            self.model.load_sgf(file_path)
        except FileNotFoundError:
            pass
        self.view.show_position(self.model.goban)

    def next_move(self):
        """ Next move to navigate the move tree """
        try:
            self.model.next_move()
        except ModelError as e:
            print("Error when going to next move " + str(e))
        self.view.show_position(self.model.goban)

    def next_variation(self):
        try:
            self.model.next_variation()
        except ModelError as e:
            print("Error when doing next_variation " + str(e))
        self.view.show_position(self.model.goban)

    def previous_variation(self):
        try:
            self.model.previous_variation()
        except ModelError as e:
            print("Error when doing previous_variation " + str(e))
        self.view.show_position(self.model.goban)


if __name__ == "__main__":
    try:
        controller = Controller()
        controller.mainloop()
    except IOError as exc:
        input()
