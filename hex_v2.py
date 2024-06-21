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
    ###############################################################################################################

    # Takes x and y (Cartesian coordinates where (0, 0) is the top left corner)
    # Returns a list of 6 coordinates defining a hexagon
    @staticmethod
    def create_coor(x, y):
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

        self.coordinates = Hex.create_coor(self.x, self.y)

        # Default color (no idents): light blue
        self.color =(190, 240, 255)
       
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

    # Checks where a specific ident occurs within this hex's list
    # If it contains the ident, returns the index
    # Else returns -1
    def get_ident_index(self, to_find):

        # TODO: What if the hex contains multiple idents with that state?
        for i in range(len(self.idents)):
            if self.idents[i] == to_find:
                return i
        return -1

    ##########################################################################################################

    # Graphics
    def draw(self, screen):
            
        color_to_draw = self.color


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

    # returns an Ident with the same properties as self
    def copy(self):
        # TODO: Review copy method
        new_copy = Ident(self.matrix_index, self.list_index, self.world, self.color, self.state, self.serial_number, self.hist)
        return new_copy

    
    # TODO: Write this method
    def advance_or_flip(self):
        pass

    # TODO: Write this method
    # note that I should never have to deal with walls in this method
    def repair_collisions(self):

        w = self.world

        # obtain the hex that this ident is a part of
        hex = w.hex_matrix[self.matrix_index][self.list_index]
        if len(hex.idents) <= 1:
            print("No collision to resolve")
            return
        
        # now we have determined that the ident has other idents with it
        my_index = hex.get_ident_index(self)
        dir = self.state

        directions = []

        # TODO: consider appending just the directions/states of the idents instead of appending the idents themselves
        for i in range(len(hex.idents)):
            if i != my_index:
                directions.append(hex.idents[i])

        # if there was only one other ident in the collision, take its attributes
        if len(directions) == 1:
            to_become = self.copy()
            to_become.state = directions[0].state
            # additionally, move it forward depending on the direction
            # if the other hex was stationary, do not move it forward at all, keep it in place
            w.ident_list_new.append(to_become)
            w.hex_matrix_new[self.matrix_index][self.list_index].idents.append(to_become)
        # if there is more than one other ident than self, we do averaging things
        # if the idents contain an opposite direction ident, we bounce!! :)
        elif hex.contains_direction((dir + 3) % 6) is not None:
            to_become = self.copy()
            to_become.state = (self.state + 3) % 6
            w.ident_list_new.append(to_become)
            w.hex_matrix_new[self.matrix_index][self.list_index].idents.append(to_become)
        # otherwise, determine whether we contain a stationary hex or not
        # if not, we are all moving hexes and none of them are opposite me, so we average them
        elif hex.contains_direction(-1) is None:
            # if we contain opposite pairs, remove them from the directions list
            if (hex.contains_direction(dir + 1) is not None) and (hex.contains_direction(dir - 2) is not None):
                directions.remove(hex.contains_direction(dir + 1))
                directions.remove(hex.contains_direction(dir - 2))
            if (hex.contains_direction(dir + 2) is not None) and (hex.contains_direction(dir - 1) is not None):
                directions.remove(hex.contains_direction(dir + 2))
                directions.remove(hex.contains_direction(dir - 1))
            # if, at this point, there is only one direction left, take that one
            if len(directions == 1):
                to_become = self.copy()
                to_become.state = directions[0].state
                w.ident_list_new.append(to_become)
                w.hex_matrix_new[self.matrix_index][self.list_index].idents.append(to_become)
            # otherwise, we ended up with a net zero average and use the opposite of our own direction to break ties
            elif len(directions == 0):
                to_become = self.copy()
                to_become.state = (dir - 3) %  6
                w.ident_list_new.append(to_become)
                w.hex_matrix_new[self.matrix_index][self.list_index].idents.append(to_become)

        # else, we are dealing with multiple hexes, including a stationary hex
        # TODO: stationary cases here!!!
        else:
            pass


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
        self.hex_matrix_new = []

        for x in range(15):
            hex_list = []
            self.hex_matrix.append(hex_list)

            for y in range(16):
                myHex = Hex(x, y)
                hex_list.append(myHex)

        # Set up ident list
        self.ident_list = []
        self.ident_list_new = []


        # reading the intiial state of the hex board from a file
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file = open(os.path.join(__location__, "initial_state.txt"), "r")
        for line in file:
            self.read_line(line)

    ##########################################################################################################

    @classmethod
    def get_color(self, color_text):
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

    def read_line(self, line):
        # actual parsing of the text file
        line_parts = line.split(" ")
        
        matrix_index = int(line_parts[0])
        list_index = int(line_parts[1])
        command = line_parts[2]

        if command == "move":
            direction = int(line_parts[4])
            color_text = line_parts[3]
            color = World.get_color(color_text)
            new_ident = Ident(matrix_index, list_index, self, color = color, state = direction)
            self.ident_list.append(new_ident)
            # TODO: Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
            # self.hex_matrix[matrix_index][list_index].make_move(direction, color)
        elif command == "occupied":
            color_text = line_parts[3]
            color = World.get_color(color_text)
            new_ident = Ident(matrix_index, list_index, color = color)
            self.ident_list.append(new_ident)
            # TODO: Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
            # self.hex_matrix[matrix_index][list_index].make_occupied(color)
        elif command == "wall" or command == "wall\n":
            new_ident = Ident(matrix_index, list_index, color = (0,0,0), state = -2)
            self.ident_list.append(new_ident)
            # TODO: Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
            # self.hex_matrix[matrix_index][list_index].make_wall()

    ##########################################################################################################

    def draw(self):
        # Reset screen
        self.screen.fill((0, 0, 0))

        # Draw all blank hexes
        for hex_list in self.hex_matrix:
            for hex in hex_list:
                hex.draw(self.screen)

        # TODO: Draw all idents
        '''for ident in self.ident_list:
            # TODO: Write Ident.draw()
            ident.draw()'''

    ##########################################################################################################


    def update(self):

        # Move or flip all idents
        for ident in self.ident_list:
            ident.advance_or_flip()
                
        # Fix collisions
        for ident in self.ident_list:
            ident.repair_collisions()

        # TODO: Write this method, iterating through idents
    
    ##########################################################################################################

    def run(self):
        run = True
        while run:

            # Event handler (closing window)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            
            self.draw()

            # flips to the next frame
            pygame.display.flip()
            
            self.update()
        
        # Exit
        pygame.quit()
