import os
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

Coord = tuple[int, int]
Grid = list[list[bool]]
FileType = str | bytes | os.PathLike


NEIGHBORHOOD = [
	(-1,  1), (0,  1), (1,  1),
	(-1,  0),          (1,  0),
	(-1, -1), (0, -1), (1, -1),
]


@dataclass
class Cell:
	live: bool = False
	neighbors: int = 0


def get_cell_table(live_cells: Iterable[Coord]):
	cells = defaultdict(Cell)
	for x, y in live_cells:
		cells[(x, y)].live = True
		for dx, dy in NEIGHBORHOOD:
			cells[(x + dx, y + dy)].neighbors += 1
	return cells


def generate(live_cells: Iterable[Coord]):
	for coord, cell in get_cell_table(live_cells).items():
		if cell.neighbors == 3 or (cell.neighbors == 2 and cell.live):
			yield coord


def life_generator(live_cells, gen=0):
	yield live_cells, gen
	print(gen)
	while True:
		live_cells = list(generate(live_cells))
		gen += 1
		print(gen)
		yield live_cells, gen


def advance(live_cells: Iterable[Coord], steps: int):
	for _ in range(steps):
		live_cells = list(generate(live_cells))
	return live_cells


def bounding_box(live_cells: Iterable[Coord]):
	min_x = sys.maxsize
	min_y = sys.maxsize
	max_x = ~sys.maxsize
	max_y = ~sys.maxsize
	for x, y in live_cells:
		min_x = min(x, min_x)
		min_y = min(y, min_y)
		max_x = max(x, max_x)
		max_y = max(y, max_y)
	if min_x == sys.maxsize:
		raise ValueError
	return min_x, min_y, max_x - min_x + 1, max_y - min_y + 1


def get_grid(
		live_cells: Iterable[Coord], 
		grid_x: int,
		grid_y: int,
		width: int,
		height: int):
			
	grid = [[False] * width for _ in range(height)]
	for x, y in live_cells:
		x -= grid_x
		y -= grid_y
		if 0 <= x < width and 0 <= y < height:
			grid[y][x] = True
	return grid
