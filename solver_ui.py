import sys
import argparse
import os
from board_io import parse_from_text
from solver import solve
from visualizer import run_visualizer

def main():
    parser = argparse.ArgumentParser(description="Jump In Solver Visualizer")
    parser.add_argument("problem_id", nargs="?", default="1", help="ID of the level to solve (e.g. 1)")
    parser.add_argument("--autoplay", action="store_true", help="Start the visualizer in auto-play mode")
    parser.add_argument("--no-controls", action="store_false", dest="show_controls", help="Hide helper control text in UI")
    parser.set_defaults(show_controls=True)
    
    args = parser.parse_args()
    problem_id = args.problem_id
    
    # Try to find the file
    file_path = f"jump-in-solver/questions/{problem_id}.txt"
    if not os.path.exists(file_path):
        # try without prefix
        file_path = f"questions/{problem_id}.txt"
        if not os.path.exists(file_path):
             print(f"Error: Question {problem_id} not found.")
             return

    try:
        print(f"Loading challenge {problem_id}...")
        with open(file_path, 'r') as f:
            content = f.read()
        initial_state = parse_from_text(content)
    except Exception as e:
        print(f"Error parsing board: {e}")
        return

    print("Searching for shortest solution...")
    solution_info = solve(initial_state)
    solution, visited_count, duration = solution_info

    if solution is None:
        print(f"No solution found for this challenge. (Visited {visited_count} states in {duration:.4f}s)")
        run_visualizer(initial_state, None, autoplay=False, show_controls=args.show_controls, level_id=problem_id)
    else:
        print(f"Found solution in {len(solution)} moves.")
        print(f"States visited: {visited_count}")
        print(f"Search time: {duration:.4f}s")
        print("Opening visualizer...")
        run_visualizer(initial_state, solution, autoplay=args.autoplay, show_controls=args.show_controls, level_id=problem_id)

if __name__ == "__main__":
    main()
