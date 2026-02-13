import pygame
import random
import numpy

#constants
CELL_SIZE = 3 #pixels

running = True
redtotal = 0
bluetotal = 0

#size (in cells)
ROWS = 300
COLS = 500





#states
DEAD = 0

RED = 1
RRF1 = 2
RRF2 = 3

BLUE = 4
BRF1 = 5
BRF2 = 6

NEUTRAL = 7 #magenta
NRF1 = 8
NRF2 = 9

grid = numpy.zeros((ROWS, COLS), dtype=numpy.uint8)
new_grid = numpy.zeros((ROWS, COLS), dtype=numpy.uint8)

rows = len(grid)
cols = len(grid[0])

def state_to_colour(state):
    if state == 0:
        return (0,0,0)
    if state == 1:
        return (255,0,0)
    if state == 2:
        return (255,70,70)
    if state == 3:
        return (255,140, 140)
    if state == 4:
        return (0,0,255)
    if state == 5:
        return (70,70,255)
    if state == 6:
        return (140,140,255)
    if state == 7:
        return (255,0,255)
    if state == 8:
        return (255,70,255)
    if state == 9:
        return (255,140,255)

def count(list, num):
    numlist = []
    for i in list:
        if i == num:
            numlist.append(i)
    return len(numlist)

def drawgrid():
    # Create an empty RGB array
    rgb_array = numpy.zeros((ROWS, COLS, 3), dtype=numpy.uint8)

    rgb_array[grid == RED] = [255, 0, 0]
    rgb_array[grid == RRF1] = [255, 70, 70]
    rgb_array[grid == RRF2] = [255, 140, 140]

    rgb_array[grid == BLUE] = [0, 0, 255]
    rgb_array[grid == BRF1] = [70, 70, 255]
    rgb_array[grid == BRF2] = [140, 140, 255]

    rgb_array[grid == NEUTRAL] = [255, 0, 255]
    rgb_array[grid == NRF1] = [255, 70, 255]
    rgb_array[grid == NRF2] = [255, 140, 255]

    # Transpose to convert (ROWS, COLS, 3) to (COLS, ROWS, 3)
    rgb_array = numpy.transpose(rgb_array, (1, 0, 2))
    
    # Scale the small RGB array to pixel size
    surface = pygame.surfarray.make_surface(rgb_array)
    surface = pygame.transform.scale(surface, (COLS*CELL_SIZE, ROWS*CELL_SIZE))
    screen.blit(surface, (0, 0))

def starwars():
    global grid
    red_mask = (grid == RED)
    blue_mask = (grid == BLUE)
    neutral_mask = (grid == NEUTRAL)

    # Neighbor counting WITHOUT wrapping
    def count_neighbors(mask):
        padded = numpy.pad(mask, 1, mode='constant', constant_values=0)
        neighbors = numpy.zeros_like(mask, dtype=int)
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                neighbors += padded[1+dr:1+dr+ROWS, 1+dc:1+dc+COLS]
        
        return neighbors

    red_neighbours = count_neighbors(red_mask)
    blue_neighbours = count_neighbors(blue_mask)
    neutral_neighbours = count_neighbors(neutral_mask)
    #neutral cannot change other cells colours
    #neutral cannot count to neighbours
    #neutral can be converted 
    total = red_neighbours + blue_neighbours
    new_grid = grid.copy()

    #refractory progression
    new_grid[grid == RRF1] = RRF2
    new_grid[grid == BRF1] = BRF2
    new_grid[grid == NRF1] = NRF2
    new_grid[grid == RRF2] = DEAD
    new_grid[grid == BRF2] = DEAD
    new_grid[grid == NRF2] = DEAD

            #death/refractory creation
    alive = (grid == RED) | (grid == BLUE) | (grid == NEUTRAL)
    survive = alive & ((total == 3) | (total == 4) | (total == 5))
    die = alive & ~survive

    new_grid[die & (grid ==RED)] = RRF1
    new_grid[die & (grid ==BLUE)] = BRF1
    new_grid[die & (grid ==NEUTRAL)] = NRF1

        #conversion
    maj_red = red_neighbours > (total/2)
    maj_blue = blue_neighbours > (total/2)
    maj_neutral = neutral_neighbours > (total/2)
    stalemate = ((total > 0) & (red_neighbours == blue_neighbours))# & (blue_neighbours == neutral_neighbours) & (neutral_neighbours == red_neighbours))
    
    new_grid[survive & maj_blue] = BLUE
    new_grid[survive & maj_red] = RED
    new_grid[survive & stalemate] = NEUTRAL
    #new_grid[survive & maj_neutral] = NEUTRAL

            #birth logic
    birth = (grid == DEAD) & ((total == 2))
    new_grid[birth & maj_blue] = BLUE
    new_grid[birth & maj_red] = RED
    new_grid[birth & stalemate] = NEUTRAL
    #new_grid[birth & maj_neutral] = NEUTRAL
    grid[:, :] = new_grid
    





def conway():
    global grid, new_grid
    for row in range(1, rows-1):
        for col in range(1, cols-1):
            current = grid[row][col]
            nn = grid[row-1][col]
            nw = grid[row-1][col-1]
            ww = grid[row][col-1]
            sw = grid[row+1][col-1]
            ss = grid[row+1][col]
            se = grid[row+1][col+1]
            ee = grid[row][col+1]
            ne = grid[row-1][col+1]
            neighbours = [nn,nw,ww,sw,ss,se,ee,ne]
            bluec = count(neighbours, BLUE)

            if current == DEAD and (bluec == 3):
                new_grid[row][col] = BLUE
            elif current == BLUE and bluec not in (2,3):
                new_grid[row][col] = DEAD
            else: new_grid[row][col] = current
    grid, new_grid = new_grid, grid




def edge_spawners(blob_size=5, rate=3):
    """
    Spawns random blobs along the left and right edges.
    blob_size: max width/height of each blob
    rate: number of blobs per frame
    """
    for _ in range((rate)):
        # --- Left edge (red blobs) ---
        r_start = random.randint(0, ROWS - blob_size)
        c_start = 0  # leftmost column
        height = random.randint(2, blob_size)
        width = random.randint(2, blob_size)
        for r in range(r_start, min(r_start + height, ROWS)):
            for c in range(c_start, min(c_start + width, COLS)):
                grid[r][c] = RED

    for _ in range((rate)):
        # --- Right edge (blue blobs) ---
        r_start = random.randint(0, ROWS - blob_size)
        c_start = COLS - blob_size  # rightmost columns
        height = random.randint(2, blob_size)
        width = random.randint(2, blob_size)
        for r in range(r_start, min(r_start + height, ROWS)):
            for c in range(c_start, COLS):
                grid[r][c] = BLUE






#game loop
pygame.init()
screen = pygame.display.set_mode((COLS*CELL_SIZE, ROWS*CELL_SIZE))
pygame.display.set_caption("Star Wars Cellular Automaton")
clock = pygame.time.Clock()

while running == True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    edge_spawners(blob_size=4, rate=2)
    starwars()
    drawgrid()
    pygame.display.flip()
    clock.tick(20)
