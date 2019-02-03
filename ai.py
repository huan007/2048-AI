from __future__ import absolute_import, division, print_function
import copy
import random
from heapq import nlargest
from Node import *
MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}

class Gametree:
	"""main class for the AI"""
	# Hint: Two operations are important. Grow a game tree, and then compute minimax score.
	# Hint: To grow a tree, you need to simulate the game one step.
	# Hint: Think about the difference between your move and the computer's move.
	def __init__(self, root_state, depth_of_tree, current_score): 
            #State will be a 2d matrix. With the mini matrix being the column,
            #NOT the ROW

            #TODO Change 4 to generic board size
            self.rootNode = Node(root_state, "max", current_score, 4)
            self.depth_of_tree = depth_of_tree

            pass
	# expectimax for computing best move
	def expectimax(self, node):
            if terminal(node):
                #print("Terminal")
                return payoff(node)
            elif max_player(node):
                #print("Max Player")
                value = float("-inf")
                for n in node.children:
                    value = max(value, self.expectimax(n))
                return value
            elif chance_player(node):
                #print("Chance Player")
                value = 0
                for n in node.children:
                    value = value + self.expectimax(n) * chance(n)
                return value
            else:
                print("Error!")

	# function to return best decision to game
	def compute_decision(self):
            #This is where we should construct the tree
            Simulator.buildTree(self.rootNode, self.depth_of_tree, 0)

            # Assuming that we already have 4 different child
            values = []
            for i in range(len(self.rootNode.children)):
                nextChild = self.rootNode.children[i]
                direction = nextChild.direction
                value = self.expectimax(nextChild)
                values.append((value, direction))

            #Check if all the options are the same value
            first = values[0][0]
            repeatCount = 0
            for i in range(len(values)):
                print("(",values[i][1],") Value: ", values[i][0])
                if values[i][0] == first:
                    repeatCount += 1
            if repeatCount == len(values):
                print("Had to pick random")
                return random.randint(0,4)

            #Pick the best choice
            bestChoice = nlargest(1, values)
            if (bestChoice[0][1] != Node.lastMove):
                # Reset staleFactor
                Node.lastMove = bestChoice[0][1]
                Node.staleFactor = 0
            else:
                #If we're picking the same direction, increase stale factor
                Node.staleFactor = Node.staleFactor + 0.1

            print("Choosing direction: ", bestChoice[0][1])
            #Return direction
            return bestChoice[0][1]

            


class Simulator:
    weightMatrix = [[4**15, 4**8,  4**7, 4**0], 
                    [4**14, 4**9,  4**6, 4**1],
                    [4**13, 4**10, 4**5, 4**2],
                    [4**12, 4**11, 4**4, 4**3]]

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
                newNode.setDirection(i)
                #Expand tree of the new node
                Simulator.buildTree(newNode, level-1, (nextPlayer + 1) % 2)
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
                        Simulator.buildTree(newNode, level-1, (nextPlayer + 1) % 2)
                        #Append to root node
                        node.addChild(newNode)
            chance = 0
            if count != 0:
                chance = 1 / count
            for n in node.children:
                n.setChance(chance)
    # }}}

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
    value = 0
    for y in range(node.board_size):
        for x in range(node.board_size):
            value += board[x][y] * Simulator.weightMatrix[x][y]

    spaceCount = 0
    for y in range(0, board_size):
        for x in range(0, board_size):
            #Going through the board now
            if board[x][y] == 0:
                spaceCount = spaceCount + 1

    value += spaceCount * 50

    return value

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

def distance(tile1, tile2):
    # Get coordinates of tile1
    x1 = tile1[1]
    y1 = tile1[2]
    # Get coordinates of tile2
    x2 = tile2[1]
    y2 = tile2[2]
    # Calculate euclidean distance
    return math.sqrt( ((x1-x2)**2) + ((y1-y2)**2))

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
