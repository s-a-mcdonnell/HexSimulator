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

    def make_wall(self):
        # Wipe idents currently stored
        self.idents.clear()
        # Walls are black
        # -2 state is a wall
        self.idents.append(Ident((0, 0, 0), -2))

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

    def is_occupied(self):
        if len(self.idents) == 0:
            return False
        else:
            return True

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

    def __init__(self, matrix_index, list_index, color=(255, 255, 255), state = -1, serial_number = -1, hist = None, myworld = None):
        if hist is None:
            hist = []
        self.color = color

        self.myworld = myworld

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

    def move_to(self, new_matrix_index, new_list_index):
        # remove trace
        self.myworld.hex_matrix[self.matrix_index][self.list_index].idents = []

        # put into new spot
        self.myworld.hex_matrix[new_matrix_index][new_list_index].idents.append(self)

        # update index
        self.matrix_index = new_matrix_index
        self.list_index = new_list_index




    
    # TODO: Write this method
    # Writes to hex_matrix_new
    def advance_or_flip(self):
        global hex_matrix_new

        # Maintain walls and stationaries and return

        if self.state >= 0: # if moving
            # first, check the one in front of you

            # this will depend on which direction you are moving in

            # moving up
            if self.state == 0: # moving up

                # first see if you crash
                if self.myworld.hex_matrix[self.matrix_index][self.list_index-1].contains_direction(-1) != None or self.myworld.hex_matrix[self.matrix_index][self.list_index-1].contains_direction(3) != None:
                    print("might move, deal with later")

                # else, you can move
                else:
                    self.move_to(self.matrix_index, self.list_index-1)
                pass

            elif self.state == 1:  # moving northeast
                # first see if you can go
                # else, you collide
                pass

            elif self.state == 2:  # moving southeast
                # first see if you can go
                # else, you collide
                pass

            elif self.state == 3:  # moving down
                # first see if you can go
                # else, you collide
                pass

            elif self.state == 4:  # moving southwest
                # first see if you can go
                # else, you collide
                pass

            elif self.state == 5:  # moving northwest
                # first see if you can go
                # else, you collide
                pass


        # If need to bounce (wall or head-on), then bounce and return

        # Advance all others


        pass

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
            new_ident = Ident(matrix_index, list_index, color = color, state = direction, myworld = self)
            self.ident_list.append(new_ident)
            # TODO: Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
            # self.hex_matrix[matrix_index][list_index].make_move(direction, color)
        elif command == "occupied":
            color_text = line_parts[3]
            color = World.__get_color(color_text)
            new_ident = Ident(matrix_index, list_index, color = color, myworld = self)
            self.ident_list.append(new_ident)
            # TODO: Add ident to hex
            self.hex_matrix[matrix_index][list_index].idents.append(new_ident)
            # self.hex_matrix[matrix_index][list_index].make_occupied(color)
        elif command == "wall" or command == "wall\n":
            new_ident = Ident(matrix_index, list_index, color = (0,0,0), state = -2, myworld = self)
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
        temp_matrix = self.hex_matrix
        self.hex_matrix = self.hex_matrix_new
        self.hex_matrix_new = temp_matrix

        temp_list = self.ident_list
        self.ident_list = self.ident_list_new
        self.ident_list_new = temp_list

    ##########################################################################################################

    def __update(self):
        # TODO: Note that this (calling swap_matrices) will just cause flashing until these two methods are written

        # Move or flip all idents
        for ident in self.ident_list:
            ident.advance_or_flip()
                
        # Fix collisions
        for ident in self.ident_list_new:
            ident.repair_collisions()
        
        # TODO: Have advance_or_flip write from original and new
        # TODO: Have repair_collisions write from new to original
        # self.__swap_matrices_and_lists()
    
    #########################################################################################################


    def run(self):
        clock = pygame.time.Clock()
        dt = 0

        # Create walls around the edges
        # Left edge
        for hex in self.hex_matrix[0]:
            hex.make_wall()
        # Right edge
        for hex in self.hex_matrix[13]:
            hex.make_wall()
        for i in range(6):
            # Top edge
            self.hex_matrix[1 + 2 * i][6 - i].make_wall()
            self.hex_matrix[2 + 2 * i][6 - i].make_wall()

            # Bottom edge
            self.hex_matrix[1 + 2 * i][15 - i].make_wall()
            self.hex_matrix[2 + 2 * i][14 - i].make_wall()

        run = True
        while run:

            # Event handler (closing window)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            
            self.__draw()

            dt = clock.tick(5) / 1000

            # flips to the next frame
            pygame.display.flip()
            
            self.__update()
        
        # Exit
        pygame.quit()