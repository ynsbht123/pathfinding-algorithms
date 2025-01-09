import pygame
import heapq
import sys
import time
from collections import deque
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 700, 700
ROWS, COLS = 20, 20
TILE_SIZE = WIDTH // COLS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Initialize grid
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]


difficulty = 'normal'  # Start with normal (BFS)

# Directions for movement
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

def heuristic(a, b):
    """Manhattan distance heuristic for A*."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def is_valid_move(nx, ny, visited):
    """Check if the move is valid (within bounds and not blocked)."""
    return 0 <= nx < ROWS and 0 <= ny < COLS and grid[nx][ny] != -1 and (nx, ny) not in visited


def search_path_bfs(start_x, start_y, end_x, end_y, obstacles):
    start_time = time.time()

    frontier = deque([(start_x, start_y)])
    visited = set()  
    visited.add((start_x, start_y))
    parent = {}
    path_found = False

    while frontier:
        x, y = frontier.popleft()

        if (x, y) == (end_x, end_y):  
            path_found = True
            break

        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in visited and is_valid_move(nx, ny, visited):
                visited.add((nx, ny))
                frontier.append((nx, ny))
                parent[(nx, ny)] = (x, y)
    end_time = time.time()
    elapsed_time =float(end_time - start_time)
    return parent, path_found, elapsed_time

def a_star(start, goal):
    """Complete A* algorithm implementation."""
    start_time = time.time()
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {(r, c): float('inf') for r in range(ROWS) for c in range(COLS)}
    f_score = {(r, c): float('inf') for r in range(ROWS) for c in range(COLS)}
    searched = set()  

    g_score[start] = 0
    f_score[start] = heuristic(start, goal)

    while open_set:
        _, current = heapq.heappop(open_set)
        searched.add(current)  

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1], g_score, f_score, came_from, searched

        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS and grid[neighbor[0]][neighbor[1]] != -1:
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
    end_time = time.time()

    elapsed_time = float(end_time - start_time)

    return path, g_score, f_score, searched, elapsed_time

def draw_grid(win):
    """Draw the grid and its current state."""
    font = pygame.font.SysFont(None, 20)
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE
            if grid[row][col] == -1:
                color = BLACK
            elif (row, col) == start:
                color = GREEN
            elif (row, col) == goal:
                color = RED
            pygame.draw.rect(win, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(win, GRAY, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

            

def draw_path(win, path):
    """Draw path with gradient colors."""
    if path is None:
        return
    for i, (row, col) in enumerate(path):
        if (row, col) != start and (row, col) != goal:
            intensity = int(255 * (i / len(path)))
            pygame.draw.rect(win, (0, intensity, 255 - intensity), 
                             (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))




def draw_instructions(win):
    """Display game instructions."""
    instructions = [
        "Instructions:",
        "1. Left-click to set obstacles.",
        "2. Right-click to remove obstacles.",
        "3. Press SPACE to run pathfinding.",
        "4. Press TAB to switch algorithms (BFS/A*)."
    ]
    font = pygame.font.SysFont(None, 25)
    for i, line in enumerate(instructions):
        text_surface = font.render(line, True, (0, 0, 0))
        win.blit(text_surface, (10, 100 + i * 20))


def draw_text(win, text, pos, font_size=30, color=(0, 0, 0)):
    """Draw text to the screen."""
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    win.blit(text_surface, pos)


def randomize_start_and_goal():
    """Randomize the start and goal points ensuring they are not the same."""
    global start, goal
    start = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
    goal = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
    while goal == start:
        goal = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))


def calculate_time_limit_dynamic(start_x,start_y,end_x,end_y,obstacles):
    """Calculate the shortest path and set the timer dynamically."""
    parent, path_found, elapsed_time = search_path_bfs(start_x, start_y, end_x, end_y,obstacles)
    return round((elapsed_time*1e4)*2 +3,2)



def reset_game(reset_start_goal=False):
    """Reset the game state."""
    global grid, open_set, came_from, searched, path, finished, elapsed_time, win_message, level_time_limit
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    open_set, came_from, searched = [], {}, set()
    finished = False
    elapsed_time = 0
    win_message = ""
    if reset_start_goal:
        randomize_start_and_goal()
        level_time_limit = calculate_time_limit_dynamic(start[0], start[1], goal[0], goal[1], grid)

global level_time_limit 
randomize_start_and_goal()
level_time_limit = calculate_time_limit_dynamic(start[0], start[1], goal[0], goal[1], grid)



def main():
    global start, goal, difficulty, time_taken
    time_taken = 0
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pathfinding Algorithm")
    clock = pygame.time.Clock()

    randomize_start_and_goal()  # Initial random positions
   



    running = True
    path = []
    finished = False
    start_time = None

    while running:
        win.fill(WHITE)
        draw_grid(win)
        draw_instructions(win)

        draw_path(win, path)
        
        
        


        
        # Display current difficulty
        draw_text(win, f"Difficulty: {difficulty}", (10, 10), font_size=25)
        
        # Display target and elapsed time
        draw_text(win, f"Target Time: {level_time_limit}s", (10, 40), font_size=25)
        draw_text(win, f"Time Taken: {time_taken}s", (10, 70), font_size=25)

        if time_taken >= level_time_limit and finished:
            draw_text(win, "You won! Would you like to go to the next level?", (WIDTH // 2 - 250, HEIGHT // 2 - 50), font_size=30,color='green')
        if finished and time_taken < level_time_limit :
            draw_text(win, "You lost press N to reset", (WIDTH // 2 - 150, HEIGHT // 2), font_size=30,color='red')
            
        

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                row, col = y // TILE_SIZE, x // TILE_SIZE
                if (row, col) != start and (row, col) != goal:
                    grid[row][col] = -1
            elif pygame.mouse.get_pressed()[2]:
                x, y = pygame.mouse.get_pos()
                row, col = y // TILE_SIZE, x // TILE_SIZE
                if (row, col) != start and (row, col) != goal:
                    grid[row][col] = 0        
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and goal and not finished:
                    # Measure algorithm computation time
                    start_time = time.time()
                    if difficulty == 'normal':
                        parent, path_found, elapsed_time = search_path_bfs(start[0], start[1], goal[0], goal[1], grid)
                        if path_found:
                            path = []
                            current = goal
                            while current in parent:
                                path.append(current)
                                current = parent[current]
                            path.reverse()
                    elif difficulty == 'hard':
                        path, g_score, f_score, searched, elapsed_times = a_star(start, goal)
                    finished = True
                    end_time = time.time()
                    time_taken = round(float(end_time - start_time)*1e4,2)
                    
                    # Check win condition
                    
                    
                elif event.key == pygame.K_TAB:
                    difficulty = 'hard' if difficulty == 'normal' else 'normal'
                elif event.key == pygame.K_r:
                    reset_game()
                    finished = False
                    path =[]
                    time_taken = 0
                elif event.key == pygame.K_y and finished:  # "Yes" to next level
                    reset_game(reset_start_goal=True)
                    finished = False
                    path =[]
                    time_taken = 0
                elif event.key == pygame.K_n and finished:  # "No" to reset current level
                    reset_game()
                    finished = False
                    path=[]
                    time_taken=0


        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
