import copy
import random
import math
from heapq import heappush, heappop
#Node class
class Node:
        staleFactor = 0
        lastMove = 0

        #Constructor
        def __init__(self, state, nextTurn, point=0, board_size=4):
            self.state = state
            self.nextTurn = nextTurn
            self.point = point
            self.board_size = board_size
            self.children = []

        def addChild(self, child):
            self.children.append(child)

        def children(self):
            return self.children

        def setChance(self, chance):
            self.chance = chance

# {{{
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
# }}}

# {{{
#Build tree steming from the specified node
def buildTree(node, level, nextPlayer):
    if (node is None) or level == 0:
        return

    #print("Current state")
    #printMatrix(node.state, 4)
    #Next player: Me
    if nextPlayer % 2 == 0:
        #Expand by speculating 4 directions
        for i in range(0, 4):
            #Create a deep copy of the current state
            tm = copy.deepcopy(node.state)
            #Make a move TODO: Work to insert current score
            newScore = move(tm, node.board_size, i, node.point)

            #Check if the board hasn't changed, if not discard the branch
            if (isMatrixEqual(tm, node.state, node.board_size)):
                continue
            #Create a node 
            newNode = Node(tm, "chance", newScore, node.board_size)
            #TODO Evaluate the value of the new node
            #Expand tree of the new node
            buildTree(newNode, level-1, (nextPlayer + 1) % 2)
            #Append to root node
            node.addChild(newNode)
    #Next player: Computer
    else:
        #Check every slot to see if we have an empty spot, fill it in
        count = 0
        for y in range(0, node.board_size):
            for x in range(0, node.board_size):
                #If we found an empty space then add a "2" tile to it
                if node.state[x][y] == 0:
                    count = count + 1
                    #Create a deep copy of the current state
                    tm = copy.deepcopy(node.state)
                    #Add new tile
                    tm[x][y] = 2
                    newNode = Node(tm, "max", node.point, node.board_size)
                    #TODO Evaluate the value of the new node
                    #Expand tree of the new node
                    buildTree(newNode, level-1, (nextPlayer + 1) % 2)
                    #Append to root node
                    node.addChild(newNode)
        chance = 0
        if count != 0:
            chance = 1 / count
        for n in node.children:
            n.setChance(chance)
# }}}

def terminal(node):
    if len(node.children) == 0:
        return True
    else:
        return False

# This function will calculate the payoff of any given state
def payoff(node):
    board_size = node.board_size
    board = node.state
    # Sorted values in tuples: (position, x, y)
    sortedValues = []
    tileBuckets = {}
    spaceCount = 0
    for y in range(0, board_size):
        for x in range(0, board_size):
            #Going through the board now
            if board[x][y] == 0:
                spaceCount = spaceCount + 1
            else: 
                # Preprocess the grid
                sortedValues.append((board[x][y], x, y))
                # Counting number of of same tiles
                # Creating new bucket if needed
                if board[x][y] not in tileBuckets:
                    tileBuckets[board[x][y]] = []
                tileBuckets[board[x][y]].append((board[x][y], x, y))
    #Sort the tiles
    sortedValues.sort(reverse=True)
    largestTile = sortedValues[0]
    openSpaceRating = 0.3 * spaceCount
    randomness = Node.staleFactor * random.random()
    closenessRating = 0
    cornerRating = 0


    # Check if the fourth largest tiles are close together
    for i in range(len(sortedValues) // 2):
        closenessRating += 2 * rateTilesDistance(sortedValues[i], sortedValues[i+1])

    # Check if same kinda are far apart
    for tile, bucket in tileBuckets.items():
        for i in range(len(bucket)):
            for j in range(i+1, len(bucket)):
                closenessRating += rateTilesDistance(bucket[i], bucket[j])

    #Check if the largest tile is in a corner
    coordinates = largestTile[1:3]
    if coordinates == (0,0) or coordinates == (0, board_size-1) or coordinates == (board_size-1, 0) or coordinates == (board_size-1, board_size-1):
        #TODO: Good position, give positive values
        cornerRating = 1
    else:
        #TODO: Bad position, punish for being in this position
        cornerRating = -10

    return openSpaceRating + closenessRating + cornerRating + randomness

def max_player(node):
    if node.nextTurn == "max":
        return True
    else:
        return False

def chance_player(node):
    if node.nextTurn == "chance":
        return True
    else:
        return False

def chance(node):
    return node.chance

def rateTilesDistance(tile1, tile2):
    # Get coordinates of tile1
    x1 = tile1[1]
    y1 = tile1[2]
    # Get coordinates of tile2
    x2 = tile2[1]
    y2 = tile2[2]
    # Calculate euclidean distance
    distance = math.sqrt( ((x1-x2)**2) + ((y1-y2)**2))
    #If tiles are right next to each other
    if distance == 1:
        return 1
    #If tiles are diagonal to each other
    if 1 < distance < 2:
        return 0
    #Punish for tiles that are far apart
    else:
        return -2


def printMatrix(tm, board_size):
    for y in range(0, board_size):
        for x in range(0, board_size):
            if x != 0:
                print(" | ", end="")
            print(tm[x][y], end="")
        print("")
    ("")

def isMatrixEqual(m1, m2, board_size):
    if m1 == m2:
        return True
    else:
        return False
