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
            elif char in ['f', 'F']:
                fox_locs[char].append((y, x))
                
    foxes = []
    for char_type in ['f', 'F']:
        locs = fox_locs[char_type]
        used = [False] * len(locs)
        for i in range(len(locs)):
            if used[i]:
                continue
            y1, x1 = locs[i]
            found_pair = False
            # Look for a neighbor to the right or below to form a pair
            for j in range(i + 1, len(locs)):
                if used[j]:
                    continue
                y2, x2 = locs[j]
                # Check adjacency
                if (y1 == y2 and abs(x1 - x2) == 1) or (x1 == x2 and abs(y1 - y2) == 1):
                    used[i] = True
                    used[j] = True
                    if y1 == y2:
                        orientation = Orientation.HORIZONTAL
                        loc = Loc(y1, min(x1, x2))
                    else:
                        orientation = Orientation.VERTICAL
                        loc = Loc(min(y1, y2), x1)
                    foxes.append(Fox(loc, orientation))
                    found_pair = True
                    break
            if not found_pair:
                raise ValueError(f"Unpaired fox character '{char_type}' at ({y1}, {x1})")
        
    setup = BoardSetup(mushrooms)
    return BoardState(setup, rabbits, foxes)

def save_as_text(state: BoardState) -> str:
    grid = np.full((5, 5), ' ')
    
    for m in state.setup.mushrooms:
        grid[m.loc.y, m.loc.x] = 'M'
        
    for r in state.rabbits:
        grid[r.loc.y, r.loc.x] = 'R'
        
    # To handle multiple foxes potentially having the same character type,
    # we assign 'f' and 'F' based on their index in the list.
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
