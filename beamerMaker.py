import Goban
import MoveTree
import os
import sys

def isInt(string):
    i = 0
    while i < len(string):
        if string[i] not in '0123456789':
            return False
        i += 1
    return True
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
class BeamerMaker:
    def __init__(self):
        self.frameFile = open(os.path.join(os.getcwd(),'framestart.tex')).read()
        self.prediag = open(os.path.join(os.getcwd(),'prediag.tex')).read()
        self.postdiag = open(os.path.join(os.getcwd(), 'postdiag.tex')).read()
        self.frametitle = 'FrameTitle'
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
    def ml_from(self,node):
        pathStack = [node]
        current = node
        while current.hasNext():
            current = current.getChild(0)
            pathStack.append(current)
        pathStack.reverse()
        return pathStack

    def ml_to(self,node):
        pathStack = [node]
        current = node
        while current.hasParent():
            current = current.parent
            pathStack.append(current)
        return pathStack
    def ml_between(self,start,end):
        pathStack = [node]
        current = node
        while current.hasParent() and current != end:
            current = current.parent
            pathStack.append(current)
        return pathStack
    def makeFile(self,nodeList):
        fileS = ''
        fileS = self.makePage(nodeList.pop(),'position')
        while len(nodeList) > 0:
            fileS += self.makePage(nodeList.pop(),'diff')
        return fileS
    def saveFile(self,string,filename):
        f = open(filename,'w')
        f.write(string)
        f.close()
    def mainline_from(self,node):
        nodeList = self.ml_from(node)
        return self.makeFile(nodeList)
    def allOptions(self,node,prefix):
        fileS = ''
        todo_stack = []
        for branch in node.children:
            todo_stack.append((node,branch))
        uniqueID = 0
        while len(todo_stack) > 0:
            # Get Todo from stack
            todo = todo_stack.pop()
            branchPoint = todo[0]
            branch = todo[1]
            fileS = self.makePage(branchPoint,'position')
            current = branch
            fileS += self.makePage(current,'diff')
            while not current.isLeaf():
                current = current.getChild(0)
                fileS += self.makePage(current,'diff')
                if current.isBranchPoint():
                    for branch in current.children[1:]:
                        todo_stack.append((current,branch))
            uniqueID += 1
            self.saveFile(fileS,prefix + str(uniqueID) + 'branchPoint' + str(branchPoint.moveNumber) + '_branch' + str(branch))
            fileS = ''
class Sai:
    def __init__(self):
        self.states = { 'init':self.introScreen, 'mainMenu':self.mainMenu,\
                'finished': self.finished, 'findNode':self.trouverNoeud,\
                'validateFile': self.userValidate, 'saveFile':self.saveFile,\
                'open':self.ouvrirFichier,'save':self.saveFile,\
                'findEndNode':self.trouverNoeudFin}
        self.fileS = ''
        self.state = 'open'
        self.bm = BeamerMaker()
    def __exec__(self):
        while self.state != 'finished':
            self.states[self.state]()
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print "=========================================== BeamerMaker v.0.1 ============================================="
    def printCurrent(self):
        print "============================================== Current Move ==============================================="
        self.current.nodePrint()
    def printEnd(self):
        print "================================================ End move ================================================="
        self.end.nodePrint()
    def clearPrint(self):
        self.clear()
        self.printCurrent()
        self.printEnd()
    def finished():
        return 0
    def ouvrirFichier(self):
        self.clear()
        filename = raw_input("""
        Jean-Sebastien, peux-tu me dire quel fichier tu veux ouvir? 
        En passant c'est correct si je t'appelle par ton
        prenom?
        
        Fichier:""")
        self.tree = MoveTree.Tree(filename)
        self.current = self.tree.head
        self.end = self.tree.head
        info = self.tree.info.data
        self.bm.frametitle = info['PW'] + ' vs ' + info['PB']
        self.state = 'mainMenu'
    def mainMenu(self):
        self.clear()
        self.tree.printInfo()
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
        # elif choix == 'E' or choix == 'e':
        #     for child in self.end.children:
        #         child.nodePrint()
        elif choix == 'C' or choix == 'c':
            searchString = raw_input(""" Jean-Sebastien, dit moi la chaine de
            caracteres a chercher : """)
            self.end = self.findnodeFrom(self.tree.head,searchString)
        else:
            if isInt(choix):
                current = self.current
                i = 1
                while i < int(choix):
                    current = current.getChild(0)
                    i += 1
                    if not current.hasNext():
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
                    current = current.getChild(0)
                    i += 1
                    if not current.hasNext():
                        break
                self.current = current
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
if __name__ == "__main__":
    cyborg = Sai()
    cyborg.__exec__()
    mt = MoveTree.Tree('Variations.sgf')
    bm = BeamerMaker()
    bm.allOptions(mt.head,'Variations:')

    # bm.ml_to(current)
        
