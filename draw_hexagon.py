class Hex:
   @staticmethod
   def create_coor(x, y):
        # Making hex smaller so that borders will be visible
        return [(x+3, y+3), (x+37, y+3), (x+57, y+35), (x+37, y+67), (x+3, y+67), (x-17, y+35)]


    # Constructor
    # color is an optional parameter with a default value of red
    # occupied is an optional parameter with a default value of false
    # moveable is an optional parameter with a default value of true
   def __init__(self, matrix_index, list_index, color=(255, 0, 0), occupied=False, moveable=True):
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
        # Draw the hexagon
        pygame.draw.polygon(screen, self.color, self.coordinates)

        # Draw text object displaying axial hex coordiantes
        self.display_surface.blit(self.text, self.textRect)

    # TODO: Write description
   def update(self):
        print("Updating " + str(self.matrix_index) + ", " + str(self.list_index))

        future_hex = next_world[self.matrix_index][self.list_index]

        # If it has one moving neighbor moving towards it, that neighbor's state becomes its own
        # __ Should I create a new array or just point to the old one?
        '''if this_world[self.matrix_index][self.list_index - 1].state[3]:
            future_hex.state[3] = 1'''
        
        # TODO: Condense these conditionals

        # If its upper neighbor is pointing down, it will point down in the future
        if self.list_index - 1 > 0:
            future_hex.state[3] = this_world[self.matrix_index][self.list_index - 1].state[3]

        # If its lower neighbor is pointing up, it will point up in the future
        if self.list_index + 1 < len(this_world[self.matrix_index]):
            print('state 0 check')
            print('length: ' + str(len(this_world[self.matrix_index])))
            print('trying to access index: ' + str(self.list_index + 1))
            future_hex.state[0] = this_world[self.matrix_index][self.list_index + 1].state[0]

        # If its lower right neighbor is pointing up and left, it will point up and left in the future
        if self.matrix_index + 1 < len(this_world):
            future_hex.state[5] = this_world[self.matrix_index + 1][self.list_index].state[5]

        # If its lower left neighbor is pointing up and right, it will point up and right in the future
        cont = self.list_index + 1 < len(this_world[self.matrix_index - 1])
        if self.matrix_index - 1 > 0 & cont:
            print('state 1 check')
            print('length: ' + str(len(this_world[self.matrix_index - 1])))
            print('trying to access index: ' + str(self.list_index + 1))
            print('boolean check: ' + str(self.list_index + 1 < len(this_world[self.matrix_index - 1])))
            print('boolean check 2: ' + str(cont))
            future_hex.state[1] = this_world[self.matrix_index - 1][self.list_index + 1].state[1]

        # If its upper left neighbor is pointing down and right, it will point down and right in the future
        if self.matrix_index - 1 > 0:
            future_hex.state[2] = this_world[self.matrix_index - 1][self.list_index].state[2]

        # If its upper right neighbor is pointing down and left, it will point down and left in the future
        if self.matrix_index + 1 < len(this_world) & self.list_index - 1 > 0:
            future_hex.state[4] = this_world[self.matrix_index + 1][self.list_index - 1].state[4]
        
        '''# Update occupied boolean and color
        if self.state[0] | self.state[1] | self.state[2] | self.state[3] | self.state[4] | self.state[5]:
            self.occupied = True
            # If it is occupied and moving, blue
            self.color = (0, 0, 255)
            # __ print(str(self.matrix_index) + ", " + str(self.list_index) + " switched to blue")    
        elif self.occupied:
            # If it is occupied and not moving, white
            self.color = (255, 255, 255)
            # __ print(str(self.matrix_index) + ", " + str(self.list_index) + " switched to white")    
        else:
            # If it is not occupied, red
            self.color = (255, 0, 0)'''
        
        # Update occupied boolean and color
        if future_hex.state[0] | future_hex.state[1] | future_hex.state[2] | future_hex.state[3] | future_hex.state[4] | future_hex.state[5]:
            future_hex.occupied = True
            # If it is occupied and moving, blue
            future_hex.color = (0, 0, 255)
            # __ print(str(self.matrix_index) + ", " + str(self.list_index) + " switched to blue")    
        elif future_hex.occupied:
            # If it is occupied and not moving, white
            future_hex.color = (255, 255, 255)
            # __ print(str(self.matrix_index) + ", " + str(self.list_index) + " switched to white")    
        else:
            # If it is not occupied, red
            future_hex.color = (255, 0, 0)

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
hex_matrix[0][0].movable = True
hex_matrix[0][0].state[5] = 2
hex_matrix[10][10].movable = True
hex_matrix[10][10].state[0] = 1
hex_matrix[4][7].movable = True
hex_matrix[4][7].state[3] = 3
hex_matrix[6][10].movable = True
hex_matrix[6][10].state[2] = 1

# Create second matrix to alternate with
alt_matrix = hex_matrix_init()

# TODO: Doing the same thing here as for hex_matrix. Is this necessary?
# Update the state of a few hexagons to reflect motion
alt_matrix[0][0].state[5] = 2
alt_matrix[10][10].state[0] = 1
alt_matrix[10][10].occupied = True
alt_matrix[4][7].state[3] = 3
alt_matrix[6][10].state[2] = 1

worlds = [hex_matrix, alt_matrix]

# integer to indicate which world we are currently using
curr_world = 0

run = True
while run:
    this_world = worlds[curr_world]
    next_world = worlds[(curr_world + 1)%2]

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

    # Update to handle movement
    # TODO: Update to handle movement
    for hex_list in this_world:
        for hexagon in hex_list:
            # Copy unmovables into the other world
            if not hexagon.movable:
                next_world[hexagon.matrix_index][hexagon.list_index].movable = False
                next_world[hexagon.matrix_index][hexagon.list_index].state = [0,0,0,0,0,0]
            else:
                # If a hex is movable, update it
                hexagon.update()

    '''# Alternate curr_world between 0 and 1
    curr_world += 1
    curr_world %= 2'''

pygame.quit()

