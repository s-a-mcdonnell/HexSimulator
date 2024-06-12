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

   def upper_neighbor_is_wall(self):
        # If the upper neighbor does not exist, it cannot be a wall
        if self.list_index - 1 < 0:
            return False

        return not this_world[self.matrix_index][self.list_index - 1].movable
   
   def upper_right_neighbor_is_wall(self):
        # If the upper right neighbor does not exist, it cannot be a wall
        if (self.list_index - 1 < 0) or (self.matrix_index + 1 >= len(this_world)):
            return False
        
        return not this_world[self.matrix_index + 1][self.list_index - 1].movable
   
   def lower_right_neighbor_is_wall(self):
        # If the lower right neighbor does not exist, it cannot be a wall
        if self.matrix_index + 1 >= len(this_world):
            return False
        
        return not this_world[self.matrix_index + 1][self.list_index].movable
   
   def lower_neighbor_is_wall(self):
        # If the lower  neighbor does not exist, it cannot be a wall
        if self.list_index + 1 >= len(this_world[self.matrix_index]):
            return False
        
        return not this_world[self.matrix_index][self.list_index + 1].movable
   
   def lower_left_neighbor_is_wall(self):
        # If the lower left neighbor does not exist, it cannot be a wall
        if (self.matrix_index - 1 < 0) or (self.list_index + 1 >= len(this_world[self.matrix_index - 1])):
            return False

        return not this_world[self.matrix_index - 1][self.list_index + 1].movable
   
   def upper_left_neighbor_is_wall(self):
        # If the upper left neighbor does not exist, it cannot be a wall
        if self.matrix_index - 1 < 0:
            return False

        return not this_world[self.matrix_index - 1][self.list_index].movable

   
    # TODO: Write description
   def update(self):
        # __ print("Updating " + str(self.matrix_index) + ", " + str(self.list_index))

        future_hex = next_world[self.matrix_index][self.list_index]

        # If it has one moving neighbor moving towards it, that neighbor's state becomes its own
        
        # TODO: Condense these conditionals

        future_hex.occupied = False
        # TODO: Does it make sense to reset states as well?
        future_hex.state = [0,0,0,0,0,0]

        if self.list_index - 1 > 0:
            # If its upper neighbor is a wall and it is moving up and to the right, it will move down and to the right
            # TODO: Do I need to check if an unmovable object is occupied?
            # TODO: Add similar statements coping with walls to the conditionals checking the other neighbors (write a function taking advantage of the fact that 2 and 4 are adjacent to 3?)
            if this_world[self.matrix_index][self.list_index - 1].movable:
                
                # Only transfer momentum if the upper right neighbor is not a wall
                if (self.matrix_index + 1 >= len(this_world)) or (this_world[self.matrix_index + 1][self.list_index - 1].movable):

                    if this_world[self.matrix_index][self.list_index - 1].state[3]:
                        # If its upper neighbor is pointing down (and is not a wall), it will point down in the future

                        # TODO: Simplify this to future_hex.state[3] = 1
                        future_hex.state[3] = this_world[self.matrix_index][self.list_index - 1].state[3]

            else:
                if self.state[1]:
                    future_hex.state[2] = 1
    
                if self.state[5]:
                    future_hex.state[4] = 1                

        if self.list_index + 1 < len(this_world[self.matrix_index]):
            # If its lower neighbor is a wall and it is moving down and to the right, it will move up and to the right
            if not this_world[self.matrix_index][self.list_index + 1].movable:
                '''print("Unmovable neighbor found")
                print("I am " + str(self.matrix_index) + ", " + str(self.list_index))
                print("My states are " + str(self.state))'''
                if self.state[2]:
                    future_hex.state[1] = 1
                    '''print("reflected 2 to 1")
                    print("My new states are " + str(future_hex.state))'''

                if self.state[4]:
                    future_hex.state[5] = 1
                    '''print("reflected 4 to 5")'''
            elif this_world[self.matrix_index][self.list_index + 1].state[0]:
                # If its lower neighbor is pointing up, it will point up in the future

                # TODO: Simplify this to future_hex.state[0] = 1
                future_hex.state[0] = this_world[self.matrix_index][self.list_index + 1].state[0]

        # If its lower right neighbor is pointing up and left, it will point up and left in the future
        # TODO: Write case for when the lower right neighbor is a wall and it is moving down (state 3 --> state 4)
        if self.matrix_index + 1 < len(this_world):

            # Unless the upper right neighbor (the upper neighbor of the lower right neighbor) is a wall
            # TODO: Check this exception for the adjacent wall
            # __if (self.list_index - 1 < 0) or (this_world[self.matrix_index + 1][self.list_index - 1].movable):
            if (self.list_index - 1 < 0) or (this_world[self.matrix_index + 1][self.list_index].movable):
                if this_world[self.matrix_index + 1][self.list_index].state[5]:
                    # __ future_hex.state[5] = this_world[self.matrix_index + 1][self.list_index].state[5]
                    future_hex.state[5] = 1
            else:
                # TODO: Adjacent wall case
                print("Reflecting " + str(self.matrix_index) + ", " + str(self.list_index))
                if self.state[3]:
                    future_hex.state[4] = 1
                    print("My new states are " + str(future_hex.state))
                if self.state[1]:
                    future_hex.state[0] = 1
                    print("My new states are " + str(future_hex.state))

        # If its lower left neighbor is pointing up and right, it will point up and right in the future
        # TODO: Write case for when the lower left neighbor is a wall and it is moving down (state 3 --> state 2)
        if (self.matrix_index - 1 > 0) and (self.list_index + 1 < len(this_world[self.matrix_index - 1])):
            # Unless the upper left neighbor (the upper neighbor of the lower left neighbor) is a wall
            # TODO: Check this exception for the adjacent wall
            if this_world[self.matrix_index - 1][self.list_index].movable:
                if this_world[self.matrix_index - 1][self.list_index + 1].state[1]:
                    # TODO: simplify
                    # __ future_hex.state[1] = this_world[self.matrix_index - 1][self.list_index + 1].state[1]
                    future_hex.state[1] = 1
            else:
                if this_world[self.matrix_index - 1][self.list_index + 1].state[1]:
                    print("No transfer of momentum due to adjacent wall")
                    print("I am " + str(self.matrix_index) + ", " + str(self.list_index))


        # If its upper left neighbor is pointing down and right, it will point down and right in the future
        # TODO: Write case for when the upper left neighbor is a wall and it is moving up (state 0 --> state 1)
        if (self.list_index + 1 < len(this_world[self.matrix_index - 1])) and (self.matrix_index - 1 > 0):
            if this_world[self.matrix_index - 1][self.list_index + 1].movable:
                if this_world[self.matrix_index - 1][self.list_index].state[2]:
                    # TODO: simplify
                    future_hex.state[2] = this_world[self.matrix_index - 1][self.list_index].state[2]
            else:
                # TODO: Explain exception for the adjacent wall
                if this_world[self.matrix_index - 1][self.list_index].state[2]:
                    print("No transfer of momentum due to adjacent wall")
                    print("I am " + str(self.matrix_index) + ", " + str(self.list_index))

        # If its upper right neighbor is pointing down and left, it will point down and left in the future
        # TODO: Write case for when the upper right neighbor is a wall and it is moving up (state 0 --> state 5)
        if (self.matrix_index + 1 < len(this_world)) and (self.list_index - 1 > 0):

            # Only transfer momentum if the upper right neighbor is not a wall
            if this_world[self.matrix_index + 1][self.list_index - 1].movable:
                
                # Only transfer momentum if the lower right neighbot (the lower neighbor of the upper right neighbor) is not a wall
                if this_world[self.matrix_index + 1][self.list_index].movable:

                    # Transfer momentum
                    if this_world[self.matrix_index + 1][self.list_index - 1].state[4]:
                        future_hex.state[4] = 1
            else:
                # If the upper right neighbor is a wall, bounce off of it
                if self.state[1]:
                    future_hex.state[0] = 1
                    print("My new states are " + str(future_hex.state))
                '''if self.state[1]:
                    future_hex.state[0] = 1
                    print("My new states are " + str(future_hex.state))'''

            '''if this_world[self.matrix_index + 1][self.list_index].movable:
                if this_world[self.matrix_index + 1][self.list_index - 1].state[4]:
                    # TODO: Simplify
                    future_hex.state[4] = this_world[self.matrix_index + 1][self.list_index - 1].state[4]'''

        # TODO: Handle head-on collisions with walls


        # Update occupied boolean and color
        moving = future_hex.state[0] | future_hex.state[1] | future_hex.state[2] | future_hex.state[3] | future_hex.state[4] | future_hex.state[5]
        if moving:
            future_hex.occupied = True
            # If it is occupied and moving, blue
            future_hex.color = (0, 0, 255)
            print(str(self.matrix_index) + ", " + str(self.list_index) + " occupied and moving")
        elif future_hex.occupied:
            # If it is occupied and not moving, white
            future_hex.color = (255, 255, 255)
            print(str(self.matrix_index) + ", " + str(self.list_index) + " occupied and stationary")    
        else:
            # If it is not occupied, red
            future_hex.color = (255, 0, 0)
            # __ print(str(self.matrix_index) + ", " + str(self.list_index) + " not occupied")    


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
'''hex_matrix[0][0].movable = True
hex_matrix[0][0].state[5] = 2
hex_matrix[10][10].movable = True
hex_matrix[10][10].state[0] = 1
hex_matrix[4][7].movable = True
hex_matrix[4][7].state[3] = 3
hex_matrix[6][10].movable = True
hex_matrix[6][10].state[2] = 1'''

'''# Head-on collision test (vertical)
hex_matrix[5][6].state[3] = 1
hex_matrix[5][11].state[0] = 1'''

'''# Head-on collision test (angles 2 and 5)
hex_matrix[4][7].state[2] = 1
hex_matrix[8][7].state[5] = 1'''

'''# Head-on collision test (angles 1 and 4)
hex_matrix[3][10].state[1] = 1
hex_matrix[7][6].state[4] = 1'''


# Diagonal collision test (angles 1 and 2)
'''hex_matrix[3][7].state[2] = 1
hex_matrix[3][10].state[1] = 1'''

'''# Diagonal collision test (angles 2 and 3)
hex_matrix[4][7].state[2] = 1
hex_matrix[6][5].state[3] = 1'''

'''# Diagonal collision test (angles 3 and 4)
hex_matrix[5][5].state[3] = 1
hex_matrix[8][5].state[4] = 1'''

# Create second matrix to alternate with
alt_matrix = hex_matrix_init()

# TODO: If there are any unmovable hexes, copy them over

'''# Adjacent wall bounce test (upper wall from the left)
hex_matrix[5][6].movable = False
hex_matrix[5][6].occupied = True
alt_matrix[5][6].movable = False
alt_matrix[5][6].occupied = True
hex_matrix[2][10].state[1] = 1'''

'''# Adjacent wall bounce test (upper wall from the right)
hex_matrix[5][6].movable = False
hex_matrix[5][6].occupied = True
alt_matrix[5][6].movable = False
alt_matrix[5][6].occupied = True
hex_matrix[8][7].state[5] = 1'''

'''# Adjacent wall bounce test (lower wall from the left)
hex_matrix[5][9].movable = False
hex_matrix[5][9].occupied = True
alt_matrix[5][9].movable = False
alt_matrix[5][8].occupied = True
hex_matrix[2][8].state[2] = 1'''

'''# Adjacent wall bounce test (lower wall from the right)
hex_matrix[5][9].movable = False
hex_matrix[5][9].occupied = True
alt_matrix[5][9].movable = False
alt_matrix[5][8].occupied = True
hex_matrix[9][4].state[4] = 1'''

'''# Adjacent wall bounce test (right wall from above)
hex_matrix[5][9].movable = False
hex_matrix[5][9].occupied = True
alt_matrix[5][9].movable = False
alt_matrix[5][8].occupied = True
hex_matrix[4][5].state[3] = 1'''

# Adjacent wall bounce test (right wall from lower left)
hex_matrix[5][9].movable = False
hex_matrix[5][9].occupied = True
alt_matrix[5][9].movable = False
alt_matrix[5][8].occupied = True
hex_matrix[1][12].state[1] = 1
# __ head-on
# __ hex_matrix[5][11].state[0] = 1


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
                # TODO: If everything is set up right initially, this shouldn't be necessary
                next_world[hexagon.matrix_index][hexagon.list_index].occupied = True
                next_world[hexagon.matrix_index][hexagon.list_index].movable = False
                # __ white for occupied and not moving
                next_world[hexagon.matrix_index][hexagon.list_index].color = (255, 255, 255)
                next_world[hexagon.matrix_index][hexagon.list_index].state = [0,0,0,0,0,0]
            else:
                # If a hex is movable, update it
                hexagon.update()

    # Alternate curr_world between 0 and 1
    curr_world += 1
    curr_world %= 2

    # TODO: Do this more elegantly
    # Slow the whole thing down
    for i in range(10000000):
        i += 1

pygame.quit()

