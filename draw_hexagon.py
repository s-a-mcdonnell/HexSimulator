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
        self.idents = None
        self.idents = []
        # Walls are black
        # -2 state is a wall
        self.idents.append(Ident((0,0,0), -2))

    ##########################################################################################################

    ##########################################################################################################

    # sets the given hex to act as a portal
    # TODO: How to set destiantion?
    def make_portal(self, pmi, pli):
        # Portals are dark purple
        # TODO: What state to pass?
        # TODO: Rename variables
        # TODO: Ideally, portals should be linked just to idents, not to hexes (so they can move)
        self.idents.append(Ident((75, 4, 122), property="portal", pair_matrix_index=pmi, pair_list_index=pli))

    ##########################################################################################################

    ##########################################################################################################

    def make_sticky(self):
        self.idents = "sticky"

    ##########################################################################################################

    ##########################################################################################################

    # sets the given hex to move in a given direction
    def make_move(self, dir, color=(255,0,0)):
        # Note: Does not overwrite idents currently stored
        self.idents.append(Ident(color, dir))

    # Appends the passed ident to the given hex
    def take_ident(self, ident):
        if ident.state != -2:
            print("hex at " + str(self.matrix_index) + ", " + str(self.list_index) + " taking ident " + str(ident.serial_number))
        self.idents.append(ident)    

    def make_occupied(self, color=(0, 255, 0)):
        # TODO: Clear out current idents? (does not currently overwrite pre-existing idents)
        self.idents.append(Ident(color, -1))

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
    def check_movables(self): 
        hex_movable = [0, 0, 0, 0, 0, 0]

        # Initializing hexToCheck with default value (reducing repeated memory allocation and deallocation)
        hexToCheck = self

        # check upper hex (pos 0)
        # If the upper hex exists and is occupied, moving, and stationary, flip the boolean in the array
        if self.list_index - 1 >= 0:
           hexToCheck = hex_matrix[self.matrix_index][self.list_index - 1]
           hex_movable[0] = hexToCheck.check_movable_hex()

        # check northeast hex (pos 1)
        if (self.matrix_index + 1 < len(hex_matrix)) and (self.list_index - 1 >= 0):
           hexToCheck = hex_matrix[self.matrix_index + 1][self.list_index - 1]
           hex_movable[1] = hexToCheck.check_movable_hex()

        # check southeast hex (pos 2)
        if self.matrix_index + 1 < len(hex_matrix):
            hexToCheck = hex_matrix[self.matrix_index + 1][self.list_index]
            hex_movable[2] = hexToCheck.check_movable_hex()

        # check down hex (pos 3)
        if self.list_index + 1 < len(hex_list):
            hexToCheck = hex_matrix[self.matrix_index][self.list_index + 1]
            hex_movable[3] = hexToCheck.check_movable_hex()

        # check southwest hex (pos 4)
        if (self.matrix_index - 1 >= 0) and (self.list_index + 1 < len(hex_list)):
            hexToCheck = hex_matrix[self.matrix_index - 1][self.list_index + 1]
            hex_movable[4] = hexToCheck.check_movable_hex()

        # check northwest hex (pos 5)
        if self.matrix_index - 1 >= 0:
            hexToCheck = hex_matrix[self.matrix_index - 1][self.list_index]
            hex_movable[5] = hexToCheck.check_movable_hex()

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
                return True
           
        return False    

    ##########################################################################################################

    # Checks if a hex contains a portal ident
    # If it does, returns that ident
    # Else returns None
    
    def contains_portal(self):
        for ident in self.idents:
            # TODO: Use int insteal of string for faster processing
            if ident.property == "portal":
                return ident

        return None    
    
    ##########################################################################################################

    def is_sticky(self):
        for ident in self.idents:
            if ident.property == "sticky":
                return ident
        return None

    ###########################################################################################################

   # returns a list of length 6 to determine which of the neighbors around self hex are walls
    def check_walls(self):
        hex_walls = [0, 0, 0, 0, 0, 0]

        # Default value of hexToCheck (not used)
        hexToCheck = self

        # check upper hex (pos 0)
        if self.list_index - 1 >= 0:
            hexToCheck = hex_matrix[self.matrix_index][self.list_index - 1]
            hex_walls[0] = hexToCheck.contains_wall()

         # check northeast hex (pos 1)
        if (self.matrix_index + 1 < len(hex_matrix)) and (self.list_index - 1 >= 0):
            hexToCheck = hex_matrix[self.matrix_index + 1][self.list_index - 1]
            hex_walls[1] = hexToCheck.contains_wall()


        # check southeast hex (pos 2)
        if self.matrix_index + 1 < len(hex_matrix):
            hexToCheck = hex_matrix[self.matrix_index + 1][self.list_index]
            hex_walls[2] = hexToCheck.contains_wall()


        # check down hex (pos 3)
        if self.list_index + 1 < len(hex_list):
            hexToCheck = hex_matrix[self.matrix_index][self.list_index + 1]
            hex_walls[3] = hexToCheck.contains_wall()


        # check southwest hex (pos 4)
        if (self.matrix_index - 1 >= 0) and (self.list_index + 1 < len(hex_list)):
            hexToCheck = hex_matrix[self.matrix_index - 1][self.list_index + 1]
            hex_walls[4] = hexToCheck.contains_wall()


         # check northwest hex (pos 5)
        if self.matrix_index - 1 >= 0:
            hexToCheck = hex_matrix[self.matrix_index - 1][self.list_index]
            hex_walls[5] = hexToCheck.contains_wall()


        return hex_walls

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
                future.take_ident(ident_to_stop)

    ##########################################################################################################

    # Handles interactions between a hex and its environment with respect to the given direction
    def motion_handler(self, future, my_neighbors, neighbors_movable, neighbors_wall, dir):
        # straight_neighbor is the neighbor in that direction (ex. when dir = 0, straight_neighbor is the upper neighbor of self)
        straight_neighbor = my_neighbors[dir]

        # TODO: Janky quick fix for portals (In this method, no collisions happen in/on portals)
        if self.contains_portal():
            neighbor_ident = straight_neighbor.contains_direction((dir+3)%6)
            if neighbor_ident:
                future.take_ident(neighbor_ident)
            return
        
        if self.is_sticky():
            #check if the hex 'dead ahead' from direction is a wall, if so, become wall in future, elsewise, move on to normal movement
            if my_neighbors[dir] == neighbors_wall[dir]:
                self.make_wall

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

                elif dir_neighbor_ident and opp_neighbor_ident:
                    # Handle head-on collision with an empty hex in the middle
                    print("case 6")
                    ident_to_flip = dir_neighbor_ident.copy()
                    ident_to_flip.state = (ident_to_flip.state + 3)%6
                    future.take_ident(ident_to_flip)
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
        
        # handle impact of hitting occupied neighbor
        if self.contains_direction(dir): 
            self.hit_neighbor(future, my_neighbors, neighbors_movable, neighbors_wall, dir)

    # returns an array of neighbors (the entry in the array is None when the neighbor does not exist)
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


    ##########################################################################################################

    ##########################################################################################################

   #update self hexagon
    def update(self):
        # determine the state of the current hex based on the states of the hexes around it
        future = hex_matrix_new[self.matrix_index][self.list_index]
        future.idents = []

        # TODO: If self is a portal, future is its paired location
        portal_ident = self.contains_portal()
        if portal_ident:
            future.take_ident(portal_ident)
            future = hex_matrix_new[portal_ident.pair_matrix_index][portal_ident.pair_list_index]

        neighbors_movable = self.check_movables()
        neighbors_wall = self.check_walls()

        # If the hex is a wall, it will remain occupied and not movable
        if(self.contains_wall()):
            future.take_ident(self.contains_direction(-2))
            return


        my_neighbors = self.get_neighbors()
        
        # TODO: Convert if self.movable: to ident
        # If the hex does not contains a wall
        if not self.contains_wall():
            # TODO: Adjust to account for idents

            for i in range(6):
                if my_neighbors[i] != None:
                    self.motion_handler(future, my_neighbors, neighbors_movable, neighbors_wall, i)

        # If the hex is currently occupied and not moving, it will still be occupied in the next generation
        # If that hasn't already been seen to by the motion handler, that must mean that the hex is occupied and stationary in the next generation
        # TODO: It is not necessarily true, however, that it will still be occupied and STATIONARY in the next generation, which is what I'm going here
        # TODO: Explain logic better --> Could this be the cause of the stationary hex being obliterated when hit by two moving hexes?
        is_stationary = self.contains_direction(-1)
        if is_stationary and (len(future.idents) == 0):
            future.idents.append(is_stationary.copy())



class Ident:
    # Constructor
    # Default color white
    # Default state -1 (movable but not moving)
    idents_created = 0

    def __init__(self, color=(255, 255, 255), state=-1, serial_number=-1, property=None, pair_matrix_index=-1, pair_list_index=-1):
        self.color = color

        # States:
        # -2 = wall
        # -1 = stationary but movable
        # 0 through 5 = directions of motion (0 = 12 o'clock)
        self.state = state
        
        self.property = property

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
        # return copy.copy(self)
        # TODO: Review copy method
        new_copy = Ident(self.color, self.state, self.serial_number, self.property)
        return new_copy
    

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
        pair_matrix_index = int(line_parts[3])
        pair_list_index = int(line_parts[4])  
        hex_matrix[matrix_index][list_index].make_portal(pair_matrix_index, pair_list_index)
        hex_matrix[pair_matrix_index][pair_list_index].make_portal(matrix_index, list_index)
    elif command == "sticky" or command == "sticky\n":
        direction = int(line_parts[4])
        color_text = line_parts[3]
        color = get_color(color_text)
        hex_matrix[matrix_index][list_index].make_move(direction, color)

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

                                # Attempt to go back in time by one frame (not working):
                                '''swap_matrices()
                                print("matrices swapped back")

                                # Reset screen
                                screen.fill((0, 0, 0))

                                 # Draw all hexagons
                                for hex_list in hex_matrix:
                                    for hexagon in hex_list:
                                        hexagon.draw(screen)

                                # flips to the next frame
                                pygame.display.flip()'''

                                time.sleep(100000)

# Updates all the states
def next_generation():
    global frames_created
    frames_created += 1

    print("---")
    print("Calculating next generation")

    # Iterates through the hexagons, determining what their next state should be
    for hex_list in hex_matrix:
                for hexagon in hex_list:
                    hexagon.update()
    
    swap_matrices()

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
            pygame.time.delay(1000)
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


