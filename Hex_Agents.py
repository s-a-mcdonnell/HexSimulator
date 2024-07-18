
import pygame
from search import Run

#######################################################################################################################
#######################################################################################################################
#                                                  AGENT CLASS                                                        #

class Agent:

    ###################################################################################################################

    def __init__(self, ident=None, index=0):
        self.index = index
        self.ident = ident

    ###################################################################################################################

    def set_ident(self, identtoput):
        self.ident = identtoput

    def get_dir(self, state, keys):
        """
        The Agent will receive a GameState (from hex) and
        must return an action from Directions.{Clockwise, CounterClockwise, Forward}
        """
        print("incorrect, please load a type of agent")

#######################################################################################################################
#######################################################################################################################
#                                              KEYBOARD AGENT CLASS                                                   #

class KeyboardAgent(Agent):

    ###################################################################################################################

    # Constructor

    def __init__(self, ident=None, index=0):

        self.index = index
        self.ident = ident

    ###################################################################################################################

    def set_ident(self, identtoput):
        self.ident = identtoput

    def get_dir(self, state, keys, cur_dir):

        if keys != None:
            if keys[pygame.K_d]:
                influence = 1
            elif keys[pygame.K_a]:
                influence = -1
            else:
                influence = 0
        else:
            influence = 0

        if cur_dir >= 0:
            cur_dir += influence
            cur_dir %= 6

        return cur_dir


#######################################################################################################################
#######################################################################################################################
#                                                 ASTAR AGENT CLASS                                                   #

class AstarAgent(Agent):

    # Constructor 
    def __init__(self, ident=None, index = 0):
        self.index = index
        self.ident = ident
        self.direction_list = []
        self.dir_index = 0
    
    def set_ident(self, identtoput):
        self.ident = identtoput

    def initializeAstar(self):
        newWorld = Run()
        info = [self.ident.world.goals[0], (self.ident.matrix_index, self.ident.list_index), self.ident.world.wall_list]
        self.direction_list = newWorld.start(file)

    def get_dir(self, state, keys, cur_dir):
        if self.direction_list == []:
            self.initializeAstar()
        if self.dir_index >= len(self.direction_list):
            return None
        self.dir_index += 1
        return self.direction_list[self.dir_index - 1]






