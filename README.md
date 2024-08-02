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
Describe the start state in `initial_state.txt` <br/>
`python hex_tester.py` (or use `python3`, `py`, etc. as required by your operating system and version of Python).

## How to Use
The initial state of the world must be described in `initial_state.txt`. Each identity (moving objects, stationary objects, agents, walls, etc.) must be listed on a new line of `initial_state.txt`, but the order in which they are listed is insubstantial. <br/>

__[describe column, row system]__

__[describe directions 0 through 6]__

A regular (non-agent) moving identity is described using the following syntax: <br/>
`<column> <row> move <COLOR> <direction>` <br/>
For example, `9 6 move MAROON 5` <br/> describes a maroon identity located at (9, 6) moving in direction 5 (upper left). <br/>
Valid color keywords are PINK, RED, ORANGE, YELLOW, GREEN, BLUE, CYAN, PURPLE, MAROON, and BROWN. If an invalid color is provided, the default is grey.

__[describe agents]__ (swap "move" for "agent")<br/>

Goals are described with the following syntax:<br/>
`<column> <row> goal`<br/>

Portals are described as follows:<br/>
`<column 1> <row 1> portal <column 2> <row 2>`,<br/>
where one portal is located at (column 1, row 1) and its pair is located at (column 2, row 2).

## File Contents

Hex_Agents.py -> <br/>
agent_choices.txt -> <br/>
astar_tester.py -> <br/>
hex_tester.py -> <br/>
hex_world.py -> <br/>
initial_state.txt -> <br/>
requirements.txt -> <br/>
search.py -> <br/>
