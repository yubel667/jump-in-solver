import pygame
import sys
import os
import time
from board import Loc, Orientation, Mushroom, Rabbit, Fox, BoardSetup, BoardState
import board_io
import visualizer as vis

# UI Constants
SIDEBAR_WIDTH = 250
EDITOR_WIDTH = vis.BOARD_SIZE + vis.MARGIN * 2
WINDOW_WIDTH = EDITOR_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = vis.BOARD_SIZE + vis.MARGIN * 2 + 50

class LevelEditor:
    def __init__(self, problem_id):
        self.problem_id = problem_id
        # Try to find the file in multiple locations
        self.file_path = f"questions/{problem_id}.txt"
        if not os.path.exists(self.file_path):
            alt_path = f"jump-in-solver/questions/{problem_id}.txt"
            if os.path.exists(alt_path):
                self.file_path = alt_path
        
        # Piece Pool: 4 Rabbits, 2 Foxes, 3 Mushrooms
        self.pool = []
        for _ in range(4): self.pool.append({'type': 'rabbit', 'loc': None})
        for _ in range(2): self.pool.append({'type': 'fox', 'loc': None, 'orientation': Orientation.HORIZONTAL})
        for _ in range(3): self.pool.append({'type': 'mushroom', 'loc': None})
        
        self.dragging_idx = None
        self.offset_x = 0
        self.offset_y = 0
        
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    content = f.read()
                state = board_io.parse_from_text(content)
                
                # Assign pieces to pool
                r_idx, f_idx, m_idx = 0, 4, 6
                for r in state.rabbits:
                    if r_idx < 4:
                        self.pool[r_idx]['loc'] = (r.loc.y, r.loc.x)
                        r_idx += 1
                for f in state.foxes:
                    if f_idx < 6:
                        self.pool[f_idx]['loc'] = (f.loc.y, f.loc.x)
                        self.pool[f_idx]['orientation'] = f.orientation
                        f_idx += 1
                for m in state.setup.mushrooms:
                    if m_idx < 9:
                        self.pool[m_idx]['loc'] = (m.loc.y, m.loc.x)
                        m_idx += 1
            except Exception as e:
                print(f"Error loading level: {e}")

    def get_piece_sidebar_pos(self, idx):
        # 3 columns, 3 rows
        col = idx % 3
        row = idx // 3
        return EDITOR_WIDTH + 30 + col * 70, 80 + row * 100

    def get_occupied_cells(self, piece):
        if piece['loc'] is None:
            return []
        y, x = piece['loc']
        if piece['type'] == 'fox':
            if piece['orientation'] == Orientation.HORIZONTAL:
                return [(y, x), (y, x + 1)]
            else:
                return [(y, x), (y + 1, x)]
        return [(y, x)]

    def check_valid(self):
        all_cells = {}
        for i, p in enumerate(self.pool):
            cells = self.get_occupied_cells(p)
            for cell in cells:
                if not (0 <= cell[0] < 5 and 0 <= cell[1] < 5):
                    return False, f"Piece {i+1} out of bounds"
                if cell in all_cells:
                    return False, f"Collision at {cell}"
                all_cells[cell] = i
        
        rabbit_count = sum(1 for p in self.pool if p['type'] == 'rabbit' and p['loc'] is not None)
        if rabbit_count == 0:
            return False, "Add at least one rabbit"
            
        return True, "Ready to save (S)"

    def save(self):
        valid, msg = self.check_valid()
        if not valid:
            return False, f"Cannot Save: {msg}"
        
        mushrooms = []
        rabbits = []
        foxes = []
        
        for p in self.pool:
            if p['loc'] is None: continue
            loc = Loc(p['loc'][0], p['loc'][1])
            if p['type'] == 'rabbit':
                rabbits.append(Rabbit(loc))
            elif p['type'] == 'fox':
                foxes.append(Fox(loc, p['orientation']))
            elif p['type'] == 'mushroom':
                mushrooms.append(Mushroom(loc))
                
        state = BoardState(BoardSetup(mushrooms), rabbits, foxes)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            f.write(board_io.save_as_text(state))
        return True, "Level saved!"

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"Jump In Level Editor - {self.problem_id}")
        clock = pygame.time.Clock()
        
        status_msg = ""
        status_color = (255, 255, 255)
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        # Check sidebar
                        for i in range(len(self.pool)):
                            sx, sy = self.get_piece_sidebar_pos(i)
                            if pygame.Rect(sx, sy, 60, 60).collidepoint(mouse_pos):
                                self.dragging_idx = i
                                self.pool[i]['loc'] = None # Remove from board while dragging
                                break
                        # Check board
                        if self.dragging_idx is None and mouse_pos[0] < EDITOR_WIDTH:
                            for i, p in enumerate(self.pool):
                                if p['loc'] is not None:
                                    cells = self.get_occupied_cells(p)
                                    for cy, cx in cells:
                                        rect = pygame.Rect(vis.MARGIN + cx * vis.TILE_SIZE, vis.MARGIN + cy * vis.TILE_SIZE, vis.TILE_SIZE, vis.TILE_SIZE)
                                        if rect.collidepoint(mouse_pos):
                                            self.dragging_idx = i
                                            p['loc'] = None
                                            break
                                    if self.dragging_idx is not None: break
                    elif event.button == 3: # Right click to rotate or remove
                        if mouse_pos[0] < EDITOR_WIDTH:
                            for i, p in enumerate(self.pool):
                                if p['loc'] is not None:
                                    cells = self.get_occupied_cells(p)
                                    for cy, cx in cells:
                                        rect = pygame.Rect(vis.MARGIN + cx * vis.TILE_SIZE, vis.MARGIN + cy * vis.TILE_SIZE, vis.TILE_SIZE, vis.TILE_SIZE)
                                        if rect.collidepoint(mouse_pos):
                                            if p['type'] == 'fox':
                                                p['orientation'] = Orientation.VERTICAL if p['orientation'] == Orientation.HORIZONTAL else Orientation.HORIZONTAL
                                            else:
                                                p['loc'] = None
                                            break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging_idx is not None:
                        if mouse_pos[0] < EDITOR_WIDTH:
                            # Snap to grid
                            grid_x = (mouse_pos[0] - vis.MARGIN) // vis.TILE_SIZE
                            grid_y = (mouse_pos[1] - vis.MARGIN) // vis.TILE_SIZE
                            if 0 <= grid_x < 5 and 0 <= grid_y < 5:
                                self.pool[self.dragging_idx]['loc'] = (grid_y, grid_x)
                        self.dragging_idx = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        success, msg = self.save()
                        status_msg = msg
                        status_color = (0, 255, 0) if success else (255, 0, 0)
                        if success:
                            pygame.display.flip()
                            time.sleep(0.5) # briefly show success message
                            pygame.quit()
                            return
                    elif event.key == pygame.K_r and self.dragging_idx is not None:
                        p = self.pool[self.dragging_idx]
                        if p['type'] == 'fox':
                            p['orientation'] = Orientation.VERTICAL if p['orientation'] == Orientation.HORIZONTAL else Orientation.HORIZONTAL
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

            # Drawing
            vis.draw_board_base(screen)
            pygame.draw.rect(screen, (40, 40, 40), (EDITOR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
            
            # Draw sidebar pieces
            for i, p in enumerate(self.pool):
                sx, sy = self.get_piece_sidebar_pos(i)
                color = (100, 100, 100) if p['loc'] is not None else (200, 200, 200)
                pygame.draw.rect(screen, color, (sx, sy, 60, 60), 2)
                
                # Miniature drawing
                center = (sx + 30, sy + 30)
                if p['type'] == 'rabbit':
                    pygame.draw.circle(screen, vis.RABBIT_COLOR, center, 15)
                    pygame.draw.circle(screen, (0, 0, 0), center, 15, 1)
                elif p['type'] == 'mushroom':
                    pygame.draw.circle(screen, vis.MUSHROOM_COLOR, center, 18)
                elif p['type'] == 'fox':
                    if p['orientation'] == Orientation.HORIZONTAL:
                        pygame.draw.rect(screen, vis.FOX_COLOR, (sx + 10, sy + 20, 40, 20), 0, 5)
                    else:
                        pygame.draw.rect(screen, vis.FOX_COLOR, (sx + 20, sy + 10, 20, 40), 0, 5)

            # Draw placed pieces
            for i, p in enumerate(self.pool):
                if p['loc'] is not None and self.dragging_idx != i:
                    y, x = p['loc']
                    cx, cy = vis.get_tile_center(y, x)
                    if p['type'] == 'rabbit':
                        pygame.draw.circle(screen, vis.RABBIT_COLOR, (cx, cy), int(vis.TILE_SIZE * 0.25))
                        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), int(vis.TILE_SIZE * 0.25), 1)
                    elif p['type'] == 'mushroom':
                        pygame.draw.circle(screen, vis.MUSHROOM_COLOR, (cx, cy), int(vis.TILE_SIZE * 0.3))
                    elif p['type'] == 'fox':
                        px, py = vis.MARGIN + x * vis.TILE_SIZE + 5, vis.MARGIN + y * vis.TILE_SIZE + 5
                        if p['orientation'] == Orientation.HORIZONTAL:
                            pygame.draw.rect(screen, vis.FOX_COLOR, (px, py, vis.TILE_SIZE * 2 - 10, vis.TILE_SIZE - 10), 0, 15)
                        else:
                            pygame.draw.rect(screen, vis.FOX_COLOR, (px, py, vis.TILE_SIZE - 10, vis.TILE_SIZE * 2 - 10), 0, 15)

            # Draw dragging piece
            if self.dragging_idx is not None:
                p = self.pool[self.dragging_idx]
                if p['type'] == 'rabbit':
                    pygame.draw.circle(screen, vis.RABBIT_COLOR, mouse_pos, int(vis.TILE_SIZE * 0.25))
                    pygame.draw.circle(screen, (0, 0, 0), mouse_pos, int(vis.TILE_SIZE * 0.25), 1)
                elif p['type'] == 'mushroom':
                    pygame.draw.circle(screen, vis.MUSHROOM_COLOR, mouse_pos, int(vis.TILE_SIZE * 0.3))
                elif p['type'] == 'fox':
                    if p['orientation'] == Orientation.HORIZONTAL:
                        pygame.draw.rect(screen, vis.FOX_COLOR, (mouse_pos[0] - vis.TILE_SIZE//2, mouse_pos[1] - vis.TILE_SIZE//2, vis.TILE_SIZE * 2 - 10, vis.TILE_SIZE - 10), 0, 15)
                    else:
                        pygame.draw.rect(screen, vis.FOX_COLOR, (mouse_pos[0] - vis.TILE_SIZE//2, mouse_pos[1] - vis.TILE_SIZE//2, vis.TILE_SIZE - 10, vis.TILE_SIZE * 2 - 10), 0, 15)

            # UI Text
            font = pygame.font.SysFont(None, 24)
            valid, msg = self.check_valid()
            if status_msg:
                display_msg, color = status_msg, status_color
            else:
                display_msg, color = msg, ((0, 255, 0) if valid else (200, 200, 200))
            
            img = font.render(display_msg, True, color)
            screen.blit(img, (vis.MARGIN, vis.BOARD_SIZE + vis.MARGIN + 10))
            
            ctrl_font = pygame.font.SysFont(None, 20)
            instructions = [
                f"Editing: {self.problem_id}",
                "S: Save",
                "R: Rotate dragging fox",
                "Right-Click: Rotate/Remove",
                "ESC: Quit"
            ]
            for i, line in enumerate(instructions):
                screen.blit(ctrl_font.render(line, True, (180, 180, 180)), (EDITOR_WIDTH + 20, WINDOW_HEIGHT - 120 + i * 20))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    problem_id = sys.argv[1] if len(sys.argv) > 1 else "new_level"
    LevelEditor(problem_id).run()
