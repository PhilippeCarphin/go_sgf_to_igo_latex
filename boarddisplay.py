import movetree
import goban
from tkinter import *


class BoardCanvas:
    """ Class board canvas.  This class manages a canvas and displays a goban
    position

    Attributes:
        cellsize : the sidelenght of the squares on the board
        parent : the parent Tk composite object
        canvas : Tk canvas object to draw in
        position : dictionary with key being board coordinates and values are
            'B' or 'W' """
    def __init__(self, parent):
        self.cell_size = 25
        self.parent = parent
        self.canvas = Canvas(self.parent)
        self.position = {}
        self.draw_position()
        self.canvas.pack()
        self.parent.bind('<Configure>', lambda e: self.draw_position())

    def set_position(self, my_goban):
        self.position = my_goban

    def draw_position(self):
        print(self.position)
        self.canvas.delete('all')
        # Regler la grandeur du canevas pour qu'il remplisse le parent
        side_length = min( self.parent.winfo_height(), self.parent.winfo_width()) - 15
        self.canvas.config( height = side_length, width = side_length)
        # Calculer les dimensions du board resultant
        stone_size = (self.cell_size * 23) // 13
        self.cell_size = side_length // 19
        # Valeurs pour centrer les cercles sur les intersections
        x_offset = 0
        y_offset = 3
        # Dessiner les lignes verticales du goban
        for x in range(19):
            self.canvas.create_line(x * self.cell_size + self.cell_size // 2,
                                    self.cell_size // 2,
                                    x * self.cell_size + self.cell_size // 2,
                                    18 * self.cell_size + self.cell_size // 2)
        # Dessiner les lignes horizontales du gobank
        for y in range(19):
            self.canvas.create_line(self.cell_size // 2,
                                    y * self.cell_size + self.cell_size // 2,
                                    18 * self.cell_size + self.cell_size // 2,
                                    y * self.cell_size + self.cell_size // 2)
        # Dessiner 
        for key in self.position:
            x = key[0]
            y = key[1]
            if self.position[key] == 'W':
                # Dessiner un cercle unicode aux coordonnees ( x, y)
                self.canvas.create_text(x * self.cell_size - self.cell_size // 2 + x_offset,
                                        y * self.cell_size - self.cell_size // 2 - y_offset,
                                        text=u'\u25CB', font=('Arial', stone_size), fill='black')
            else:
                # Dessiner un cercle unicode rempli
                self.canvas.create_text(x * self.cell_size - self.cell_size // 2 + x_offset,
                                        y * self.cell_size - self.cell_size // 2 - y_offset,
                                        text=u'\u25CF', font=('Arial', stone_size))


if __name__ == "__main__":
    # Creation d'une fenetre principale
    root = Tk()
    
    root.minsize(400,400)
    # Creation d'un objet boardCanvas et je lui assigne comme parent la fenetre
    # root.
    bc = BoardCanvas(root)

    # Charger le fichier d'une partie de Go 
    moveTree = movetree.Tree("test_files/expected_write_sgf.sgf")

    # Naviguer l'arbre jusqu'a la fin
    current = moveTree.head
    main_goban = goban.Goban(19,19)
    while current.has_next():
        main_goban.play_move(current)
        current = current.get_child(0)

    my_position = main_goban.board
    bc.set_position(my_position)
    root.mainloop()
    
