import time
import copy
import os

###############################################################################################################
###############################################################################################################

class Hex:

    # Create Coordinate
   @staticmethod
   def create_coor(x, y):
        # Making hex smaller so that borders will be visible
        return [(x+3, y+3), (x+37, y+3), (x+57, y+35), (x+37, y+67), (x+3, y+67), (x-17, y+35)]

    ##########################################################################################################

    # Constructor
    # color is an optional parameter with a default value of red
    # movable is an optional parameter with a default value of true
   def __init__(self, matrix_index, list_index, color=(255, 0, 0), movable=True, occupied=False):
       self.matrix_index = matrix_index
       self.list_index = list_index

       self.x = 60*matrix_index - 20
       self.y = 35*matrix_index + 70*list_index - 490

       self.coordinates = Hex.create_coor(self.x, self.y)
       
       # Store identities of hexes
       self.idents = []
       if occupied:
           self.idents.append(Ident(color))

       if not movable:
           self.make_wall()

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

    # sets the given hex to act as a wall
   def make_wall(self):
       # Wipe idents currently stored
       self.idents.clear()
       # Walls are black
       # -2 state is a wall
       self.idents.append(Ident((0,0,0), -2))

    ##########################################################################################################

    ##########################################################################################################

    # sets the given hex to act as a portal
    # TODO: How to set destiantion?
   def make_portal(self, pmi, pli, color=(75, 4, 122)):
       # Portals are dark purple
       # TODO: What state to pass?
       # TODO: Rename variables
       # TODO: Ideally, portals should be linked just to idents, not to hex locations (so they can move)
       self.idents.append(Ident(color, property="portal", pair_matrix_index=pmi, pair_list_index=pli))

    ##########################################################################################################

    ##########################################################################################################

    # sets the given hex to move in a given direction
   def make_move(self, dir, color=(255,0,0)):
       #   # we want to make the creation of a space redundent fot the limit tic
       #   # this is for backtracing later
        global limit_tic
        limit_tic = limit_tic - 1

       # storing this into am object makes it easier to mark
        ident = Ident(color, dir)

       #   # just like when taking, we want to store the first instance of an ident
       #   # don't actually need the check for wall, but for fail-safe
        if ident.state != -2:
            ident.visited(self.list_index, self.matrix_index)

       # Note: Does not overwrite idents currently stored
        self.idents.append(ident)

    # Appends the passed ident to the given hex
   def take_ident(self, ident):

       if ident.state != -2:
            print("hex at " + str(self.matrix_index) + ", " + str(self.list_index) + " taking ident " + str(ident.serial_number))
       self.idents.append(ident)

   def make_occupied(self, color=(0, 255, 0)):
       # TODO: Clear out current idents? (does not currently overwrite pre-existing idents)

       #   # we want to make the creation of a space redundent fot the limit tic
       #   # this is for backtracing later
        global limit_tic
        limit_tic = limit_tic - 1

       #   # same reasoning as in make move
        ident = Ident(color, -1)

       #   # just like when taking, we want to store the first instance of an ident
       #   # don't actually need the check for wall, but for fail-safe
        if ident.state != -2:
            ident.visited(self.list_index, self.matrix_index)

       # TODO: Clear out current idents? (does not currently overwrite pre-existing idents)
        self.idents.append(ident)

   # returns a boolean indicating if a hex is occupied 
   # TODO: Maybe have this return false for portals?
   def is_occupied(self):
       return len(self.idents != 0)

    ##########################################################################################################

    # graphics
   def draw(self, screen):
    
    # Default color (no idents): light blue
    my_color = (190, 240, 255)

    if (len(self.idents) >= 1):
        # If a hex contains only one ident, take that color
        # If a hex contains multiple idents, the ident stored first will be the outermost color
        my_color = self.idents[0].color
        
    # Draw the hexagon
    pygame.draw.polygon(screen, my_color, self.coordinates)

    # Draw an extra hexagon to visually show that a hexagon is stationary even with the different colors
    if self.contains_direction(-1) != None:
        new_color = [max(0, c - 120) for c in my_color]
        pygame.draw.polygon(screen, new_color, self.small_hexagon)
    
    # Draw multiple nesting circles indicating colors for hexes with superimposed idents/states
    for i in range(1, len(self.idents)):
        if (33 - 5*i) > 0:
            pygame.draw.circle(screen, self.idents[i].color, (self.x+20, self.y+35), 33-5*i)
    
    # Draw text object displaying axial hex coordiantes
    # self.display_surface.blit(self.text, self.textRect)

    # polygon rotation tips from: https://stackoverflow.com/questions/75116101/how-to-make-rotate-polygon-on-key-in-pygame

    # draw an arrow on the hex if the hex is moving
    # TODO: Make smaller arrows for superimposed states? (to not hide nested colors)
    if self.is_moving:
        #pivot is the center of the hexagon
        pivot = pygame.Vector2(self.x + 20, self.y + 35)
        # set of arrow points should be the vectors from the pivot to the edge points of the arrow
        arrow = [(0, -15), (10, -5), (5, -5), (5, 15), (-5, 15), (-5, -5), (-10, -5)]
        # get arrow by adding all the vectors to the pivot point => allows for easy rotation
        for i in range(6):
            if self.contains_direction(i):
                pygame.draw.polygon(screen, (0, 0, 0), self.arrows[i])

    # returns a boolean indicating if the given hex is occupied, movable, and stationary (not currently moving)
   def check_movable_hex(self):
       #return (not self.is_moving) and self.movable and self.occupied
       for ident in self.idents:
           if ident.state == -1:
               return True
       # If none of the idents contain state -1, the hex is not movable
       return False

    # returns a boolean indicating if the hex is currently moving
   def is_moving(self):
        return self.contains_direction(0) or self.contains_direction(1) or self.contains_direction(2) or self.contains_direction(3) or self.contains_direction(4) or self.contains_direction(5)
   
   # returns a list of length six representing the six neighboring hexes of self, with 1 if the hex neighboring in that direction is movable, nonmoving, and occupied
   def check_movables(self, neighbors): 
        hex_movable = []

        # Check if each neighboring hex is movable
        for hex in neighbors:
            if hex != None:
                hex_movable.append(hex.check_movable_hex())
            else:
                hex_movable.append(False)

        return hex_movable

    ##########################################################################################################

# Checks if a hex contains an ident heading in the given directon
   # If it does, returns that ident
   # Else returns None
   def contains_direction(self, dir):

       for ident in self.idents:
           if ident.state == dir:
               return ident

       return None 
   
   # Returns true if the given hex contains a wall ident, else returns false
   def contains_wall(self):
       for ident in self.idents:
           if ident.state == -2:
                assert (len(self.idents) == 1)

                return ident
           
       return None    

    ##########################################################################################################

    # Checks if a hex contains a portal ident
    # If it does, returns that ident
    # Else returns None
   def contains_portal(self):
       for ident in self.idents:
           # TODO: Use int insteal of string for faster processing
           if ident.property == "portal":
                # For debugging
                if len(self.idents) > 1:
                    print("Portal contains multiple idents")

                return ident

       return None    

    ##########################################################################################################

   # returns a list of length 6 to determine which of the neighbors around self hex are walls
   def check_walls(self, neighbors):
        hex_walls = []

        # Check if each neighboring hex is a wall
        for hex in neighbors:
            if hex != None:
                hex_walls.append(bool(hex.contains_wall()))
            else:
                hex_walls.append(False)

        return hex_walls
   
   def get_neighbors(self):
        my_neighbors = [None, None, None, None, None, None]

        try:
            my_neighbors[0] = hex_matrix[self.matrix_index][self.list_index - 1]
        except:
            #print("Neighbor 0 does not exist")
            pass

        try:
            my_neighbors[1] = hex_matrix[self.matrix_index + 1][self.list_index - 1]    
        except:
            #print("Neighbor 1 does not exist")
            pass

        try:
            my_neighbors[2] = hex_matrix[self.matrix_index + 1][self.list_index]
        except:
            #print("Neighbor 2 does not exist")
            pass

        try:
            my_neighbors[3] = hex_matrix[self.matrix_index][self.list_index + 1]
        except:
            #print("Neighbor 3 does not exist")
            pass

        try:
            my_neighbors[4] = hex_matrix[self.matrix_index - 1][self.list_index + 1]
        except:
            #print("Neighbor 4 does not exist")
            pass
        
        try:
            my_neighbors[5] = hex_matrix[self.matrix_index - 1][self.list_index]
        except:
            #print("Neighbor 5 does not exist")
            pass
        
        return my_neighbors

   # Takes an array of neighboring hexes
   # Returns an array of idents pointing at self
   def get_neighbors_pointing_at_me(self, neighbors):
       idents_pointing_at_me = []

       for i in range(len(neighbors)):
           neighbor_ident = None
           
           # Avoid trying to call contains_direction on a None object
           if neighbors[i]:
               neighbor_ident = neighbors[i].contains_direction((i+3)%6)
            
           if neighbor_ident:
               # TODO: What if the neighbor contains multiple idents pointing at me?
               idents_pointing_at_me.append(neighbor_ident)
           else:
               idents_pointing_at_me.append(None)

       return idents_pointing_at_me         

   # removes influence of this hex from neighbors
   def cleanse_neighbor(self, direction):
        if (direction == 0):
            neighbor = hex_matrix_new[self.matrix_index][self.list_index - 1]
            if neighbor.contains_direction(0) is not None:
                neighbor.idents.remove(neighbor.contains_direction(0))
        elif (direction == 1):
            neighbor = hex_matrix_new[self.matrix_index + 1][self.list_index - 1]
            if neighbor.contains_direction(1) is not None:
                neighbor.idents.remove(neighbor.contains_direction(1))
        elif (direction == 2):
            neighbor = hex_matrix_new[self.matrix_index + 1][self.list_index]
            if neighbor.contains_direction(2) is not None:
                neighbor.idents.remove(neighbor.contains_direction(2))
        elif (direction == 3):
            neighbor = hex_matrix_new[self.matrix_index][self.list_index + 1]
            if neighbor.contains_direction(3) is not None:
                neighbor.idents.remove(neighbor.contains_direction(3))
        elif (direction == 4):
            neighbor = hex_matrix_new[self.matrix_index - 1][self.list_index + 1]
            if neighbor.contains_direction(4) is not None:
                neighbor.idents.remove(neighbor.contains_direction(4))
        elif (direction == 5):
            neighbor = hex_matrix_new[self.matrix_index - 1][self.list_index]
            if neighbor.contains_direction(5) is not None:
                neighbor.idents.remove(neighbor.contains_direction(5))

    # calls movement handler on all the neighboring hexes of self in case we need to re-check them after changing the idents that are in self
   def influence_neighbor(self, future, my_neighbors, neighbors_movable, neighbors_wall):
       for i in self.idents:
            if(i.state >= 0) and (i.state <= 5):
                if (i.state == 0):
                    neighbor = hex_matrix_new[self.matrix_index][self.list_index - 1]
                elif (i.state == 1):
                    neighbor = hex_matrix_new[self.matrix_index + 1][self.list_index - 1]
                elif (i.state == 2):
                    neighbor = hex_matrix_new[self.matrix_index + 1][self.list_index]
                elif (i.state == 3):
                    neighbor = hex_matrix_new[self.matrix_index][self.list_index + 1]
                elif (i.state == 4):
                    neighbor = hex_matrix_new[self.matrix_index - 1][self.list_index + 1]
                elif (i.state == 5):
                    neighbor = hex_matrix_new[self.matrix_index - 1][self.list_index]
            # check if neighbor already has an ident with the same serial number as i
            check = next((Ident for Ident in neighbor.idents if Ident.serial_number == i.serial_number), None)
            # if not, put the effects of i's movement on neighbor with movement_handler
            if check is None:
                toMove = hex_matrix[neighbor.matrix_index][neighbor.list_index]
                # get my neighboors, and my movable neighbors, and my wall neighbors
                toMove.motion_handler(neighbor, toMove.get_neighbors(), toMove.check_movables(), toMove.check_walls(), (i.state - 3) % 6)



    ##########################################################################################################

    # handles the impacts of hitting an occupied neighbor (either a stationary object or a wall)
   def hit_neighbor(self, future, my_neighbors, neighbors_movable, neighbors_wall, dir):
        # cases for individual side glancing walls
        if (neighbors_wall[(dir-1)%6] == 1) and not (neighbors_wall[(dir+1)%6] == 1):
            print("hit neighbor case 1, dir = " + str(dir))
            print("self color " + str(self.contains_direction(dir).color))
            print("self location (" + str(self.matrix_index) + ", " + str(self.list_index) + ")")
            ident_to_rotate = self.contains_direction(dir).copy()
            ident_to_rotate.state = (dir+1)%6
            future.take_ident(ident_to_rotate)
        elif (neighbors_wall[(dir+1)%6] == 1) and not (neighbors_wall[(dir-1)%6] == 1):
            print("hit neighbor case 2, dir = " + str(dir))
            ident_to_rotate = self.contains_direction(dir).copy()
            ident_to_rotate.state = (dir-1)%6
            future.take_ident(ident_to_rotate)

        # if my neighbor is a wall (or if I have two neighors to the side in front), bounce off
        elif (neighbors_wall[dir] == 1) or ((neighbors_wall[(dir-1)%6] == 1) and (neighbors_wall[(dir+1)%6] == 1)):
            print("hit neighbor case 3, dir = " + str(dir))
            ident_to_rotate = self.contains_direction(dir).copy()
            ident_to_rotate.state = (dir+3)%6
            future.take_ident(ident_to_rotate)
            
        
        # if I am moving toward my neighbor, and my neighbor is occupied but not moving, then I become occupied but not moving
        # TODO: Discuss order in which rules are applied
        # TODO: Also discuss if collisions off of a side wall should take priority over head-on collisions
        # TODO: Also explain and de-jankify portal patch
        elif neighbors_movable[dir] == 1:

            if my_neighbors[dir].contains_portal():
                print("hit portal neighbor")
            else:
                print("hit neighbor case 4, dir = " + str(dir))
                # If I am hitting a stationary neighbor, I become stationary but maintain my identity
                ident_to_stop = self.contains_direction(dir).copy()
                ident_to_stop.state = -1
                if(future.contains_direction(-1) is None):
                    future.take_ident(ident_to_stop)
                    print("Took ident " + str(ident_to_stop.color) + " " + str(ident_to_stop.state))

   # Handles case with six neighbors pointing at self
   def six_neighbors_case(self, pointing_neighbors):
       future = hex_matrix_new[self.matrix_index][self.list_index]

       for neighbor_ident in pointing_neighbors:
           # All idents are turned around 180 degrees
           ident_to_flip = neighbor_ident.copy()
           ident_to_flip.state = (ident_to_flip.state + 3)%6
           future.take_ident(ident_to_flip)
           

    ##########################################################################################################

   # Handles interactions between a hex and its environment with respect to the given direction
   def motion_handler(self, future, my_neighbors, neighbors_movable, neighbors_wall, dir):
        # straight_neighbor is the neighbor in that direction (ex. when dir = 0, straight_neighbor is the upper neighbor of self)
       straight_neighbor = my_neighbors[dir]


        # if I am in a collision state (with multiple idents) and the neighbors in the direction I came from are stationary, move me up
        # HOWEVER if I am in a collision state that resulted from people hitting me stationary from opposite sides, I act as a wall
       if (len(self.idents) > 1):
            stationary_left_behind = [] # list of booleans for each ident if there is a neighbor in its opposite direction 
            for i in self.idents:
                direction = i.state
                if(direction >= 0):
                    stationary_left_behind.append(neighbors_movable[(int(direction) + 3) % 6])
            # checks if all elements that current states are pointing away from are in fact movable
            # if so, special case!!!

            # resolving cases of two hexes colliding into one stationary hex
            if "True, False, False, True" in str(neighbors_movable) and len(stationary_left_behind) == 2:
                # if this is true, the collision was from opposing sides (180 degrees)
                # then, the center immovable object acts as a wall
                future_to_store = []
                for i in self.idents:
                    if(i.state >= 0):
                        i.state = (i.state + 3) % 6
                        future_to_store.append(i)
                # passing stationary hex of the correct color to the future
                forward = self.contains_direction(-1).color
                self.idents.clear()
                future.idents.clear()
                to_take = Ident(forward, -1)
                self.take_ident(to_take)
                future.take_ident(to_take)
                for i in future_to_store:
                    self.take_ident(i)


            elif ("True, True" in str(neighbors_movable) or str(neighbors_movable) == "[True, False, False, False, False, True]") and len(stationary_left_behind) == 2:
                # if this is true, the collision had its two incoming hexes at a 60 degree angle from each other
                if(all(flag == 1 for flag in stationary_left_behind)):
                    # for 60 degree case, the stationary object moves in the direction that the more counterclockwise hex shows
                    future_direction = 0
                    if str(neighbors_movable) == "[True, False, False, False, False, True]":
                        future_direction = 2
                    else:
                        # find first "True"
                        future_direction = (min([i for i, val in enumerate(neighbors_movable) if val]) - 3) % 6
                        # minimum true value => clockwise movable neighbor
                    forward = Ident((self.contains_direction(-1).color), future_direction)
                    for i in self.idents:
                        if(i.state >= 0) and (i.state <= 5):
                            # if an ident in this one is greater than zero, check to ensure the hexes it would act onto do not contain influence from it
                            self.cleanse_neighbor(i.state)
                    self.idents.clear()
                    self.take_ident(forward)
                    # function here to make sure the effects of the newly moved ident are put in the code
                    self.influence_neighbor(future, my_neighbors, neighbors_movable, neighbors_wall)

            elif len(stationary_left_behind) == 2:
                # this picks the direction correctly for 120 degreee collisions, but perhaps this should be done upon the initial collision???
                if(all(flag == 1 for flag in stationary_left_behind)):
                    future_direction = []
                    for i in self.idents:
                        # perhaps only append if we have a neighbor in that direction 
                        if(neighbors_movable[int(i.state) - 3 % 6] == 1):
                            future_direction.append((i.state - 3) % 6)
                    # different cases for future_direction_real
                    # both of these are just for 120 degree differences 
                    if(max(future_direction) - min(future_direction) == 2):
                        future_direction_real = ((min(future_direction) - 2) % 6)
                    elif(max(future_direction) - min(future_direction) == 4):
                        future_direction_real = ((max(future_direction) - 2) % 6)
                    forward = Ident((self.contains_direction(-1).color), future_direction_real)
                    for i in self.idents:
                        if(i.state >= 0) and (i.state <= 5):
                            # if an ident in this one is greater than zero, check to ensure the hexes it would act onto do not contain influence from it
                            self.cleanse_neighbor(i.state)
                            # TODO: also have to make sure the required indices exist for checking them in the first place
                    self.idents.clear()
                    # future.idents.clear()
                    self.take_ident(forward)
                    # TODO: effects of this ident so that it doesn't take longer than the other collision cases to move forward?
                    self.influence_neighbor(future, my_neighbors, neighbors_movable, neighbors_wall)
                    # note to self: check how long framewise the other animations take
        # --- END CASES FOR TWO HEXES COLLIDING WITH ONE STATIONARY CASE
        # TODO: possibly generalize the above cases for multiple hexes colliding with a stationary hex?

       if self.contains_direction(-1) is not None:
            ident_to_take = self.contains_direction(-1)

        # if my neighbor is moving toward me and is not blocked by either of two side walls, I will gain motion
       if (not neighbors_wall[(dir+1)%6]) and (not neighbors_wall[(dir-1)%6]):
           neighbor_ident = straight_neighbor.contains_direction((dir+3)%6)
           if neighbor_ident != None:
                # My identity pointing in the given direction, if it exists
                my_ident = self.contains_direction(dir)

                clockwise_neighbor_ident = None
                if my_neighbors[(dir+1)%6] != None:
                    clockwise_neighbor_ident = my_neighbors[(dir+1)%6].contains_direction((dir-2)%6)

                counterclockwise_neighbor_ident = None
                if my_neighbors[(dir-1)%6] != None:
                    counterclockwise_neighbor_ident = my_neighbors[(dir-1)%6].contains_direction((dir+2)%6)
                
                clockwise_step_ident = None
                if my_neighbors[(dir+2)%6] != None:
                    clockwise_step_ident = my_neighbors[(dir+2)%6].contains_direction((dir-1)%6)
                
                counterclockwise_step_ident = None
                if my_neighbors[(dir-2)%6] != None:
                    counterclockwise_step_ident = my_neighbors[(dir-2)%6].contains_direction((dir+1)%6)
                
                # TODO: Is this just neighbor_ident?
                dir_neighbor_ident = None
                if my_neighbors[dir] != None:
                    dir_neighbor_ident = my_neighbors[dir].contains_direction((dir+3)%6)

                opp_neighbor_ident = None
                if my_neighbors[(dir+3)%6] != None:
                    opp_neighbor_ident = my_neighbors[(dir+3)%6].contains_direction(dir)

                if my_ident != None:
                    # If in a head-on collision with a neighbor moving in the opposite direction, maintain identity and switch direction
                    print("case 1")
                    ident_to_flip = my_ident.copy()
                    ident_to_flip.state = (ident_to_flip.state+3)%6
                    future.take_ident(ident_to_flip)
                elif counterclockwise_neighbor_ident != None and clockwise_neighbor_ident != None:
                    # If three arrows are approaching at 60 degree angles and I am in the middle, I go straight
                    # TODO: The prioritization of 3-hex collisions over 2-hex collisions makes it difficult/unclear how to implement 4 hexes
                    print("case 1.5")
                    future.take_ident(neighbor_ident)
    
                elif clockwise_step_ident != None:
                    # Deal with 120-degree collision (version 1)
                    print("case 4, dir " + str(dir))

                    if neighbors_wall[(dir+3)%6] or self.contains_direction((dir+2)%6):
                        # If a wall gets in the way or I contain an arrow that will collide with the incoming arrow, do not bounce
                        print("case 4 alt")
                        future.take_ident(neighbor_ident)
                    else:
                        # Bounce
                        ident_to_flip = clockwise_step_ident.copy()
                        ident_to_flip.state = (ident_to_flip.state-2)%6
                        future.take_ident(ident_to_flip)
                        if self.contains_direction(-1) is not None:
                            future.idents.insert(0, ident_to_take)

                elif counterclockwise_step_ident != None:
                    # Deal with 120-degree collision (version 2)
                    print("case 5, dir " + str(dir))

                    if neighbors_wall[(dir+3)%6] or self.contains_direction((dir-2)%6):
                        # If a wall gets in the way or I contain an arrow that will collide with the incoming arrow, do not bounce
                        print("case 5 alt")
                        future.take_ident(neighbor_ident)
                    else:
                        ident_to_flip = counterclockwise_step_ident.copy()
                        ident_to_flip.state = (ident_to_flip.state+2)%6
                        future.take_ident(ident_to_flip)
                        if self.contains_direction(-1) is not None:
                            future.idents.insert(0, ident_to_take)
                
                # TODO: Find more edge cases of 3+ hexes colliding

                elif clockwise_neighbor_ident != None:
                    # Deal with 60-degree collision (version 1)
                    print("case 2, dir = " + str(dir))
                    # if I have two adjacent neighbors pointing at me
                    # take the ident from the straight_neighbor but flip its state to match that from the other neighbor (adjacent to straight_neighbor)
                    
                    if neighbors_wall[(dir+2)%6] or self.contains_direction((dir+1)%6):
                        # If a wall blocks it or it collides with an arrow in self, take on identity of neighbor
                        print("case 2 alt")
                        future.take_ident(neighbor_ident)
                    elif opp_neighbor_ident != None:
                        # If our direct neighbor will be colliding in a 120 degree collision (and thus not colliding with us), rotate
                        ident_to_rotate = neighbor_ident.copy()
                        ident_to_rotate.state = (ident_to_rotate.state + 2)%6
                        future.take_ident(ident_to_rotate)
                    else:
                        # Bounce
                        ident_to_flip = clockwise_neighbor_ident.copy()
                        ident_to_flip.state = (ident_to_flip.state-1)%6
                        future.take_ident(ident_to_flip)
                        if self.contains_direction(-1) is not None:
                            future.take_ident(ident_to_take)
                elif counterclockwise_neighbor_ident != None:
                    # Deal with 60-degree collision (version 2)
                    print("case 3, dir = " + str(dir))
                    
                    if neighbors_wall[(dir-2)%6] or self.contains_direction((dir-1)%6):
                        # If a wall blocks it of it collides with an arrow in self, take on identity of neighbor
                        print("case 3 alt/")
                        future.take_ident(neighbor_ident)
                    elif opp_neighbor_ident != None:
                        # If our direct neighbor will be colliding in a 120 degree collision (and thus not colliding with us), rotate
                        ident_to_rotate = neighbor_ident.copy()
                        ident_to_rotate.state = (ident_to_rotate.state - 2)%6
                        future.take_ident(ident_to_rotate)
                    else:
                        # Bounce
                        ident_to_flip = counterclockwise_neighbor_ident.copy()
                        print("I am hex (" + str(self.matrix_index) + ", " + str(self.list_index) + ")")
                        print("flipping ident with color " + str(ident_to_flip.color) + ", original direction " + str(ident_to_flip.state))
                        ident_to_flip.state = (ident_to_flip.state+1)%6
                        future.take_ident(ident_to_flip)
                        if self.contains_direction(-1) is not None:
                            future.take_ident(ident_to_take)

                elif dir_neighbor_ident and opp_neighbor_ident:
                    # Handle head-on collision with an empty hex in the middle
                    print("case 6")
                    ident_to_flip = dir_neighbor_ident.copy()
                    ident_to_flip.state = (ident_to_flip.state + 3)%6
                    future.take_ident(ident_to_flip)
                    if self.contains_direction(-1) and (future.contains_direction(-1) == None):
                        future.take_ident(self.contains_direction(-1).copy())
                elif self.check_movable_hex() and not self.contains_portal():
                    print("case 7")
                    # If I am currently stationary and none of the previous statements have been triggered, I will be bumped
                    # TODO: Check that the descriptive comment is accurate
                    # TODO: What is there's superimposition on a portal?
                    
                    ident_to_edit = self.contains_direction(-1).copy()
                    ident_to_edit.state = (dir+3)%6
                    future.take_ident(ident_to_edit)
                else:
                    # Else take on identity of neighbor
                    print("case 8, taking on ident " + str(neighbor_ident.serial_number) + " with state " + str(neighbor_ident.state))
                    future.take_ident(neighbor_ident)
                    if self.contains_direction(-1) and (future.contains_direction(-1) == None):
                        future.take_ident(self.contains_direction(-1).copy())
                        print("Case 8: took on ident of my neighbor, I am " + str(self.matrix_index) + " " + str(self.list_index))
        
        # handle impact of hitting occupied neighbor
       if self.contains_direction(dir): 
           self.hit_neighbor(future, my_neighbors, neighbors_movable, neighbors_wall, dir)

    # returns an array of neighbors (the entry in the array is None when the neighbor does not exist)



    ##########################################################################################################

    ##########################################################################################################

   #update self hexagon
   def update(self):
        # determine the state of the current hex based on the states of the hexes around it
        future = hex_matrix_new[self.matrix_index][self.list_index]
        
        # Clear idents from prev generation
        portal_ident = self.contains_portal()
        future.idents.clear()
        if portal_ident:
            future.take_ident(portal_ident)
      

        # If the hex is a wall, it will remain occupied and not movable
        wall_ident = self.contains_wall()
        if wall_ident:
            future.take_ident(wall_ident)
            return

        my_neighbors = self.get_neighbors()

        my_neighbors_pointing_at_me = self.get_neighbors_pointing_at_me(my_neighbors)
        # Count number of neighbors pointing at me
        num_pointing_neighbors = 0
        for nbr in my_neighbors_pointing_at_me:
            if nbr:
                num_pointing_neighbors += 1 

        neighbors_movable = self.check_movables(my_neighbors)
        neighbors_wall = self.check_walls(my_neighbors)
        
        # TODO: Convert if self.movable: to ident
        # If the hex does not contains a wall
        if not self.contains_wall():
            if num_pointing_neighbors == 6:
                # Case for 6 neighbors pointing at me
                self.six_neighbors_case(my_neighbors_pointing_at_me)


# TODO: Maybe let 4-, 5-, and 6-hex collisions be handled in some other way? (rather than by passing direction)
            else:
               for i in range(6):
                   if my_neighbors[i] != None:
                       self.motion_handler(future, my_neighbors, neighbors_movable, neighbors_wall, i)

        # If the hex is currently occupied and not moving, it will still be occupied in the next generation
        # If that hasn't already been seen to by the motion handler, that must mean that the hex is occupied and stationary in the next generation
        # TODO: It is not necessarily true, however, that it will still be occupied and STATIONARY in the next generation, which is what I'm going here
        # TODO: Explain logic better --> Could this be the cause of the stationary hex being obliterated when hit by two moving hexes?
        # TODO: Does it make sense to make an exception for portals?
        is_stationary = self.contains_direction(-1)

        if (is_stationary and not self.contains_portal()) and (len(future.idents) == 0):
            future.idents.append(is_stationary.copy())

        trouble = next((Ident for Ident in self.idents if Ident.serial_number == 60), None)
        if trouble is not None:
            print("New trouble (60) hex at: ")
            print(str(self.matrix_index) + " " + str(self.list_index))



class Ident:
    # Constructor
    # Default color white
    # Default state -1 (movable but not moving)
    idents_created = 0

    def __init__(self, color=(255, 255, 255), state=-1, serial_number=-1, property=None, hist=None, pair_matrix_index=-1, pair_list_index=-1):
        # history needs to be kept, and is only empty at initial creation
        if hist is None:
            hist = []
        self.color = color

        # States:
        # -2 = wall
        # -1 = stationary but movable
        # 0 through 5 = directions of motion (0 = 12 o'clock)
        self.state = state
        
        self.property = property

        # this lets us be able to update history
        self.hist = hist

        # For portals
        self.pair_matrix_index = pair_matrix_index
        self.pair_list_index=pair_list_index

        # Record serial number and iterate
        if serial_number == -1:
            # If no serial number is provided
            self.serial_number = Ident.idents_created

            print("Ident with serial number " + str(self.serial_number) + " created")
            if state == -2:
                print("Is a wall")
            elif state == -1:
                print("Is stationary")
                if self.property == "portal":
                    print("Is a portal")
            else:
                print("Is moving")
            Ident.idents_created += 1
        else:
            self.serial_number = serial_number
            print("Ident with serial number " + str(self.serial_number) + " copied")
            print("color: " + str(self.color))


    def copy(self):
        # TODO: Review copy method
        new_copy = Ident(self.color, self.state, self.serial_number, self.property, self.hist)
        return new_copy

    def visited(self, x, y):
        # using limit_tic to stop user from going backwards too much
        global limit_tic

        # push onto stack history
        # pushed onto the history is
        # hex matix index (x,y)
        # current state

        # note, we want to keep up to 5 past states at a time
        # to change amount, just change limit #
        limit = 5

        if len(self.hist) == limit + 1:
            self.hist.pop(0)
            self.hist.append((x, y, self.state))
        else:
            self.hist.append((x, y, self.state))
            limit_tic += 1

    def back(self):

        # first we want to clear out our current state
        #self.hist.pop()

        # then we want to pop off the code we are going back to
        # because the code is deterministic, we will go down the same path again, so we can delete the last one
        gohere = self.hist.pop()

        return gohere
    

###############################################################################################################
###############################################################################################################

def get_color(color_text):
    if color_text == "YELLOW" or color_text == "YELLOW\n":
        return (255, 255, 102)
    elif color_text == "PURPLE" or color_text == "PURPLE\n":
        return (204, 0, 255)
    elif color_text == "ORANGE" or color_text == "ORANGE\n":
        return(255, 102, 0)
    elif color_text == "GREEN" or color_text == "GREEN\n":
        return(106, 232, 100)
    elif color_text == "BLUE" or color_text == "BLUE\n":
        return(45, 70, 181)
    elif color_text == "CYAN" or color_text == "CYAN\n":
        return (71, 230, 216) 
    elif color_text == "RED" or color_text == "RED\n":
        return(219, 24, 24)
    elif color_text == "MAROON" or color_text == "MAROON\n":
        return (143, 6, 15)
    elif color_text == "PINK" or color_text == "PINK\n":
        return(230, 57, 129)
    else:
        return (100, 100, 100)

def read_line(line):

    # actual parsing of the text file
    line_parts = line.split(" ")
    
    matrix_index = int(line_parts[0])
    list_index = int(line_parts[1])
    command = line_parts[2]

    if command == "move":
        direction = int(line_parts[4])
        color_text = line_parts[3]
        color = get_color(color_text)
        hex_matrix[matrix_index][list_index].make_move(direction, color)
    elif command == "occupied":
        color_text = line_parts[3]
        color = get_color(color_text)
        hex_matrix[matrix_index][list_index].make_occupied(color)
    elif command == "wall" or command == "wall\n":
        hex_matrix[matrix_index][list_index].make_wall()
    elif command == "portal" or command == "portal\n":  
        # TODO: Could change this to enable one-way portals
        pair_matrix_index = int(line_parts[3])
        pair_list_index = int(line_parts[4])  
        hex_matrix[matrix_index][list_index].make_portal(pair_matrix_index, pair_list_index)
        hex_matrix_new[matrix_index][list_index].make_portal(pair_matrix_index, pair_list_index)
        global portal_list

        portal_list.append((matrix_index, list_index))

        hex_matrix[pair_matrix_index][pair_list_index].make_portal(matrix_index, list_index)
        hex_matrix_new[pair_matrix_index][pair_list_index].make_portal(matrix_index, list_index)
        
        portal_list.append((pair_matrix_index, pair_list_index))



def swap_matrices():
    global hex_matrix
    global hex_matrix_new

    temp_matrix = hex_matrix
    hex_matrix = hex_matrix_new
    hex_matrix_new = temp_matrix

# Traverses hex_matrix and check for repeated identities (identified by serial number), issuing error message
def check_for_repeat_identities():
    # TODO: make this work and make it less ugly (maintain list of hexes with identities?)
    for k in range(len(hex_matrix)):
        for i in range(len(hex_matrix[k])):
            for i_ident in hex_matrix[k][i].idents:
                for l in range(k+1, len(hex_matrix)):
                    for j in range(i+1, len(hex_matrix[l])):
                        for j_ident in hex_matrix[l][j].idents:
                            if j_ident.serial_number == i_ident.serial_number:
                                # Debugging message
                                print("Two idents with serial number " + str(i_ident.serial_number) + " at (" + str(k) + ", " + str(i) + ") and (" + str(l) + ", " + str(j) + ")")
                                print(str(frames_created) + " frame(s) created")

                                # TODO: De-jankify this (there must be a better way than like 10 for-loops)

                                time.sleep(100000)

# Transfers identities between paired portals
def portal_handler():

    # TODO: Is this a necessary declaration?
    global hex_matrix_new

    # Set up temp storage for idents to be moved
    # TODO: There must be a better way to initialize this
    updated_portal_idents = []
    
    for i in range(len(portal_list)):
        sub_list = []
        updated_portal_idents.append(sub_list)


    # Fill temp storage
    for i in range(len(portal_list)):
        coords = portal_list[i]

        origin_hex = hex_matrix_new[coords[0]][coords[1]]
        assert(origin_hex)

        sub_list_temp = updated_portal_idents[i]

        # Pass all non-portal idents to temp storage
        for ident in origin_hex.idents:
            if ident.property != "portal":
                sub_list_temp.append(ident)

    for i in range(len(portal_list)):
        coords = portal_list[i]

        origin_hex = hex_matrix_new[coords[0]][coords[1]]
        assert(origin_hex)

        # Remove all non-portal idents from the origin hex
        origin_portal = origin_hex.contains_portal()
        origin_hex.idents.clear()

        # Sanity checking
        assert(len(origin_hex.idents) == 0)
        assert(len(hex_matrix_new[coords[0]][coords[1]].idents) == 0)
        assert(not hex_matrix_new[coords[0]][coords[1]].contains_portal())

        # Re-assign portal identity
        if origin_portal:
            print("add portal back in")
            origin_hex.idents.append(origin_portal)

        # Throw error if the origin_hex still contains any non-portal identities (debugging)
        assert(len(origin_hex.idents) == 1)
        assert(len(hex_matrix_new[coords[0]][coords[1]].idents) == 1)
        assert(origin_hex.idents[0].property == "portal")

    # Checking length of idents lists
    for coords in portal_list:
        hex_to_check = hex_matrix_new[coords[0]][coords[1]]
        assert(len(hex_matrix_new[coords[0]][coords[1]].idents)==1)
        assert(len(hex_to_check.idents)==1)

    for i in range(len(portal_list)):
        coords = portal_list[i]
        
        origin_portal = hex_matrix_new[coords[0]][coords[1]].contains_portal()
        
        assert(origin_portal)

        destination_hex = hex_matrix_new[origin_portal.pair_matrix_index][origin_portal.pair_list_index]

        # Pass idents from temp storage to destination hex
        
        for ident in updated_portal_idents[i]:
            destination_hex.take_ident(ident)


# Updates all the states
def next_generation():
    global frames_created
    frames_created += 1

    print("---")
    print("Calculating next generation")

    # back tracing is done here
    # to execute, we want to collect every item that exists and push them back 1 space
    items = []

    for hex_list in hex_matrix:
        for hexagon in hex_list:
            # find all items, store into list
            if len(hexagon.idents) != 0:
                # a hexagon might have multiple identities, we collect them all in a list
                check = hexagon.idents
                # we iterate thorugh the list of idents
                for c in check:
                    # we don't want to mark walls, so check if it is one
                    # mark as visited
                    c.visited(hexagon.list_index,hexagon.matrix_index)

    # calculation bellow

    # Iterates through the hexagons, determining what their next state should be
    for hex_list in hex_matrix:
                for hexagon in hex_list:
                    hexagon.update()
    
    portal_handler()

    swap_matrices()

def past_generation():
    # updating limit_tic
    global limit_tic

    if limit_tic > 0:
        # when paused, we can go back up to all steps
        print("---")
        print("Going back 1")

        # to execute, we want to collect every item that exists and push them back 1 space
        items = []

        for hex_list in hex_matrix:
            for hexagon in hex_list:
                # find all items, store into list
                if len(hexagon.idents) != 0:
                    # a hexagon might have multiple identities, we collect them all in a list
                    check = hexagon.idents
                    # we iterate thorugh the list of idents
                    for c in check:
                        # we don't want to change walls, so check if it is one
                        if c.state != -2:
                            # ince we find items, add them to our item list
                            items.append(c)
                            # erase current state
                            hexagon.idents = []

        for item in items:
            # item.back pops off 2 states and returns the 'previous' one
            past = item.back()
            limit_tic = limit_tic - 2
            # first we change the state to the state it was at that point in time
            item.state = past[2]
            # then we put the ident into the hex it was before
            hex_matrix[past[1]][past[0]].take_ident(item)
    else:
        print("ran out of memory")


import pygame

pygame.init()

SCREEN_WIDTH = 800

SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hex Simulator")

# set up pygame timer
clock = pygame.time.Clock()
run = True
dt = 0

# set up state
state = "pause"
# states are "pause" "go" "step"

# set up limit tic
limit_tic = 0

##########################################################################################################

# Create hexagons
hex_matrix = []

for x in range(15):
    hex_list = []
    hex_matrix.append(hex_list)

    for y in range(16):
        myHex = Hex(x, y)
        hex_list.append(myHex)


# create additional matrix
hex_matrix_new = []

for x in range(15):
    hex_list_new = []
    hex_matrix_new.append(hex_list_new)

    for y in range(16):
        myHex = Hex(x, y)
        hex_list_new.append(myHex)

# List of coordinate pairs describing portal locations
# TODO: Will need to update if portals are able to move
portal_list = []

# IMPORTANT: format of text file input is "matrix_index, list_index, state, color, direction"

# get initial state of the board from a file
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
file = open(os.path.join(__location__, "initial_state.txt"), "r")
for line in file:
    read_line(line)

##########################################################################################################

# Create walls around the edges
# Left edge
for hex in hex_matrix[0]:
    hex.make_wall()
# Right edge
for hex in hex_matrix[13]:
    hex.make_wall()
for i in range(6):
    # Top edge
    hex_matrix[1+2*i][6-i].make_wall()
    hex_matrix[2+2*i][6-i].make_wall()

    # Bottom edge
    hex_matrix[1+2*i][15-i].make_wall()
    hex_matrix[2+2*i][14-i].make_wall()


fast = True
##########################################################################################################

run = True
frames_created = 0
while run:

    if fast == False:
        pygame.time.delay(100)
    # Reset screen
    screen.fill((0, 0, 0))

    # Event handler (closing window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Draw all hexagons
    for hex_list in hex_matrix:
        for hexagon in hex_list:
            hexagon.draw(screen)


    # flips to the next frame
    pygame.display.flip()

    # sets animation to n frames per second where n is inside the parentheses (feel free to change)
    #dt = clock.tick(5) / 1000


    # HOW TO GET CODE TO START:
        # press g key after running file to start the animation
        # press h to go into hyper mode
        # press p to pause the animation
        # press s while paused to step through the animation
        # press f to print number of frames created so far
    if event.type == pygame.TEXTINPUT:
        # takes the key input
        keys = pygame.key.get_pressed()

        if keys[pygame.K_g]:
            state = "go"
        elif keys[pygame.K_p]:
            state = "pause"
        elif keys[pygame.K_h]:
            state = "hyper"

        if state == "pause" and keys[pygame.K_s]:
            fast = False
            next_generation()

            pygame.time.delay(100)
            # Take one second pause

        if state == "pause" and keys[pygame.K_b]:
            fast = False
            # go back a generation
            past_generation()

            pygame.time.delay(100)
            # Take one second pause

        
         # Print number of frames created so far (for debugging)
         # TODO: make this only print once (need to edit keys[pygame.K_f], but I don't think I can)
        if keys[pygame.K_f]:
            print(str(frames_created) + " frame(s) created")
                

    if state == "go":
        fast = True
        next_generation()
        dt = clock.tick(5) / 1000
    elif state == "hyper":
        fast = True
        next_generation()
        dt = clock.tick(2000) / 1000        
    
    check_for_repeat_identities()


pygame.quit()


