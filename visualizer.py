import pygame
import time
from board import BoardState, Orientation

# Colors
BG_COLOR = (34, 139, 34)       # Forest Green
HOLE_COLOR = (139, 69, 19)     # Saddle Brown
RABBIT_COLOR = (255, 255, 255) # White
MUSHROOM_COLOR = (220, 20, 60) # Crimson Red
FOX_COLOR = (255, 140, 0)      # Dark Orange
GRID_COLOR = (0, 100, 0)       # Dark Green
TEXT_COLOR = (240, 240, 240)

TILE_SIZE = 100
MARGIN = 50
BOARD_SIZE = TILE_SIZE * 5
ANIMATION_DURATION = 0.4
MOVE_DELAY = 0.2
TOTAL_STEP_TIME = ANIMATION_DURATION + MOVE_DELAY

def get_tile_center(y, x):
    return MARGIN + x * TILE_SIZE + TILE_SIZE // 2, MARGIN + y * TILE_SIZE + TILE_SIZE // 2

def get_tile_rect(y, x):
    return MARGIN + x * TILE_SIZE, MARGIN + y * TILE_SIZE, TILE_SIZE, TILE_SIZE

def draw_board_base(screen):
    screen.fill(BG_COLOR)
    # Draw Grid
    for i in range(6):
        pygame.draw.line(screen, GRID_COLOR, (MARGIN, MARGIN + i * TILE_SIZE), (MARGIN + BOARD_SIZE, MARGIN + i * TILE_SIZE), 2)
        pygame.draw.line(screen, GRID_COLOR, (MARGIN + i * TILE_SIZE, MARGIN), (MARGIN + i * TILE_SIZE, MARGIN + BOARD_SIZE), 2)
    
    # Draw Holes
    hole_radius = int(TILE_SIZE * 0.35)
    for hy, hx in [(0,0), (4,0), (2,2), (0,4), (4,4)]:
        cx, cy = get_tile_center(hy, hx)
        pygame.draw.circle(screen, HOLE_COLOR, (cx, cy), hole_radius)

def draw_pieces(screen, state, moving_info=None, alpha=0.0):
    piece_type, moving_f, moving_t = moving_info if moving_info else (None, None, None)
    
    # Draw Mushrooms
    mushroom_radius = int(TILE_SIZE * 0.3)
    for m in state.setup.mushrooms:
        cx, cy = get_tile_center(m.loc.y, m.loc.x)
        pygame.draw.circle(screen, MUSHROOM_COLOR, (cx, cy), mushroom_radius)
        
    # Draw Foxes
    for fox in state.foxes:
        fy, fx = fox.loc.y, fox.loc.x
        if piece_type == "fox" and (fy, fx) == moving_f:
            # Interpolate position
            curr_y = fy + (moving_t[0] - fy) * alpha
            curr_x = fx + (moving_t[1] - fx) * alpha
        else:
            curr_y, curr_x = fy, fx
            
        px, py = MARGIN + curr_x * TILE_SIZE + 5, MARGIN + curr_y * TILE_SIZE + 5
        if fox.orientation == Orientation.HORIZONTAL:
            pygame.draw.rect(screen, FOX_COLOR, (px, py, TILE_SIZE * 2 - 10, TILE_SIZE - 10), 0, 15)
        else:
            pygame.draw.rect(screen, FOX_COLOR, (px, py, TILE_SIZE - 10, TILE_SIZE * 2 - 10), 0, 15)
            
    # Draw Rabbits
    rabbit_radius = int(TILE_SIZE * 0.25)
    for r in state.rabbits:
        ry, rx = r.loc.y, r.loc.x
        arc_offset = 0
        if piece_type == "rabbit" and (ry, rx) == moving_f:
            # Interpolate position
            curr_y = ry + (moving_t[0] - ry) * alpha
            curr_x = rx + (moving_t[1] - rx) * alpha
            # Calculate jump height (parabolic arc)
            jump_height = TILE_SIZE * 0.6
            arc_offset = jump_height * 4 * alpha * (1 - alpha)
        else:
            curr_y, curr_x = ry, rx
            
        cx, cy = get_tile_center(curr_y, curr_x)
        
        if arc_offset > 0:
            # Draw a simple shadow while jumping
            shadow_radius = int(rabbit_radius * 0.8)
            pygame.draw.circle(screen, (0, 60, 0), (cx, cy), shadow_radius)
            # Shift the rabbit upwards on the screen to simulate height
            cy -= arc_offset
            
        pygame.draw.circle(screen, RABBIT_COLOR, (cx, cy), rabbit_radius)

def run_visualizer(initial_state, solution, autoplay=False, show_controls=True, level_id=None):
    pygame.init()
    W_S = BOARD_SIZE + MARGIN * 2
    screen = pygame.display.set_mode((W_S, W_S + (150 if show_controls else 50)))
    pygame.display.set_caption("Jump In Solver")
    
    move_steps = []
    curr = initial_state
    if solution:
        for move in solution:
            # move is {"piece": "rabbit/fox", "from": (y,x), "to": (y,x)}
            move_steps.append((curr, move))
            curr = curr.do_move(move["piece"], move["from"], move["to"])
    move_steps.append((curr, None))
    
    running, step_idx, anim_start_time, paused, single_step = True, 0, time.time(), not autoplay, False
    clock = pygame.time.Clock()
    
    while running:
        is_final_state = (step_idx == len(move_steps) - 1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN] and is_final_state:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if paused and not is_final_state:
                        paused, single_step, anim_start_time = False, True, time.time()
                elif event.key == pygame.K_RETURN:
                    paused, single_step = not paused, False
                    anim_start_time = time.time()
                elif event.key == pygame.K_RIGHT:
                    step_idx, paused, single_step = min(step_idx + 1, len(move_steps) - 1), True, False
                elif event.key == pygame.K_LEFT:
                    step_idx, paused, single_step = max(step_idx - 1, 0), True, False
                elif event.key == pygame.K_r:
                    step_idx, anim_start_time = 0, time.time()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    
        now = time.time()
        state_before, move = move_steps[step_idx]
        alpha = 0.0
        
        if move and not paused:
            elapsed = now - anim_start_time
            if elapsed >= TOTAL_STEP_TIME:
                if step_idx < len(move_steps) - 1:
                    step_idx += 1
                    anim_start_time += TOTAL_STEP_TIME
                    state_before, move = move_steps[step_idx]
                    elapsed = now - anim_start_time
                    if single_step:
                        paused, single_step = True, False
            
            if move and not paused:
                alpha = min(1.0, elapsed / ANIMATION_DURATION)
                
        # Draw everything
        draw_board_base(screen)
        
        moving_info = None
        if move:
            moving_info = (move["piece"], move["from"], move["to"])
            
        draw_pieces(screen, state_before, moving_info, alpha)
        
        # UI Text
        font = pygame.font.SysFont(None, 24)
        status_text = f"Move {step_idx}/{len(move_steps)-1}"
        if is_final_state and state_before.get_is_finished():
            status_text += " - SOLVED!"
        if paused:
            status_text += " (PAUSED)"
        
        img = font.render(status_text, True, TEXT_COLOR)
        screen.blit(img, (MARGIN, W_S + 10))
        
        if level_id:
            level_font = pygame.font.SysFont(None, 28, bold=True)
            level_img = level_font.render(f"LEVEL: {level_id}", True, TEXT_COLOR)
            screen.blit(level_img, (MARGIN, 10))
            
        if show_controls:
            ctrl_font = pygame.font.SysFont(None, 20)
            controls = [
                "ENTER: Toggle Auto-play",
                "SPACE: Animate next step",
                "RIGHT/LEFT: Jump next/prev",
                "R: Reset to start",
                "ESC: Quit"
            ]
            for i, line in enumerate(controls):
                screen.blit(ctrl_font.render(line, True, (180, 180, 180)), (MARGIN, W_S + 40 + i * 18))
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
