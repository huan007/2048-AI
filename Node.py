import copy
import random
import math
from heapq import heappush, heappop
#Node class
class Node:
        staleFactor = 0
        lastMove = 0
        cornerRatingValue = 100
        lineRatingValue = 8
        wallRatingValue = 6
        adjacentRatingValue = 3
        spacePunishment = -10

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

        def setDirection(self, direction):
            self.direction = direction
