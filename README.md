# Jump In' Solver

An automated solver and graphical interface for the **"Jump In'"** puzzle by **SmartGames**. (I highly recommend buying a physical copy!)

## About the project

This is a "vibe coding" project born from a love for sequential movement puzzles. The project includes a complete engine to model the board, an optimized BFS solver to find the shortest paths, and a polished Pygame UI to visualize the solutions with smooth jumping animations.

Currently, this project is considered complete as all 100 levels (Standard + XL expansion) are included and solved.

You can find all questions (in ASCII format) in the `questions/` folder and animated solutions in the `solutions/` folder.

Below is a sample solution webp for the first puzzle.

![Level 01 Solution](solutions/1.webp)

## Rules & Useful links
Click the image (YouTube link) to get an overview of the rules.
[![Instructions](https://img.youtube.com/vi/R3LqFv-YlIk/0.jpg)](https://www.youtube.com/watch?v=R3LqFv-YlIk)

Here's the designer's webpage introduction to the game:
https://www.smartgames.eu/uk/compact-games/jump-in

Due to copyright, I will not show any instruction or booklet, but you can download them for free here if you are interested:
https://www.smartgames.eu/uk/compact-games/jump-in#downloads

# == Everything below is generated ==

## Project Overview

This project provides a complete suite of tools to model, solve, and visualize the Jump In' sequential movement puzzle. It includes an optimized solver, a graphical user interface for playback, an interactive level editor, and batch export capabilities for generating animations.

## Level Mapping & Naming Convention

The `questions/` folder contains two sets of levels:

- **Standard Levels (`01.txt` - `60.txt`)**: These correspond to the 60 levels found in the original version.
- **XL Expansion Levels (`eXX.txt`)**: These are the additional 40 levels introduced in the XL version, prefixed with `e` followed by their original XL sequence number (e.g., `e25.txt`, `e100.txt`).

## Executables & Commands

### 1. Solver & Visualizer (`solver_ui.py`)
Finds the shortest sequence of moves and launches the graphical interface.
- **Run with manual control:** `python3 solver_ui.py 22`
- **Run with Autoplay:** `python3 solver_ui.py 22 --autoplay`

### 2. Level Editor (`level_editor.py`)
Create or modify puzzle levels using a mouse-driven interface.
- **Usage:** `python3 level_editor.py 01`
- **Controls:** 
  - **Left Click:** Drag pieces from the sidebar or move them on the grid.
  - **Right Click / 'R':** Rotate a dragging fox or remove a piece.
  - **'S':** Save to `questions/XX.txt` and exit.
  - **ESC:** Quit without saving.

### 3. Edit and Solve Script (`edit_and_solve.sh`)
Streamlined workflow to edit a level and immediately see its solution.
- **Usage:** `./edit_and_solve.sh 22`

### 4. WebP Exporter (`export_webp.py`)
Renders a solution path into an optimized animated WebP file.
- **Usage:** `python3 export_webp.py 01`
- **Output:** Saved to `solutions/01.webp`.

### 5. Batch Exporter (`batch_export.py`)
Automatically exports all missing solutions in parallel.
- **Usage:** `python3 batch_export.py -p 10`
- **Flag:** `-p` sets the level of parallelism (default: 10).

## Core Components

- **`board.py`**: The underlying engine that handles piece movement, boundary checks, and obstacle mapping.
- **`board_io.py`**: Handles serialization and deserialization of board states to/from ASCII text.
- **`visualizer.py`**: A shared rendering module using Pygame for smooth animations and consistent visuals.
- **`solver.py`**: The BFS search engine that calculates the shortest path to reach the goal state.

## Technical Highlights
- **Optimized BFS**: Efficient state-space search using unique identifiers for deduplication.
- **Parabolic Jump Animation**: Rabbits follow a curved arc and cast a shadow while jumping to simulate height.
- **Smart Pairing Logic**: I/O parser handles complex fox configurations (like adjacent same-type foxes) automatically.
- **Headless Rendering**: WebP exporter supports off-screen rendering for automated batch processing.
