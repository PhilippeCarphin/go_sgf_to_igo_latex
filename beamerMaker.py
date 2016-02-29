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
    diagram = ''
    blackStones = commaList(node.goban_data['gobanState']['B'])
    whiteStones = commaList(node.goban_data['gobanState']['W'])
    diagram += '\\white{' + whiteStones + '}\n'
    diagram += '\\black{' + blackStones + '}\n'
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
    return diagram
def putLabels(node):
    noop
def makePage(node,pageType):
    page = '%%%%%%%%%%%%%%%%%%%% MOVE ' + str(node.moveNumber) + ' %%%%%%%%%%%%%%%%%%%%%%%\n'
    page += '\\begin{frame}\n\n'
    page += '% % BEGIN SGF COMMENTS % %\n'
    page += node.getComment() + '\n'
    page += '% % END SGF COMMENTS % %\n'
    if pageType == 'diff':
        page += makeDiffDiagram(node)
    else:
        page += makeDiagram(node)
    page += '\\end{frame}\n'
    return page
class Sai:
    def ouvrirFichier(self):
        #filename = raw_input("""
        #Jean-Sebastien, peux-tu me dire quel fichier tu veux ouvir? 
        #En passant c'est correct si je t'appelle par ton
        #prenom?
        #
        #Fichier:""")
        filename = 'Variations.sgf'
        self.tree = MoveTree.Tree(filename)
        self.parcourirFichier()
    def parcourirFichier(self):
        #choix = raw_input(""" >>>> JS, (c'est correct si je t'appelle JS?), je suis pret a produire des
        #diagrammes LaTeX vraiment sick pour toi!!
        #
        #Je peux produire plusieurs sortes de diagrammes pour toi. Choisis le
        #type de diagramme que tu veux produire
        #
        #1: Mainline Complet 
        #2: Mainline partant d'un noeud specifique 
        choix = '2'
        print 'PARCOURIR FICHIER'

        #Choix :""")
        if choix == '1':
            current = self.tree.head
            fileS = ''
            while current.hasNext():
                fileS += makePage(current,'diff')
                current = current.getChild(0)
            return self.userValidate(fileS)
        if choix == '2':
            self.trouverNoeud()
    def trouverNoeud(self):
        choix = raw_input(""" Mes systemes sont a la fine pointe de la
        technologie.  J'ai donc plusieurs facons de trouver des noeuds

        C: par commentaire
        N: par numero
        E: Enfanta
        a: accepter

        Ton choix:""")
        if choix == 'A' or choix == 'a':
            noop
        elif choix == 'E' or choix == 'e':
            for child in self.current.children:
                child.nodePrint()
        elif choix == 'C' or choix == 'c':
            print 'Pas encore disponible'
        else:
            self.current = self.tree.head
            i = 1
            while i < int(choix):
                self.current = self.current.getChild(0)
                i += 1
                if not self.current.hasNext():
                    break
            self.current.nodePrint()
        self.trouverNoeud()

        
    def userValidate(self,fileS):
        print fileS
        choix = raw_input(""" >>>> Voici le code genere, est-ce qu'il te plait? 

        o : oui
        n : non

        Ton choix: """)
        if choix == 'o' or choix == 'O':
            return self.saveFile(fileS)
        else:
            return self.fichierOuvert()
    def saveFile(self, fileS):
        name = raw_input(""" >>>> Super! Je suis content d'avoir pu rencontrer
        tes exigences.

        Quel nom veux-tu donner au fichier?

        Nom: """)

        f = open(name,'w')
        f.write(fileS)
        f.close()
    def bonjour(self):
        #print """
        #Bonjour Jean-Sebastien, je suis ton assistant Sai, que puis-je faire pour
        #toi aujoutd'hui?

        #Ouvrir Fichier SGF : O

        #"""
        #choix = raw_input(" Ton choix :")
        choix = 'o'
        if choix == 'o' or choix == 'O':
            self.ouvrirFichier()
if __name__ == "__main__":
    t = MoveTree.Tree('./ShusakuvsInseki.sgf')
    t = MoveTree.Tree('Variations.sgf')
    t.head.acceptVisitor(MoveTree.mainlineVisitor())
    current = t.head.getChild(0)
    while current.hasNext():
        current = current.getChild(0)
        latex = makePage(current,'diff')
        print latex
    current = t.head
    while current.hasNext():
        current = current.getChild(0)
        latex = makePage(current,'')
        print latex
    cyborg = Sai()
    cyborg.bonjour()
