import os
import sys
from collections import defaultdict
from collections.abc import Iterable, Collection
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

import parselife

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


def write_cells_txt(grid: Grid, symbols: str = '.O'):
	for row in grid:
		print(''.join(symbols[c] for c in row).rstrip(symbols[0]))


def create_animated_gif(
		file: FileType,
		live_cells: Iterable[Coord],
		grid_x: int,
		grid_y: int,
		width: int,
		height: int,
		steps: int,
		step_time: int,
		scale: int,
		grid: int = 0,
		live_color: str = 'black',
		dead_color: str = 'white',
		grid_color: str = 'lightgray',
		info=False,
		generations_per_step=1):

	font = ImageFont.truetype('FSEX300.ttf', 16)

	def create_image(generation):
		image = Image.new('RGB', (width * scale - grid, height * scale - grid), dead_color)
		draw = ImageDraw.Draw(image)
		for x, y in live_cells:
			x -= grid_x
			y -= grid_y
			draw.rectangle((
				x * scale, 
				y * scale,
				(x + 1) * scale - 1 - grid,
				(y + 1) * scale - 1 - grid), fill=live_color)
		if grid:
			for x in range(1, width):
				x = x * scale - 1
				draw.rectangle((x - grid + 1, 0, x, height * scale), fill=grid_color)
			for y in range(1, height):
				y = y * scale - 1
				draw.rectangle((0, y - grid + 1, width * scale, y), fill=grid_color)

		if info:
			draw.text((2, height * scale - 16), f"Generation {generation}", info, font=font)
				
		return image

	live_cells = set(live_cells)
	head = create_image(0)
	frames = []
	for step in range(1, steps):
		gen = step * generations_per_step
		prev = live_cells
		live_cells = advance(live_cells, generations_per_step - 1)
		live_cells = set(generate(live_cells))
		print(f"{gen}/{steps * generations_per_step}", end='\r')
		frames.append(create_image(gen))
		if live_cells == prev:
			step_time = [step_time] * step + [step_time * (steps - step - 1)]
			break
	print('Saving GIF...')
	head.save(
		file,
		save_all=True,
		append_images=frames,
		duration=step_time,
		loop=0)


def bounds(width, height, pad_width, pad_height):
	return -pad_width, -pad_height, width + 2 * pad_width, height + 2 * pad_height


def test():
	import os
	file = 'rle/rpentomino.rle'
	# -50, -24, 100, 48
	live_cells, width, height = parselife.parse(file)
	gen = 0
	while True:
		os.system('cls')
		write_cells_txt(get_grid(live_cells, -50, -24, 100, 48), ['  ', '()'])
		try:
			if input(f"Generation {gen:<6} Population: {len(live_cells):<6}"):
				break
		except KeyboardInterrupt:
			break
		live_cells = list(generate(live_cells))
		gen += 1


if __name__ == '__main__':
	file = 'rle/blockstacker.rle'
	live_cells, width, height = parselife.parse(file)
	create_animated_gif(
		'output.gif',
		live_cells,
		# bounds(width, height, 1, 1),
		341 - 80, 283 - 80, 160, 160,
		630 * 6,  # steps
		20,  # interval
		3,  # scale
		0,  # grid
		'lime', 'black', '#222',
		generations_per_step=1,
	)
