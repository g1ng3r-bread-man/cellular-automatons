import pygame
import random

#constants
CELL_SIZE = 5 #pixels

running = True
redtotal = 0
bluetotal = 0

#size (in cells)
ROWS = 150
COLS = 280





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

grid = [[DEAD for _ in range(COLS)] for _ in range(ROWS)]
new_grid = [[DEAD for _ in range(COLS)] for _ in range(ROWS)]

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
    for r in range(ROWS):
        for c in range(COLS):
            state = grid[r][c]
            color = state_to_colour(state)
            pygame.draw.rect(screen, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def starwars():
    bluetemp = 0
    redtemp = 0
    global grid, new_grid
    for row in range(1, rows-1):
        for col in range(1, cols-1):
            current = grid[row][col]
            if current == RED:
                redtemp += 1
            elif current == BLUE:
                bluetemp += 1
    #neutral cannot change other cells colours
    #neutral cannot count to neighbours
    #neutral can be converted 
            nn = grid[row-1][col]
            nw = grid[row-1][col-1]
            ww = grid[row][col-1]
            sw = grid[row+1][col-1]
            ss = grid[row+1][col]
            se = grid[row+1][col+1]
            ee = grid[row][col+1]
            ne = grid[row-1][col+1]
            neighbours = [nn,nw,ww,sw,ss,se,ee,ne]
            redc = count(neighbours, RED)
            bluec = count(neighbours, BLUE)
            neutralc = count(neighbours, NEUTRAL)

            total = redc+bluec+neutralc

            #refractory progression
            if current in (RRF1, RRF2, BRF1, BRF2, NRF1, NRF2):
                if current == RRF1:
                    new_grid[row][col] = RRF2
                elif current == BRF1:
                    new_grid[row][col] = BRF2
                elif current == NRF1:
                    new_grid[row][col] = NRF2

                elif current in (RRF2, BRF2, NRF2):
                    new_grid[row][col] = 0

            #death/refractory creation
            elif current in (RED, BLUE, NEUTRAL):
                if total not in (3,4,5):
                    if current == RED:
                        new_grid[row][col] = RRF1
                    if current == BLUE:
                        new_grid[row][col] = BRF1
                    if current == NEUTRAL:
                        new_grid[row][col] = NRF1
            #conversion
                else:
                    if redc > total/2:
                        new_grid[row][col] = RED
                    elif bluec > total/2:
                        new_grid[row][col] = BLUE
                    else:
                        new_grid[row][col] = NEUTRAL

            #birth logic
            elif current == 0:
                if total in (2,):
                    if bluec > total/2:
                        new_grid[row][col] = BLUE
                    elif redc > total/2:
                        new_grid[row][col] = RED
                    else: new_grid[row][col] = NEUTRAL
                else: new_grid[row][col] = current
    grid, new_grid = new_grid, grid
    global redtotal, bluetotal
    bluetotal = bluetemp
    redtotal = redtemp


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
    for _ in range((redtotal // 10000 + 1)):
        # --- Left edge (red blobs) ---
        r_start = random.randint(0, ROWS - blob_size)
        c_start = 0  # leftmost column
        height = random.randint(2, blob_size)
        width = random.randint(2, blob_size)
        for r in range(r_start, min(r_start + height, ROWS)):
            for c in range(c_start, min(c_start + width, COLS)):
                grid[r][c] = RED

    for _ in range((bluetotal // 10000 + 1)):
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
        
    edge_spawners(blob_size=4, rate=3)
    #update_starwars()
    starwars()
    drawgrid()
    pygame.display.flip()
    clock.tick(800)
