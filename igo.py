import os

def sgf_list_to_igo(sgf_list):
    igo_list = []
    for sgf in sgf_list:
        igo_list.append(MoveTree.SGF_to_IGO(sgf,19))
    return igo_list
def glyphCommand(node,symbol):
    symbols = {'TR':'\\igotriangle', 'SQ':'\\igosquare','CR':'\\igocircle'}
    igo_list = commaListStr(sgf_list_to_igo(node.data[symbol]))
    return '\\gobansymbol[' + symbols[symbol] + ']{' + igo_list + '}\n'
def glyphCommands(node):
    commands = ''
    for key in ['TR','SQ','CR']:
        if node.data.has_key(key):
            commands += glyphCommand(node,key)
    return commands
def commaListStr(coordList):
    commaList = ''
    for coord in coordList:
        commaList += coord + ','
    return commaList[0:len(commaList)-1]

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
    diagram += '\\cleargobansymbols\n'
    diagram += glyphCommands(node)
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
    if len(removedList) > 0:
        diagram += '\\clear{'+ removedList + '}\n'
    diagram += '\\cleargobansymbols\n'
    diagram += glyphCommands(node)
    diagram += '\\showfullgoban\n'
    return diagram
def putLabels(node):
    noop
class BeamerMaker:
    """ Creates the beamer-LaTeX code from go games

    Attributes: 
        frametitle : string : text content of framestart.tex used to let the
            user customize title of beamer frames.
        prediag : string : text content of prediag.tex lets the user define text
            that will be inserted right before diagrams.
        postdiag : string : text content of postdiag.tex placed right after
            diagrams
        framestart : string : text content of framestart.tex placed before
            SGF-commentary.
    """
        
    def __init__(self):
        """ Sets frametitle, framestart, prediag and postdiag with content from
        corresponding *.tex files """
        self.frameFile = open(os.path.join(os.getcwd(),'framestart.tex')).read()
        self.prediag = open(os.path.join(os.getcwd(),'prediag.tex')).read()
        self.postdiag = open(os.path.join(os.getcwd(), 'postdiag.tex')).read()
        self.frametitle = open(os.path.join(os.getcwd(),'frametitle.tex')).read().replace('\n','').replace('\r','')

    def makePage(self,node,pageType):
        """ Generate a beamer page (frame) from the given node. Frame beginning,
        SGF commentary, diagram (diff or position) and frame end, with contents
        of frametitle, framestart, prediag, postdiag added at the right places."""
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
        """ Visits the tree starting at the given node going to first child
        until a leaf is reached """
        pathStack = [node]
        current = node
        while current.hasNext():
            current = current.getChild(0)
            pathStack.append(current)
        pathStack.reverse()
        return pathStack

    def ml_to(self,node):
        """ Generates a path of nodes starting at the root of the tree and
        ending at the given node. """
        pathStack = [node]
        current = node
        while current.hasParent():
            current = current.parent
            pathStack.append(current)
        return pathStack

    def ml_between(self,start,end):
        """ Generates a path of nodes starting at the start node and ending at
        the end node. """
        pathStack = [node]
        current = node
        while current.hasParent() and current != end:
            current = current.parent
            pathStack.append(current)
        return pathStack

    def makeFile(self,nodeList):
        """ Creates a file from a node list. The file consists of the position
        at the first node in the list, the diff diagrams for each subsequent
        node until the end of the list."""
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
        """ Generates files for many of the options susceptible of being
        required by the user. In the future the files will have better unique
        names that will not require the to have a numeric ID to avoid name
        collisions."""
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
                    for branch in current.children:
                        todo_stack.append((current,branch))
            uniqueID += 1
            self.saveFile(fileS,prefix + str(uniqueID) + 'branchPoint' + str(branchPoint.moveNumber) + '_branch' + str(branch))
            fileS = ''
