import time
import copy
import os
import pygame
import sys
import inspect
import heapq, random

# # Code from pacman repo -> search.py
class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        '''
        PriorityQueue constructor
        '''
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

class Node:
    def __init__(self, state, direction = 0, cost = 0, parent = None):
        self.state = state
        self.pathCost = cost
        self.direction = direction
        self.parent = parent

# Code influenced by pacman repo -> searchAgents.py
class SearchProblem:

    def __init__(self, walls, goal, startState, startDirection):
        self.walls = walls
        self.goal = goal
        self.startState = startState
        self.direction = startDirection
        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def getStartDirection(self):
        return self.direction

    def getStartState(self):
        return self.startState
    
    def isGoalState(self, state):
        return state == self.goal
    
    def getSuccessors(self, state, direction):
        direction = int(direction)
        successors = []
        straight = left = right = None
        if direction == 0:
            straight = (state[0], state[1]-1)
            left = (state[0] - 1, state[1])
            right = (state[0] + 1, state[1] - 1)
        elif direction == 1:
            straight = (state[0] + 1, state[1] - 1)
            left = (state[0], state[1] - 1)
            right = (state[0] + 1, state[1])
        elif direction == 2:
            straight = (state[0] + 1, state[1])
            left = (state[0] + 1, state[1] - 1)
            right = (state[0], state[1] + 1)
        elif direction == 3:
            straight = (state[0], state[1] + 1)
            left = (state[0]+1, state[1])
            right = (state[0]-1, state[1]+1)
        elif direction == 4:
            straight = (state[0] - 1, state[1] + 1)
            left = (state[0], state[1] + 1)
            right = (state[0]-1, state[1])
        elif direction == 5:
            straight = (state[0] - 1, state[1])
            left = (state[0]-1, state[1]+1)
            right = (state[0], state[1]-1)
        else:
            print("Invalid direction " + str(direction) + " passed to Ident.__get_neighbor(dir)")


        if left != None and left not in self.walls:
            successors.append((left, (direction - 1)%6, 1))
        else:
            successors.append(None)
        if straight != None and straight not in self.walls:
            successors.append((straight, direction, 1))
        else:
            successors.append(None)
        if right != None and right not in self.walls:
            successors.append((right, (direction + 1)%6, 1))
        else:
            successors.append(None)

        # for debugging
        newStates = [left, straight, right]
        self._expanded += 1
        for state in newStates:
            if state not in self._visited:
                self._visited[state] = True
                self._visitedlist.append(state)
        #print("Successors: ", successors)
        return successors


    # not required right now
    def getCostOfActions(self, actions):
        util.raiseNotDefined()

# Code from pacman repo -> search.py
def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def manhattanHeuristic(position, problem, info={}):
    "The Manhattan distance heuristic for a PositionSearchProblem"
    #print("calculating Manhattan distance...")
    xy1 = position
    xy2 = problem.goal
    #print("abs(", xy1[0], " - ", xy2[0], ") + abs(", xy1[1], " - ", xy2[1], ")")
    #print(abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1]), end = '\n')
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def aStarSearch(problem, heuristic=manhattanHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    startState = problem.getStartState()
    startDirection = problem.getStartDirection()
    root = Node(startState, startDirection)
    frontier = PriorityQueue()
    frontier.push(root, 0)

    explored = []   # list of explored states

    while True:
        if frontier.isEmpty():
            print("returning empty list")
            return []
        node = frontier.pop()
        print("We are here ", node.state, " facing ", node.direction)
        if problem.isGoalState(node.state):
            return Solution(node)
        if node.state not in explored:
            explored.append(node.state)
            #print("State and direction: ", node.state, node.direction)
            successors = problem.getSuccessors(node.state, node.direction)
            for item in successors:
                #manhattan = util.manhattanDistance(item[0][0], item[0][1])
                if item != None:
                    heur = heuristic(item[0], problem)
                    child = Node(item[0], item[1], item[2] + node.pathCost, node)   # state, direction, cost, parent
                    #print("heuristic score: ", child.pathCost + heur)
                    frontier.push(child, child.pathCost + heur)

def Solution(node):
    print("Goal reached. Solution forming...")
    directions = []
    while node.parent != None:
        directions.append(node.direction)
        node = node.parent
    #print("actions: ", actions)
    #print("actions reversed: ", actions[::-1])
    return directions[::-1]


class Run:
    
    def start(self, info = None):
        # reading the intial state of the hex board from a file
        
        if not info:
            __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            file = open(os.path.join(__location__, "initial_state.txt"), "r")
        info = self.__read_file(file)        #[goal, start, wall]
        
        problem = SearchProblem(info[3], info[0], info[1], info[2])
        directions = aStarSearch(problem)
        print(directions)
        return directions

    def __read_file(self, file):
        goal = None
        start = None
        direction = 0
        wall = []
        for line in file:
            line_parts = line.split(" ")
            matrix_index = int(line_parts[0])
            list_index = int(line_parts[1])
            command = line_parts[2]
            if command == "goal" or command == "goal\n":
                goal = (matrix_index, list_index)
            elif command == "wall" or command == "wall\n":
                wall.append((matrix_index, list_index))
            # Print error message
            elif command == "agent" or command == "agent\n":
                start = (matrix_index, list_index)
                direction = line_parts[4]
            else:
                print("Command " + command + " invalid.")
        return [goal, start, direction, wall]

