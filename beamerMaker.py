import Goban
import MoveTree
import os
import sys

def commaList(stoneList):
    commaList = ''
    for stone in stoneList:
        commaList += stone.igo(19) + ','
    return commaList[0:len(commaList)-1]
def makeDiagram(node):
    diagram = '\\cleargoban\n'
    blackStones = commaList(node.goban_data['gobanState']['B'])
    whiteStones = commaList(node.goban_data['gobanState']['W'])
    diagram += '\\white{' + whiteStones + '}\n'
    diagram += '\\black{' + blackStones + '}\n'
    diagram += '\\showfullgoban\n'
    return diagram
def makeDiffDiagram(node):
    diagram = ''
    if node.color == 'W':
        diagram += '\\white{' + node.igo(19) + '}\n'
    else:
        diagram += '\\black{' + node.igo(19) + '}\n'
    removedStones = []
    for group in node.goban_data['removed']:
        removedStones += group
    removedList = commaList(removedStones)
    diagram += '\\clearintersection{'+ removedList + '}\n'
    diagram += '\\showfullgoban\n'
    return diagram
def putLabels(node):
    noop
class Sai:
    def __init__(self):
        self.states = { 'init':self.bonjour, 'mainMenu':self.parcourirFichier,\
                'finished': self.finished, 'findNode':self.trouverNoeud,\
                'validateFile': self.userValidate, 'saveFile':self.saveFile,\
                'open':self.ouvrirFichier,'save':self.saveFile,\
                'findEndNode':self.trouverNoeudFin}
        self.fileS = ''
        self.state = 'init'
        self.frameFile = open(os.path.join(os.getcwd(),'framestart.tex')).read()
        self.prediag = open(os.path.join(os.getcwd(),'prediag.tex')).read()
        self.postdiag = open(os.path.join(os.getcwd(), 'postdiag.tex')).read()
    def makePage(self,node,pageType):
        page = '%%%%%%%%%%%%%%%%%%%% MOVE ' + str(node.moveNumber) + ' %%%%%%%%%%%%%%%%%%%%%%%\n'
        page += '\\begin{frame}\n\n'
        page += '\\frametitle{' + self.frametitle + '}\n'
        page += self.frameFile
        page += '% % BEGIN SGF COMMENTS % %\n'
        page += node.getComment() + '\n'
        page += '% % END SGF COMMENTS % %\n'
        page += self.prediag
        if pageType == 'diff':
            page += makeDiffDiagram(node)
        else:
            page += makeDiagram(node)
        page += self.postdiag
        page += '\\end{frame}\n'
        return page
    def __exec__(self):
        while self.state != 'finished':
            self.states[self.state]()
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    def printCurrent(self):
        self.current.nodePrint()
    def clearPrint(self):
        self.clear()
        self.printCurrent()
    def finished():
        return 0
    def ouvrirFichier(self):
        filename = raw_input("""
        Jean-Sebastien, peux-tu me dire quel fichier tu veux ouvir? 
        En passant c'est correct si je t'appelle par ton
        prenom?
        
        Fichier:""")
        self.tree = MoveTree.Tree(filename)
        self.current = self.tree.head
        self.end = self.tree.head
        info = self.tree.info.data
        self.frametitle = info['PW'] + ' vs ' + info['PB']
        self.state = 'mainMenu'
    def parcourirFichier(self):
        self.clear()
        self.tree.printInfo()
        self.printCurrent()
        choix = raw_input(""" >>>> JS, (c'est correct si je t'appelle JS?), je suis pret a produire des
        diagrammes LaTeX vraiment sick pour toi!!
        
        Je peux produire plusieurs sortes de diagrammes pour toi. Choisis le
        type de diagramme que tu veux produire
        
        1: Mainline partant du noeud courant 
        2: Trouver noeud de depart
        3: Trouver noeud de fin

        Choix :""")
        if choix == '1':
            self.fileS = ''
            current = self.current
            self.fileS = self.makePage(current,'position')
            while current.hasNext():
                current = current.getChild(0)
                self.fileS += self.makePage(current,'diff')
            self.state = 'validateFile'
        if choix == '2':
            self.state = 'findNode'
        if choix == '3':
            self.state = 'findEndNode'
    def trouverNoeudFin(self):
        self.clearPrint()
        self.end.nodePrint()
        choix = raw_input(""" Whyyyy is the ice slippery ?

        Chercher un noeud de fin par
        
        C:commentaire
        N:Numero (entrer le numero)
        a accepter

        choix : """)
        if choix == 'A' or choix == 'a':
            self.state = 'mainMenu'
        elif choix == 'E' or choix == 'e':
            for child in self.end.children:
                child.nodePrint()
        elif choix == 'C' or choix == 'c':
            searchString = raw_input(""" Jean-Sebastien, dit moi la chaine de
            caracteres a chercher : """)
            self.end = self.findnodeFrom(self.tree.head,searchString)
        else:
            current = self.current
            i = 1
            while i < int(choix):
                current = current.getChild(0)
                i += 1
                if not current.hasNext():
                    break
        
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
        elif choix == 'E' or choix == 'e':
            for child in self.current.children:
                child.nodePrint()
        elif choix == 'C' or choix == 'c':
            searchString = raw_input(""" Jean-Sebastien, dit moi la chaine de
            caracteres a chercher : """)
            self.current = self.findnodeFrom(self.tree.head,searchString)
        else:
            self.current = self.tree.head
            i = 1
            while i < int(choix):
                self.current = self.current.getChild(0)
                i += 1
                if not self.current.hasNext():
                    break
    def findnodeFrom(self,start,string):
        ts = MoveTree.textSearchVisitor(string)
        start.acceptVisitor(ts)
        return ts.getResult()
        
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
    def bonjour(self):
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
if __name__ == "__main__":
    cyborg = Sai()
    cyborg.__exec__()
