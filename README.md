# Jump In Solver

A BFS-based solver and visualizer for the "Jump In" puzzle game by SmartGames.

## Level Mapping & Naming Convention

The `questions/` folder contains two sets of levels:

- **Standard Levels (`01.txt` - `60.txt`)**: These correspond to the 60 levels found in the original regular version of the game.
    - Note: For levels that differ between the Regular and XL versions (e.g., adding a 4th rabbit), the XL variant is used but kept under the standard Normal ID for easier reference.
- **XL Expansion Levels (`eXX.txt`)**: These are the additional 40 levels introduced in the XL version, prefixed with `e` followed by their original XL sequence number (e.g., `e25.txt`, `e100.txt`).

## How to Use

### Solver & Visualizer
To solve a level and visualize the solution:
```bash
./edit_and_solve.sh <level_id>
```
Example: `./edit_and_solve.sh 22` or `./edit_and_solve.sh e25`

### Level Editor
To create or edit a level:
```bash
python3 level_editor.py <level_id>
```
