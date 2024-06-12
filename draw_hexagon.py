import numpy as np
col1 = (120, 0, 120)
col2 = (0, 150, 150)
col3 = (100, 140, 10)
class Hex:
   
    @staticmethod
    def create_coor(x, y):
        # __ x-=40
        # __ y-=490
        # __ return [(x, y), (x+40, y), (x+60, y+35), (x+40, y+70), (x, y+70), (x-20, y+35)]
        # Making hex smaller so that borders will be visible
        return [(x+3, y+3), (x+37, y+3), (x+57, y+35), (x+37, y+67), (x+3, y+67), (x-17, y+35)]

    
    # Constructor
    # color is an optional parameter with a default value of red
    # moveable is an optional parameter with a default value of true
    def __init__(self, matrix_index, list_index, color=col1, moveable=True):
        self.matrix_index = matrix_index
        self.list_index = list_index

        self.x = 60*matrix_index - 20
        self.y = 35*matrix_index + 70*list_index - 490

        self.coordinates = Hex.create_coor(self.x, self.y)
        #self.button = Hex.makeButton(self.x, self.y)
        self.color = color
        self.movable = moveable
        self.state = [0, 0, 0, 0, 0, 0] # top, top right, bottom right, bottom, bottom left, top left

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


    def is_point_in_triangle(self, px, py, ax, ay, bx, by, cx, cy):
        # Compute vectors
        v0x, v0y = cx - ax, cy - ay
        v1x, v1y = bx - ax, by - ay
        v2x, v2y = px - ax, py - ay

        # Compute dot products
        dot00 = v0x * v0x + v0y * v0y
        dot01 = v0x * v1x + v0y * v1y
        dot02 = v0x * v2x + v0y * v2y
        dot11 = v1x * v1x + v1y * v1y
        dot12 = v1x * v2x + v1y * v2y

        # Compute barycentric coordinates
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom

        # Check if point is in triangle
        return (u >= 0) and (v >= 0) and (u + v <= 1)

    # To check whether a coordinate is in the hexagon.
    def is_within_hexagon(self, px, py, vertices):
        for i in range(len(vertices)):
            ax, ay = vertices[i]
            bx, by = vertices[(i + 1) % len(vertices)]
            cx, cy = vertices[(i + 2) % len(vertices)]
            if self.is_point_in_triangle(px, py, ax, ay, bx, by, cx, cy):
                return True
        return False

    def draw(self, screen):
        if self.state[0] | self.state[1] | self.state[2] | self.state[3] | self.state[4] | self.state[5]:
            self.color = col1
        else:
            self.color = col2
        
        # Draw the hexagon
        pygame.draw.polygon(screen, self.color, self.coordinates)

        # Draw text object displaying axial hex coordinates
        self.display_surface.blit(self.text, self.textRect)

import pygame

pygame.init()

SCREEN_WIDTH = 1000

SCREEN_HEIGHT = 650

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Draw Hexagon")




# Create hexagons
hex_matrix = []

for x in range(17):
    hex_list = []
    hex_matrix.append(hex_list)

    for y in range(17):
        myHex = Hex(x, y)
        hex_list.append(myHex)

# Update the state of a few hexagons to reflect motion
# __ hex_matrix[1][1].state[0] = 1
# __ hex_matrix[2][3].state[4] = 1
# __ hex_matrix[5][2].state[2] = 1
hex_matrix[10][10].state[0] = 1
#hex_matrix[4][7].state[3] = 3
# __ hex_matrix[8][12].state[4] = 1
#hex_matrix[6][10].state[2] = 1
print('Events: ', pygame.event)
run = True
col3 = (10, 120, 10)
while run:
    # Reset screen
    screen.fill((0, 0, 0))

    # Draw hexagons
    r = 10
    g = 10
    b = 10
    mouse = pygame.mouse.get_pos()
    for hex_list in hex_matrix:
        for hexagon in hex_list:
            # If mouse is on hex, color it differently
            if hexagon.is_within_hexagon(mouse[0], mouse[1], hexagon.coordinates): 
                pygame.draw.polygon(screen, col3, hexagon.coordinates)
            else:
                hexagon.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
         


    pygame.display.update()

pygame.quit()

## making sure I remember how to commit

