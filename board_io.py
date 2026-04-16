from board import Loc, Orientation, Mushroom, Rabbit, Fox, BoardSetup, BoardState
import numpy as np

def parse_from_text(text: str) -> BoardState:
    lines = text.strip().split('\n')
    # Filter out border lines if present
    grid_lines = [line for line in lines if line.startswith('|')]
    
    mushrooms = []
    rabbits = []
    fox_locs = {'f': [], 'F': []}
    
    for y, line in enumerate(grid_lines):
        # Strip the | borders
        content = line[1:6]
        for x, char in enumerate(content):
            loc = Loc(y, x)
            if char == 'M':
                mushrooms.append(Mushroom(loc))
            elif char == 'R':
                rabbits.append(Rabbit(loc))
            elif char == 'f':
                fox_locs['f'].append((y, x))
            elif char == 'F':
                fox_locs['F'].append((y, x))
                
    foxes = []
    for key in ['f', 'F']:
        locs = fox_locs[key]
        if not locs:
            continue
        if len(locs) != 2:
            raise ValueError(f"Fox {key} must occupy exactly 2 spaces, found {len(locs)}")
        
        y1, x1 = locs[0]
        y2, x2 = locs[1]
        
        if y1 == y2:
            # Horizontal
            orientation = Orientation.HORIZONTAL
            loc = Loc(y1, min(x1, x2))
        elif x1 == x2:
            # Vertical
            orientation = Orientation.VERTICAL
            loc = Loc(min(y1, y2), x1)
        else:
            raise ValueError(f"Fox {key} spaces are not adjacent horizontally or vertically")
        
        foxes.append(Fox(loc, orientation))
        
    setup = BoardSetup(mushrooms)
    return BoardState(setup, rabbits, foxes)

def save_as_text(state: BoardState) -> str:
    grid = np.full((5, 5), ' ')
    
    for m in state.setup.mushrooms:
        grid[m.loc.y, m.loc.x] = 'M'
        
    for r in state.rabbits:
        grid[r.loc.y, r.loc.x] = 'R'
        
    for i, fox in enumerate(state.foxes):
        char = 'f' if i == 0 else 'F'
        if fox.orientation == Orientation.HORIZONTAL:
            grid[fox.loc.y, fox.loc.x] = char
            grid[fox.loc.y, fox.loc.x + 1] = char
        else:
            grid[fox.loc.y, fox.loc.x] = char
            grid[fox.loc.y + 1, fox.loc.x] = char
            
    res = ["+-----+"]
    for row in grid:
        res.append("|" + "".join(row) + "|")
    res.append("+-----+")
    
    return "\n".join(res)
