import movetree
import boardcanvas
from tkinter import *

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


class MoveTreeCanvas(Canvas, object):
    def __init__(self, master):
        Canvas.__init__(self, master, bd=3, relief=SUNKEN)
        self.move_tree = movetree.Tree('nassima_phil.sgf')
        self.bind('<Configure>', self.configure_event)
        self.width = self.master.winfo_width()
        self.height = self.master.winfo_height() - self.master.winfo_width()

    def configure_event(self, event):
        self.width = event.width
        self.height = event.height
        self.draw()

    def draw(self):
        self.delete('all')
        self.create_text(200, 100, text='This canvas will be \nused for displaying a \nmovetree', font=('Arial', 20), fill='black')


if __name__ == '__main__':
    root = Tk()
    bc = boardcanvas.BoardCanvas(root)
    mtc = MoveTreeCanvas(root)
    root.minsize(400, 400)
    root.mainloop()
