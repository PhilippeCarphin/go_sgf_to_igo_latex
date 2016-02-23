import os
import sys
import re

class Parser:
    def __init__(self):
        self.usage = 'Parses SGF_file into data structures to make it ready for creating LaTeX ready files'
        self.moveTree = []

    # MOVES UTIL
    def isMove(self, token):
        if token[0] == 'W' or token[0] == 'B':
            return True
        else:
            return False

    def splitParens(self, tokenList ,level):
        tempList = []
        i = 0
        while i < len(tokenList):
            if (self.isMove(tokenList[i])):
                tempList.append(tokenList[i])
            if tokenList[i] == '(':
                start = i
                stack = 1
                while i < len(tokenList) and stack != 0:
                    i += 1
                    if tokenList[i] == '(':
                        stack += 1
                    if tokenList[i] == ')':
                        stack -= 1
                        if stack == 0:
                            end = i
                            break
                sublist = tokenList[start+1:end]
                tempList.append(self.splitParens( sublist ,level + 1))
            i += 1
        return tempList

    def makeTree(self,filename):
        # filePath = os.path.join(os.getcwd(),raw_input('Please enter filename: '))
        filePath = os.path.join(os.getcwd(),'Variations.sgf')
        fileContent = open(filePath).read()
        moveRegex = r'[WB]\[[a-z]{2}\]\r?\n?C\[.*?[^\\]\]|[WB]\[[a-z]{2}\]'
        tokenRegex = re.compile(r'\(|\)|' + moveRegex, re.DOTALL )
        tokenList = tokenRegex.findall(fileContent)
        self.moveTree = self.splitParens(tokenList,0)

    def getMainline(self,tree,number, branchPoint):
        """Creates a dictionnary with the complete mainline and the mainline of
        the variation starting at the specified branching point"""
        retDict = {'mainline':[], 'variations':[]}
        i = 0
        while i < len(tree) and self.isMove(tree[i]):
            number += 1
            retDict['mainline'].append((tree[i],number))
            i+=1
        if i < len(tree):
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
  
    print (parser.moveTree)

    print ('===============================================================')
    mainline = parser.getMainlineBranchAt(8)
    print (mainline)
    print ('===============================================================')
    dicti = parser.getMainlineBranchAt(3)
    print (dicti['mainline'])
    print ('\n\n')
    for var in dicti['variations']:
        print ( var )
        print ('\n\n')
