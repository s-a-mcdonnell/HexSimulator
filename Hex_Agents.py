
import pygame
from search import Run

#######################################################################################################################
#######################################################################################################################
#                                                  AGENT CLASS                                                        #

class Agent:

    ###################################################################################################################

    def __init__(self, ident, index=0):
        '''
        Generic Agent constructor
        '''
        self.index = index
        self.ident = ident

    ###################################################################################################################

    def get_dir(self, state, keys):
        '''
        The Agent will receive a GameState (from hex) and
        must return an action from Directions.{Clockwise, CounterClockwise, Forward}
        '''
        
        print("Error: Please load a type of agent")
        raise NotImplementedError

#######################################################################################################################
#######################################################################################################################
#                                              KEYBOARD AGENT CLASS                                                   #

class Keyboard_Agent(Agent):

    ###################################################################################################################

    def __init__(self, ident, index=0):
        '''Keyboard_Agent constructor'''

        self.index = index
        self.ident = ident

    ###################################################################################################################

    def get_dir(self, state, keys, cur_dir):
        '''Returns direction in which agent will head'''

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
    
        ###################################################################################################################

#######################################################################################################################

class A_Star_Agent(Agent):

    ###################################################################################################################

    # Constructor 
    def __init__(self, ident, index = 0):
        '''
        A_Star_Agent constructor
        :param ident: the Ident corresponding to this agent
        :param index:
        '''
        self.index = index
        self.ident = ident
        self.direction_list = []
        self.dir_index = 0

    ###################################################################################################################
    
    def initializeAstar(self):
        '''Initalize A* algorithm'''
        newWorld = Run()
        info = [self.ident.goals[0], (self.ident.matrix_index, self.ident.list_index), self.ident.world.wall_list]
        self.direction_list = newWorld.start(info)
    
    ###################################################################################################################

    def get_dir(self, state, keys, cur_dir):
        '''Returns direction in which agent will head'''
        if self.direction_list == []:
            self.initializeAstar()
        if self.dir_index >= len(self.direction_list):
            return None
        self.dir_index += 1
        return self.direction_list[self.dir_index - 1]
 
    ###################################################################################################################

#######################################################################################################################
