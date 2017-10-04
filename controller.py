from view import View
from model import Model
from tkinter import *

class Controller(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Phil's SGF viewer")
        self.view = View(self)
        self.model = Model()
        self.bind('<Key>', self.key_pressed_dispatch)
        self.key_map = {'a': self.undo_key,
                        'b' : self.new_function}

    def key_pressed_dispatch(self, event):
        self.key_map[event.char](event)

    def board_clicked(self, goban_coord):
        self.model.play_move(goban_coord)
        self.view.show_position(self.model.goban.board)

    def undo_key(self, event):
        self.model.undo_move()
        self.view.show_position(self.model.goban.board)

    def new_function(self, event):
        print("b key pressed")

if __name__ == "__main__":
    controller = Controller()
    controller.mainloop()
