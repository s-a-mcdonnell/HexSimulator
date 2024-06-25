import time
import copy
import os
import pygame

# Debugger
import pdb

'''
Process of the game:
0. Iterate over Idents
1. a: If an ident is in a head on collision with another ident, it flips in place
   b: Else, move the ident forward into the next hex
2. Resolve collisions. For hexes that contain multiple idents...
   a: If it has an ident of opposite direction in that hex, bounce off/reverse direction
   b: Else, take the average of all other idents EXCEPT SELF, but break ties by using the opposite ident of self
'''

# for storing information about a particular moving hex
class Ident:


    # TODO: Do we still need this?
    idents_created = 0

    ##########################################################################################################
    
    def __init__(self, matrix_index, list_index, world, color=(255, 255, 255), state: int = -1, serial_number = -1, hist = None, property = None, partner_serial_number = -1):
        if hist is None:
            hist = []
        self.color = color

        self.state : int = state

        self.hist = hist
        if serial_number == -1:
            # If no serial number is provided
            self.serial_number = Ident.idents_created

            '''print("Ident with serial number " + str(self.serial_number) + " created")
            if state == -2:
                print("Is a wall")
            elif state == -1:
                print("Is stationary")
            else:
                print("Is moving")'''
            Ident.idents_created += 1
        else:
            self.serial_number = serial_number
            
            '''if self.state != -2:
                print("Ident with serial number " + str(self.serial_number) + " copied")
                print("color: " + str(self.color))'''

        self.matrix_index = matrix_index
        self.list_index = list_index

        self.world = world

        self.property = property

        self.partner_serial_number = partner_serial_number
    
    ##########################################################################################################

    # Returns the neighboring hex in the given direction in the given matrix
    # If that hex does not exist, returns None
    def __get_neighbor(self, matrix, dir):
        
        if dir == 0:
            try:
                return matrix[self.matrix_index][self.list_index - 1]
            except:
                return None
            
        elif dir == 1:
            try:
                return matrix[self.matrix_index + 1][self.list_index - 1]  
            except:
                return None

        elif dir == 2:
            try:
                return matrix[self.matrix_index + 1][self.list_index]
            except:
                return None

        elif dir == 3:

            try:
                return matrix[self.matrix_index][self.list_index + 1]
            except:
                return None

        elif dir == 4:

            try:
                return matrix[self.matrix_index - 1][self.list_index + 1]
            except:
                return None
            
        elif dir == 5:

            try:
                return matrix[self.matrix_index - 1][self.list_index]
            except:
                return None
            
        else:
            print("Invalid direction " + str(dir) + " passed to Ident.__get_neighbor(dir)")
            return None

    ##########################################################################################################

    # Helper method for resolve_collisions()
    # Takes the hex in which the ident is located and the direcs list of other idents in that hex
    # Returns the direcs list with pairs of idents which cancel out removed
    @staticmethod
    def __remove_pairs(hex, dir, directions):
        direcs = directions.copy()


        if dir == -1:
            '''# TODO: Explain how this needs to be written weirdly to work for dir = -1 (can't math right)
            return Ident.__remove_pairs(hex, 0, Ident.__remove_pairs(hex, 1, direcs))'''

            hex_zero = hex.contains_direction(0)
            hex_three = hex.contains_direction(3)
            if hex_zero and hex_three:
                direcs.remove(hex_zero)
                direcs.remove(hex_three)
            
            hex_one = hex.contains_direction(1)
            hex_four = hex.contains_direction(4)
            if hex_one and hex_four:
                direcs.remove(hex_one)
                direcs.remove(hex_four)

            hex_two = hex.contains_direction(2)
            hex_five = hex.contains_direction(5)
            if hex_two and hex_five:
                direcs.remove(hex_two)
                direcs.remove(hex_five)
            
            return direcs

        else:
            
            # TODO: Note that using contains_direction leaves us vulnerable if there are somehow multiple idents in the hex that share a direction

            hex_plus_one = hex.contains_direction((dir + 1) % 6)
            hex_minus_two = hex.contains_direction((dir - 2) % 6)
            if hex_plus_one and hex_minus_two:
                direcs.remove(hex_plus_one)
                direcs.remove(hex_minus_two)
            
            hex_plus_two = hex.contains_direction((dir + 2) % 6)
            hex_minus_one = hex.contains_direction((dir - 1) % 6)
            if hex_plus_two and hex_minus_one:
                direcs.remove(hex_plus_two)
                direcs.remove(hex_minus_one)
        
        return direcs

    ##########################################################################################################

    # Returns the absolute value of the difference between the directions of two idents
    def find_offset(self, other):
        for i in range(5):
            if ((self.state + i) % 6 == other.state) or ((self.state - i) % 6 == other.state):
                return i
    
    ##########################################################################################################

    # Returns a boolean indicating whether or not the given ident is a portal
    def is_portal(self):
        return self.property == "portal"
    
    ##########################################################################################################

    # Removes the ident(s) with self's serial number from the passed list
    def remove_from_list(self, my_list):
        for ident in my_list:
            if ident.serial_number == self.serial_number:
                my_list.remove(ident)

    ##########################################################################################################

    
    # Handles cases where self (a moving hex) collides with a stationary hex
    # TODO: How to handle the rounds of writing happening due to the newly stationary hexes?
    def __moving_collide_stationary(self, read_from_hex, write_to_matrix, write_to_ident_list):
        w = self.world

        assert self.state >= 0

        hex_of_origin = self.__get_neighbor(write_to_matrix, (self.state + 3)%6)
        assert hex_of_origin

        # If an ident with the opposite state is present, bounce off
        if read_from_hex.contains_direction((self.state + 3) % 6):
            # TODO: Remove stationary version of self from hex of origin
            self.__rotate_adopt(hex_of_origin, write_to_ident_list)
        
        # If two idents that sum to the opposite state are present, bounce off
        elif read_from_hex.contains_direction((self.state + 2) % 6) and read_from_hex.contains_direction((self.state + 4) % 6):
            # TODO: Remove stationary version of self from hex of origin
            self.__rotate_adopt(hex_of_origin, write_to_ident_list)

        # Else become stationary
        else:

            # Remove alt version of self from the to remove list
            self.remove_from_list(w.alt_idents_to_remove)

            # Get neighbors pointing at self
            neighbors_pointing_at_me = [None]*6
            for i in range(6):
                # NOTE: This method automatically uses hex_matrix, which I'm not sure is helpful here
                neighbors_pointing_at_me[i] = self.__neighbor_contains_direction((i+3)%6, i)

            # Add said neighbors to a list in world of moving hexes to double check
           #  w.idents_to___.append(neighbor)
            

            # 

            # TODO: What about the moving ident we want to hit this and turn stationary? (triangle collision)
            # Does our newly stationary hex have any identities running into it?

            '''
            example case:
            5 7 occupied CYAN
            5 8 move PURPLE 0
            4 8 move GREEN 2

            What to do about green?
            '''

            # NOTE: the folowing commented-out code should be taken care of by the adjustment to advance_or_flip
            #self.__rotate_adopt(hex_of_origin, write_to_ident_list, dir_final = - 1)

    ##########################################################################################################

    # Handle collisions between self (stationary) and moving idents within the same hex
    def __stationary_collide_moving(self, directions, hex, write_to_hex, write_to_list):
        dir = self.state
        w = self.world

        # if we contain opposite pairs, remove them from the directions list
        directions = self.__remove_pairs(hex, dir, directions)

        # If there are no idents left in directions, remain stationary
        if len(directions) == 0:
            # TODO: Is copying necessary?
            my_copy = self.__copy()
            write_to_hex.idents.append(my_copy)
            write_to_list.append(my_copy)

            if self in w.agents:
                w.swap_agents(self, my_copy)

        # If there is only one ident left in directions, take its state
        elif len(directions) == 1:
            self.__rotate_adopt(write_to_hex, write_to_list, dir_final = directions[0].state)
    
        elif len(directions) == 2:
            # TODO: Note that this is copied directly from above --> how can we restructure?
                # if the other two are at 120 degrees to each other, take the value in between
            if (directions[0].state + 2)%6 == directions[1].state:
                print("rotate call a")
                self.__rotate_adopt(write_to_hex, write_to_list, dir_final = (directions[0].state + 1)%6)
            elif (directions[0].state - 2)%6 == directions[1].state:
                print("rotate call b")
                self.__rotate_adopt(write_to_hex, write_to_list, dir_final = (directions[0].state - 1)%6)
            
            # if the other two cohabitants are adjacent to one another (60 degrees), take one of the states (arbitrary formula)
            # TODO: ^^ Note that this is an arbitrary decision ^^
            else:
                # TODO: Note that this runs into issues when there is superimposition of multiple stationary idents
                assert(directions[0].state != -1 and directions[1].state != -1)

                assert(((directions[0].state + 1)%6 == directions[1].state) or ((directions[0].state - 1)%6 == directions[1].state))
                
                # TODO: Change decision-making for which state to take?
                state_to_take = directions[0].state
                if (directions[0].state - directions[1].state)%6 > 2:
                    state_to_take = directions[1].state
                
                self.__rotate_adopt(write_to_hex, write_to_list, dir_final = state_to_take)
                
                
        elif len(directions) == 3:
            # If there are three moving idents which have not been removed from directions,
            # they are either all adjacent to one another
            # or they are symmetrical (all at 120 degrees from one another)
            
            # Symmetrical case --> stationary hex does not move
            if (directions[0].find_offset(directions[1]) == 2 and directions[1].find_offset(directions[2]) == 2):
                # TODO: Is copying necessary?
                my_copy = self.__copy()
                write_to_hex.idents.append(my_copy)
                write_to_list.append(my_copy)

                if self in w.agents:
                    w.swap_agents(self, my_copy)
            
            # Adjacent case (the three moving idents are clumped together) --> stationary hex is bumped in the direction of the middle ident
            else:

                # TODO: Add assertion here?
                
                direc_0_1_offset = directions[0].find_offset(directions[1])
                direc_1_2_offset = directions[1].find_offset(directions[2])
                direc_0_2_offset = directions[0].find_offset(directions[2])
                
                # If directions[0] has the middle state, take that state
                if direc_0_1_offset == 1 and direc_0_2_offset == 1:
                    # TODO: Is copying necessary?
                    self.__rotate_adopt(write_to_hex, write_to_list, dir_final = directions[0].state)
                
                # If directions[1] has the middle state, take that state
                elif direc_1_2_offset == 1 and direc_0_1_offset == 1:
                    # TODO: Is copying necessary?
                    self.__rotate_adopt(write_to_hex, write_to_list, dir_final = directions[1].state)

                # If directions[2] has the middle state, take that state
                elif direc_0_2_offset == 1 and direc_1_2_offset == 1:
                    # TODO: Is copying necessary?
                    self.__rotate_adopt(write_to_hex, write_to_list, dir_final = directions[2].state)

                else:
                    # None of the three idents have been calcualted to be in the middle
                    print("Error: No middle direction found")
                    pass

        else:
            print("Error: Unexpected length of directions")
            pass

    ##########################################################################################################

     # TODO: Write this method
    # note that I should never have to deal with walls in this method
    # note that this reads from hex_matrix_new and ident_list_new and writes to hex_matrix and ident_list
    def resolve_collisions(self):
        w = self.world

        # If self is a portal, do nothing
        if self.is_portal():
            w.hex_matrix[self.matrix_index][self.list_index].idents.append(self)
            w.ident_list.append(self)
            return

        # The hex to which we will be writing
        write_to_hex = w.hex_matrix[self.matrix_index][self.list_index]

        # obtain the hex that this ident is currently a part of
        hex = w.hex_matrix_new[self.matrix_index][self.list_index]
        if len(hex.idents) <= 1:
            print("No collision to resolve")

            # TODO: Is copying necessary here?
            my_copy = self.__copy()

            w.ident_list.append(my_copy)
            write_to_hex.idents.append(my_copy)

            if self in w.agents:
                w.swap_agents(self, my_copy)

            return
        
        # If the hex contains only one other state, and that state is a portal, nothing else needs be done
        if len(hex.idents) == 2 and hex.contains_portal():
            w.hex_matrix[self.matrix_index][self.list_index].idents.append(self)
            w.ident_list.append(self)
            return
        
        # now we have determined that the ident has other idents with it
        # TODO: I think we can do this without getting index (just only append to directions if ident is not self)
        '''my_index = hex.get_ident_index(self)'''
        dir = self.state

        # Store the other idents in the same hex
        directions = []

        for ident in hex.idents:
            # Do not add portal idents to list
            if (ident.serial_number != self.serial_number) and (not ident.is_portal()):
                directions.append(ident)

        # if there was only one other ident in the collision, take its attributes
        # Note that this also deals with the most simple collision betwen a moving ident and a stationary one
        # TODO: ^^ Check if this is true ^^
        
        # TODO: What if something contains both a stationary hex and a portal? (How would that come to be?)
        if (hex.contains_direction(-1) is None) or (hex.contains_portal()):
            # if we contain opposite pairs, remove them from the directions list
            directions = self.__remove_pairs(hex, dir, directions)
            
            # if we ended up with a net zero average (all other idents in the hex cancelled out in opposite pairs),
            # bounce off in the opposite direction from what is currently held
            if len(directions) == 0:
                self.__rotate_adopt(write_to_hex, w.ident_list)

            # if, at this point, there is only one direction left, take that one
            elif len(directions) == 1:
                print("rotate call e")
                self.__rotate_adopt(write_to_hex, w.ident_list, dir_final = directions[0].state)

                # TODO: Do something with self.world.alt_idents_to_remove

            # otherwise, there are exactly two other directions stored in this hex
            else:
                # Sanity checks
                assert(len(directions) == 2)
                assert(directions[0].state != directions[1].state)
                assert(directions[0].state != self.state)
                assert(directions[1].state != self.state)

                # if the other two are at 120 degrees to each other, take the value in between
                if (directions[0].state + 2)%6 == directions[1].state:
                    print("rotate call a")
                    self.__rotate_adopt(write_to_hex, w.ident_list, dir_final = (directions[0].state + 1)%6)
                elif (directions[0].state - 2)%6 == directions[1].state:
                    print("rotate call b")
                    self.__rotate_adopt(write_to_hex, w.ident_list, dir_final = (directions[0].state - 1)%6)
                
                # if the other two cohabitants are adjacent to one another (60 degrees), take the state of the one we are further away from
                else:
                    assert(((directions[0].state + 1)%6 == directions[1].state) or ((directions[0].state - 1)%6 == directions[1].state))
                    
                    closer_to_dir_0 = (abs(self.state - directions[0].state)%6) < (abs(self.state - directions[1].state)%6)
                    
                    # if current direction is closer to directions[0] than directions[1], take the state of directions[1]
                    if closer_to_dir_0:
                        print("rotate call c")
                        self.__rotate_adopt(write_to_hex, w.ident_list, dir_final = directions[1].state)
                    # else take the state of directions[0]
                    else:
                        print("rotate call d")
                        self.__rotate_adopt(write_to_hex, w.ident_list, dir_final = directions[0].state)

        # else, we are dealing with multiple idents, including a stationary ident
        else:
            assert(hex.contains_direction(-1))
            
            # A stationary ident colliding with a moving ident
            if self.state == -1:
                self.__stationary_collide_moving(directions, hex, write_to_hex, w.ident_list)

            # A moving ident (self) colliding with a stationary ident (another ident in the hex)
            else:
                self.__moving_collide_stationary(hex, w.hex_matrix, w.ident_list)


                
    ##########################################################################################################
    

    # If the head-on (direction of self.state) neighboring hex contains an ident with the given direction, returns said ident
    # Else returns None
    # TODO: Does this method still have a purpose?
    def __neighbor_contains_direction(self, neighbor_state, neighbor_index=None, ):
        # Default value
        if neighbor_index == None:
            neighbor_index = self.state

        try:
            return self.__get_neighbor(self.world.hex_matrix, neighbor_index).contains_direction(neighbor_state)
        except:
            print("Neighbor DNE")
            return None

    ##########################################################################################################


    # If the neighbor in the direction in which the ident is pointing is a wall, returns that ident
    # Else returns None
    def __neighbor_is_wall(self, neighbor_index_offset=0):
        neighbor_index = (self.state + neighbor_index_offset)%6

        return self.__neighbor_contains_direction(-2, neighbor_index)
        
    ##########################################################################################################

    # If there will be a head-on-collision, returns the ident with which it will collide
    # Else returns none
    # TODO: Could just use a boolean
    def __head_on_collision(self):
        return self.__neighbor_contains_direction((self.state + 3)%6)

    ##########################################################################################################
    
    # Copies self and rotates it by the indicated number of directions
    # Adopts said rotated ident
    def __rotate_adopt(self, future_hex, future_ident_list, dir_offset: int = 3, dir_final : int =-3):

        # Calculate final direction if none is given
        if dir_final == -3:
            dir_final = (self.state + dir_offset)%6
        
        
        print("Rotating ident " + str(self.serial_number) + " from state " + str(self.state) + " to " + str(dir_final))

        ident = self.__copy()
        ident.state = dir_final

        # This is necessary for moving hexes colliding with stationary hexes
        ident.matrix_index = future_hex.matrix_index
        ident.list_index = future_hex.list_index

        future_ident_list.append(ident)
        future_hex.idents.append(ident)

        if self in self.world.agents:
            self.world.swap_agents(self, ident)

    ##########################################################################################################

    # If an ident is stationary or a wall, writes this value to the hex_matrix_new
    # Elif an ident is running into a wall or a head-on collision, flips it in place (writing to hex_matrix_new)
    # Else advances an ident by one hex in its direction of motion (if that hex exists)
    def advance_or_flip(self):
        
        future_matrix = self.world.hex_matrix_new
        future_hex = future_matrix[self.matrix_index][self.list_index]
        future_list = self.world.ident_list_new
    
        # Maintain stationaries and return
        if self.state == -1:
            my_copy = self.__copy()

            future_list.append(my_copy)
            future_hex.idents.append(my_copy)

            if self in self.world.agents:
                self.world.swap_agents(self, my_copy)
            return

        # If need to bounce head-on off of a wall, then bounce and return
        head_on_wall = self.__neighbor_is_wall() and not (self.__neighbor_is_wall(1) or self.__neighbor_is_wall(-1))
        double_adjacent_wall = self.__neighbor_is_wall(1) and self.__neighbor_is_wall(-1)
        if head_on_wall or double_adjacent_wall:
            
            self.__rotate_adopt(future_hex, future_list)
            
            return


        # If need to bounce diagonally off of a wall, then bounce and return
        if self.__neighbor_is_wall(-1):
            self.__rotate_adopt(future_hex, future_list, dir_offset=1)

            return
        
        # Other diagonal wall bounce case
        if self.__neighbor_is_wall(1):
            self.__rotate_adopt(future_hex, future_list, dir_offset=-1)

            return
                
        # If need to bounce head-on off of another ident, then bounce and return
        if self.__head_on_collision():
            self.__rotate_adopt(future_hex, future_list)

            return
        
        # If hitting a stationary ident, freeze (and don't return, because you should also pass a version of yourself into it
        # TODO: Check how head_on_stationary is calcuated
        head_on_stationary = self.__neighbor_contains_direction(-1, self.state)
        if head_on_stationary:
            print("Becoming stationary in advance_or_flip()")
            self.world.alt_idents_to_remove.append(self)
            self.__rotate_adopt(future_hex, future_list, dir_final = -1)

        # Advance all others (if the location where they would advance to exists)
        future_neighbor = self.__get_neighbor(future_matrix, self.state)
        if future_neighbor:
            print("advance to future neighbor")
            copy_to_move = self.__copy()
            copy_to_move.matrix_index = future_neighbor.matrix_index
            copy_to_move.list_index = future_neighbor.list_index
                
            future_list.append(copy_to_move)
            future_neighbor.idents.append(copy_to_move)

            if self in self.world.agents:
                self.world.swap_agents(self, copy_to_move)

    ##########################################################################################################

    def visited(self, m, l):
        # push onto stack history
        # pushed onto the history is
            # hex matrix index
            # hex list index
            # current state

        # note, we want to keep up to 5 past states at a time
        # to change amount, just change limit #
        limit = 5

        if len(self.hist) == limit + 1:
            self.hist.pop(0)
            self.hist.append((m, l, self.state))
        else:
            self.hist.append((m, l, self.state))

        # print("------------------------------------------------------------------------------------------------------------------------", self.hist)

    ##########################################################################################################

    def __copy(self):
        # TODO: Should any of these components be done with .copy()?
        new_copy = Ident(self.matrix_index, self.list_index, self.world, color = self.color, state = self.state, serial_number = self.serial_number, hist = self.hist, property = self.property, partner_serial_number=self.partner_serial_number)
        return new_copy
    
        # TODO: Relocate the re-assigning of World.agent here?

    ###############################################################################################################

    def backstep(self):

        past = self.hist.pop()

        # first we change the state to the state it was at that point in time
        self.state = past[2]
        # then we put the ident into the hex it was before
        self.matrix_index = past[0]
        self.list_index = past[1]


    ###############################################################################################################

    # Adjust's agent's state based on input from file, read into world.agent_choices
    def get_next_move(self):

        assert self in self.world.agents

        w = self.world
        my_index = w.agents.index(self)

        if len(w.agent_choices[my_index]) == 0:
            print("No instructions provided for agent " + str(my_index))
            return


        # Get influence of the agent on its direction, wrapping around to the start of the file if necessary
        w.agent_indices[my_index] %= len(w.agent_choices[my_index])
        influence = w.agent_choices[my_index][w.agent_indices[my_index]]

        print("Next move " + str(influence))

        # TODO: What if the agent is currently stationary?
        if self.state >= 0:
            self.state += influence
            self.state %= 6

            # TODO: Make sure adjusted state is passed on
            '''adjusted_state = self.state + influence
            adjusted_state %= 6

            copy = self.__copy()
            copy.state = adjusted_state'''

        # Iterature agent index
        w.agent_indices[my_index] += 1

    
###############################################################################################################

# hex class is now just for graphics/displaying the board/storing idents
class Hex:
    # Default color (no idents): light blue
    DEFAULT_COLOR =(190, 240, 255)

    ##########################################################################################################

    # Checks where a specific ident occurs within this hex's list
    # If it contains the ident, returns the index
    # Else returns -1
    def get_ident_index(self, to_find):

        # TODO: What if the hex contains multiple idents with that state?
        for i in range(len(self.idents)):
            if self.idents[i] == to_find:
                return i
        return -1

    ###############################################################################################################

    # Takes x and y (Cartesian coordinates where (0, 0) is the top left corner)
    # Returns a list of 6 coordinates defining a hexagon
    @staticmethod
    def __create_coor(x, y):
        # Making hex smaller so that borders will be visible
        return [(x+3, y+3), (x+37, y+3), (x+57, y+35), (x+37, y+67), (x+3, y+67), (x-17, y+35)]

    ##########################################################################################################

    # Constructor
    def __init__(self, matrix_index, list_index):
        self.matrix_index = matrix_index
        self.list_index = list_index

        # Store relevant idents
        self.idents = []

        # Map matrix_index and list_index to Cartesian coordinates
        self.x = 60*matrix_index - 20
        self.y = 35*matrix_index + 70*list_index - 490

        self.coordinates = Hex.__create_coor(self.x, self.y)

       
        # TODO: Move arrows and smaller hexagon to idents? (maybe)
        # Create arrows for later use
        #pivot is the center of the hexagon
        pivot = pygame.Vector2(self.x + 20, self.y + 35)
        # set of arrow points should be the vectors from the pivot to the edge points of the arrow
        arrow = [(0, -15), (10, -5), (5, -5), (5, 15), (-5, 15), (-5, -5), (-10, -5)]
        # get arrow by adding all the vectors to the pivot point => allows for easy rotation
        self.arrows = []
        for i in range(6):
            self.arrows.append([(pygame.math.Vector2(x, y)).rotate(60.0*i) + pivot for x, y in arrow]) 
    
        # Coordinates used to draw smaller hexagon later if the hex becomes stationary
        self.small_hexagon = [(self.x+9, self.y+11), (self.x+31, self.y+11), (self.x+47, self.y+35), (self.x+31, self.y+59), (self.x+9, self.y+59), (self.x-7, self.y+35)]
    ##########################################################################################################

    # Returns a boolean indicating if the given hex contains any moving idents
    def is_moving(self):

        for ident in self.idents:
            if ident.state >= 0:
            # if (ident.state != -1) and (ident.state != -2):
                return True
        
        return False
    
    ##########################################################################################################

    # If the given hex contains any portal idents, returns the first one found
    # Otherwise returns None
    def contains_portal(self):
        for ident in self.idents:
            if ident.is_portal():
                return ident
            
        return None
    
    ##########################################################################################################

    # Gives the designated hex a wall identity
    # TODO: Could also clear other idents?
    def make_wall(self, world, list_to_append):
        wall_ident = Ident(self.matrix_index, self.list_index, world, color = (0,0,0), state = -2)
        self.idents.append(wall_ident)
        list_to_append.append(wall_ident)

    ##########################################################################################################

    # Checks if a hex contains an ident heading in the given directon
    # If it does, returns that ident
    # Else returns None
    def contains_direction(self, dir: int):

        # TODO: What if the hex contains multiple idents with that state?
        for ident in self.idents:
            if ident.state == dir:
                return ident

        return None

    ##########################################################################################################

    # Graphics (drawing hexes and the corresponding idents)
    def draw(self, screen):
            
        color_to_draw = Hex.DEFAULT_COLOR


        if (len(self.idents) >= 1):
            # If a hex contains only one ident, take that color
            # If a hex contains multiple idents, the ident stored first will be the outermost color
            color_to_draw = self.idents[0].color
        
        # Draw the hexagon
        pygame.draw.polygon(screen, color_to_draw, self.coordinates)

        # Draw an extra hexagon to visually show that a hexagon is stationary even with the different colors
        if self.contains_direction(-1) != None:
            new_color = [max(0, c - 120) for c in color_to_draw]
            pygame.draw.polygon(screen, new_color, self.small_hexagon)
        
    
        # Draw multiple nesting circles indicating colors for hexes with superimposed idents/states
        for i in range(1, len(self.idents)):
            if (33 - 5*i) > 0:
                pygame.draw.circle(screen, self.idents[i].color, (self.x+20, self.y+35), 33-5*i)
    
        # Draw an arrow on the hex if the hex is moving
        if self.is_moving():
            for i in range(6):
                if self.contains_direction(i):
                    pygame.draw.polygon(screen, (0, 0, 0), self.arrows[i])

    ##########################################################################################################


# for setting initial state of the world / having a student interact
# while loop for running game goes in World
class World:

    @staticmethod
    # Initializes a matrix of hexes of the given dimensions
    def __init_matrix(dimension_1, dimension_2):
        matrix = []

        for x in range(dimension_1):
            hex_list = []
            matrix.append(hex_list)

            for y in range(dimension_2):
                myHex = Hex(x, y)
                hex_list.append(myHex)
        
        return matrix

    def __init__(self, automatic_walls=True):
        pygame.init()

        SCREEN_WIDTH = 800

        SCREEN_HEIGHT = 600

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hex Simulator")

        # Set up hex matrix
        self.hex_matrix = World.__init_matrix(15, 16)
        
        # Set up new hex matrix
        self.hex_matrix_new = World.__init_matrix(len(self.hex_matrix), len(self.hex_matrix[0]))

        # Set up ident list
        self.ident_list = []

        # Set up new ident list
        self.ident_list_new = []

        # Set up wall list
        self.wall_list = []

        # Set up agents list (will be filled in __read_line if agents exist)
        self.agents = []

        # Set up list to track doubled idents
        self.alt_idents_to_remove = []



        # reading the intiial state of the hex board from a file
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file = open(os.path.join(__location__, "initial_state.txt"), "r")
        for line in file:
            self.__read_line(line)

        # reading the decisions of the agent from the provided file
        # NOTE: This would not be part of the final project, but is helpful for demonstration/testing
        if len(self.agents) > 0:
            agent_file = open(os.path.join(__location__, "agent_choices.txt"), "r")
            
            # Initialize arrays with information about agents
            # agent_indices stores the index in the row of influences which is currently effecting the agent
            self.agent_indices = []
            # agent_choices stores the row of potential influences in list form for easy access
            self.agent_choices = []
            for agent in self.agents:
                self.agent_indices.append(0)

                empty_list = []
                self.agent_choices.append(empty_list)
            
            row_counter = 0
            for agent_line in agent_file:

                # Sanity checker that we haven't provided more instructions than we have agents for
                if row_counter >= len(self.agents):
                    break

                self.__read_agent_line(row_counter, agent_line)
                row_counter += 1

        
        # Create walls around the edges, if requested
        if automatic_walls:
            # Left edge
            for hex in self.hex_matrix[0]:
                hex.make_wall(self, self.wall_list)
            # Right edge
            for hex in self.hex_matrix[13]:
                hex.make_wall(self, self.wall_list)
            for i in range(6):
                # Top edge
                self.hex_matrix[1+2*i][6-i].make_wall(self, self.wall_list)
                self.hex_matrix[2+2*i][6-i].make_wall(self, self.wall_list)

                # Bottom edge
                self.hex_matrix[1+2*i][15-i].make_wall(self, self.wall_list)
                self.hex_matrix[2+2*i][14-i].make_wall(self, self.wall_list)

    ##########################################################################################################
    
    # Swaps one agent in for another in the agents list
    def swap_agents(self, agent_to_remove, agent_to_append):
        self.agents.remove(agent_to_remove)
        self.agents.append(agent_to_append)
    
    ##########################################################################################################
    @classmethod
    def __get_color(self, color_text):
        if color_text == "YELLOW" or color_text == "YELLOW\n":
            return (255, 255, 102)
        elif color_text == "PURPLE" or color_text == "PURPLE\n":
            return (204, 0, 255)
        elif color_text == "ORANGE" or color_text == "ORANGE\n":
            return (255, 102, 0)
        elif color_text == "GREEN" or color_text == "GREEN\n":
            return (106, 232, 100)
        elif color_text == "BLUE" or color_text == "BLUE\n":
            return (45, 70, 181)
        elif color_text == "CYAN" or color_text == "CYAN\n":
            return (71, 230, 216) 
        elif color_text == "RED" or color_text == "RED\n":
            return (219, 24, 24)
        elif color_text == "MAROON" or color_text == "MAROON\n":
            return (143, 6, 15)
        elif color_text == "PINK" or color_text == "PINK\n":
            return (230, 57, 129)
        elif color_text == "BROWN" or color_text == "BROWN\n":
            return (166, 129, 85)
        else:
            return (100, 100, 100)

    ##########################################################################################################

    def __read_line(self, line):
        # actual parsing of the text file
        line_parts = line.split(" ")
        
        matrix_index = int(line_parts[0])
        list_index = int(line_parts[1])
        command = line_parts[2]

        if command == "move":
            direction = int(line_parts[4])
            color_text = line_parts[3]
            color = World.__get_color(color_text)
            new_ident = Ident(matrix_index, list_index, self, color = color, state = direction)
            
            # Add ident to ident list
            self.ident_list.append(new_ident)
            
            # Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
        elif command == "occupied":
            color_text = line_parts[3]
            color = World.__get_color(color_text)
            new_ident = Ident(matrix_index, list_index, self, color = color)
            
            # Add ident to ident list
            self.ident_list.append(new_ident)
            
            # Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
        elif command == "wall" or command == "wall\n":
            new_ident = Ident(matrix_index, list_index, self, color = (0,0,0), state = -2)
            
            # Add wall ident to wall list instead of ident list
            self.wall_list.append(new_ident)     
               
            # Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
        elif command == "portal" or command == "portal\n":
            # TODO: Replace string property tag with int (easier to compair)
            new_ident_1 = Ident(matrix_index, list_index, self, color = (75, 4, 122), state = -1, property = "portal")
             
            pair_matrix_index = int(line_parts[3])
            pair_list_index = int(line_parts[4])
               
            new_ident_2 = Ident(pair_matrix_index, pair_list_index, self, color = (75, 4, 122), state = -1, property = "portal", partner_serial_number = new_ident_1.serial_number)
            new_ident_1.partner_serial_number = new_ident_2.serial_number

            # Add idents to hexes and lists
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident_1)
            self.ident_list.append(new_ident_1)

            self.hex_matrix[pair_matrix_index][pair_list_index].idents.append(new_ident_2)
            self.ident_list.append(new_ident_2)

        elif command == "agent" or command == "agent\n":
            
            color_text = line_parts[3]
            color = World.__get_color(color_text)

            new_agent = Ident(matrix_index, list_index, self, color = color)

            # The defauly agent initializes to stationary, but it can initialize with a direction
            # NOTE: A stationary agent will not begin to move unitl hit
            if len(line_parts) > 4:
                new_agent.state =  int(line_parts[4])


            # Add ident to ident list
            self.ident_list.append(new_agent)
            
            # Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_agent)

            # Store ident as agent
            self.agents.append(new_agent)
        
        # Print error message
        else:
            print("Command " + command + " invalid.")
    ##########################################################################################################

    # Parses agent choices text file
    def __read_agent_line(self, agent_num, line):
        # breakpoint()
        print("Reading agent line " + str(agent_num))

        line_parts = line.split(" ")
        
        for direction in line_parts:
            self.agent_choices[agent_num].append(int(direction))

    ##########################################################################################################
    

    # Draws world
    def __draw(self):
        # Reset screen
        self.screen.fill((0, 0, 0))

        # Draw all hexes with idents
        for hex_list in self.hex_matrix:
            for hex in hex_list:
                hex.draw(self.screen)

    ##########################################################################################################

    # Moves other idents stored in the same hex as this portal ident to its paired location
    def __handle_portals(self):

    # Set up temp storage for idents to be moved
        # TODO: There must be a better way to initialize this
        updated_portal_idents = []
        
        # TODO: Use portal list instead of ident list?
        for i in range(len(self.ident_list)):
            sub_list = []
            updated_portal_idents.append(sub_list)


        # Fill temp storage
        for i in range(len(self.ident_list)):
            # If not a portal, do nothing
            if not self.ident_list[i].is_portal():
                continue

            portal = self.ident_list[i]

            origin_hex = self.hex_matrix[portal.matrix_index][portal.list_index]
            assert(origin_hex)

            sub_list_temp = updated_portal_idents[i]

            # Pass all non-portal idents in the hex to temp storage
            for ident in origin_hex.idents:
                if not ident.is_portal():
                    sub_list_temp.append(ident)

        # Clear out existing idents
        for i in range(len(self.ident_list)):
            if not self.ident_list[i].is_portal():
                continue

            portal = self.ident_list[i]

            origin_hex = self.hex_matrix[portal.matrix_index][portal.list_index]
            assert(origin_hex)

            # Remove all non-portal idents from the origin hex
            origin_hex.idents.clear()

            # Sanity checking
            assert(len(origin_hex.idents) == 0)

            # Re-assign portal identity
            origin_hex.idents.append(portal)

            # Throw error if the origin_hex still contains any non-portal identities (debugging)
            assert(len(origin_hex.idents) == 1)
            assert(origin_hex.idents[0].is_portal())

        '''# Checking length of idents lists
        for coords in portal_list:
            hex_to_check = hex_matrix_new[coords[0]][coords[1]]
            assert(len(hex_matrix_new[coords[0]][coords[1]].idents)==1)
            assert(len(hex_to_check.idents)==1)'''

        # Move idents from temp storage into destination hexes
        for i in range(len(self.ident_list)):
            if not self.ident_list[i].is_portal():
                continue            

            portal = self.ident_list[i]

            # Find the destination portal ident
            portal_partner = None
            #TODO: More efficient way to access portal partner
            for ident in self.ident_list:
                if ident.serial_number == portal.partner_serial_number:
                    portal_partner = ident
                    break

            assert (portal_partner)

            # TODO: Will have to change this depending on how portals are copied
            destination_hex = self.hex_matrix[portal_partner.matrix_index][portal_partner.list_index]

            # Pass idents from temp storage to destination hex
            
            for ident in updated_portal_idents[i]:
                ident.matrix_index = destination_hex.matrix_index
                ident.list_index = destination_hex.list_index
                destination_hex.idents.append(ident)


    ##########################################################################################################

    def __update(self):
        
        # Clear out list that helps remove redundant stationary identities
        self.alt_idents_to_remove.clear()

        # Agents act
        for agent in self.agents:
            agent.get_next_move()

        # Push history of idents and walls
        for ident in self.ident_list:
            ident.visited(ident.matrix_index, ident.list_index)
        
        for wall in self.wall_list:
            wall.visited(wall.matrix_index, wall.list_index)


        # Clear the new matrix and list so that advance_or_flip can write to it
        for hex_list in self.hex_matrix_new:
            for hex in hex_list:
                # Save wall_ident to add back in, if applicable
                wall_ident = hex.contains_direction(-2)
                
                hex.idents.clear()
                
                if wall_ident:
                    self.hex_matrix_new[wall_ident.matrix_index][wall_ident.list_index].idents.append(wall_ident)
        
        self.ident_list_new.clear()

        # Move or flip all idents (except for walls)
        for ident in self.ident_list:
            ident.advance_or_flip()

        # Clear the current hex matrix and ident list list so that resolve_collisions can write to it
        for hex_list in self.hex_matrix:
            for hex in hex_list:
                # Save wall_ident to add back in, if applicable
                wall_ident = hex.contains_direction(-2)
                
                hex.idents.clear()
                
                if wall_ident:
                    self.hex_matrix[wall_ident.matrix_index][wall_ident.list_index].idents.append(wall_ident)
        
        self.ident_list.clear()
                
        # Fix collisions in all idents (except for walls)
        for ident in self.ident_list_new:
            ident.resolve_collisions()

        # TODO: Fix something with self.alt_idents_to_remove
        # Remove redunant stationary idents (stored in alt_idents_to_remove)\
        for ident in self.alt_idents_to_remove:
            ident.remove_from_list(self.ident_list)
            ident.remove_from_list(self.hex_matrix[ident.matrix_index][ident.list_index].idents)

        # TODO: Could move the clearing of self.alt_idents_to_remove to here

        # Move idents between portals
        # TODO: Maintain separate portal list?
        self.__handle_portals()

    ##########################################################################################################

    def __backstep(self):
        # Reverts every hex to how it was one state back.
        # Each ident holds its own history of the past 5 steps at any given time.
        # Because the code is deterministic, the next step will be re-calculated the same way.
        
        # Only take any steps if there is history left to be shown
        # TODO: This is a pretty janky way to check if there is space to step back
        if (len(self.ident_list) > 0) and (len(self.ident_list[0].hist) > 0):
        
            # First, clear the matrix and list
            for hex_list in self.hex_matrix:
                for hex in hex_list:

                    # Walls are managed separately to other idents, so re-draw them from their own list
                    wall_ident = hex.contains_direction(-2)

                    hex.idents.clear()

                    if wall_ident:
                        self.hex_matrix[wall_ident.matrix_index][wall_ident.list_index].idents.append(wall_ident)

            # Then, apply step back on all idents
            # After applying the step back, return those idents to the list in their respective hexes
            for ident in self.ident_list:
                ident.backstep()

                self.hex_matrix[ident.matrix_index][ident.list_index].idents.append(ident)
            
            for wall in self.wall_list:
                # wall.backstep()
                self.hex_matrix[wall.matrix_index][wall.list_index].idents.append(wall)

                ident.world.hex_matrix[ident.matrix_index][ident.list_index].idents.append(ident)
        
        # If there are no previous states to step back to, print an error message
        else:
            print("Maximum steps back have been taken.")


    ##########################################################################################################

    def run(self):
        run = True

        state = "pause"
        clock = pygame.time.Clock()
        dt = 0

        while run:

            # Event handler (closing window)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                # the following takes in and reacts to keyboard input
                if event.type == pygame.TEXTINPUT:

                    # takes the key input
                    keys = pygame.key.get_pressed()

                    # changes state based on keyboard input
                        # g = "go" ; runs at normal speed
                        # p = "pause" ; stops
                        # h = "hyper" ; goes really fast
                    if keys[pygame.K_g]:
                        state = "go"
                    elif keys[pygame.K_p]:
                        state = "pause"
                    elif keys[pygame.K_h]:
                        state = "hyper"

                    # when in pause, you can step forward or back
                    if state == "pause" and keys[pygame.K_s]:
                        self.__update()

                        pygame.time.delay(100)
                        # Take one second pause

                    if state == "pause" and keys[pygame.K_b]:
                        self.__backstep()

                        pygame.time.delay(100)
                        # Take one second pause
            
            self.__draw()

            # flips to the next frame
            pygame.display.flip()

            if state == "go":
                print("--------------------on go--------------------")
                dt = clock.tick(2) / 1000
                self.__update()
            elif state == "hyper":
                dt = clock.tick(20) / 1000
                self.__update()
        
        # Exit
        pygame.quit()
