class Hex:
   @staticmethod
   def create_coor(x, y):
        # Making hex smaller so that borders will be visible
        return [(x+3, y+3), (x+37, y+3), (x+57, y+35), (x+37, y+67), (x+3, y+67), (x-17, y+35)]


    # Constructor
    # color is an optional parameter with a default value of red
    # occupied is an optional parameter with a default value of false
    # moveable is an optional parameter with a default value of false
   def __init__(self, matrix_index, list_index, color=(255, 0, 0), occupied=False, moveable=False):
       self.matrix_index = matrix_index
       self.list_index = list_index

       self.x = 60*matrix_index - 20
       self.y = 35*matrix_index + 70*list_index - 490

       self.coordinates = Hex.create_coor(self.x, self.y)
       
       self.color = color

       self.occupied = occupied
       self.movable = moveable
       self.state = [0, 0, 0, 0, 0, 0]

       # Writing text to screen according to this tutorial:https://www.geeksforgeeks.org/python-display-text-to-pygame-window/

        # create the display surface object
        # of specific dimension..e(X, Y).
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
       self.textRect.center = (self.x + 20, self.y + 35)
   
   def draw(self, screen):
    '''if self.state[0] | self.state[1] | self.state[2] | self.state[3] | self.state[4] | self.state[5]:
       self.color = (0, 0, 255)
    else:
        self.color = (255, 0, 0)'''
    
    '''if self.occupied:
        if self.state[0] | self.state[1] | self.state[2] | self.state[3] | self.state[4] | self.state[5]:
            # If it is occupied and moving, blue
            self.color = (0, 0, 255)
        else:
            # If it is occupied and not moving, white
            self.color = (255, 255, 255)
    else:
        # If it is not occupied, red
        self.color = (255, 0, 0)'''
    
        # Draw the hexagon
        pygame.draw.polygon(screen, self.color, self.coordinates)

        # Draw text object displaying axial hex coordiantes
        self.display_surface.blit(self.text, self.textRect)

    # TODO: Write description
    def update(self):
        # If it is non-moveable, copy it over and change nothing

        if self.state[0] | self.state[1] | self.state[2] | self.state[3] | self.state[4] | self.state[5]:
            self.occupied = true
            # If it is occupied and moving, blue
            self.color = (0, 0, 255)    
        elif self.occupied:
            # If it is occupied and not moving, white
            self.color = (255, 255, 255)
        else:
            # If it is not occupied, red
            self.color = (255, 0, 0)

def hex_matrix_init():
    matrix = []

    for x in range(15):
        list = []
        matrix.append(list)

        for y in range(16):
            myHex = Hex(x, y)
            list.append(myHex)

    return matrix

import pygame

pygame.init()

SCREEN_WIDTH = 800

SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Draw Hexagon")
    

# Create hexagons
hex_matrix = hex_matrix_init()

# Update the state of a few hexagons to reflect motion
hex_matrix[0][0].state[5] = 2
hex_matrix[10][10].state[0] = 1
hex_matrix[4][7].state[3] = 3
hex_matrix[6][10].state[2] = 1

# Create second matrix to alternate with
alt_matrix = hex_matrix_init()

worlds = [hex_matrix, alt_matrix]

# integer to indicate which world we are currently using
curr_world = 0

run = True
while run:

    # Reset screen
    screen.fill((0, 0, 0))

    # Draw hexagons
    r = 10
    g = 10
    b = 10
    for hex_list in worlds[curr_world]:
        for hexagon in hex_list:
            hexagon.draw(screen)

    # Event handler (closing window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

    # Alternate curr_world between 0 and 1
    curr_world += 1
    curr_world %= 2

    # Update to handle movement
    # TODO: Update to handle movement
    for hex_list in worlds[curr_world]:
        for hexagon in hex_list:
            hexagon.update()

pygame.quit()

