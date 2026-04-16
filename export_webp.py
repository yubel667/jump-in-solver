import os
import sys
import pygame
from PIL import Image
from board_io import parse_from_text
from solver import solve
import visualizer as vis

# Offscreen rendering
os.environ['SDL_VIDEODRIVER'] = 'dummy'

FPS = 60
ANIM_DUR = vis.ANIMATION_DURATION
WAIT_DUR = vis.MOVE_DELAY + 0.3
SLIDE_FRAMES = int(ANIM_DUR * FPS)
WAIT_FRAMES = int(WAIT_DUR * FPS)

def surface_to_pil(surface):
    raw_str = pygame.image.tostring(surface, "RGB")
    return Image.frombytes("RGB", surface.get_size(), raw_str)

def export_webp(problem_id):
    pygame.init()
    
    # Resolve path
    file_path = f"jump-in-solver/questions/{problem_id}.txt"
    if not os.path.exists(file_path):
        file_path = f"questions/{problem_id}.txt"
        if not os.path.exists(file_path):
             print(f"Error: Question {problem_id} not found.")
             return

    try:
        with open(file_path, 'r') as f:
            content = f.read()
        initial_state = parse_from_text(content)
    except Exception as e:
        print(f"Error loading {problem_id}: {e}")
        return

    print(f"Solving {problem_id}...")
    solution_info = solve(initial_state)
    solution, visited, duration = solution_info
    
    if solution is None:
        print("No solution found.")
        return

    print(f"Solution found in {len(solution)} moves. Generating frames...")

    W_S = vis.BOARD_SIZE + vis.MARGIN * 2
    surface = pygame.Surface((W_S, W_S + 50))
    
    frames = []
    curr_state = initial_state
    
    def render_frame(state, move_info, alpha, step_idx):
        status = f"Move {step_idx}/{len(solution)}"
        if state.get_is_finished(): status += " - SOLVED!"
        vis.draw_board(surface, state, moving_info=move_info, alpha=alpha, level_id=problem_id, status_text=status)
        frames.append(surface_to_pil(surface))

    # 1. Initial pause
    for _ in range(FPS):
        render_frame(curr_state, None, 0.0, 0)

    for move_idx, move in enumerate(solution):
        # 2. Animation frames
        for i in range(SLIDE_FRAMES):
            alpha = i / float(SLIDE_FRAMES)
            render_frame(curr_state, (move["piece"], move["from"], move["to"]), alpha, move_idx)
        
        # Update state
        curr_state = curr_state.do_move(move["piece"], move["from"], move["to"])
        
        # 3. Wait frames
        for _ in range(WAIT_FRAMES):
            render_frame(curr_state, None, 0.0, move_idx + 1)
        
        print(f"  Processed move {move_idx + 1}/{len(solution)}")

    # 4. Final pause
    for _ in range(FPS * 2):
        render_frame(curr_state, None, 0.0, len(solution))

    # Save
    os.makedirs("solutions", exist_ok=True)
    out_path = f"solutions/{problem_id}.webp"
    
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        quality=80,
        method=6
    )
    
    print(f"Exported to {out_path}")
    pygame.quit()

if __name__ == "__main__":
    problem_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    export_webp(problem_id)
