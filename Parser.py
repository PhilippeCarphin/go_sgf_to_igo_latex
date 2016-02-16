import os
import sys
import re


class SGF_file:
    def __init__(self):
        self.usage = 'Use to translate SGF files into format friendly for usage with IGO-LaTeX package'
        self.fileContent = ''
   
    def getFilePath(self):
        self.filePath = os.path.join(os.getcwd(),raw_input('Please enter path to SGF file : '))
    
    def setFilePath(self, filename):
        self.filePath = os.path.join(os.getcwd(), filename)

    def openFile(self):
        fileHandle = open(self.filePath)
        self.fileContent = fileHandle.read()

class Parser:
    def __init__(self):
        self.usage = 'Parses SGF_file into data structures to make it ready for creating LaTeX ready files'
        self.whiteMoves_RAW = []
        self.whiteMoves = []
        self.blackMoves_RAW = []
        self.blackMoves = []
        self.numberedVariation_RAW = []
        self.sgf_file = SGF_file()

    def preprocess(self):
        self.sgf_file.fileContent = re.sub(r'(CA|LB|ST|GM|TB|TW|FF|SZ|AP|GN|PW|WR|EV|PB|BR|DT|PC|KM|RU|CH)\[.*?\]','',self.sgf_file.fileContent)
        self.sgf_file.fileContent = re.sub(r'\[..:.*?\]','',self.sgf_file.fileContent)
        i = 2
        string = self.sgf_file.fileContent
        c = string[i]
        while i < len(string):
            if string[i] == '(':
                stack = 1
                openParen = i
                i += 1
                print len(string)
                while i < len(string):
                    if string[i] == '(':
                        stack += 1
                    if string[i] == ')':
                        stack -= 1
                        if stack == 0:
                            closeParen = i
                            string = string[0:closeParen+1] 
                    i+=1
                i = openParen + 1
            i += 1
        i = 0
        print string + '\n\n\n'
        while i < len(string):
            if string[i] == '(':
                string = string[0:i] + string[i + 1:len(string)]
            i += 1
        self.sgf_file.fileContent = string




        
    
    def getMoves(self):
        regexWM = re.compile(r'W\[..\]')
        regexBM = re.compile(r'B\[..\]')
        self.whiteMoves_RAW = regexWM.findall(self.sgf_file.fileContent)
        self.blackMoves_RAW = regexBM.findall(self.sgf_file.fileContent)

    def getMoveList(self,filename):
        self.sgf_file.setFilePath(filename)
        self.sgf_file.openFile()
        regexMove = re.compile(r'[WB]\[[a-z]{2}\]')
        self.allMoves = regexMove.findall(self.sgf_file.fileContent)
        return self.allMoves

    def translateMoves(self):
        for move in self.whiteMoves_RAW:
            self.whiteMoves.append(self.SGF_to_IGO(move))
        for move in self.blackMoves_RAW:
            self.blackMoves.append(self.SGF_to_IGO(move))

    def SGF_to_IGO(self, move):
        charX = move[2]
        charY = self.letter_to_number(move[3])
        return charX + charY

    def SGF_to_Goban(self, move):
        color = move[0]
        x = 1 + (ord(move[2]) - ord('a'))
        y = 1 + (ord(move[3]) - ord('a'))
        return (color, (x,y))

    def Goban_to_IGO(self, coord):
        charX = chr(coord[0] + ord('a'))
        charY = str( 19 - coord[1] + 1 ) 
        return charX + charY

    def letter_to_number(self,letter):
        return str(19 - ( ord(letter) - ord('a')))

    def getNumberdVariation(self):
        regexNVAR = re.compile(r'\[..:\d*\]')
        regexNumber = re.compile(r'\d\d*')
        self.numberedVariation_RAW = regexNVAR.findall(self.sgf_file.fileContent)
        self.numericLabelDict = {}
        self.numberedMoves = []
        for numLabel in self.numberedVariation_RAW:
            move = numLabel[1] + self.letter_to_number(numLabel[2])
            number = regexNumber.search(numLabel).group()
            self.numericLabelDict[move] = number
            self.numberedMoves.append(move)

    def createLatexOutput(self):
        # Remove labeled moves
        self.whiteNumberedMoves = []
        self.blackNumberedMoves = []
        self.nocolorNumberedMoves = []
        whiteMoves = list(self.whiteMoves)
        blackMoves = list(self.blackMoves)
        numberedDict = dict(self.numericLabelDict)
        for move in self.numberedMoves:
            if( move in self.whiteMoves ):
                self.whiteNumberedMoves.append(move)
                whiteMoves.remove(move)
            elif( move in self.blackMoves ):
                self.blackNumberedMoves.append(move)
                blackMoves.remove(move)
            else: 
                self.nocolorNumberedMoves.append(move)

        whiteMoveString = '\\white{' + self.commaList(whiteMoves) + '}'
        blackMoveString = '\\black{' + self.commaList(blackMoves) + '}'

        numberedMovesString = ''
        for move in self.blackNumberedMoves:
            number = self.numericLabelDict[move]
            numberedMove = '\\black[' + number + ']{' + move + '}\n'
            numberedMovesString = numberedMovesString + numberedMove
        for move in self.whiteNumberedMoves:
            number = self.numericLabelDict[move]
            numberedMove = '\\white[' + number + ']{' + move + '}\n'
            numberedMovesString = numberedMovesString + numberedMove

        self.latexOutput = whiteMoveString + '\n' + blackMoveString + '\n' + numberedMovesString

    
    def commaList(self, moveList):
        moveString = ''
        for move in moveList:
            moveString += move + ','
        moveString = moveString[0:moveString.__len__()-1]
        return  moveString

            


        

if __name__ == "__main__":
    parser = Parser()
    parser.sgf_file.setFilePath('Phil_vs_Chantale.sgf')
    parser.sgf_file.openFile()
    parser.getMoves()
    parser.translateMoves()
    parser.getNumberdVariation()
    parser.createLatexOutput()
    print(parser.numberedVariation_RAW)
    print(parser.numericLabelDict)
    print(parser.latexOutput)

    print parser.sgf_file.fileContent
    parser.preprocess()
    print parser.sgf_file.fileContent

