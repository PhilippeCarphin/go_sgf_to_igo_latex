import movetree
import os
import igo

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
along with Foobar.  If not, see <http://www.gnu.org/licenses/>."""


def is_int(string):
    i = 0
    while i < len(string):
        if string[i] not in '0123456789':
            return False
        i += 1
    return True


class Sai:
    """ Command line interface to the beamer class.  This interface is
    implemented as state machine with various menus performing different actions
    and setting the following state.

    Attributes:
        states : Dictionnary of states with names as keys and function objects
            as valures
        state : The current state of the machine
        fileS : The string of a file returned by a call to beamerMaker.  This
            file will be shown to the user and saved as a file. 
        bm : BeamerMaker instance used to generate LaTeX output as per the
            user's demands
        tree : Move tree created from an SGF file and eventually with a user
            interface.
    """
    def __init__(self):
        """ Defines the dictionnary of states, sets the initial state and
        creates a BeamerMaker instance """
        self.states = {'init': self.intro_screen, 'mainMenu': self.main_menu,
                       'finished': None, 'findNode': self.find_node,
                       'validateFile': self.user_validate, 'saveFile': self.save_file,
                       'open': self.choose_file, 'save': self.save_file,
                       'findEndNode': self.find_end_node}
        self.fileS = ''
        self.current = None
        self.end = None
        self.state = 'open'
        self.bm = igo.BeamerMaker()
        self.tree = None

    def __exec__(self):
        """ Main loop of the state machine.  Calls the function (menu)
        associated with the current state """
        while self.state != 'finished':
            self.states[self.state]()

    @staticmethod
    def clear():
        """ Clears the screen and displays the heading """
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=============================== IGO-LaTeX v.0.1 =================================")

    def print_current(self):
        """ Displays the current start move """
        print("================================== Current Move ===================================")
        self.current.node_print()

    def print_end(self):
        """ Displays the current end move """
        print("==================================== End move =====================================")
        self.end.node_print()

    def clear_print(self):
        """ Clears the screen and displays the current information """
        self.clear()
        self.print_current()
        self.print_end()
    
    def main_menu(self):
        """ Main menu with options for navigating the game tree and creating a
        mainline starting at the current node """
        self.clear()
        self.tree.print_info()
        self.print_current()
        self.print_end()
        choix = input(""" >>>> JS, (c'est correct si je t'appelle JS?), je suis pret a produire des
        diagrammes LaTeX vraiment sick pour toi!!
        
        Je peux produire plusieurs sortes de diagrammes pour toi. Choisis le
        type de diagramme que tu veux produire
        
        1: Mainline partant du noeud courant 
        2: Trouver noeud de depart
        3: Trouver noeud de fin

        Choix :""")
        if choix == '1':
            self.fileS = self.bm.mainline_from(self.current)
            self.state = 'validateFile'
        if choix == '2':
            self.state = 'findNode'
        if choix == '3':
            self.state = 'findEndNode'

    def find_end_node(self):
        self.clear_print()
        choix = input(""" Whyyyy is the ice slippery ?

        Chercher un noeud de fin par
        
        C:commentaire
        N:Numero (entrer le numero)
        a accepter

        choix : """)
        if choix == 'A' or choix == 'a':
            self.state = 'mainMenu'
        elif choix == 'C' or choix == 'c':
            search_string = input(""" Jean-Sebastien, dit moi la chaine de
            caracteres a chercher : """)
            self.end = self.find_node_from(self.tree.head, search_string)
        else:
            if is_int(choix):
                current = self.current
                i = 1
                while i < int(choix):
                    current = current.get_child(0)
                    i += 1
                    if not current.has_next():
                        break
                self.end = current

    def find_node(self):
        self.clear_print()
        choix = input(""" Mes systemes sont a la fine pointe de la
        technologie.  J'ai donc plusieurs facons de trouver des noeuds

        C: par commentaire
        N: par numero (entrer le numero)
        E: Enfant
        a: accepter

        Ton choix:""")
        if choix == 'A' or choix == 'a':
            self.state = 'mainMenu'
        # elif choix == 'E' or choix == 'e':
        #     for child in self.end.children:
        #         child.nodePrint()
        elif choix == 'C' or choix == 'c':
            search_string = input(""" Jean-Sebastien, dit moi la chaine de
            caracteres a chercher : """)
            self.current = self.find_node_from(self.current, search_string)
        else:
            if is_int(choix):
                current = self.tree.head
                i = 1
                while i < int(choix):
                    current = current.get_child(0)
                    i += 1
                    if not current.has_next():
                        break
                self.current = current

    @staticmethod
    def find_node_from(start, string):
        ts = movetree.TextSearchVisitor(string)
        start.accept_visitor(ts)
        return ts.get_result()

    def user_validate(self):
        self.clear()
        print(self.fileS)
        choix = input(""" >>>> Voici le code genere, est-ce qu'il te plait? 

        o : oui
        n : non

        Ton choix: """)
        if choix == 'o' or choix == 'O':
            self.state = 'saveFile'
        else:
            self.state = 'mainMenu'

    def save_file(self):
        self.clear()
        name = input(""" >>>> Super! Je suis content d'avoir pu rencontrer
        tes exigences.

        Quel nom veux-tu donner au fichier?

        Nom: """)

        f = open(name, 'w')
        f.write(self.fileS)
        f.close()
        self.state = 'mainMenu'

    def intro_screen(self):
        self.clear()
        print("""
        Bonjour Jean-Sebastien, je suis ton assistant Sai, que puis-je faire pour
        toi aujoutd'hui?

        Ouvrir Fichier SGF : O

        """)
        choix = input(" Ton choix :")
        if choix == 'o' or choix == 'O':
            self.state = 'open'

    def choose_file(self):
        # Get list of files
        file_list = os.listdir(os.getcwd())

        # Choose only SGF files
        sgf_files = []
        for file in file_list:
            if file.endswith('sgf'):
                sgf_files.append(file)

        # Write message
        print(""""
        \" Listen up maggots, Popo's about to teach you the pecking order...\"

        Choisi parmi les fichiers suivants lequel tu veux ouvrir
        """)
        # Write list
        i = 1
        for f in sgf_files:
            print("        ", i, ': ', f)
            i += 1
        # Get number from user
        choix = input("""
        Ton choix: """)
        # Open selected file
        choix = int(choix) - 1
        if choix >= len(sgf_files):
            choix = len(sgf_files) - 1
        self.tree = movetree.Tree(sgf_files[choix])
        self.current = self.tree.head
        self.end = self.tree.head
        self.state = 'mainMenu'


if __name__ == "__main__":
    cyborg = Sai()
    cyborg.__exec__()
