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

            #This is where we should construct the tree
            buildTree(self.rootNode, depth_of_tree, 0)
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
            # Assuming that we already have 4 different child
            values = []
            for i in range(len(self.rootNode.children)):
                nextChild = self.rootNode.children[i]
                value = self.expectimax(nextChild)
                values.append((value, i))

            #Check if all the options are the same value
            first = values[0][0]
            last = values[0][0]
            for i in range(len(values)):
                print("Value: ", values[i][0])
                if values[i][0] > last:
                    last = values[i][0]
            if first == last:
                return random.randint(0,4)

            #Pick the best choice
            bestChoice = nlargest(1, values)
            if (bestChoice[0][1] != Node.lastMove):
                # Reset staleFactor
                Node.lastMove = bestChoice[0][1]
                Node.staleFactor = 0
            else:
                #If we're picking the same direction, increase stale factor
                Node.staleFactor = Node.staleFactor + 0.4

            #Return direction
            return bestChoice[0][1]

            


class Simulator:
	pass
