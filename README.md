# HexWorld: A Discrete Hexagonal 2-D Physics Simulator

## Summary
HexWorld is a discrete and deterministic 2-D hexagonal physics simulator in which any hex can move in one of six directions across the hexagonal grid. <br/>
<br/>
HexWorld was created by Skyler McDonnell (@s-a-mcdonnell), Allison Klingler (@amklinglerr), Nahia Pino (@NahiaP), Richa D'Mello(@RichaDMello), and Crawford Dawson (@ddawson97) as a part of the Summer Undergraduate Research Fellowship (SURF) 2024 at Amherst College, under Professor Scott Alfeld.
The implementation of the A* Search algorithm for hex agents was done by Nahia and Richa.

## How to Install/Run
To install dependencies: <br/>
`pip install -r requirements.txt` <br/>

To run the simulation: <br/>
Describe the start state in `initial_state.txt`. <br/>
Run either `python hex_tester.py`or `python astar_tester.py` (or use `python3`, `py`, etc. as required by your operating system and version of Python).<br/>
If run with `hex_tester.py`, all agents will be keyboard agents (controlled by the user). If run using `astar_tester.py`, all agents will operate autonomously according to the A* search algorithm.

## How to Use
The initial state of the world must be described in `initial_state.txt`. Each identity (moving objects, stationary objects, agents, walls, etc.) must be listed on a new line of `initial_state.txt`, but the order in which they are listed is insubstantial. <br/>

There are a few things that will be helpful to know when describing an initial state.<br/>

### Grid Layout

Locations in HexWorld are described using axial coordiantes, meaning locations are given in (column, row) pairs, with (0, 0) being the upper left corner.<br/>
Columns run vertically (from top to bottom), and rows run diagonally from upper left to lower right. The following diagram shows the coordinates of six hexes relative to their neighbor (a, b).<br/>

![Axial Coordinates Diagram](https://github.com/user-attachments/assets/40e0914d-c927-47d9-afba-3eb113ffb882)

For more information on axial coordinates, see [Red Blob Games](https://www.redblobgames.com/grids/hexagons/#:~:text=Axial%20coordinates).

### Directions of Motion
In HexWorld, an identity can either be stationary or moving in one of six directions. These six directions are labelled with the integers 0 through 5, moving clockwise, starting from the top, as shown in the following diagram. <br/>

![HexWorld Directions Diagram Mini](https://github.com/user-attachments/assets/c7b64bcd-9208-4e76-b61d-048874a3facb)



### Describing Identities

A regular (non-agent) moving identity is described using the following syntax: <br/>
`<column> <row> move <COLOR> <direction>` <br/>
For example, `9 6 move MAROON 5` <br/> describes a maroon identity located at (9, 6) moving in direction 5 (upper left). <br/>
Valid color keywords are PINK, RED, ORANGE, YELLOW, GREEN, BLUE, CYAN, PURPLE, MAROON, and BROWN. If an invalid color is provided, the default is grey.<br/>

Agents, which are able to influence their own movement, are described with very similar syntax.<br/>
`<column> <row> agent <COLOR>`<br/>

Goals are described with the following syntax:<br/>
`<column> <row> goal`<br/>

Portals are described as follows:<br/>
`<column 1> <row 1> portal <column 2> <row 2>`,<br/>
where one portal is located at (column 1, row 1) and its pair is located at (column 2, row 2).

## File Contents

`Hex_Agents.py` -> defines the agent class, as well as two subclasses `Keyboard_Agent` and `A_Star_Agent` <br/>
`astar_tester.py` -> A version of `hex_tester.py` that includes search elements and allows the user to test A* with a text file input world state<br/>
`hex_tester.py` -> Executes World.run() from `hex_world.py`. Agents can be put in hex_tester, but they are keyboard agents instead of A Star agents <br/>
`hex_world.py` -> Includes `Ident`, `Hex`, and `World` classes. This is the main part of the code that handles HexWorld <br/>
`initial_state.txt` -> Text file that determines the initial state of the world, ie, what hexes are in what spaces in the grid <br/>
`requirements.txt` -> The required Python packages in a text file for ease of pip installation <br/>
`search.py` -> Establishes the Search Problem, and various heuristics, and `Solution` class in order to run A*<br/>
