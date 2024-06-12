

####################################################################################################
####################################################################################################
# HEXAGON CLASS
class Hex:

    ################
    ########### Create coordiantes (graphics)
    ################
    @staticmethod
    def create_coor(x, y):
        # __ x-=40
        # __ y-=490
        # __ return [(x, y), (x+40, y), (x+60, y+35), (x+40, y+70), (x, y+70), (x-20, y+35)]
        # Making hex smaller so that borders will be visible
        return [(x+3, y+3), (x+37, y+3), (x+57, y+35), (x+37, y+67), (x+3, y+67), (x-17, y+35)]

   ################
   ########### Constructor
   ################
    # color is an optional parameter with a default value of red
    # moveable is an optional parameter with a default value of true
    def __init__(self, matrix_index, list_index, color=(255, 0, 0), moveable=True):
        self.matrix_index = matrix_index
        self.list_index = list_index

        self.x = 60*matrix_index - 20
        self.y = 35*matrix_index + 70*list_index - 490

        self.oldx = matrix_index
        self.oldy = list_index

        self.coordinates = Hex.create_coor(self.x, self.y)

        self.color = color
        self.movable = moveable
        self.state = [0, 0, 0, 0, 0, 0]

       ################################# these are for the coordinates
       # Writing text to screen according to this tutorial:https://www.geeksforgeeks.org/python-display-text-to-pygame-window/
       # create the display surface object
       # of specific dimension..e(X, Y).
       # __ self.display_surface = pygame.display.set_mode((X, Y))
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # create a font object.
        # 1st parameter is the font file
        # which is present in pygame.
        # 2nd parameter is size of the font
        font = pygame.font.Font('freesansbold.ttf', 15)
        
        # create a text surface object,
        # on which text is drawn on it.
        self.text = font.render(('(' + str(matrix_index) + ',' + str(list_index) + ')'), True, (0, 255, 0))
        
        # create a rectangular object for the
        # text surface object
        self.textRect = self.text.get_rect()

        # set the center of the rectangular object.
        # __ self.textRect.center = (x + 30, y + 35)
        self.textRect.center = (self.coordinates[0][0] + 10, self.coordinates[0][1] + 35)

    ################
    ########### Draw based on state
    ################
    def draw(self, screen):
        if self.state[0]:
            self.color = (151, 33, 255)
        elif self.state[1]:
            self.color = (194, 255, 138)
        elif self.state[2]:
            self.color = (209, 209, 209)
        elif self.state[3]:
            self.color = (2, 115, 104)
        elif self.state[4]:
            self.color = (255, 244, 145)
        elif self.state[5]:
            self.color = (184, 255, 255)
        else:
            self.color = (252, 96, 177)

        # Draw the hexagon
        pygame.draw.polygon(screen, self.color, self.coordinates)

        # Draw text object displaying axial hex coordiantes
        self.display_surface.blit(self.text, self.textRect)

    def movea(self, hex_matrix):
        #if self.oldy+1 < len(hex_matrix[self.oldx]):
        hex_matrix[self.oldx][self.oldy-1].state[0] = 1
        self.state[0] = 0

    def moveb(self, hex_matrix):
            hex_matrix[self.oldx+1][self.oldy-1].state[1] = 1
            self.state[1] = 0

    def movec(self, hex_matrix):
        hex_matrix[self.oldx+1][self.oldy].state[2] = 1
        self.state[2] = 0

    def moved(self, hex_matrix):
        hex_matrix[self.oldx][self.oldy+1].state[3] = 1
        self.state[3] = 0

    def movee(self, hex_matrix):
        hex_matrix[self.oldx-1][self.oldy+1].state[4] = 1
        self.state[4] = 0

    def movef(self, hex_matrix):
        hex_matrix[self.oldx-1][self.oldy].state[5] = 1
        self.state[5] = 0


####################################################################################################
####################################################################################################

################
########### Setting up pygame and window
################
import pygame

# initializing "game"
pygame.init()

# screen dimensions
SCREEN_WIDTH = 14000
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Draw Hexagon")

#  setting up pygame timer
clock = pygame.time.Clock()
run = True
dt = 0

####################################################################################################
####################################################################################################

################
########### Setting up hexagons
################

# Create hexagons
hex_matrix = []

for x in range(15):
    hex_list = []
    hex_matrix.append(hex_list)

    for y in range(16):
        myHex = Hex(x, y)
        hex_list.append(myHex)

################
########### Add in moving haxagons in initial
################

# Update the state of a few hexagons to reflect motion
hex_matrix[6][7].state[0] = 1
hex_matrix[7][7].state[1] = 1
hex_matrix[7][8].state[2] = 1
hex_matrix[6][9].state[3] = 1
hex_matrix[5][9].state[4] = 1
hex_matrix[5][8].state[5] = 1

####################################################################################################
####################################################################################################

# running game
while run:
    # Event handler (closing window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Reset screen
    screen.fill((0, 0, 0))

    # Draw hexagons
    for hex_list in hex_matrix:
        for hexagon in hex_list:
            hexagon.draw(screen)

    ##for hex_list in hex_matrix:
    ##   for hexagon in hex_list:
            # check surroundings
             # insert code later, would return a boolean
            # if affected, update direction
             # insert code later
            # if affected, update direction



    #for hex_list in hex_matrix:
     #   for i in range(len(hex_list) - 1):
      #      if hex_list[i+1].state[0] == 1:
       #         hex_list[i].state[0] = 1
        #        hex_list[i+1].state[0] = 0

    for hex_list in hex_matrix:
        for hexagon in hex_list:
            if hexagon.state[0] == 1:
                hexagon.movea(hex_matrix)
            if hexagon.state[5] == 1:
                hexagon.movef(hex_matrix)

    #for hex_list in hex_matrix:
    #    for hexagon in hex_list:
     #       if hexagon.state[1] == 1:
     #           hexagon.moveb(hex_matrix)

    #for hex_list in hex_matrix:
    #    for hexagon in hex_list:
    #        if hexagon.state[2] == 1:
    #            hexagon.movec(hex_matrix)

    #for hex_list in hex_matrix:
    #    for hexagon in hex_list:
    #        if hexagon.state[3] == 1:
    #            hexagon.moved(hex_matrix)

    #for hex_list in hex_matrix:
    #    for hexagon in hex_list:
    #        if hexagon.state[4] == 1:
    #            hexagon.movee(hex_matrix)

    #for hex_list in hex_matrix:
    #    for hexagon in hex_list:
    #        if hexagon.state[5] == 1:
    #            hexagon.movef(hex_matrix)




    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(1) / 1000

pygame.quit()


