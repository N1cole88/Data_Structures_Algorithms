import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Visualizer")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        # If red, we already looked at it
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == BLUE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = BLUE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
        # Right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    # Manhattan distance (L)
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(width):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid


def draw_grid(win, rows, width):
    # Draw grid lines
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()


# Function that translates the mouse click to which node to be updated
def get_click_position(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


def algorithm(draw, grid, start, end):
    draw()
    count = 0  # To break ties, we wil pop off whatever was inserted first
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    distTo = {node: float("inf") for row in grid for node in row}
    distTo[start] = 0
    distTo_plus_h = {node: float("inf") for row in grid for node in row}
    distTo_plus_h[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start} # Keeps track of the items in the priority queue
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # Pop one from PQ and get the node
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            # We are done with the path and then we need to draw the path
            reconstruct_path(came_from, end, draw)
            return True

        for neighbor in current.neighbors:
            temp_distTo = distTo[current] + 1

            # If we found a shorter way to reach this neighbor
            if temp_distTo < distTo[neighbor]:
                came_from[neighbor] = current
                distTo[neighbor] = temp_distTo
                distTo_plus_h[neighbor] = distTo[neighbor] + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((distTo_plus_h[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()
        # If the node that we just considered is not the start, we won't consider it again and it won't be
        # added to the open_set
        if current != start:
            current.make_closed()

    return False


def reconstruct_path(came_from, current, draw):
    current.make_end()
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()
    current.make_start()
    print("Found the path :))")
    draw()


def main(win, width):
    ROWS = 80
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:  # Left click
                pos = pygame.mouse.get_pos()
                row, col = get_click_position(pos, ROWS, width)
                node = grid[row][col]
                # We can change the end node but once we change the start node, we should reset the end node
                if not start and not end:
                    start = node
                    start.make_start()
                elif not end and start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()
                elif node == start:
                    node.reset()
                    start = None
                    end.reset()
                    end = None
                elif node == end:
                    node.reset()
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    print("Starting the algorithm.....")
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                if event.key == pygame.K_c:
                    print("Clearing the window....")
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WINDOW, WIDTH)
