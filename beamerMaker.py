import Goban
import Parser
import sys


def getComment(sgfMove):
    if len(sgfMove) > 7:
        comment = sgfMove[7:len(sgfMove)-1] + '\n'
        comment = comment.replace('\\\\','\\')
        comment = comment.replace('\\]',']')
        return comment
    else:
        return ''

def SGF_to_IGO(move):
    charX = move[2]
    charY = letter_to_number(move[3])
    return charX + charY

def SGF_to_Goban(move):
    color = move[0]
    x = 1 + (ord(move[2]) - ord('a'))
    y = 1 + (ord(move[3]) - ord('a'))
    return (color, (x,y))

def Goban_to_IGO(coord):
    charX = chr(coord[0] + ord('a'))
    charY = str( 19 - coord[1] + 1 ) 
    return charX + charY

def letter_to_number(letter):
    return str(19 - ( ord(letter) - ord('a')))

def commaList(moveList):
    """ Transforms a list of strings into a comma separated list of these
    strings """
    moveString = ''
    for move in moveList:
        moveString += move + ','
    moveString = moveString[0:moveString.__len__()-1]
    return  moveString

class BeamerMaker:
    def __init__(self,size,frameTitle):
        self.frameTitle = frameTitle
        self.frameStart = '\\begin{frame} \n\\frametitle{' + frameTitle + '}\n'
        self.frameEnd = '\\showfullgoban\n\\end{frame}\n'
        self.move = 1
        self.goban = Goban.Goban(size,size)
        self.parser = Parser.Parser()
        self.parser.makeTree('Variations.sgf')

    def positionPage(self,moveNumber):
        # Clear goban
        self.goban.clear()

        # Play moves on goban
        mainline = self.parser.getMainlineBranchAt(0)['mainline']
        i = 0
        while i < len(mainline) and (moveNumber == 0 or i < moveNumber):
            sgfMove = mainline[i][0]
            print(sgfMove)
            gobanMove = SGF_to_Goban(sgfMove)
            self.goban.playMove(gobanMove[0],gobanMove[1])
            i += 1

        # Get stones from goban
        whiteStones = self.goban.getStones('W')
        blackStones = self.goban.getStones('B')

        # Translate to IGO coordinates
        whiteStonesIGO = []
        for coord in whiteStones:
            whiteStonesIGO.append(Goban_to_IGO(coord))
        blackStonesIGO = []
        for coord in blackStones:
            blackStonesIGO.append(Goban_to_IGO(coord))

        # Make into comma list
        commaListWhite = commaList(whiteStonesIGO)
        commaListBlack = commaList(blackStonesIGO)

        # Create LaTeX output
        output = ''
        output += '%%%%%%%%%%%%%%%% Position at move ' + str(moveNumber) + ' %%%%%%%%%%%%\n'
        output += self.frameStart
        output += '\\cleargoban\n'
        output += getComment(sgfMove)
        output += '\\white{' + commaListWhite + '}\n'
        output += '\\black{' + commaListBlack + '}\n'
        output += self.frameEnd

        return output

    def numberedPage(self, number, sgfMove,Title,writeNumber):
        # Obtain differences caused by move
        gobanMove = SGF_to_Goban(sgfMove)
        color = gobanMove[0]
        coord = gobanMove[1]
        
        differences = self.goban.playMove(color,coord)
        if not differences.has_key('move'):
            print ( 'AddNumberedPage(): invalid move')
            return '\n move number ' + str(number) + ' at ' + str(coord) + ' is invalid \n\n'

        # Start of page
        pageText = '\n\n\n%%%%%%%%%%%%%%%% ' + Title + ' %%%%%%%%%%%% \n'
        pageText += self.frameStart
        pageText += getComment(sgfMove)

        # Remove stones
        for remGroup in differences['removed']:
            for remCoord in remGroup:
                pageText += '\\clear{' + Goban_to_IGO(remCoord) + '}\n'

        # Put stone
        if color == 'W':
            pageText += '\\white'
        else:
            pageText += '\\black'

        if writeNumber:
            pageText += '[' + str(number) + ']'
        pageText += '{' + Goban_to_IGO(coord) + '}\n'

        # End page
        pageText += self.frameEnd
        return pageText

    def makeVariation(self, branchPoint, variationNumber):
        output = self.positionPage(branchPoint)
        
        # Get the moveList for the variation
        variations = self.parser.getMainlineBranchAt(branchPoint)['variations']
        if variationNumber < len(variations):
            variation = variations[variationNumber]
        else:
            variation = []
            print ( 'No such variation: ' + str(variationNumber) )

        # Make a numbered move page for each move
        number = 1
        for moveTuple in variation:
            sgfMove = moveTuple[0]
            gobanMove = SGF_to_Goban(sgfMove)
            pageTitle = 'Variation after move '+ str(branchPoint) + ': move ' + str(number) 
            output += self.numberedPage(number,sgfMove,pageTitle,True)
            number += 1
        return output
            
    def playMovesTill(self, moveNumber):
        mainline = self.parser.getMainlineBranchAt(0)['mainline']
        self.goban.clear()
        i = 0
        output = ''
        while i < len(mainline) and (moveNumber == 0 or i < moveNumber):
            sgfMove = mainline[i][0]
            i += 1
            pageTitle = 'mainline move ' + str(i)
            output += self.numberedPage(i,sgfMove,pageTitle,False)
        return output
        
if __name__ == "__main__":
    bm = BeamerMaker(19,'ALLO')
    output = bm.makeVariation(3,3)
    print ( output )
    #output = bm.playMovesTill(7)
    #print (output)
