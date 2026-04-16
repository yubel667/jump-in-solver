import collections
import time
import json
import sys
from board import BoardState, Direction, Rabbit, Fox
from board_io import parse_from_text

def solve(initial_state: BoardState):
    start_time = time.time()
    
    if initial_state.get_is_finished():
        return [], 0, 0.0

    # Queue stores (state, path)
    # Path will store (piece_type, from_loc, to_loc)
    queue = collections.deque([(initial_state, [])])
    visited = {initial_state.get_identifier()}

    while queue:
        curr_state, path = queue.popleft()

        obstacle_map = curr_state.build_obstacle_map()
        
        # Rabbits
        for i, rabbit in enumerate(curr_state.rabbits):
            for direction in list(Direction):
                jump_loc = curr_state.get_rabbit_jump_location(rabbit.loc, direction, obstacle_map)
                if jump_loc:
                    new_rabbits = curr_state.rabbits[:]
                    new_rabbits[i] = type(rabbit)(jump_loc)
                    next_state = BoardState(curr_state.setup, new_rabbits, curr_state.foxes)
                    
                    state_id = next_state.get_identifier()
                    if state_id not in visited:
                        new_path = path + [{"piece": "rabbit", "from": (rabbit.loc.y, rabbit.loc.x), "to": (jump_loc.y, jump_loc.x)}]
                        if next_state.get_is_finished():
                            end_time = time.time()
                            return new_path, len(visited), end_time - start_time
                        
                        visited.add(state_id)
                        queue.append((next_state, new_path))
                        
        # Foxes
        for i, fox in enumerate(curr_state.foxes):
            for direction in list(Direction):
                slide_loc = curr_state.get_fox_slide_location(fox, direction, obstacle_map)
                if slide_loc:
                    new_foxes = curr_state.foxes[:]
                    new_foxes[i] = type(fox)(slide_loc, fox.orientation)
                    next_state = BoardState(curr_state.setup, curr_state.rabbits, new_foxes)
                    
                    state_id = next_state.get_identifier()
                    if state_id not in visited:
                        new_path = path + [{"piece": "fox", "from": (fox.loc.y, fox.loc.x), "to": (slide_loc.y, slide_loc.x)}]
                        if next_state.get_is_finished():
                            end_time = time.time()
                            return new_path, len(visited), end_time - start_time
                        
                        visited.add(state_id)
                        queue.append((next_state, new_path))
    
    end_time = time.time()
    return None, len(visited), end_time - start_time

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 solver.py <question_file>")
        return

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        initial_state = parse_from_text(content)
    except Exception as e:
        print(f"Error loading board: {e}")
        return

    solution, visited_count, duration = solve(initial_state)

    if solution is None:
        print(json.dumps({"error": "No solution found"}))
    else:
        print(json.dumps({
            "solution": solution,
            "visited": visited_count,
            "time": f"{duration:.4f}s"
        }, indent=2))

if __name__ == "__main__":
    main()
