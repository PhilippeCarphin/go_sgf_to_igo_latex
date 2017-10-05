from view import View
from model import Model
import igo
from tkinter import *


class Controller(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Phil's SGF viewer")
        self.view = View(self)
        self.model = Model()
        self.bind('<Key>', self.key_pressed_dispatch)
        self.key_map = {'a': self.undo_key,
                        'b': self.make_beamer_slide,
                        'c': self.make_diagram}
        self.bm = igo.BeamerMaker()

    def make_beamer_slide(self):
        diag = self.bm.make_page_from_postion(self.model.goban.board)
        print(diag)

    def make_diagram(self):
        diag = igo.make_diagram_from_position(self.model.goban.board)
        print(diag)

    def key_pressed_dispatch(self, event):
        try:
            self.key_map[event.char]()
        except KeyError:
            print("Unknown key " + event.char)
            return

    def board_clicked(self, goban_coord):
        try:
            self.model.play_move(goban_coord)
        except Exception as e:
            print("Error when playing at " + str(goban_coord) + " : " + str(e))
        self.view.show_position(self.model.goban.board)

    def undo_key(self):
        self.model.undo_move()
        self.view.show_position(self.model.goban.board)


if __name__ == "__main__":
    try:
        controller = Controller()
        controller.mainloop()
    except IOError as exc:
        input()
