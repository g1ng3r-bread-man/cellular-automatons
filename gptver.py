import pygame
import random
import numpy as np

# --- Constants ---
CELL_SIZE = 5  # pixels
ROWS = 150
COLS = 280
FPS = 10

# --- States ---
DEAD = 0
RED = 1
RRF1 = 2
RRF2 = 3
BLUE = 4
BRF1 = 5
BRF2 = 6

# Colors
COLOR_MAP = {
    DEAD: (0, 0, 0),
    RED: (255, 0, 0),
    RRF1: (255, 70, 70),
    RRF2: (255, 140, 140),
    BLUE: (0, 0, 255),
    BRF1: (70, 70, 255),
    BRF2: (140, 140, 255)
}

# --- Initialize grids ---
grid = np.zeros((ROWS, COLS), dtype=np.uint8)
new_grid = np.zeros_like(grid)

# --- Functions ---

def drawgrid():
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, COLOR_MAP[grid[r, c]],
                             (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def count_neighbors(mask):
    # counts neighbors with wrap-around
    return (
        np.roll(mask, 1, 0) + np.roll(mask, -1, 0) +
        np.roll(mask, 1, 1) + np.roll(mask, -1, 1) +
        np.roll(np.roll(mask, 1, 0), 1, 1) +
        np.roll(np.roll(mask, 1, 0), -1, 1) +
        np.roll(np.roll(mask, -1, 0), 1, 1) +
        np.roll(np.roll(mask, -1, 0), -1, 1)
    )

def starwars_step():
    global grid
    red_mask = (grid == RED)
    blue_mask = (grid == BLUE)

    red_neigh = count_neighbors(red_mask)
    blue_neigh = count_neighbors(blue_mask)
    total = red_neigh + blue_neigh

    new_grid[:] = grid

    # Refractory progression
    new_grid[grid == RRF1] = RED
    new_grid[grid == BRF1] = BLUE
    new_grid[grid == RRF2] = DEAD
    new_grid[grid == BRF2] = DEAD

    # Alive/death masks
    alive = (grid == RED) | (grid == BLUE)
    survive = alive & ((total == 2) | (total == 3))
    die = alive & ~survive

    new_grid[die & (grid == RED)] = RRF1
    new_grid[die & (grid == BLUE)] = BRF1

    # Majority calculation
    maj_red = red_neigh > blue_neigh
    maj_blue = blue_neigh > red_neigh
    stalemate = red_neigh == blue_neigh

    new_grid[survive & maj_red] = RED
    new_grid[survive & maj_blue] = BLUE
    new_grid[survive & stalemate] = DEAD

    # Birth
    birth = (grid == DEAD) & (total == 3)
    new_grid[birth & maj_red] = RED
    new_grid[birth & maj_blue] = BLUE
    new_grid[birth & stalemate] = DEAD

    grid[:, :] = new_grid

def edge_spawners(blob_size=4, rate=3):
    """Spawn random blobs along left (red) and right (blue) edges."""
    for _ in range(rate):
        # Left edge (red)
        r_start = random.randint(0, ROWS - blob_size)
        c_start = 0
        for r in range(r_start, r_start + blob_size):
            for c in range(c_start, c_start + blob_size):
                grid[r, c] = RED

        # Right edge (blue)
        r_start = random.randint(0, ROWS - blob_size)
        c_start = COLS - blob_size
        for r in range(r_start, r_start + blob_size):
            for c in range(c_start, COLS):
                grid[r, c] = BLUE

# --- Pygame setup ---
pygame.init()
screen = pygame.display.set_mode((COLS*CELL_SIZE, ROWS*CELL_SIZE))
pygame.display.set_caption("Star Wars Cellular Automaton")
clock = pygame.time.Clock()

# --- Main loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    edge_spawners(blob_size=4, rate=3)
    starwars_step()
    drawgrid()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
