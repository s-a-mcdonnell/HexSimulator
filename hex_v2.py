import time
import copy
import os
import pygame

'''
Process of the game:
0. Iterate over Idents
1. a: If an ident is in a head on collision with another ident, it flips in place
   b: Else, move the ident forward into the next hex
2. Resolve collisions. For hexes that contain multiple idents...
   a: If it has an ident of opposite direction in that hex, bounce off/reverse direction
   b: Else, take the average of all other idents EXCEPT SELF, but break ties by using the opposite ident of self
'''

# hex class is now just for graphics/displaying the board/storing idents
class Hex:
    # Default color (no idents): light blue
    DEFAULT_COLOR =(190, 240, 255)

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
                return True
        
        return False

    ##########################################################################################################

    # Checks if a hex contains an ident heading in the given directon
    # If it does, returns that ident
    # Else returns None
    def contains_direction(self, dir):

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


# for storing information about a particular moving hex
class Ident:

    # TODO: Do we still need this?
    idents_created = 0

    ##########################################################################################################

    def __init__(self, matrix_index, list_index, world, color=(255, 255, 255), state = -1, serial_number = -1, hist = None):
        if hist is None:
            hist = []
        self.color = color

        self.state = state
        self.hist = hist
        if serial_number == -1:
            # If no serial number is provided
            self.serial_number = Ident.idents_created

            print("Ident with serial number " + str(self.serial_number) + " created")
            if state == -2:
                print("Is a wall")
            elif state == -1:
                print("Is stationary")
            else:
                print("Is moving")
            Ident.idents_created += 1
        else:
            self.serial_number = serial_number
            print("Ident with serial number " + str(self.serial_number) + " copied")
            print("color: " + str(self.color))

        self.matrix_index = matrix_index
        self.list_index = list_index

        self.world = world

    ##########################################################################################################

    def __copy(self):
        # TODO: Should a copy of self.hist be passed?
        new_copy = Ident(self.matrix_index, self.list_index, self.world, self.color, self.state, self.serial_number, self.hist)
        return new_copy
    
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


    # If the head-on (direction of self.state) neighboring hex contains an ident with the given direction, returns said ident
    # Else returns None
    # TODO: Does this method still have a purpose?
    def __neighbor_contains_direction(self, dir):

        return self.__get_neighbor(self.world.hex_matrix, self.state).contains_direction(dir)

    ##########################################################################################################


    # If the neighbor in the direction in which the ident is pointing is a wall, returns that ident
    # Else returns None
    def __neighbor_is_wall(self):
        return self.__neighbor_contains_direction(-2)
        
    ##########################################################################################################

    # If there will be a head-on-collision, returns the ident with which it will collide
    # Else returns none
    # TODO: Could just use a boolean
    def __head_on_collision(self):
        return self.__neighbor_contains_direction((self.state + 3)%6)


    ##########################################################################################################

    # If an ident is stationary or a wall, writes this value to the hex_matrix_new
    # Elif an ident is running into a wall or a head-on collision, flips it in place (writing to hex_matrix_new)
    # Else advances an ident by one hex in its direction of motion (if that hex exists)
    def advance_or_flip(self):
        future_matrix = self.world.hex_matrix_new
        future_hex = future_matrix[self.matrix_index][self.list_index]
        future_list = self.world.ident_list_new
    
        # Maintain walls and stationaries and return
        if (self.state == -2) or (self.state == -1):
            future_list.append(self.__copy())
            future_hex.idents.append(self.__copy())

            return

        # If need to bounce (wall or head-on), then bounce and return
        if self.__neighbor_is_wall():
            # TODO: Reintroduce flip and append method?
            copy_to_flip = self.__copy()
            copy_to_flip.state = (copy_to_flip.state + 3)%6
            future_list.append(copy_to_flip)
            future_hex.idents.append(copy_to_flip)
            
            return
        
        if self.__head_on_collision():
            # TODO: Reintroduce flip and append method?
            copy_to_flip = self.__copy()
            copy_to_flip.state = (copy_to_flip.state + 3)%6
            future_list.append(copy_to_flip)
            future_hex.idents.append(copy_to_flip)
            
            return

        # Advance all others (if the location where they would advance to exists)
        future_neighbor = self.__get_neighbor(future_matrix, self.state)
        if future_neighbor:
            # TODO: Append self or self.copy()?
            future_list.append(self)
            future_neighbor.idents.append(self)

    ##########################################################################################################

    # TODO: Write this method
    # Write from hex_matrix_new to hex_matrix
    def repair_collisions(self):

        pass

    def visited(self, m, l):
        # push onto stack history
        # pushed onto the history is
            # hex matix index
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

###############################################################################################################


# for setting initial state of the world / having a student interact
# while loop for running game goes in World
class World:
    def __init__(self):
        pygame.init()

        SCREEN_WIDTH = 800

        SCREEN_HEIGHT = 600

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hex Simulator")

        # TODO: Copy over timer

        # Set up hex matrix
        self.hex_matrix = []

        for x in range(15):
            hex_list = []
            self.hex_matrix.append(hex_list)

            for y in range(16):
                myHex = Hex(x, y)
                hex_list.append(myHex)
        
        # Set up new hex matrix
        self.hex_matrix_new = []

        for x in range(15):
            hex_list_new = []
            self.hex_matrix_new.append(hex_list_new)

            for y in range(16):
                myHex = Hex(x, y)
                hex_list_new.append(myHex)

        # Set up ident list
        self.ident_list = []

        # Set up new ident list
        self.ident_list_new = []

        # reading the intiial state of the hex board from a file
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file = open(os.path.join(__location__, "initial_state.txt"), "r")
        for line in file:
            self.__read_line(line)
            # pass
            # TODO: uncomment the above line for proper fie reading once we implement moving, stationary, wall hexes back into the program

    ##########################################################################################################

    @classmethod
    def __get_color(self, color_text):
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
            self.ident_list.append(new_ident)
            # TODO: Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
            # self.hex_matrix[matrix_index][list_index].make_move(direction, color)
        elif command == "occupied":
            color_text = line_parts[3]
            color = World.__get_color(color_text)
            new_ident = Ident(matrix_index, list_index, self, color = color)
            self.ident_list.append(new_ident)
            # TODO: Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
            # self.hex_matrix[matrix_index][list_index].make_occupied(color)
        elif command == "wall" or command == "wall\n":
            new_ident = Ident(matrix_index, list_index, self, color = (0,0,0), state = -2)
            self.ident_list.append(new_ident)
            # TODO: Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
            # self.hex_matrix[matrix_index][list_index].make_wall()

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

    # Swaps which matrix is being used
    def __swap_matrices_and_lists(self):
        # TODO: Janky pause
        counter = 0
        for i in range(10000):
            counter += 1

        temp_matrix = self.hex_matrix
        self.hex_matrix = self.hex_matrix_new
        self.hex_matrix_new = temp_matrix

        temp_list = self.ident_list
        self.ident_list = self.ident_list_new
        self.ident_list_new = temp_list

    ##########################################################################################################

    def __update(self):

        # Move or flip all idents
        for ident in self.ident_list:
            ident.advance_or_flip()
                
        # Fix collisions
        for ident in self.ident_list_new:
            ident.repair_collisions()
        
        # TODO: Have advance_or_flip write from original and new
        # TODO: Have repair_collisions write from new to original
        #self.__swap_matrices_and_lists()
    
    ##########################################################################################################

    def run(self):
        run = True
        while run:

            # Event handler (closing window)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            
            self.__draw()

            # flips to the next frame
            pygame.display.flip()
            
            self.__update()
        
        # Exit
        pygame.quit()
