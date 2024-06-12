import time
import copy

class Hex:
   @staticmethod
   def create_coor(x, y):
        # Making hex smaller so that borders will be visible
        return [(x+3, y+3), (x+37, y+3), (x+57, y+35), (x+37, y+67), (x+3, y+67), (x-17, y+35)]


    # Constructor
    # color is an optional parameter with a default value of red
    # moveable is an optional parameter with a default value of true
   def __init__(self, matrix_index, list_index, color=(255, 0, 0), moveable=True, occupied=False):
       self.matrix_index = matrix_index
       self.list_index = list_index

       self.x = 60*matrix_index - 20
       self.y = 35*matrix_index + 70*list_index - 490

       self.coordinates = Hex.create_coor(self.x, self.y)
       
        # TODO: need to make something for occupied vs unoccupied hexes

       self.color = color
       self.movable = moveable
       self.occupied = occupied
       self.state = [0, 0, 0, 0, 0, 0]

       self.init_text()

   def init_text(self):
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
       self.text = font.render(('(' + str(self.matrix_index) + ',' + str(self.list_index) + ')'), True, (0, 255, 0))
        
        # create a rectangular object for the
        # text surface object
       self.textRect = self.text.get_rect()
        
       # set the center of the rectangular object.
       self.textRect.center = (self.x + 20, self.y + 35)
   
   def draw(self, screen):
    if self.occupied == False:
        # If not occupied: white
        self.color = (255, 255, 255)
    elif self.movable == False:
        # If occupied and not movable (wall): dark grey
        self.color = (20, 20, 20)
    elif self.state[0] | self.state[1] | self.state[2] | self.state[3] | self.state[4] | self.state[5]:
       # If moving: blue
       self.color = (0, 0, 255)
    else:
        # If occupied and not moving (but movable): teal
        self.color = (50, 175, 175)
    
    # Draw the hexagon
    pygame.draw.polygon(screen, self.color, self.coordinates)

    # Draw text object displaying axial hex coordiantes
    self.display_surface.blit(self.text, self.textRect)


    
    # returns a list of length six representing the six neighboring hexes of self, with 1 if the hex neighboring in that direction is movable, nonmoving, and occupied
   def check_movables(self): 
        hex_movable = [0, 0, 0, 0, 0, 0]

        # check upper hex (pos 0)
        if self.list_index - 1 > 0:
           hexToCheck = hex_matrix[self.matrix_index][self.list_index - 1]
           if (str(hexToCheck.state) == "[0, 0, 0, 0, 0, 0]") and hexToCheck.movable == True and hexToCheck.occupied == True:
               hex_movable[0] = 1

        # check northeast hex (pos 1)
        if (self.matrix_index + 1 < len(hex_matrix)) and (self.list_index - 1 > 0):
           hexToCheck = hex_matrix[self.matrix_index + 1][self.list_index - 1]
           if (str(hexToCheck.state) == "[0, 0, 0, 0, 0, 0]") and hexToCheck.movable == True and hexToCheck.occupied == True:
               hex_movable[1] = 1

        # check southeast hex (pos 2)
        if self.matrix_index + 1 < len(hex_matrix):
            hexToCheck = hex_matrix[self.matrix_index + 1][self.list_index]
            if (str(hexToCheck.state) == "[0, 0, 0, 0, 0, 0]") and hexToCheck.movable == True and hexToCheck.occupied == True:
               hex_movable[2] = 1

        # check down hex (pos 3)
        if self.list_index + 1 < len(hex_list):
            hexToCheck = hex_matrix[self.matrix_index][self.list_index + 1]
            if (str(hexToCheck.state) == "[0, 0, 0, 0, 0, 0]") and hexToCheck.movable == True and hexToCheck.occupied == True:
               hex_movable[3] = 1

        # check southwest hex (pos 4)
        if (self.matrix_index - 1 > 0) and (self.list_index + 1 < len(hex_list)):
            hexToCheck = hex_matrix[self.matrix_index - 1][self.list_index + 1]
            if (str(hexToCheck.state) == "[0, 0, 0, 0, 0, 0]") and hexToCheck.movable == True and hexToCheck.occupied == True:
               hex_movable[4] = 1

        # check northwest hex (pos 5)
        if self.matrix_index - 1 > 0:
            hexToCheck = hex_matrix[self.matrix_index - 1][self.list_index]
            if (str(hexToCheck.state) == "[0, 0, 0, 0, 0, 0]") and hexToCheck.movable == True and hexToCheck.occupied == True:
               hex_movable[5] = 1

        return hex_movable
   

    # returns a list of length 6 to determine which of the neighbors around self hex are walls
   def check_walls(self):
        hex_walls = [0, 0, 0, 0, 0, 0]

        # check upper hex (pos 0)
        if self.list_index - 1 > 0:
           hexToCheck = hex_matrix[self.matrix_index][self.list_index - 1]
           if (hexToCheck.movable == False) and (hexToCheck.occupied == True):
               hex_walls[0] = 1

         # check northeast hex (pos 1)
        if (self.matrix_index + 1 < len(hex_matrix)) and (self.list_index - 1 > 0):
           hexToCheck = hex_matrix[self.matrix_index + 1][self.list_index - 1]
           if (hexToCheck.movable == False) and (hexToCheck.occupied == True):
               hex_walls[1] = 1

        # check southeast hex (pos 2)
        if self.matrix_index + 1 < len(hex_matrix):
            hexToCheck = hex_matrix[self.matrix_index + 1][self.list_index]
            if (hexToCheck.movable == False) and (hexToCheck.occupied == True):
               hex_walls[2] = 1

        # check down hex (pos 3)
        if self.list_index + 1 < len(hex_list):
            hexToCheck = hex_matrix[self.matrix_index][self.list_index + 1]
            if (hexToCheck.movable == False) and (hexToCheck.occupied == True):
               hex_walls[3] = 1

        # check southwest hex (pos 4)
        if (self.matrix_index - 1 > 0) and (self.list_index + 1 < len(hex_list)):
            hexToCheck = hex_matrix[self.matrix_index - 1][self.list_index + 1]
            if (hexToCheck.movable == False) and (hexToCheck.occupied == True):
               hex_walls[4] = 1

         # check northwest hex (pos 5)
        if self.matrix_index - 1 > 0:
            hexToCheck = hex_matrix[self.matrix_index - 1][self.list_index]
            if (hexToCheck.movable == False) and (hexToCheck.occupied == True):
               hex_walls[5] = 1

        return hex_walls


    #update self hexagon
   def update(self):
        # determine the state of the current hex based on the states of the hexes around it
        future = hex_matrix_new[self.matrix_index][self.list_index]

        future.state = [0,0,0,0,0,0]
        future.occupied = False

        neighbors_movable = self.check_movables()
        neighbors_wall = self.check_walls()

        # If the hex is a wall, it will remain occupied and not movable
        if(hex_matrix[self.matrix_index][self.list_index].movable == False):
            future.movable = False
            future.occupied = True

        # If the hex is currently occupied and not moving, it will still be occupied in the next generation
        if(hex_matrix[self.matrix_index][self.list_index].occupied == True) and (str(hex_matrix[self.matrix_index][self.list_index].state) == "[0, 0, 0, 0, 0, 0]"):
            future.occupied = True

        if self.movable:

            # UPPER NEIGHBOR EFFECTS
            # if my upper (0) neighbor is pointing down (3) then I will move down
            if self.list_index - 1 > 0:
                future.state[3] = hex_matrix[self.matrix_index][self.list_index - 1].state[3]
                if future.state[3] != 0:
                    future.occupied = True
                # if I am moving toward my upper neighbor, and my upper neighbor is occupied but not moving, then I become occupied but not moving
                if(self.state[0] != 0):
                    if neighbors_movable[0] == 1:
                        future.occupied = True
                        future.movable = True
                    elif neighbors_wall[0] == 1:
                        future.occupied = True
                        future.movable = True
                        future.state[0] = 0
                        future.state[3] = 1


            # DOWN NEIGHBOR EFFECTS
            if self.list_index + 1 < len(hex_list):
                future.state[0] = hex_matrix[self.matrix_index][self.list_index + 1].state[0]
                if future.state[0] != 0:
                    future.occupied = True
                # if I am moving down to my lower neighbor and it is occupied but not moving, I become occupied but not moving
                elif (self.state[3] != 0) and (neighbors_movable[3] == 1):
                    future.occupied = True
                    future.movable = True

            # NORTHEAST NEIGHBOR
            if (self.matrix_index + 1 < len(hex_matrix)) and (self.list_index - 1 > 0):
                future.state[4] = hex_matrix[self.matrix_index + 1][self.list_index - 1].state[4]
                if future.state[4] != 0:
                    future.occupied = True
                # if I am moving toward my northeast neighbor and it is movable, I become movable
                elif (self.state[1] != 0) and (neighbors_movable[1] == 1):
                    future.occupied = True
                    future.movable = True

            # NORTHWEST NEIGHBOR
            if self.matrix_index - 1 > 0:
                future.state[2] = hex_matrix[self.matrix_index - 1][self.list_index].state[2]
                if future.state[2] != 0:
                    future.occupied = True
                # if I am moving toward my northwest neighbor and it is movable, I become movable
                elif (self.state[5] != 0) and (neighbors_movable[5] == 1):
                    future.occupied = True
                    future.movable = True

            # SOUTHEAST NEIGHBOR
            if self.matrix_index + 1 < len(hex_matrix):
                future.state[5] = hex_matrix[self.matrix_index + 1][self.list_index].state[5]
                if future.state[5] != 0:
                    future.occupied = True
                elif (self.state[2] != 0) and (neighbors_movable[2] == 1):
                    future.occupied = True
                    future.movable = True

            # SOUTHWEST NEIGHBOR
            if (self.matrix_index - 1 > 0) and (self.list_index + 1 < len(hex_list)):
                future.state[1] = hex_matrix[self.matrix_index - 1][self.list_index + 1].state[1]
                if future.state[1] != 0:
                    future.occupied = True
                elif (self.state[4] != 0) and (neighbors_movable[4] == 1):
                    future.occupied = True
                    future.movable = True



import pygame

pygame.init()

SCREEN_WIDTH = 800

SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Draw Hexagon")

# Create hexagons
hex_matrix = []

for x in range(15):
    hex_list = []
    hex_matrix.append(hex_list)

    for y in range(16):
        myHex = Hex(x, y)
        hex_list.append(myHex)

# create additional matrix
hex_matrix_new = []

for x in range(15):
    hex_list_new = []
    hex_matrix_new.append(hex_list_new)

    for y in range(16):
        myHex = Hex(x, y)
        hex_list_new.append(myHex)

# Update the state of a few hexagons to reflect motion
hex_matrix[10][8].occupied = True
hex_matrix[10][4].occupied = True
# hex_matrix[4][7].occupied = True
# hex_matrix[6][10].occupied = True
# hex_matrix[3][5].occupied = True
hex_matrix[5][6].occupied = True
hex_matrix[7][8].occupied = True
hex_matrix[5][9].occupied = True

hex_matrix[10][8].state[5] = 1
hex_matrix[5][9].state[0] = 1
# hex_matrix[4][7].state[3] = 3
# hex_matrix[6][10].state[2] = 1
# hex_matrix[3][5].state[4] = 1
hex_matrix[5][6].movable = False

run = True
while run:

    # Reset screen
    screen.fill((0, 0, 0))

    # Draw hexagons
    r = 10
    g = 10
    b = 10

    for hex_list in hex_matrix:
        for hexagon in hex_list:
            hexagon.draw(screen)
        
            # polygon rotation tips from: https://stackoverflow.com/questions/75116101/how-to-make-rotate-polygon-on-key-in-pygame

            # draw an arrow on the hex if the hex is moving
            if(str(hexagon.state) != "[0, 0, 0, 0, 0, 0]"):
                #pivot is the center of the hexagon
                pivot = pygame.Vector2(hexagon.x + 20, hexagon.y + 35)
                # set of arrow points should be the vectors from the pivot to the edge points of the arrow
                arrow = [(0, -15), (10, -5), (5, -5), (5, 15), (-5, 15), (-5, -5), (-10, -5)]
                # get arrow by adding all the vectors to the pivot point => allows for easy rotation

                if(hexagon.state[0] != 0):
                    arrow_new = [(pygame.math.Vector2(x, y)) + pivot for x, y in arrow]
                    pygame.draw.polygon(screen, (0, 0, 0), arrow_new)

                if(hexagon.state[1] != 0):
                    arrow_new = [(pygame.math.Vector2(x, y)).rotate(60.0) + pivot for x, y in arrow]
                    pygame.draw.polygon(screen, (0, 0, 0), arrow_new)

                if(hexagon.state[2] != 0):
                    arrow_new = [(pygame.math.Vector2(x, y)).rotate(120.0) + pivot for x, y in arrow]
                    pygame.draw.polygon(screen, (0, 0, 0), arrow_new)

                if(hexagon.state[3] != 0):
                    arrow_new = [(pygame.math.Vector2(x, y)).rotate(180.0) + pivot for x, y in arrow]
                    pygame.draw.polygon(screen, (0, 0, 0), arrow_new)

                if(hexagon.state[4] != 0):
                    arrow_new = [(pygame.math.Vector2(x, y)).rotate(240.0) + pivot for x, y in arrow]
                    pygame.draw.polygon(screen, (0, 0, 0), arrow_new)

                if(hexagon.state[5] != 0):
                    arrow_new = [(pygame.math.Vector2(x, y)).rotate(300.0) + pivot for x, y in arrow]
                    pygame.draw.polygon(screen, (0, 0, 0), arrow_new)


    # Event handler (closing window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

    for hex_list in hex_matrix:
        for hexagon in hex_list:
            hexagon.update()

    # need to use the python deepcopy in order to copy the inner lists of a 2D array
    hex_matrix = copy.deepcopy(hex_matrix_new)
    # hex_matrix = hex_matrix_new.copy()

    # TODO: less janky way of time to slow down the animation
    time.sleep(1)

pygame.quit()

