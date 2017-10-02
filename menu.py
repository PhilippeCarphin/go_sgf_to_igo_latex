import Goban
import MoveTree
import os
import sys
import igo
def isInt(string):
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
        self.states = { 'init':self.introScreen, 'mainMenu':self.mainMenu,\
                'finished': None, 'findNode':self.trouverNoeud,\
                'validateFile': self.userValidate, 'saveFile':self.saveFile,\
                'open':self.chooseFile,'save':self.saveFile,\
                'findEndNode':self.trouverNoeudFin}
        self.fileS = ''
        self.current = None
        self.end = None
        self.state = 'open'
        self.bm = igo.BeamerMaker()

    def __exec__(self):
        """ Main loop of the state machine.  Calls the function (menu)
        associated with the current state """
        while self.state != 'finished':
            self.states[self.state]()

    def clear(self):
        """ Clears the screen and displays the heading """
        os.system('cls' if os.name == 'nt' else 'clear')
        print "=============================== IGO-LaTeX v.0.1 ================================="

    def printCurrent(self):
        """ Displays the current start move """
        print "================================== Current Move ==================================="
        self.current.node_print()

    def printEnd(self):
        """ Displays the current end move """
        print "==================================== End move ====================================="
        self.end.node_print()

    def clearPrint(self):
        """ Clears the screen and displays the current information """
        self.clear()
        self.printCurrent()
        self.printEnd()
    
    def mainMenu(self):
        """ Main menu with options for navigating the game tree and creating a
        mainline starting at the current node """
        self.clear()
        self.tree.print_info()
        self.printCurrent()
        self.printEnd()
        choix = raw_input(""" >>>> JS, (c'est correct si je t'appelle JS?), je suis pret a produire des
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

    def trouverNoeudFin(self):
        self.clearPrint()
        choix = raw_input(""" Whyyyy is the ice slippery ?

        Chercher un noeud de fin par
        
        C:commentaire
        N:Numero (entrer le numero)
        a accepter

        choix : """)
        if choix == 'A' or choix == 'a':
            self.state = 'mainMenu'
        elif choix == 'C' or choix == 'c':
            searchString = raw_input(""" Jean-Sebastien, dit moi la chaine de
            caracteres a chercher : """)
            self.end = self.findnodeFrom(self.tree.head,searchString)
        else:
            if isInt(choix):
                current = self.current
                i = 1
                while i < int(choix):
                    current = current.get_child(0)
                    i += 1
                    if not current.has_next():
                        break
                self.end = current

    def trouverNoeud(self):
        self.clearPrint()
        choix = raw_input(""" Mes systemes sont a la fine pointe de la
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
            searchString = raw_input(""" Jean-Sebastien, dit moi la chaine de
            caracteres a chercher : """)
            self.current = self.findnodeFrom(self.current,searchString)
        else:
            if isInt(choix):
                current = self.tree.head
                i = 1
                while i < int(choix):
                    current = current.get_child(0)
                    i += 1
                    if not current.has_next():
                        break
                self.current = current

    def findnodeFrom(self,start,string):
        ts = MoveTree.TextSearchVisitor(string)
        start.accept_visitor(ts)
        return ts.get_result()

    def userValidate(self):
        self.clear()
        print self.fileS
        choix = raw_input(""" >>>> Voici le code genere, est-ce qu'il te plait? 

        o : oui
        n : non

        Ton choix: """)
        if choix == 'o' or choix == 'O':
            self.state = 'saveFile'
        else:
            self.state = 'mainMenu'

    def saveFile(self):
        self.clear()
        name = raw_input(""" >>>> Super! Je suis content d'avoir pu rencontrer
        tes exigences.

        Quel nom veux-tu donner au fichier?

        Nom: """)

        f = open(name,'w')
        f.write(self.fileS)
        f.close()
        self.state = 'mainMenu'

    def introScreen(self):
        self.clear()
        print """
        Bonjour Jean-Sebastien, je suis ton assistant Sai, que puis-je faire pour
        toi aujoutd'hui?

        Ouvrir Fichier SGF : O

        """
        choix = raw_input(" Ton choix :")
        choix = 'o'
        if choix == 'o' or choix == 'O':
            self.state = 'open'

    def chooseFile(self):
        # Get list of files
        fileList = os.listdir(os.getcwd())

        # Choose only SGF files
        sgf_files = []
        for file in fileList:
            if file.endswith('sgf'):
                sgf_files.append(file)

        # Write message
        print """
        \" Listen up maggots, Popo's about to teach you the pecking order...\"

        Choisi parmi les fichiers suivants lequel tu veux ouvrir
        """
        # Write list
        i = 1
        for f in sgf_files:
            print "        ",i, ': ',f
            i += 1
        # Get number from user
        choix = raw_input("""
        Ton choix: """)
        # Open selected file
        choix = int(choix) - 1
        if choix >= len(sgf_files):
            choix = len(sgf_files) - 1
        self.tree = MoveTree.Tree(sgf_files[choix])
        self.current = self.tree.head
        self.end = self.tree.head
        self.state = 'mainMenu'

        self.state = 'mainMenu'
if __name__ == "__main__":
    cyborg = Sai()
    cyborg.__exec__()
    mt = MoveTree.Tree('Variations.sgf')
    bm = BeamerMaker()
    bm.all_options(mt.head, 'Variations:')

    # bm.ml_to(current)
        
