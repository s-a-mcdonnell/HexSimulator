from draw_hexagon import Hex
from draw_hexagon import World

myWorld = World()

# Update the state of a few hexagons to reflect motion (test cases)
myWorld.hex_matrix[10][4].occupied = True

myWorld.hex_matrix[10][8].make_move(5)
myWorld.hex_matrix[2][8].make_move(5)

myWorld.hex_matrix[7][7].make_move(3)
myWorld.hex_matrix[7][6].make_move(3)

myWorld.hex_matrix[7][9].make_wall()
myWorld.hex_matrix[7][8].make_wall()

myWorld.run_simulation()
