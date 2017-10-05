import boardcanvas
import tkinter
if __name__ == "__main__":
    # Creation d'une fenetre principale
    root = tkinter.Tk()
    root.minsize(400, 400)
    bc = boardcanvas.BoardCanvas(root)
    root.mainloop()

