

####################################################################################################
####################################################################################################

import numpy as np

col1 = (120, 0, 120)

col2 = (0, 150, 150)

col3 = (100, 140, 10)

#########################################################
class Hex:

    @staticmethod
    def create_coor(x, y):
        # __ x-=40
        # __ y-=490
        # __ return [(x, y), (x+40, y), (x+60, y+35), (x+40, y+70), (x, y+70), (x-20, y+35)]
        # Making hex smaller so that borders will be visible
        return [(x + 3, y + 3), (x + 37, y + 3), (x + 57, y + 35), (x + 37,y + 67), (x + 3, y + 67), (x - 17, y + 35)]

    # Constructor
    # color is an optional parameter with a default value of red
    # moveable is an optional parameter with a default value of true

    def __init__(self, matrix_index, list_index, color=col1, moveable=True):
        self.matrix_index = matrix_index
        self.list_index = list_index

        self.x = 60 * matrix_index - 20
        self.y = 35 * matrix_index + 70 * list_index - 490

        self.hitup = self.y + 55
        self.hitdown = self.y + 15
        self.hitr = self.x + 40
        self.hitl = self.x

        self.coordinates = Hex.create_coor(self.x, self.y)

        self.color = color
        self.movable = moveable
        self.state = [0, 0, 0, 0, 0, 0]  # top, top right, bottom right, bottom, bottom left, top left

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


# def get_hex(self, mouse_coord):
# (x+3, y+3), (x+37, y+3), (x+57, y+35), (x+37, y+67), (x+3, y+67), (x-17, y+35)
    #
    def draw(self, screen):
        if self.state[0] | self.state[1] | self.state[2] | self.state[3] | self.state[4] | self.state[5]:
            self.color = col1
        else:
            self.color = col2

        # Draw the hexagon
        pygame.draw.polygon(screen, self.color, self.coordinates)

        # Draw text object displaying axial hex coordiantes
        self.display_surface.blit(self.text, self.textRect)

#########################################################

import pygame

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Draw Hexagon")

clock = pygame.time.Clock()
run = True
dt = 0

#########################################################

# Create hexagons
hex_matrix = []
for x in range(17):
    hex_list = []
    hex_matrix.append(hex_list)

    for y in range(17):
        myHex = Hex(x, y)
        hex_list.append(myHex)


# check for a hit box
def postohex(position):
    print('Mouse button pressed!', position)

    print('Mouse button pressed!', position[0])

    uum = (position[0]-20,position[1]-35)
    print('maybe?', uum)

    ummx = (uum[0]+20)/60
    ummy = (uum[1]+490-(35*ummx))/70

    print('intish?', ummx)
    print('intish?', ummy)

    hex_matrix[round(ummx)][round(ummy)].state[0] = 1

#########################################################

run = True
while run:
    # Reset screen
    screen.fill((0, 0, 0))

    # Draw hexagons
    for hex_list in hex_matrix:
        for hexagon in hex_list:
            hexagon.draw(screen)

    print('mouse pos:', pygame.mouse.get_pos())


      # Event handler (closing window)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if event.type == pygame.MOUSEBUTTONDOWN:
        postohex(pygame.mouse.get_pos())
    # flip() the display to put your work on screen

    pygame.display.flip()
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(30) / 1000

pygame.quit()

## making sure I remember how to commit
