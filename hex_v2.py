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

        # Map matrix_index and list_index to Cartesian coordinates
        self.x = 60*matrix_index - 20
        self.y = 35*matrix_index + 70*list_index - 490

        self.coordinates = Hex.create_coor(self.x, self.y)

        # Default color (no idents): light blue
        self.color =(190, 240, 255)
       
        # TODO: Store idents

        '''# TODO: Move arrows and smaller hexagon to idents? (maybe)
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
        self.small_hexagon = [(self.x+9, self.y+11), (self.x+31, self.y+11), (self.x+47, self.y+35), (self.x+31, self.y+59), (self.x+9, self.y+59), (self.x-7, self.y+35)]'''
 
##########################################################################################################

    # Graphics
    def draw(self, screen):
            
        # TODO: If we want idents to be drawn over blank hexes, this is not necessary
        '''if (len(self.idents) >= 1):
            # If a hex contains only one ident, take that color
            # If a hex contains multiple idents, the ident stored first will be the outermost color
            my_color = self.idents[0].color'''
        
        # Draw the hexagon
        pygame.draw.polygon(screen, self.color, self.coordinates)

        '''# Draw an extra hexagon to visually show that a hexagon is stationary even with the different colors
        if self.contains_direction(-1) != None:
            new_color = [max(0, c - 120) for c in my_color]
            pygame.draw.polygon(screen, new_color, self.small_hexagon)
    
        # Draw multiple nesting circles indicating colors for hexes with superimposed idents/states
        for i in range(1, len(self.idents)):
            if (33 - 5*i) > 0:
            pygame.draw.circle(screen, self.idents[i].color, (self.x+20, self.y+35), 33-5*i)
    
        # Draw an arrow on the hex if the hex is moving
        if self.is_moving:
            for i in range(6):
                if self.contains_direction(i):
                    pygame.draw.polygon(screen, (0, 0, 0), self.arrows[i])'''

    ##########################################################################################################


# for storing information about a particular moving hex
class Ident:

    idents_created = 0

    def __init__(self, color=(255, 255, 255), state = -1, serial_number = -1, hist = None):
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

    def draw(self):
        # Reset screen
        self.screen.fill((0, 0, 0))

        # Draw all blank hexes
        for hex_list in self.hex_matrix:
            for hex in hex_list:
                hex.draw(self.screen)

        # TODO: Draw all idents
    
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
            
            # TODO: Update everything
        
        # Exit
        pygame.quit()

    
    @classmethod
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

    @classmethod
    def read_line(line):
        # actual parsing of the text file
        line_parts = line.split(" ")
        
        matrix_index = int(line_parts[0])
        list_index = int(line_parts[1])
        command = line_parts[2]

        if command == "move":
            direction = int(line_parts[4])
            color_text = line_parts[3]
            color = World.get_color(color_text)
            hex_matrix[matrix_index][list_index].make_move(direction, color)
        elif command == "occupied":
            color_text = line_parts[3]
            color = World.get_color(color_text)
            hex_matrix[matrix_index][list_index].make_occupied(color)
        elif command == "wall" or command == "wall\n":
            hex_matrix[matrix_index][list_index].make_wall()
