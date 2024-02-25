import bisect
import pygame

if not pygame.get_init():
    pygame.init()

class Cell():
    def __init__(self, pos : tuple[int, int]):
        self.f_cost : int = 0
        self.pos : tuple[int, int] = pos
        self.parent : "Cell" = None
        self.g_cost = 0
        self.h_cost = 0
        self.direction = None
        self.distance = 0
        self.distance_to_next = 0
    
    def get_f_cost(self):
        return self.g_cost + self.h_cost

def get_direction(a_cell : Cell, b_cell : Cell):
    return (b_cell.pos[0] - a_cell.pos[0], b_cell.pos[1] - a_cell.pos[1])
    
def get_distance(a_cell : Cell, b_cell : Cell):
    dif_pos = [abs(b_cell.pos[0] - a_cell.pos[0]), abs(b_cell.pos[1] - a_cell.pos[1])]

    if dif_pos[0] < dif_pos[1]:
        return 14 * dif_pos[0] + 10 * (dif_pos[1] - dif_pos[0])
    else:
        return 14 * dif_pos[1] + 10 * (dif_pos[0] - dif_pos[1])

def cell_neighbours(cell : Cell, player_pos : tuple):
    neighbours = []
    for j in range(-1, 2):
        for i in range(-1, 2):
            if j == 0 and i == 0:
                continue
            check_x = cell.pos[0] + i
            check_y = cell.pos[1] + j
            if not (player_pos[0] - 18 <= check_x < player_pos[0] + 18) or not (player_pos[1] - 10 <= check_y < player_pos[1] + 10):
                continue
            ng = Cell((check_x, check_y))
            neighbours.append(ng)
    return neighbours

def find_way(start_pos, end_pos, blocks_pos : list[tuple]):

    if not (start_pos[0] - 18 <= end_pos[0] < start_pos[0] + 18) or not (start_pos[1] - 10 <= end_pos[1] < start_pos[1] + 10):
        return PathData()
    elif end_pos in blocks_pos:
        return PathData()

    opened_cell = []
    opened_cell_pos = []
    closed_cell_pos : list[tuple] = []
    start_node = Cell(start_pos)
    end_node = Cell(end_pos)
    start_node.h_cost = get_distance(start_node, end_node)

    found = False
    current = None
    opened_cell.append(start_node)
    opened_cell_pos.append(start_node.pos)

    timer = 0
    clock = pygame.Clock()

    while not found:
        timer += clock.tick()
        if timer > 50:
            return PathData()
        try:
            current = opened_cell[0]
        except:
            return PathData()
        opened_cell.remove(current)
        opened_cell_pos.remove(current.pos)
        closed_cell_pos.append(current.pos)
        if current.pos == end_node.pos:
            found = True
            return retrace_path(current, start_node)

        for neighbour in cell_neighbours(current, start_pos):
            if neighbour.pos in blocks_pos or neighbour.pos in closed_cell_pos:
                continue
            new_cost = current.g_cost + get_distance(current, neighbour)
            if new_cost < current.g_cost or neighbour.pos not in opened_cell_pos:
                neighbour.g_cost = new_cost
                neighbour.h_cost = get_distance(neighbour, end_node)
                neighbour.parent = current
                if neighbour.pos not in opened_cell_pos:
                    bisect.insort(opened_cell, neighbour, key=lambda c : c.get_f_cost())
                    opened_cell_pos.append(neighbour.pos)

class PathData():
    def __init__(self):
        self.cells : list[Cell] = []
        self.distance : float = 0

def retrace_path(cell : Cell, start_cell : Cell) -> PathData:
    path = PathData()
    current_cell = cell
    current_cell.distance = 0
    while current_cell.pos != start_cell.pos:
        current_cell.parent.direction = get_direction(current_cell.parent, current_cell)
        if abs(current_cell.parent.direction[0]) == abs(current_cell.parent.direction[1]):
            distance = 22.4
        else:
            distance = 16
        current_cell.parent.distance = distance + path.distance
        current_cell.parent.distance_to_next = distance
        path.distance += distance
        path.cells.append(current_cell)
        current_cell = current_cell.parent
    else:
        path.cells.append(current_cell)
    path.cells.reverse()
    return path