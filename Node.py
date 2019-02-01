import copy
#Node class
class Node:

        #Constructor
        def __init__(self, state, value=0, board_size=4):
            self.state = state
            self.value = value
            self.board_size = board_size
            self.children = []

        def addChild(self, child):
            self.children.append(child)

def move(tm, board_size, direction, oldScore):
    newScore = oldScore
    for i in range(0, direction):
        rotateMatrixClockwise(tm, board_size)
    if canMove(tm, board_size):
        moveTiles(tm, board_size)
        newScore = mergeTiles(tm, board_size, oldScore)
    for j in range(0, (4 - direction) % 4):
        rotateMatrixClockwise(tm, board_size)
    return newScore

#Move tiles to one side
def moveTiles(tm, board_size):
    for i in range(0, board_size):
        for j in range(0, board_size - 1):
            while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
                for k in range(j, board_size - 1):
                    tm[i][k] = tm[i][k + 1]
                tm[i][board_size - 1] = 0
#Merge tiles to one side
def mergeTiles(tm, board_size, oldScore):
    newScore = oldScore
    for i in range(0, board_size):
        for k in range(0, board_size - 1):
            if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
                tm[i][k] = tm[i][k] * 2
                tm[i][k + 1] = 0
                newScore += tm[i][k]
                moveTiles(tm, board_size)
    return newScore

def canMove(tm, board_size):
    for i in range(0, board_size):
        for j in range(1, board_size):
            if tm[i][j-1] == 0 and tm[i][j] > 0:
                return True
            elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
                return True
    return False

def rotateMatrixClockwise(tm, board_size):
    for i in range(0, int(board_size/2)):
        for k in range(i, board_size- i - 1):
            temp1 = tm[i][k]
            temp2 = tm[board_size - 1 - k][i]
            temp3 = tm[board_size - 1 - i][board_size - 1 - k]
            temp4 = tm[k][board_size - 1 - i]
            tm[board_size - 1 - k][i] = temp1
            tm[board_size - 1 - i][board_size - 1 - k] = temp2
            tm[k][board_size - 1 - i] = temp3
            tm[i][k] = temp4

#Build tree steming from the specified node
def buildTree(node, level, nextPlayer):
    if (node is None) or level == 0:
        print("Depth of 0!")
        return

    print("Current state")
    printMatrix(node.state, 4)
    #Next player: Me
    if nextPlayer % 2 == 0:
        #Expand by speculating 4 directions
        for i in range(0, 4):
            #Create a deep copy of the current state
            tm = copy.deepcopy(node.state)
            #Make a move TODO: Work to insert current score
            newScore = move(tm, node.board_size, i, node.value)
            #DEBUG print out
            print("New state (ME): ", i)
            printMatrix(tm, node.board_size)
            #Create a node 
            newNode = Node(tm, newScore, node.board_size)
            print("New Score: ", newScore)
            #TODO Evaluate the value of the new node
            #Expand tree of the new node
            buildTree(newNode, level-1, (nextPlayer + 1) % 2)
            #Append to root node
            node.addChild(newNode)
    #Next player: Computer
    else:
        #Check every slot to see if we have an empty spot, fill it in
        for y in range(0, node.board_size):
            for x in range(0, node.board_size):
                #If we found an empty space then add a "2" tile to it
                if node.state[x][y] == 0:
                    #Create a deep copy of the current state
                    tm = copy.deepcopy(node.state)
                    #Add new tile
                    tm[x][y] = 2
                    #DEBUG print out
                    print("New state (CP): ")
                    printMatrix(tm, node.board_size)
                    newNode = Node(tm, node.value, node.board_size)
                    #TODO Evaluate the value of the new node
                    #Expand tree of the new node
                    buildTree(newNode, level-1, (nextPlayer + 1) % 2)
        pass

def printMatrix(tm, board_size):
    for y in range(0, board_size):
        for x in range(0, board_size):
            if x != 0:
                print(" | ", end="")
            print(tm[x][y], end="")
        print("")
    print("")
