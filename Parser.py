import os
import sys
import re

def tokenList( string ):
    move = r'([WB]\[[a-z]{2}\])'
    comment = r'(\r?\n?C\[.*?[^\\]\]|[WB]\[[a-z]{2}\])?'
    paren = r'([()])|'
    label = r'(\r?\n?LB(?:\[[a-z]{2}\])+)?'
    tokenRegex = re.compile(paren + move + label + comment, re.DOTALL )
    return tokenRegex.findall(string)
    
# MOVES UTIL
def isMove(token):
    return len(token[0]) != 1

def splitParens(tokenList ,level):
    tempList = []
    i = 0
    while i < len(tokenList):
        if (isMove(tokenList[i])):
            tempList.append(move(tokenList[i]))
        if tokenList[i][0] == '(':
            start = i
            stack = 1
            while i < len(tokenList) and stack != 0:
                i += 1
                if tokenList[i][0] == '(':
                    stack += 1
                if tokenList[i][0] == ')':
                    stack -= 1
                    if stack == 0:
                        end = i
                        break
            sublist = tokenList[start+1:end]
            tempList.append(splitParens( sublist ,level + 1))
        i += 1
    return tempList

def token_to_move(token):
    return token[1:len(token)]

class move:
    def __init__(self,_token):
        self.token = _token[1:len(_token)]

    def sgf(self):
        """ returns SGF coordinates of move """
        return self.token[0]
    def goban(self):
        """ returns goban coordinates of move """
        return 'allo'
    def igo(self):
        """ returns IGO coordinates of move """
        return 'allo'
    def comment(self):
        """ returns comment string of move with special characters treated (see
        global getComment() for treatment of backslashes """
        return 'allo'
    def labels(self):
        return 'allo'
    def numbers(self):
        return 'allo'
    def __str__(self):
        return str(self.token)
    def __repr__(self):
        return repr(self.token)
    def __getitem__(self,i):
        return self.token[i]

    

class Parser:
    def __init__(self):
        self.usage = 'Parses SGF_file into data structures to make it ready for creating LaTeX ready files'
        self.moveTree = []

    def makeTree(self,filename):
        filePath = os.path.join(os.getcwd(),'Variations.sgf')
        fileContent = open(filePath).read()
        self.moveTree = splitParens(tokenList(fileContent),0)

    def getMainline(self,tree,number, branchPoint):
        """Creates a dictionnary with the complete mainline and the mainline of
        the variation starting at the specified branching point"""
        retDict = {'mainline':[], 'variations':[]}
        i = 0
        print ( tree )
        while  i < len(tree) and (tree[i][0][0] == 'B' or tree[i][0][0] == 'W'):
            number += 1
            retDict['mainline'].append((tree[i],number))
            i+=1
        if i < len(tree):
            if i == 0:
                print ('PURE LIST')
            mainline = tree[i]
            nextLevel = self.getMainline(mainline,number,branchPoint)
            retDict['mainline'] += nextLevel['mainline']
            retDict['variations'] = nextLevel['variations']
            if number == branchPoint and number != 0:
                varList = tree[i+1:len(tree)]
                for var in varList:
                    varMainline = self.getMainline(var,number,0)['mainline']
                    retDict['variations'].append(varMainline)
        return retDict
    
    def getMainlineBranchAt(self,moveNumber):
        return self.getMainline(self.moveTree,0,moveNumber)

if __name__ == "__main__":
     parser = Parser()
     parser.makeTree('Variations.sgf')
#  
     print (parser.moveTree)
#
#    print ('===============================================================')
#    mainline = parser.getMainlineBranchAt(8)
#    print (mainline)
#    print ('===============================================================')
#    dicti = parser.getMainlineBranchAt(3)
#    print (dicti['mainline'])
#    print ('\n\n')
#    for var in dicti['variations']:
#        print ( var )
#        print ('\n\n')
