from __future__ import absolute_import, division, print_function
import copy
import random
import time
from heapq import nlargest
from Node import *

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}


# Name:  Huan Nguyen
# PID:   A12871523
# Email: hpn007@ucsd.edu

class Gametree:
    """main class for the AI"""
    globalLargest = 0

    # Hint: Two operations are important. Grow a game tree, and then compute minimax score.
    # Hint: To grow a tree, you need to simulate the game one step.
    # Hint: Think about the difference between your move and the computer's move.
    def __init__(self, root_state, depth_of_tree, current_score):
        # State will be a 2d matrix. With the mini matrix being the column,
        # NOT the ROW

        self.rootNode = Node(root_state, "max", current_score, 4)
        self.depth_of_tree = depth_of_tree
        self.m_callCount = 0
        self.m_dupCount = 0
        self.m_memory_counts = {}
        self.m_memory = {}
        if root_state[0][0] != Gametree.globalLargest:
            Gametree.globalLargest = largestTile(root_state)
        largest = Gametree.globalLargest
        if (largest < 2048):
            self.depth_of_tree = 3
        elif largest < 4096:
            self.depth_of_tree = 5
        else:
            self.depth_of_tree = 7

    # expectimax for computing best move
    def expectimax(self, node):
        self.m_callCount += 1
        if not node in self.m_memory:
            self.m_memory_counts[node] = 1
            # Do the work
            if terminal(node):
                # print("Terminal")
                self.m_memory[node] = payoff(node)
                return payoff(node)
            elif max_player(node):
                # print("Max Player")
                value = float("-inf")
                for n in node.children:
                    value = max(value, self.expectimax(n))
                self.m_memory[node] = value
                return value
            elif chance_player(node):
                # print("Chance Player")
                value = 0
                for n in node.children:
                    value = value + self.expectimax(n) * chance(n)
                self.m_memory[node] = value
                return value
            else:
                print("Error!")
        else:
            return self.m_memory[node]



    # function to return best decision to game
    def compute_decision(self):
        # grid = self.rootNode.state
        # if (grid[3][0] == grid[2][1] == grid[3][1]):
        #    if (grid[3][0] != 0) and (grid[2][1] != 0) and (grid[3][1] != 0):
        #    return 3
        # This is where we should construct the tree
        Simulator.initAndBuildTree(self.rootNode, self.depth_of_tree, 0)

        # Assuming that we already have 4 different child
        self.m_memory = {}
        values = []
        for i in range(len(self.rootNode.children)):
            nextChild = self.rootNode.children[i]
            direction = nextChild.direction
            value = self.expectimax(nextChild)
            values.append((value, direction))

        # Check if all the options are the same value
        first = values[0][0]
        repeatCount = 0
        for i in range(len(values)):
            # print("(",values[i][1],") Value: ", values[i][0])
            if values[i][0] == first:
                repeatCount += 1
        if repeatCount == len(values):
            print("Had to pick random")
            return random.randint(0, 4)

        # Pick the best choice
        bestChoice = nlargest(1, values)

        # print("Choosing direction: ", bestChoice[0][1])
        # Return direction
        return bestChoice[0][1]


class Simulator:
    weightMatrix = [[8 ** 15, 8 ** 8, 8 ** 7, 8 ** 0],
                    [8 ** 14, 8 ** 9, 8 ** 6, 8 ** 1],
                    [8 ** 13, 8 ** 10, 8 ** 5, 8 ** 2],
                    [8 ** 12, 8 ** 11, 8 ** 4, 8 ** 3]]

    weightScale = 0.00000001
    spaceScale = 50
    m_counts = {}
    m_dupCount = 0
    m_callCount = 0
    m_memory = {}

    def initAndBuildTree(node, level, nextPlayer):
        Simulator.m_memory = {}
        Simulator.m_counts = {}
        Simulator.m_dupCount = 0
        Simulator.m_callCount = 0
        Simulator.buildTree(node, level, nextPlayer)
    # {{{
    # Build tree steming from the specified node
    def buildTree(node, level, nextPlayer):
        if (node is None) or level == 0:
            return

        Simulator.m_callCount += 1
        string = stateToString(node.state, level)
        if not string in Simulator.m_counts:
            Simulator.m_counts[string] = 1
        else:
            Simulator.m_counts[string] += 1
            Simulator.m_dupCount += 1

        # Next player: Me
        if nextPlayer % 2 == 0:
            # Expand by speculating 4 directions
            for i in range(0, 4):
                # Create a deep copy of the current state
                tm = copy.deepcopy(node.state)
                # Make a move
                newScore = move(tm, node.board_size, i, node.point)
                # Check if the board hasn't changed, if not discard the branch
                if (isMatrixEqual(tm, node.state, node.board_size)):
                    continue

                tm_string = stateToString(tm, level-1)
                if tm_string in Simulator.m_memory:
                    node.addChild(Simulator.m_memory[tm_string])
                else:
                    # Create a node
                    newNode = Node(tm, "chance", newScore, node.board_size)
                    newNode.setDirection(i)
                    # Expand tree of the new node
                    Simulator.buildTree(newNode, level - 1, (nextPlayer + 1) % 2)
                    # Append to root node
                    node.addChild(newNode)
                    Simulator.m_memory[tm_string] = newNode

        # Next player: Computer
        else:
            # Check every slot to see if we have an empty spot, fill it in
            count = 0
            for y in range(0, node.board_size):
                for x in range(0, node.board_size):
                    # If we found an empty space then add a "2" tile to it
                    if node.state[x][y] == 0:
                        count = count + 1
                        # Create a deep copy of the current state
                        tm = copy.deepcopy(node.state)
                        # Add new tile
                        tm[x][y] = 2
                        newNode = Node(tm, "max", node.point, node.board_size)
                        # Expand tree of the new node
                        Simulator.buildTree(newNode, level - 1, (nextPlayer + 1) % 2)
                        # Append to root node
                        node.addChild(newNode)
            chance = 0
            if count != 0:
                chance = 1 / count
            for n in node.children:
                n.setChance(chance)
    # }}}


# {{{ Next section is mostly codes adapted from 2048.py
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


# Move tiles to one side
def moveTiles(tm, board_size):
    for i in range(0, board_size):
        for j in range(0, board_size - 1):
            while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
                for k in range(j, board_size - 1):
                    tm[i][k] = tm[i][k + 1]
                tm[i][board_size - 1] = 0


# Merge tiles to one side
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
            if tm[i][j - 1] == 0 and tm[i][j] > 0:
                return True
            elif (tm[i][j - 1] == tm[i][j]) and tm[i][j - 1] != 0:
                return True
    return False


def rotateMatrixClockwise(tm, board_size):
    for i in range(0, int(board_size / 2)):
        for k in range(i, board_size - i - 1):
            temp1 = tm[i][k]
            temp2 = tm[board_size - 1 - k][i]
            temp3 = tm[board_size - 1 - i][board_size - 1 - k]
            temp4 = tm[k][board_size - 1 - i]
            tm[board_size - 1 - k][i] = temp1
            tm[board_size - 1 - i][board_size - 1 - k] = temp2
            tm[k][board_size - 1 - i] = temp3
            tm[i][k] = temp4


# }}}


# Determine whether or not a node is terminal
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
    baseRating = 0
    spaceRating = 0
    differenceRating = 0

    spaceCount = 0
    difference = 0
    tileMap = {}
    smoothRating = 0
    for y in range(node.board_size):
        for x in range(node.board_size):
            # Here's the core of my algorithm, we weight each tile base on the 
            # position of the tile and the value it contain. A higher value
            # in the corner or next to the corner should weight more than lower
            # value. This is an implementation of CMA-ES
            baseRating += board[x][y] * Simulator.weightMatrix[x][y]
            # Going through the board now
            if board[x][y] == 0:
                spaceCount = spaceCount + 1
            titevalue = board[x][y]
            if not titevalue in tileMap:
                tileMap[titevalue] = []
            tileMap[titevalue].append((x,y))
    for value, coordinates in tileMap.items():
        length = len(coordinates)
        for i in range(length):
            for j in range(i+1, length):
                coordinate1 = coordinates[i]
                coordinate2 = coordinates[j]
                if (abs(coordinate1[0] - coordinate2[0]) == 0) and (abs(coordinate1[1] - coordinate2[1]) == 1):
                    smoothRating += 1
                elif (abs(coordinate1[0] - coordinate2[0]) == 1) and (abs(coordinate1[1] - coordinate2[1]) == 0):
                    smoothRating += 1

    baseRating = baseRating * Simulator.weightScale
    spaceRating = spaceCount * Simulator.spaceScale
    smoothRating = smoothRating * 50

    finalRating = baseRating + spaceRating + smoothRating

    # Check if we go into bad position, poison it
    # Here we check each direction see which one we can move
    tm = copy.deepcopy(node.state)
    move(tm, node.board_size, 0, node.point)
    canUp = not (isMatrixEqual(node.state, tm, node.board_size))
    tm = copy.deepcopy(node.state)
    move(tm, node.board_size, 1, node.point)
    canLeft = not (isMatrixEqual(node.state, tm, node.board_size))
    tm = copy.deepcopy(node.state)
    move(tm, node.board_size, 2, node.point)
    canDown = not (isMatrixEqual(node.state, tm, node.board_size))
    tm = copy.deepcopy(node.state)
    move(tm, node.board_size, 3, node.point)
    canRight = not (isMatrixEqual(node.state, tm, node.board_size))

    # If we can only move down, punish the AI
    if (not canUp) and (not canLeft) and (not canRight) and canDown:
        return 0

    return finalRating


# Determine if a node is max player
def max_player(node):
    if node.nextTurn == "max":
        return True
    else:
        return False


# Determine if a node is chance player
def chance_player(node):
    if node.nextTurn == "chance":
        return True
    else:
        return False


# Get the chance of the node happening
def chance(node):
    return node.chance


# Calculate euclidean distance of two nodes
def distance(tile1, tile2):
    # Get coordinates of tile1
    x1 = tile1[1]
    y1 = tile1[2]
    # Get coordinates of tile2
    x2 = tile2[1]
    y2 = tile2[2]
    # Calculate euclidean distance
    return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))


# Check if two matrices are equal
def isMatrixEqual(m1, m2, board_size):
    if m1 == m2:
        return True
    else:
        return False


def printMatrix(tm, board_size):
    for y in range(0, board_size):
        for x in range(0, board_size):
            if x != 0:
                print(" | ", end="")
            print(tm[x][y], end="")
        print("")
    ("")

def stateToString(matrix, level):
    string = ""
    # Rows
    for r in range(len(matrix)):
        # Columns
        for c in range(len(matrix[r])):
            string += str(matrix[r][c])
            # Print column separator
            if (c != (len(matrix[r]) - 1)):
                string += ','
        string += ';'
    string += str(level)
    return string

def largestTile(matrix):
    largest = 0
    for r in range(len(matrix)):
        for c in range(len(matrix[r])):
            if matrix[r][c] > largest:
                largest = matrix[r][c]
    return largest
